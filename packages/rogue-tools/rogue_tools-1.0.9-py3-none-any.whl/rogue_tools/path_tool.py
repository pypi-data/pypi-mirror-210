
import os
import stat
import sys
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
import traceback
from rogue_tools import path_tool,file_tool,time_tool

pool = None
def init_pool():
    '''
    用来加快删除文件夹操作的进程
    '''
    global pool
    if pool==None:
        pool = ThreadPoolExecutor(max_workers=3)
        print('加载ThreadPoolExecutor')


'''        
#####################################################################
#                             简易方法                               #    
#####################################################################   
'''
def copy_(src,tar):


    #print(f'copy:{src} -->> {tar}')
    src_status =  get_path_status(src)
    tar_status =  get_path_status(tar)
    if src_status in (3,4):
        print(f'can not find src :\n{src}')
        return False
    if src_status==1 and tar_status in (1,3):           # 文件到文件
        shutil.copyfile(src, tar)
        return True

    elif src_status==1 and tar_status in (2,4):       # 文件到目录
        make_folder(tar)
        base_name = get_file_base_name(src)
        tar = join_path(tar,base_name)
        copy_(src, tar)
        return True

    if src_status==2 and tar_status in (1,3):       # 目录到文件
        # 尝试将一个文件夹复制为文件
        print(f'can not copy folder to file.\n[{src}]\n-->>[{tar}]')
        return False
    if src_status==2 and tar_status in (2,4):   # 目录到目录
        make_folder(tar)
        get_all_permission(tar)
        sub_file_list = get_sub_files(src,full_path=False)
        for sub_file in sub_file_list:
            copy_(join_path(src,sub_file),tar)
        return True
        
def copy(src, tar,is_cover=False):
    '''
    通用的复制文件或者文件夹
    is_cover = True 可以不用删除旧文件夹,直接覆盖过去
    仅支持本地copy
    '''
    #print(f'copy:{src} -->> {tar}')
    if type(src) in [tuple,list]:
        for obj in src:
            copy(obj,tar,is_cover)
        return
    # copy文件
    if os.path.isfile(src):
        #  复制到目录
        if os.path.isdir(tar):
            base_name = get_file_base_name(src)
            return shutil.copyfile(src, join_path(tar,base_name))
        # 复制到文件
        if os.path.isfile(tar):
            return shutil.copyfile(src, tar)

        else:
            make_folder(get_file_dirname(tar))
            copy(src, tar)
    # copy文件夹
    else:
        # 源文件不存在
        if not os.path.exists(src):
            raise Exception(f'can not find src :\n{src}')
        if os.path.isfile(tar):
            # 尝试将一个文件夹复制为文件
            raise Exception(f'can not copy folder to file.\n[{src}] -->>  [{tar}]')
        
        # 覆盖模式
        if is_cover:
            sub_file_list = get_sub_files(src)
            for sub_file in sub_file_list:
                sub_file = sub_file[len(src):]
                copy(join_path(src,sub_file), join_path(tar,sub_file),is_cover)
        # 普通模式，确保目标文件夹不存在才可以进行
        else:
            try:
                shutil.copytree(src, tar)
            except Exception:
                print(f'复制失败：[{src}]-->[{tar}]  可尝试添加参数[is_cover = True]')
                raise Exception(traceback.format_exc())
                


def get_file_base_name(path,is_postfix=True):
    '''
    获取文件名
    '''
    path = os.path.normpath(path)
    rs = os.path.basename(path)

    if is_postfix:
        return rs
    else:
        name,postfix = os.path.splitext(rs)
        return name
     
def get_file_type(path):
    '''
    获取文件类型
    '''
    path = os.path.normpath(path)
    rs = os.path.basename(path)
    name,postfix = os.path.splitext(rs)
    return postfix


def get_file_dirname(path):
    return os.path.dirname(path)

def copy_file(path,new_path):
    if not os.path.exists(get_file_dirname(new_path)):
        make_folder(get_file_dirname(new_path))
    shutil.copy(path,new_path)

def del_(floder_or_path,is_keep_folder=False):
    if os.path.isdir(floder_or_path):
        del_folder(floder_or_path,is_keep_folder)
    else:
        del_file(floder_or_path)
        
