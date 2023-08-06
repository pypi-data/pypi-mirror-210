import os
import sys
import time
import traceback

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from concurrent.futures import ThreadPoolExecutor
from rogue_tools import file_tool,path_tool



class mainUI():
    def __init__(self,w,h,title='PyQt5 - UI by [rogue_tools]',is_center=True):
        self.config_path        = 'save_params.text'
        self.save_dic           = self.load_input()
        self.ui_width           = w
        self.ui_height          = h
        self.pool               = ThreadPoolExecutor(max_workers=3)
        self.app                = QApplication(sys.argv)
        self.windows            = QWidget()
        self.windows.resize(self.ui_width,self.ui_height)
        self.windows.setWindowTitle(title)
        # 居中
        if is_center:
            qr = self.windows.frameGeometry()
            cp = QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
            self.windows.move(qr.topLeft())

    def show(self):
        #show()方法在屏幕上显示出widget组件
        self.windows.show()
        #循环执行窗口触发事件，结束后不留垃圾的退出，不添加的话新建的widget组件就会一闪而过
        sys.exit(self.app.exec_())
    
    def add_label(self,line_index,title, start_pos = (0,0),obj_w=200,obj_h=20):
        label = QLabel(self.windows)
        label.setGeometry(QtCore.QRect(start_pos[0] , obj_h * line_index+start_pos[1] , obj_w , obj_h))
        label.setText(title)

    def add_btn(self,line_index,title, start_pos = (0,0),call_func=None,obj_w=100,obj_h=20):
        #设置按钮并给按钮命名
        btn = QPushButton(title,self.windows)
        btn.setGeometry(start_pos[0] , obj_h * line_index+start_pos[1] , obj_w , obj_h)
        if call_func:
            btn.clicked.connect(call_func)
        return btn
        
    def add_input_editor(self,line_index,title, start_pos = (0,0) ,edit_text='',edit_tips='',obj_w_1=70,obj_w_2=200,obj_h = 20):
        key = f'{line_index}_{title}'
        input_str = self.save_dic.get(key,'') if edit_text=='' else edit_text
        # 显示标签
        label = QLabel(self.windows)
        label.setGeometry(QtCore.QRect(start_pos[0] , obj_h * line_index+start_pos[1] , obj_w_1 , obj_h))
        label.setText(title)
        # 输入框
        edit = QLineEdit(self.windows)
        edit.setPlaceholderText(str(edit_tips))
        edit.setText(str(input_str))
        edit.setGeometry(QtCore.QRect(obj_w_1+start_pos[0] , obj_h * line_index+start_pos[1] , obj_w_2 , obj_h))
        # 管理内容
        self.save_dic[key] = edit
        return edit
    def exit_exe(self):
        QtCore.QCoreApplication.instance().quit()

    def msgbox(self,msg_str,title=''):
        QMessageBox.about(self.windows, title,msg_str)
    def save_input(self):
        write_lines=[]
        for key in self.save_dic:
            write_lines.append(f'{key}={self.save_dic[key].text()}')
        file_tool.write_lines(self.config_path,write_lines)
    def load_input(self):
        rs_dic = {}
        if not path_tool.is_exists(self.config_path):
            return rs_dic
        lines = file_tool.read_simple_text(self.config_path)
        
        for line in lines:
            temp  = line.split('=')
            if len(temp)==2:
                rs_dic[temp[0]]=temp[1]
        return rs_dic

if __name__ == '__main__':
    main_ui = mainUI(400,400)
    main_ui.add_btn((10,10),1,'test1')
    main_ui.add_btn((10,10),2,'test2')
    main_ui.add_input_editor((160,10),1,'测试一下','test1')
    main_ui.add_input_editor((160,10),2,'测试一下','test2')
    main_ui.add_label((10,100),1,'test1')
    main_ui.add_label((10,100),2,'test2')
    main_ui.show()