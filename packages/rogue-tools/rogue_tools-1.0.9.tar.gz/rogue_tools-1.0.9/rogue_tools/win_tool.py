
import traceback
import win32api 
import win32con 
import win32gui 
import win32process 
import win32clipboard
import os 
import signal 
from ctypes import *
import time
import win32com.client

from rogue_tools import  string_tool, time_tool

def get_screen_info():
    w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    return (w,h)

def get_win_hwnd(exe_name):
    '''
    # 获取win进程的句柄
    '''
    return win32gui.FindWindow(None,exe_name) 


def find_win(exe_name,search_type='diff'):
    '''
    尝试用不完整名字搜索程序名
    search_type='diff',查找最接近的字符串,从而获得结果(hwnd,name)
    search_type='in'  ,查找exe_name在其中的字符串
    search_type='all' ,精准查找
    '''
    rs=(0,None)
    rate=0
    dic = get_win_dic('')
    for obj in dic:
        if search_type == 'all':
            if exe_name == dic[obj]:
                return (obj,dic[obj])

        if search_type == 'in':
            if exe_name in dic[obj]:
                return (obj,dic[obj])

        if search_type == 'diff':
            temp_rate=string_tool.diff(exe_name,dic[obj])
            if temp_rate>rate:
                rate = temp_rate
                rs=(obj,dic[obj])
    return rs 

def get_win_text(hwnd):
    '''
    # 通过句柄获取窗口名字
    '''
    return win32gui.GetWindowText(hwnd)

def get_win_hwnd_list(search_str):
    '''
    # 通过已知字符串搜索窗口
    '''
    dic = get_win_dic(search_str)
    return list(dic.keys())

def get_win_name_list(search_str):
    '''
    # 通过已知字符串搜索窗口
    '''
    dic = get_win_dic(search_str)
    return list(dic.values())

def get_win_dic(search_str):
    rs_dic={}
    def get_list_handle(hwnd,search_str):
        name = win32gui.GetWindowText(hwnd)
        if search_str in name:
            rs_dic[hwnd]=name
    win32gui.EnumChildWindows(0, get_list_handle , search_str)
    return rs_dic

def get_thread(hwnd):
    '''
    进程ID
    '''
    thread,processId =win32process.GetWindowThreadProcessId(hwnd) 
    return thread
def get_processid(hwnd):
    '''
    任务管理器中的PID
    '''
    thread,processId =win32process.GetWindowThreadProcessId(hwnd) 
    return processId
def hide_win1(hwnd):
    '''
    最小化
    '''
    print(f'hide:{hwnd}')
    win32gui.CloseWindow(hwnd)

def hide_win2(hwnd):
    '''
    隐藏,图标也看不到的那种
    '''
    print(f'hide:{hwnd}')
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE) 
def show_win(hwnd):
    '''
    将窗口去掉隐藏,取消最小化,并放到最前面
    '''
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL) 
    '''
    pywin32模块下的一个小bug，在该函数调用前，需要先发送一个其他键给屏幕，如ALT键
    '''
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)
    shell.SendKeys('%')
    
def mov_win(hwnd,x,y):
    '''
    保持窗口大小,移动到某个位置
    '''
    w,h=get_win_size(hwnd)
    set_win_pos(hwnd,x,y,w,h)
    time.sleep(0.1)

def set_win_pos(hwnd,x,y,w,h):
    '''
    激活窗口，移动到某个位置,并设置大小,通常不这么用,但挺好用的
    
    '''
    show_win(hwnd)
    win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,x,y,w-1,h-1,win32con.SWP_SHOWWINDOW)    
    time.sleep(0.1)

    # 如果全屏化了，可能移动失败，获取一下大小宽度，看看上一步是否移动成功
    # 成功了就说明不需要按alt+enter
    if not get_win_size(hwnd) == (w-1,h-1):
        press_union_key([VK_CODE_ALT],VK_CODE_ENTER)
        time.sleep(0.5)

    win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,x,y,w,h,win32con.SWP_SHOWWINDOW)    
    time.sleep(0.1)


