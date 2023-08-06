import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from rogue_tools import time_tool,win_tool,path_tool


class Android():
    def __init__(self) -> None:
        '''
        一般情况下，只连一个android可以连接
        '''
        self.device = None
        self.adb_path = 'rogue_tools\\adb\\adb.exe'
        self.default_scrcpy_window = 'scrcpy_window'
        #self.default_port = 5037
        self.device_list = self.get_device_list(60)
        if len(self.device_list)==0:
            raise Exception('\nWarning: \nNone android device has connected.')

    def get_device_list(self,wait_time=15):
        '''
        #获取已连接的设备
        '''
        rs_list=[]
        start_time = time_tool.time_stamp_s()
        while time_tool.time_stamp_s() - start_time < wait_time:
            f=os.popen(f'{self.adb_path} devices')
            cmd_rs=f.read()
            #print(f'get_device_list:{cmd_rs}')
            device_tup=cmd_rs.split('\n')
            if len(device_tup)>1 and len(device_tup[1]) > 4 :
                break
            time.sleep(1)
            f=os.popen(f'{self.adb_path} kill-server')
        for i in range(1,len(device_tup)):
            temp = device_tup[i][0:-7]
            if temp:
                rs_list.append(temp)

        return rs_list

    def set_device(self,device):
        if device in self.device_list:
            self.device = device
        else:
            raise Exception(f'DeviceError : [{device}] has not connected.')
        

    def adb_execute(self,cmd):
        adb = f'{self.adb_path} -s {self.device}' if self.device else 'adb'
        adb = f'{adb} {cmd}'
        print(f'*adb_execute:{adb}')
        rs = os.popen(adb)
        #time.sleep(1)
        return rs

    def install_apk(self,local_path , package_name , time_out=180 , is_replace = True,is_option_g=True):
        '''
        使用这个方法安装apk
        '''
        if is_replace and self.is_install(package_name):
            self.uninstall_apk(package_name)

        start_time = time_tool.time_stamp_s()
        pool = ThreadPoolExecutor(max_workers=3)
        try:
            future1 = pool.submit(self.__install_apk, local_path , is_option_g)
            while time_tool.time_stamp_s() - start_time < time_out:
                print(f'install_apk cost:{time_tool.time_stamp_s() - start_time}s')
                time.sleep(10)
                if self.is_install(package_name):
                    return time_tool.time_stamp_s() - start_time
            return -1
        except BaseException:
            traceback.print_exc()
        finally:
            pool.shutdown()
    def __install_apk(self,local_path,is_option_g):
        '''
        安装apk,并返回安装时长
        '''
        time_install=time_tool.time_stamp_s()
        cmd = f'install -g' if is_option_g else 'install'
        cmd = f'{cmd} {local_path}'
        try:
            self.adb_execute(cmd)
            return time_tool.time_stamp_s()-time_install
        except BaseException :
            traceback.print_exc()
            return -1

        
    def uninstall_apk(self,package_name):
        print(f'uninstalling:{package_name}')
        while self.is_install(package_name):
            self.adb_execute(f'uninstall {package_name}')
            time.sleep(3)


    def is_install(self,package_name):
        f=self.adb_execute('shell pm list packages')
        cmd_rs=f.read()
        if package_name in cmd_rs:
            return True
        else:
            return False

    def start_app(self,package_name):
        self.adb_execute(f'shell monkey -p {package_name} -v -v -v 1')
        
    def stop_app(self,package_name):
        self.adb_execute(f'shell am force-stop {package_name}')

    def rm(self,path):
        if path in ('/','/sdcard','/storage','/system'):
            raise Exception(f'rm error,for path = {path}')
        self.adb_execute(f'shell rm -rf {path}')
        
    def tar_folder(self,src_folder,target_full_path:str,wait_file = True):
        '''
        将某个文件夹打包
        '''
        #adb shell tar -cvf /sdcard/cache.tar /sdcard/cache
        target_full_path = target_full_path if target_full_path.endswith('.tar') else target_full_path + '.tar'
        self.adb_execute(f'shell tar -cvf {target_full_path} {src_folder}')
        # 要等待，就返回等待的结果，不等待就直接True
        if wait_file:
            return self.wait_file_prepare(target_full_path)
        return True
    def pull_file(self,file_or_files,local_folder,wait_file = True):
        '''
        拉取安卓文件,可能会报权限错误,这个无解
        一般先tar打包,再拉
        '''
        #adb pull /sdcard/Android/data/com.baitian.spacex.sx.bt/files/CustomAstralLog.log E:\\test
        if type(file_or_files)==list:
            for file in file_or_files:
                self.pull_file(file,local_folder)
        else:
            self.adb_execute(f'pull {file_or_files} {local_folder}')
            # 要等待，就返回等待的结果，不等待就直接True
            if wait_file:
                name = os.path.basename(file_or_files)
                return path_tool.wait_file_prepare(path_tool.join_path(local_folder,name))
            return True
    
    def get_file_size(self,file):
        #adb shell stat -c "%s"
        if file.endswith('/'):
            print(f'Warning!Your path [ {file} ] is folder,not file.Then you can see 3488')
        try:
            rs = self.adb_execute(f'shell stat -c "%s" {file}').read()
        except BaseException:
            rs = 0
            traceback.print_exc()
        return int(rs)

    def wait_file_prepare(self,file,time_out = 600):
        total = 0
        start_time = time_tool.time_stamp_s()
        while True and time_tool.time_stamp_s() - start_time < time_out:
            time.sleep(2)
            
            temp = self.get_file_size(file)
            print(f'waiting file:{time_tool.time_stamp_s() - start_time}s , {int(temp/1024)}kb')
            if temp == total and temp > 0:
                return True
            else:
                total = temp
        return False
    