import requests
import re
import json
import base64
import hashlib
from rogue_tools import path_tool

class MsgRobot():
    def __init__(self,webhook_list=[],webhook=None) -> None:
        self.webhook_list = webhook_list
        if webhook:
            self.webhook_list.append(webhook)

    def is_feishu(self,webhook_url):
        group = re.search(r'(feishu)',webhook_url, re.I)
        rs = group.group() if group else None
        return True if rs else False

    def is_weixin(self,webhook_url):
        group = re.search(r'(weixin)',webhook_url, re.I)
        rs = group.group() if group else None
        return True if rs else False
        
    def push_all(self,msg_or_pic:str):
        if len(msg_or_pic)>1024:
            msg_or_pic = msg_or_pic[-1024:]
        if path_tool.is_exists(msg_or_pic) and msg_or_pic[-4:] in ('.jpg','.png'):
            self.push_pic(msg_or_pic) 
        else:
            self.push_text(msg_or_pic)

    def push_pic(self,msg):
        for webhook in self.webhook_list:
            if self.is_feishu(webhook):
                self.fs_push_pic(webhook,msg)
            elif self.is_weixin(webhook):
                self.wx_push_pic(webhook,msg)

    def push_text(self,msg):
        for webhook in self.webhook_list:
            if self.is_feishu(webhook):
                self.fs_push_text(webhook,msg)
            elif self.is_weixin(webhook):
                self.wx_push_text(webhook,msg)

    def _wx_push_main(self,webhook,data):
        # 企业微信机器人的 webhook
        # 开发文档 https://work.weixin.qq.com/api/doc#90000/90136/91770
        #webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
        headers = {'content-type': 'application/json'}  # 请求头
        r = requests.post(webhook, headers=headers, data=json.dumps(data))
        r.encoding = 'utf-8'
        return r.text

    def _fs_push_main(self,webhook,data):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return '消息发送成功'
        else:
            return f'消息发送失败:{response.status_code}'

    def wx_push_pic(self,webhook,pic_path):
        pic_obj =None
        with open(pic_path,'rb') as pic:
            pic_obj = pic.read()
        pic_64  =  base64.b64encode(pic_obj)
        pic_str = str(pic_64,'utf-8')
        pic_md5 = hashlib.md5(pic_obj).hexdigest()
        # 发送图片
        webhook_data = {"msgtype": "image","image": {"base64": pic_str,"md5": pic_md5}}
        # 企业微信机器人发送
        self._wx_push_main(webhook, webhook_data)

    def fs_push_pic(self,webhook,msg):
        self.fs_push_text(webhook,'暂不支持发送飞书图片,假装这里有个超酷炫的图片吧')

    def wx_push_text(self,webhook,msg:str):
        webhook_data = {"msgtype": "text","text": {"content": msg}}
        if msg.startswith('markdown'):
            temp = msg.split('_',2)
            webhook_data = {"msgtype": "markdown","markdown": {"content": f'{temp[1]}\n<font color=\"comment\">{temp[2]}</font>'}}
        return self._wx_push_main(webhook,webhook_data)

    def fs_push_text(self,webhook,msg):
        webhook_data = {'msg_type': 'text', 'content': {'text': msg}}
        return self._fs_push_main(webhook,webhook_data)
    