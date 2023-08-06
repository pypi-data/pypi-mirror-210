import os
import hashlib
import time
import traceback
from rogue_tools import path_tool, time_tool,file_tool


def read_simple_text(path,my_encoding='utf8'):
    rs = ['']
    with open(path,"r",encoding=my_encoding) as f:
        rs = f.read().splitlines()
    return rs

def read_simple_text2(path,my_encoding='utf8'):
    rs = None
    with open(path,"r",encoding=my_encoding) as f:
        rs = f.read(file_tool.get_file_size(path))
    return rs

def write_str(path,write_string,my_mode="a+",my_encoding='utf8'):
    if not os.path.exists(path):
        base_dir = path_tool.get_file_dirname(path)
        path_tool.make_folder(base_dir)
    with open(path,my_mode,encoding=my_encoding) as f:
        f.write(write_string)

def write_lines(path,write_list,mode="a+",encoding='utf8'):
    temp=""
    for line in write_list:
        temp = f'{temp}{line}\n'
        #temp=temp+line+'\n'
    write_str(path,temp,my_mode=mode,my_encoding=encoding)

def new_file(path):
    if not os.path.exists(path):
        base_dir = path_tool.get_file_dirname(path)
        path_tool.make_folder(base_dir)
        write_str(path,'')

def clear_file(path):
    write_str(path,'',my_mode='w+')

def get_file_size(path):
    fsize = os.path.getsize(path)
    return fsize
def get_folder_size(path):
    total = 0
    sub_files = path_tool.get_sub_files(path)
    for sub_file in sub_files:
        total = total + get_file_size(sub_file)
    
    return total

def wait_file(path,time_out=600):
    '''
    等待一个文件可用，并且不再更改。
    适用于目标文件正在创建、下载、复制的情况
    最少需要2秒,默认最大等待600秒
    '''
    start_time = time_tool.time_stamp_s()
    last_bytes = None
    file_size  = 0
    while (time_tool.time_stamp_s()-start_time) < time_out:
        fo = None
        try:
            with open(path,'rb') as fo:
                fo.seek(-10,2)
                now_bytes = fo.read(10)
                now_size = get_file_size(path)
                # 读取文件的最后几个字节,如果不同，说明还不行
                # 读取文件的大小，如果文件大小还在变化，说明还不行
                if (last_bytes == now_bytes) and (file_size == now_size):
                    # 终于等到你，还好我没放弃！！！
                    return True
                last_bytes = now_bytes
                file_size = now_size
        except (FileNotFoundError,PermissionError,):
            continue
        finally:
            time.sleep(1)
    # 待到魂归故里时，只见白首不见君
    return False

def change_1024(size):
    if size < 1024:
        return size
    if size < 1048576:
        return str(int(size/1024))+'k'
    if size < 1073741824:
        return str(int(size/1048576))+'M'
    if size < 1099511627776:
        return str(int(size/1073741824))+'G'
def read_big_file():
    pass
def get_simple_info(file_path):
    t = os.path.getatime(filePath)
    return TimeStampToTime(t)

def get_FileAccessTime(filePath):
    '''
    获取文件
    访问时间+创建时间+修改时间
    '''
    a = os.path.getatime(filePath)
    c = os.path.getctime(filePath)
    m = os.path.getmtime(filePath)
    return a,c,m



def get_md5(path):
    m = hashlib.md5()  #创建md5对象
    with open(path,'rb') as f:
        while True:
            data = f.read(40960)
            if not data:
                break
            m.update(data) #更新md5对象
    return m.hexdigest()  #返回md5对象

def txt_to_html(file,title='网页版',out_html_file = None):
    # 运行日志转成html输出
    if out_html_file == None:
        out_html_file = file+'.html'
    try:
        html_head = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title></head><body>\n<p>'
        file_str = read_simple_text2(file)
        file_str = file_str.replace('\n','\n<p>')
        rs = f'{html_head}{file_str}'[:-3]
        write_str(out_html_file,rs,'w+')
    except BaseException:
        traceback.print_exc()
    return out_html_file