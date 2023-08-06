import os
import socket
import requests
import re
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import traceback


def get_ip_public(timeout=60):
    '''公网ip'''
    text = requests.get('http://myip.ipip.net',timeout=timeout).text
    pattern = r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}"
    rs = re.search(pattern,text)
    return rs.group()

def get_ip_local_area_network():
    '''局域网ip'''
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("114.114.114.114", 80))
        return s.getsockname()[0]



def download_url(url,save_folder_path,is_cover=True,is_show_process=True):
    url=url.replace('\\','/')
    if not save_folder_path.endswith('\\'):
        save_folder_path=save_folder_path+'\\'
        
    
    temp=url.split('/')
    file_name=temp[len(temp)-1]
    save_path=save_folder_path+file_name
    
    #下载条件检查,覆盖模式或者不存在文件的，才下载。
    if is_cover or not os.path.isfile(save_path):
        r = requests.get(url, stream=True)

        if is_show_process:
            total = int(r.headers.get('content-length',0))
            with open(save_path,'wb') as file,tqdm(
                desc            = file_name,
                total           = total,
                unit            = 'iB',
                unit_scale      = True,
                unit_divisor    = 1024,
                mininterval     = 2,
            )as bar:
                for data in r.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)
        else:
            with open(save_path,'wb') as file:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)


    return save_path


def thread_download_url(url,save_folder_path,is_cover=True,time_out=180):
    '''
    建议使用这个方法下载apk,防止卡死
    '''

    pool = ThreadPoolExecutor(max_workers=3)
    try:
        future1 = pool.submit(download_url, url , save_folder_path , is_cover)
        for i in range(0,time_out):
            time.sleep(1)
            if future1.done():
                time.sleep(3)
                return i
        return -1
    finally:
        pool.shutdown()