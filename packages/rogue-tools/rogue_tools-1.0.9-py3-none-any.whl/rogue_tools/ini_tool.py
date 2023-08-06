import configparser

import os
import traceback
import re


def get_ini(path,node):
    rs = None
    try:
        ini=configparser.ConfigParser()
        with open(path,"r",encoding='utf8') as f:
            lines = f.read().splitlines()
        rs = re.search('(\[)[\s\S]+',str(lines[0]))
        lines[0] = rs.group()
        ini.read_file(lines)
        #ini.sections()
        rs=dict(ini[node])

        return rs
    except BaseException as e:
        print('read ini failed',path)
        traceback.print_exc()
        return {}


def save_ini(path,node,ini_dic,is_cover_node = False):
    ini=configparser.ConfigParser()
    if os.path.exists(path):
        #ini.read(path,encoding="utf-8")
        with open(path,"r",encoding='utf8') as f:
            lines = f.read().splitlines()
        rs = re.search('(\[)[\s\S]+',str(lines[0]))
        lines[0] = rs.group()
        ini.read_file(lines)
    if is_cover_node:
        ini.remove_section(node)

    if not node in ini:
        ini.add_section(node)

    for key in ini_dic:
        #print(node,key,ini_dic[key])
        ini.set(node,key,str(ini_dic[key]))
    


    ini.write(open(path, "w",encoding="utf-8"))

def get_complete_ini(path):
    rs = {}
    try:
        ini=configparser.ConfigParser()
        with open(path,"r",encoding='utf8') as f:
            lines = f.read().splitlines()
        re_rs = re.search('(\[)[\s\S]+',str(lines[0]))
        lines[0] = re_rs.group()
        ini.read_file(lines)
        for node in ini.sections():
            rs[node]={}
            for key in ini[node]:
                rs[node][key] = str(ini[node][key])

        return rs
    except BaseException:
        traceback.print_exc()
        return rs


def save_complete_ini(path,ini_dic):
    '''
    保存完整的配置
    '''
    ini=configparser.ConfigParser()
    if os.path.exists(path):
        with open(path,"r",encoding='utf8') as f:
            lines = f.read().splitlines()
        rs = re.search('(\[)[\s\S]+',str(lines[0]))
        lines[0] = rs.group()
        ini.read_file(lines)

    for node_name in ini_dic:
        node_dic = ini_dic[node_name]
        if not node_name in ini:
                ini.add_section(node_name)
        for key_name in node_dic:
            ini.set(node_name,key_name,str(node_dic[key_name]))

    ini.write(open(path, "w",encoding="utf-8"))