def get_win_pos(hwnd):
    '''
    获取窗口位置
    '''
    rs = win32gui.GetWindowRect(hwnd)
    
    return (rs[0],rs[1])
def get_win_size(hwnd):
    '''
    获取窗口大小
    '''
    rs = win32gui.GetWindowRect(hwnd)
    return (rs[2]-rs[0],rs[3]-rs[1])
def kill_exe(hwnd):
    '''
    关闭程序
    '''
    if type(hwnd)==int:
        if hwnd:
            processid=get_processid(hwnd)
            try:
                os.kill(processid,signal.SIGBREAK)
                #print(f'kill-{hwnd}-{processid}')
            except BaseException:
                traceback.print_exc()
    else:
        hwnd = get_win_hwnd(hwnd)
        kill_exe(hwnd)
def loop_kill_exe(app_name):
    '''
    循环查找应用,然后杀掉
    '''
    hwnd,name = find_win(app_name,search_type='in') 
    print(f'try killing [{app_name}] , find [{hwnd},{name}]')
    if hwnd:
        thread,processId =win32process.GetWindowThreadProcessId(hwnd) 
        os.kill(processId,signal.SIGBREAK)
        time.sleep(3)
        return loop_kill_exe(app_name)
def kill_by_exe(exe_name):
    cmd = f'TASKKILL /im {exe_name}'
    os.system(cmd)
def re_start(app_name,start_path,start_time_out=60,search_type='all'):
    '''
    尝试重启,start_time_out是启动之后,等待查找句柄的最长时间
    search_type见find_win()解释
    '''
    loop_kill_exe(app_name)
        
    cmd = 'start "" '+start_path
    print(cmd)
    os.system(cmd)
    hwnd = 0
    start_time=time_tool.time_stamp_s()
    while True:
        time.sleep(5)
        until_time = time_tool.time_stamp_s() - start_time
        if until_time > start_time_out:
            return 0
        hwnd = find_win(app_name,search_type=search_type)[0]
        if hwnd:
            return hwnd
        print(f'wait:{until_time}/{start_time_out}s {hwnd}')

def get_clipboard():
    win32clipboard.OpenClipboard()
    rs = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    return rs
    
# ******************************鼠标相关内容******************************
def mouse_click(pos):
    if pos==None:
        pos=get_mouse_pos()
    #x = pos[0]
    #y = pos[1]
    win32api.SetCursorPos(pos)
    mouse_exe(1)


def mouse_click_double(pos):
    if pos==None:
        pos=get_mouse_pos()
    #x = pos[0]
    #y = pos[1]
    win32api.SetCursorPos(pos)
    mouse_exe(2)
def mouse_right_click(pos):
    if pos==None:
        pos=get_mouse_pos()
    #x = pos[0]
    #y = pos[1]
    win32api.SetCursorPos(pos)
    mouse_exe(1,False)

def mouse_exe(times,right_or_left=True,intevarl=0.05):
    if right_or_left==True:
        down = win32con.MOUSEEVENTF_LEFTDOWN
        up   = win32con.MOUSEEVENTF_LEFTUP
    else:
        down = win32con.MOUSEEVENTF_RIGHTDOWN
        up   = win32con.MOUSEEVENTF_RIGHTUP

    for i in range(0,times):
        time.sleep(intevarl)
        win32api.mouse_event(down, 0, 0, 0, 0)
        time.sleep(0.02)
        win32api.mouse_event(up, 0, 0, 0, 0)
    time.sleep(0.2)


def get_mouse_pos():
    '''
    获取当前鼠标位置
    '''
    return win32gui.GetCursorPos(0)

def mouse_move(pos):
    '''
    移动鼠标位置
    '''
    win32api.SetCursorPos(pos)