def del_file(path):
    if os.path.exists(path):  # 如果文件存在
        os.remove(path)


'''        
#####################################################################
#                             文件夹方法                             #    
#####################################################################   
'''
def rename(name,new_name):
    '''
    只能改文件夹
    '''
    try:
        if os.path.exists(name):
            get_all_permission(name)
            os.rename(name,new_name)
    except Exception:
        traceback.print_exc()

def move(src,dst):
    '''
    递归的去移动文件，它类似mv命令，其实就是重命名。
    '''
    try:
        if os.path.exists(src):
            shutil.move(src, dst)
    except Exception:
        traceback.print_exc()

def get_folder_objs(path,full_path=True,include='*',exclude=None):
    rs_list=[]
    if type(exclude) != list:
        exclude=[exclude]
    if type(include) != list:
        include=[include]


def get_sub_files(path,full_path = True,include_folder=False,include='*',exclude=None,step=0):
    rs_list=[]
    if type(exclude) != list:
        exclude=[exclude]
    if type(include) != list:
        include=[include]

    for root , dirs , files in os.walk(path,topdown=True):
        for name in files:
            file_full_path = os.path.normpath(os.path.join(root,name))
            if __str_list_filter(file_full_path,exclude,include):
                if full_path:
                    rs_list.append(file_full_path)
                else:
                    rs_list.append(name)
        if not include_folder :
            continue

        for name in dirs:
            file_full_path = os.path.normpath(os.path.join(root,name))
            if __str_list_filter(file_full_path,exclude,include):
                if full_path:
                    rs_list.append(file_full_path)
                else:
                    rs_list.append(name)
        step -= 1
        if step == 0:
            return rs_list
    return rs_list

def __str_list_filter(src_str,exclude_list,include_list):
    for find_str in exclude_list:
        if find_str:
            if src_str.find(find_str)>-1:
                return False
    if include_list==['*']:
        return True
    for find_str in include_list:
        if find_str:
            if src_str.find(find_str)>-1:
                return True
    return False


def clear_folder(folder_path,include_str='*',exclude=None):
    '''
    使用递归的方式,清空一个文件夹以及子文件夹,可以应用get_sub_files的过滤规则
    '''
    sub_list = get_sub_files(folder_path , include=include_str , exclude=exclude)
    for sub_file in sub_list:
        try:
            os.remove(sub_file)
        except Exception:
            traceback.print_exc()

def make_folder(folder_path):
    '''
    创建一个文件夹
    '''
    if os.path.exists(folder_path):
        return
    if folder_path in ('',None):
        return
    try:
        #print(f'make_folder:{folder_path}')
        os.makedirs(folder_path,mode=0o777)
    except FileExistsError:
        return
    except Exception:
        traceback.print_exc()
def del_folder(path,is_keep_folder=True):
    '''
    将此目录改名之后,慢慢清理,使用多线程,可以节省很多时间~~~
    '''
    global pool
    init_pool()
    if os.path.exists(path):
        temp_time=int(time.time())
        temp_path=path+str(temp_time)
        try:
            rename(path,temp_path)
            pool.submit(_del_folder_thread,temp_path)
            time.sleep(0.1)
        except BaseException:
            print(f'无法删除，未关闭{path}')
            # 执行失败，大部分原因是文件夹没关闭
            # 尝试直接删除里面文件
            files = get_sub_files(path)
            for file in files:
                del_file(file)
    if is_keep_folder:
        make_folder(path)

       
def _del_folder_thread(path):
    if os.path.exists(path):
        get_all_permission(path)
        shutil.rmtree(path)

        