def key_input(str=''):
    for c in str:
        press_key(c)
    time.sleep(0.2)  

def press_key(key='',times=1):
    # 使用VK_CODE_XXXXXX即可，其他的不一定支持喔！
    key = key.lower()
    for i in range(0,times):
        win32api.keybd_event(VK_CODE[key],0,0,0)
        win32api.keybd_event(VK_CODE[key],0,win32con.KEYEVENTF_KEYUP,0)
        time.sleep(0.1)
def press_union_key(union_list,p_key):
    '''
    按住union_list里的所有键,再按press_key
    '''
    for key in union_list:
        win32api.keybd_event(VK_CODE[key],0,0,0)
    press_key(p_key)
    for key in union_list:
        win32api.keybd_event(VK_CODE[key],0,win32con.KEYEVENTF_KEYUP,0)
    pass

    


#键盘映射
VK_CODE_BACKSPACE                   =    'backspace'
VK_CODE_TAB                         =    'tab'
VK_CODE_CLEAR                       =    'clear'
VK_CODE_ENTER                       =    'enter'
VK_CODE_SHIFT                       =    'shift'
VK_CODE_CTRL                        =    'ctrl'
VK_CODE_ALT                         =    'alt'
VK_CODE_PAUSE                       =    'pause'
VK_CODE_CAPS_LOCK                   =    'caps_lock'
VK_CODE_ESC                         =    'esc'
VK_CODE_SPACE                       =    'space'
VK_CODE_PAGE_UP                     =    'page_up'
VK_CODE_PAGE_DOWN                   =    'page_down'
VK_CODE_END                         =    'end'
VK_CODE_HOME                        =    'home'
VK_CODE_LEFT_ARROW                  =    'left_arrow'
VK_CODE_UP_ARROW                    =    'up_arrow'
VK_CODE_RIGHT_ARROW                 =    'right_arrow'
VK_CODE_DOWN_ARROW                  =    'down_arrow'
VK_CODE_SELECT                      =    'select'
VK_CODE_PRINT                       =    'print'
VK_CODE_EXECUTE                     =    'execute'
VK_CODE_PRINT_SCREEN                =    'print_screen'
VK_CODE_INSERT                      =    'insert'
VK_CODE_DEL                         =    'del'
VK_CODE_HELP                        =    'help'
VK_CODE_0                           =    '0'
VK_CODE_1                           =    '1'
VK_CODE_2                           =    '2'
VK_CODE_3                           =    '3'
VK_CODE_4                           =    '4'
VK_CODE_5                           =    '5'
VK_CODE_6                           =    '6'
VK_CODE_7                           =    '7'
VK_CODE_8                           =    '8'
VK_CODE_9                           =    '9'
VK_CODE_A                           =    'a'
VK_CODE_B                           =    'b'
VK_CODE_C                           =    'c'
VK_CODE_D                           =    'd'
VK_CODE_E                           =    'e'
VK_CODE_F                           =    'f'
VK_CODE_G                           =    'g'
VK_CODE_H                           =    'h'
VK_CODE_I                           =    'i'
VK_CODE_J                           =    'j'
VK_CODE_K                           =    'k'
VK_CODE_L                           =    'l'
VK_CODE_M                           =    'm'
VK_CODE_N                           =    'n'
VK_CODE_O                           =    'o'
VK_CODE_P                           =    'p'
VK_CODE_Q                           =    'q'
VK_CODE_R                           =    'r'
VK_CODE_S                           =    's'
VK_CODE_T                           =    't'
VK_CODE_U                           =    'u'
VK_CODE_V                           =    'v'
VK_CODE_W                           =    'w'
VK_CODE_X                           =    'x'
VK_CODE_Y                           =    'y'
VK_CODE_Z                           =    'z'
VK_CODE_NUMPAD_0                    =    'numpad_0'
VK_CODE_NUMPAD_1                    =    'numpad_1'
VK_CODE_NUMPAD_2                    =    'numpad_2'
VK_CODE_NUMPAD_3                    =    'numpad_3'
VK_CODE_NUMPAD_4                    =    'numpad_4'
VK_CODE_NUMPAD_5                    =    'numpad_5'
VK_CODE_NUMPAD_6                    =    'numpad_6'
VK_CODE_NUMPAD_7                    =    'numpad_7'
VK_CODE_NUMPAD_8                    =    'numpad_8'
VK_CODE_NUMPAD_9                    =    'numpad_9'
VK_CODE_MULTIPLY_KEY                =    'multiply_key'
VK_CODE_ADD_KEY                     =    'add_key'
VK_CODE_SEPARATOR_KEY               =    'separator_key'
VK_CODE_SUBTRACT_KEY                =    'subtract_key'
VK_CODE_DECIMAL_KEY                 =    'decimal_key'
VK_CODE_DIVIDE_KEY                  =    'divide_key'
VK_CODE_F1                          =    'f1'
VK_CODE_F2                          =    'f2'
VK_CODE_F3                          =    'f3'
VK_CODE_F4                          =    'f4'
VK_CODE_F5                          =    'f5'
VK_CODE_F6                          =    'f6'
VK_CODE_F7                          =    'f7'
VK_CODE_F8                          =    'f8'
VK_CODE_F9                          =    'f9'
VK_CODE_F10                         =    'f10'
VK_CODE_F11                         =    'f11'
VK_CODE_F12                         =    'f12'
VK_CODE_F13                         =    'f13'
VK_CODE_F14                         =    'f14'
VK_CODE_F15                         =    'f15'
VK_CODE_F16                         =    'f16'
VK_CODE_F17                         =    'f17'
VK_CODE_F18                         =    'f18'
VK_CODE_F19                         =    'f19'
VK_CODE_F20                         =    'f20'
VK_CODE_F21                         =    'f21'
VK_CODE_F22                         =    'f22'
VK_CODE_F23                         =    'f23'
VK_CODE_F24                         =    'f24'
VK_CODE_NUM_LOCK                    =    'num_lock'
VK_CODE_SCROLL_LOCK                 =    'scroll_lock'
VK_CODE_LEFT_SHIFT                  =    'left_shift'
VK_CODE_RIGHT_SHIFT                 =    'right_shift'
VK_CODE_LEFT_CONTROL                =    'left_control'
VK_CODE_RIGHT_CONTROL               =    'right_control'
VK_CODE_LEFT_MENU                   =    'left_menu'
VK_CODE_RIGHT_MENU                  =    'right_menu'
VK_CODE_BROWSER_BACK                =    'browser_back'
VK_CODE_BROWSER_FORWARD             =    'browser_forward'
VK_CODE_BROWSER_REFRESH             =    'browser_refresh'
VK_CODE_BROWSER_STOP                =    'browser_stop'
VK_CODE_BROWSER_SEARCH              =    'browser_search'
VK_CODE_BROWSER_FAVORITES           =    'browser_favorites'
VK_CODE_BROWSER_START_AND_HOME      =    'browser_start_and_home'
VK_CODE_VOLUME_MUTE                 =    'volume_mute'
VK_CODE_VOLUME_DOWN                 =    'volume_Down'
VK_CODE_VOLUME_UP                   =    'volume_up'
VK_CODE_NEXT_TRACK                  =    'next_track'
VK_CODE_PREVIOUS_TRACK              =    'previous_track'
VK_CODE_STOP_MEDIA                  =    'stop_media'
VK_CODE_PLAY_PAUSE_MEDIA            =    'play\pause_media'
VK_CODE_START_MAIL                  =    'start_mail'
VK_CODE_SELECT_MEDIA                =    'select_media'
VK_CODE_START_APPLICATION_1         =    'start_application_1'
VK_CODE_START_APPLICATION_2         =    'start_application_2'
VK_CODE_ATTN_KEY                    =    'attn_key'
VK_CODE_CRSEL_KEY                   =    'crsel_key'
VK_CODE_EXSEL_KEY                   =    'exsel_key'
VK_CODE_PLAY_KEY                    =    'play_key'
VK_CODE_ZOOM_KEY                    =    'zoom_key'
VK_CODE_CLEAR_KEY                   =    'clear_key'
VK_CODE_PLUS                        =    '+'
VK_CODE_COMMA                       =    ','
VK_CODE_MINUS                       =    '-'
VK_CODE_DOT                         =    '.'
VK_CODE_SLASH                       =    '/'
VK_CODE_DOT2                        =    '`'
VK_CODE_SEMICOLON                   =    ';'
VK_CODE_LEFT_MID_BRACKETS           =    '['
VK_CODE_SLASH2                      =    '\\'#这是一个斜杠
VK_CODE_RIGHT_MID_BRACKETS          =    ']'
VK_CODE_DOT3                        =    "'"#这是一个'


VK_CODE = {
VK_CODE_BACKSPACE:0x08,
VK_CODE_TAB:0x09,
VK_CODE_CLEAR:0x0C,
VK_CODE_ENTER:0x0D,
VK_CODE_SHIFT:0x10,
VK_CODE_CTRL:0x11,
VK_CODE_ALT:0x12,
VK_CODE_PAUSE:0x13,
VK_CODE_CAPS_LOCK:0x14,
VK_CODE_ESC:0x1B,
VK_CODE_SPACE:0x20,
VK_CODE_PAGE_UP:0x21,
VK_CODE_PAGE_DOWN:0x22,
VK_CODE_END:0x23,
VK_CODE_HOME:0x24,
VK_CODE_LEFT_ARROW:0x25,
VK_CODE_UP_ARROW:0x26,
VK_CODE_RIGHT_ARROW:0x27,
VK_CODE_DOWN_ARROW:0x28,
VK_CODE_SELECT:0x29,
VK_CODE_PRINT:0x2A,
VK_CODE_EXECUTE:0x2B,
VK_CODE_PRINT_SCREEN:0x2C,
VK_CODE_INSERT:0x2D,
VK_CODE_DEL:0x2E,
VK_CODE_HELP:0x2F,
VK_CODE_0:0x30,
VK_CODE_1:0x31,
VK_CODE_2:0x32,
VK_CODE_3:0x33,
VK_CODE_4:0x34,
VK_CODE_5:0x35,
VK_CODE_6:0x36,
VK_CODE_7:0x37,
VK_CODE_8:0x38,
VK_CODE_9:0x39,
VK_CODE_A:0x41,
VK_CODE_B:0x42,
VK_CODE_C:0x43,
VK_CODE_D:0x44,
VK_CODE_E:0x45,
VK_CODE_F:0x46,
VK_CODE_G:0x47,
VK_CODE_H:0x48,
VK_CODE_I:0x49,
VK_CODE_J:0x4A,
VK_CODE_K:0x4B,
VK_CODE_L:0x4C,
VK_CODE_M:0x4D,
VK_CODE_N:0x4E,
VK_CODE_O:0x4F,
VK_CODE_P:0x50,
VK_CODE_Q:0x51,
VK_CODE_R:0x52,
VK_CODE_S:0x53,
VK_CODE_T:0x54,
VK_CODE_U:0x55,
VK_CODE_V:0x56,
VK_CODE_W:0x57,
VK_CODE_X:0x58,
VK_CODE_Y:0x59,
VK_CODE_Z:0x5A,
VK_CODE_NUMPAD_0:0x60,
VK_CODE_NUMPAD_1:0x61,
VK_CODE_NUMPAD_2:0x62,
VK_CODE_NUMPAD_3:0x63,
VK_CODE_NUMPAD_4:0x64,
VK_CODE_NUMPAD_5:0x65,
VK_CODE_NUMPAD_6:0x66,
VK_CODE_NUMPAD_7:0x67,
VK_CODE_NUMPAD_8:0x68,
VK_CODE_NUMPAD_9:0x69,
VK_CODE_MULTIPLY_KEY:0x6A,
VK_CODE_ADD_KEY:0x6B,
VK_CODE_SEPARATOR_KEY:0x6C,
VK_CODE_SUBTRACT_KEY:0x6D,
VK_CODE_DECIMAL_KEY:0x6E,
VK_CODE_DIVIDE_KEY:0x6F,
VK_CODE_F1:0x70,
VK_CODE_F2:0x71,
VK_CODE_F3:0x72,
VK_CODE_F4:0x73,
VK_CODE_F5:0x74,
VK_CODE_F6:0x75,
VK_CODE_F7:0x76,
VK_CODE_F8:0x77,
VK_CODE_F9:0x78,
VK_CODE_F10:0x79,
VK_CODE_F11:0x7A,
VK_CODE_F12:0x7B,
VK_CODE_F13:0x7C,
VK_CODE_F14:0x7D,
VK_CODE_F15:0x7E,
VK_CODE_F16:0x7F,
VK_CODE_F17:0x80,
VK_CODE_F18:0x81,
VK_CODE_F19:0x82,
VK_CODE_F20:0x83,
VK_CODE_F21:0x84,
VK_CODE_F22:0x85,
VK_CODE_F23:0x86,
VK_CODE_F24:0x87,
VK_CODE_NUM_LOCK:0x90,
VK_CODE_SCROLL_LOCK:0x91,
VK_CODE_LEFT_SHIFT:0xA0,
VK_CODE_RIGHT_SHIFT:0xA1,
VK_CODE_LEFT_CONTROL:0xA2,
VK_CODE_RIGHT_CONTROL:0xA3,
VK_CODE_LEFT_MENU:0xA4,
VK_CODE_RIGHT_MENU:0xA5,
VK_CODE_BROWSER_BACK:0xA6,
VK_CODE_BROWSER_FORWARD:0xA7,
VK_CODE_BROWSER_REFRESH:0xA8,
VK_CODE_BROWSER_STOP:0xA9,
VK_CODE_BROWSER_SEARCH:0xAA,
VK_CODE_BROWSER_FAVORITES:0xAB,
VK_CODE_BROWSER_START_AND_HOME:0xAC,
VK_CODE_VOLUME_MUTE:0xAD,
VK_CODE_VOLUME_DOWN:0xAE,
VK_CODE_VOLUME_UP:0xAF,
VK_CODE_NEXT_TRACK:0xB0,
VK_CODE_PREVIOUS_TRACK:0xB1,
VK_CODE_STOP_MEDIA:0xB2,
VK_CODE_PLAY_PAUSE_MEDIA:0xB3,
VK_CODE_START_MAIL:0xB4,
VK_CODE_SELECT_MEDIA:0xB5,
VK_CODE_START_APPLICATION_1:0xB6,
VK_CODE_START_APPLICATION_2:0xB7,
VK_CODE_ATTN_KEY:0xF6,
VK_CODE_CRSEL_KEY:0xF7,
VK_CODE_EXSEL_KEY:0xF8,
VK_CODE_PLAY_KEY:0xFA,
VK_CODE_ZOOM_KEY:0xFB,
VK_CODE_CLEAR_KEY:0xFE,
VK_CODE_PLUS:0xBB,
VK_CODE_COMMA:0xBC,
VK_CODE_MINUS:0xBD,
VK_CODE_DOT:0xBE,
VK_CODE_SLASH:0xBF,
VK_CODE_DOT2:0xC0,
VK_CODE_SEMICOLON:0xBA,
VK_CODE_LEFT_MID_BRACKETS:0xDB,
VK_CODE_SLASH2:0xDC,
VK_CODE_RIGHT_MID_BRACKETS:0xDD,
VK_CODE_DOT3:0xDE
}