def get_all_permission(path):
    if os.path.isfile(path):
        os.chmod(path, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
        return
    for f in path_tool.get_sub_files(path):
        os.chmod(f, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)


    '''
    基于MD5进行对比,只按照子文件相对路劲作为key,MD5作为value
    例如 : D:\\a\\b 和 D:\\a\\new_b 进行比较。
    最后把文件提取到D:\\to_path,这个提取过程会保留目录结构
    '''



def pick_diff_file_list(src_folder_path , tar_folder_path , include_str='*' , exclude_str=None):
    '''
    基于MD5进行对比,只按照子文件相对路径作为key,MD5作为value
    例如 : D:\\a\\b 和 D:\\a\\new_b 进行比较。
    '''
    just_in_src=[]
    just_in_tar=[]
    update_list=[]

    src_list=pick_diff_file_handle(src_folder_path,include_str=include_str,exclude_str=exclude_str)
    tar_list=pick_diff_file_handle(tar_folder_path,include_str=include_str,exclude_str=exclude_str)

    diff_file_list =[]
    diff_file_list.extend(list(set(src_list).difference(set(tar_list))))
    diff_file_list.extend(list(set(tar_list).difference(set(src_list))))

    for diff_file in diff_file_list:
        if diff_file in src_list:
            just_in_src.append(diff_file)
        if diff_file in tar_list:
            just_in_tar.append(diff_file)

    same_file_list = list(set(src_list).intersection(set(tar_list)))
    for same_file in same_file_list:
        src_path = path_tool.join_path(src_folder_path,same_file)
        tar_path = path_tool.join_path(tar_folder_path,same_file)

        if file_tool.get_md5(src_path) != file_tool.get_md5(tar_path):
            update_list.append(same_file)

    return just_in_src,just_in_tar,update_list


def pick_diff_file_handle(folder_path,include_str='*',exclude_str=None):
    path_len=len(os.path.normpath(folder_path))
    rs_list=[]
    sub_list = path_tool.get_sub_files(folder_path,include_str=include_str,exclude_str=exclude_str)
    for sub_path in sub_list:
        rs_list.append(sub_path[path_len:len(sub_path)])
    return rs_list



'''        
#####################################################################
#                             其他方法                               #    
#####################################################################   
'''  
# 根目录path，一般是命令行所在的位置，也就是执行python xxxx.py的地方
def get_root_path():
    return os.getcwd()

# 启动脚本path,一般情况下，启动脚本.py会在根目录中
def get_main_path():
    return sys.path[0]

# 启动脚本name
def get_main_name():
    return sys.argv[0]

# 传入的这个方法的名字
def get_now_fuc_name(func):
    return func.__name__
def join_path(path1,*path2):
    path1 = path1 if isinstance(path1,str) else str(path1)
    if not isinstance(path2,tuple):
        path2 = (path2)
    for path_add in path2:
        path_add = path_add if isinstance(path_add,str) else str(path_add)
        if path_add.startswith('\\') or path_add.startswith('/'):
            path_add = path_add[1:len(path_add)]
        path1 = os.path.join(path1,path_add)

    return os.path.normpath(path1)
# 当前这一句，正在执行的py文件的路径
# os.path.realpath(__file__)

# 当前这一句，正在执行的py文件的目录
# os.path.split(os.path.realpath(__file__))[0]

# 当前这一句，正在执行的py文件的名字
# os.path.split(os.path.realpath(__file__))[1]

def get_path_status(path):
    '''
    一个路径的状态,默认结尾包含[.]的是文件,虽然文件夹也可以带[.],但不这样就没法搞了\n
    1 # 存在，且是文件\n
    2 # 存在，且是文件夹\n
    3 # 不存在，且是文件\n
    4 # 不存在，且是文件夹\n
    '''
    
    if os.path.isfile(path):
        return 1
    elif os.path.isdir(path):
        return 2
    base_name = get_file_base_name(path)
    if base_name.find('.')>-1:
        return 3
    else:
        return 4

def wait_folder_prepare(path):
    '''
    等待一个文件夹完全准备好文件,复制大文件的情况可能不适用(会提前占长度，导致失败)，通常是解压缩文件的时候
    '''
    file_list = get_sub_files(path)
    for file in file_list:
        wait_file_prepare(file)

def wait_file_prepare(path,time_out=600):
    total = 0
    start_time = time_tool.time_stamp_s()
    while True and time_tool.time_stamp_s() - start_time < time_out:
        time.sleep(2)
        temp = file_tool.get_file_size(path)
        #print(f'waiting file:{time_tool.time_stamp_s() - start_time}s , {int(temp/1024)}kb')
        if temp == total and temp > 0:
            return True
        else:
            total = temp
    return False

def is_exists(path):
    return os.path.exists(path)

def is_dir(path):
    return os.path.isdir(path)

def is_file(path):
    return os.path.isfile(path)