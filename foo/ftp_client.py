import socket
from ftp_base import FtpBase
import platform
import subprocess
import os,json,sys

import struct


sysstr = platform.system()

class FtpClient(object):
    def __init__(self, address, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.sock = socket.socket(family, type)
        self.sock.connect(address)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.close()

    def msg_handle(self,msg):
        """
        对msg进行处理
        :param msg: str
        :return: bytes
        """
        if platform.system() == 'Windows':
            msg = msg.decode("gb2312")
        elif platform.system() == 'Linux':
            msg = msg.decode()

        if hasattr(self,msg):

            func = getattr(self,msg)
            func()
        else:
            sys.stdout.write(msg)


    def sz(self):
        """
        上传文件
        :return: 
        """
        # os.chdir("c:")
        # print(os.getcwd())
        filename = input("上传文件名>>").strip()
        if len(filename) == 0:return
        if os.path.isfile(filename):
            # filename = os.path.join("c:",filename)
            f_size = os.stat(filename).st_size   #得到size文件以rb形式打开的长度
            print(f_size)

            msg = {"filename":filename,"size":f_size}
            f = json.dumps(msg).encode()   #转换成json格式，返回字符串
            pack = len(f)                    #计算包头的长度
            self.sock.send(struct.pack('i',pack))  #发送包头大小
            self.sock.send(f)                     #发送包头
            if f_size == 0:
                print("上传成功")
                return
            with open(filename,"rb") as f:
                for line in f:
                    self.sock.send(line)                #发送文件
                    # print(line)
                print("发送成功...")
        else:
            self.sock.send(struct.pack('i', 0))  # 发送包头大小
            print("文件不存在")

    def rz(self):
        """
        下载文件
        :return: 
        """
        """
        生成一个字典形式{"filename":filename,"file_size":size,"file":True}
        """
        filename = input("下载文件名>>").strip()
        if len(filename) == 0:return
        msg_dict = {"filename":filename,"file_size":None,"file":True} #生成要发送的包头格式
        msg_dict = json.dumps(msg_dict).encode()

        self.sock.send(msg_dict)  #发送文件名
        #print(struct.calcsize('i'))
        pack_size = self.sock.recv(4)   #接收文件包
        pack_size, = struct.unpack('i',pack_size)  #得到包头大小

        file_data = self.sock.recv(pack_size)
        file_data = json.loads(file_data.decode())
        file_size = file_data.get('file_size')

        if not file_data.get('file'):
            print("文件不存在")
            return

        print("文件大小",file_size)
        recv_size = 1024
        total_size = 0
        with open(filename, "wb") as f:
            while file_size > total_size:  # 中文字节长度和字符串字节长度不一样
                if file_size - total_size > 1024:
                    recv_size = file_size - total_size
                data = self.sock.recv(recv_size)  # 接收文件

                f.write(data)
                total_size += len(data)

        print("下载成功,文件大小%s..."%total_size)

    def auc(self):
        print("鉴权界面".center(50,'-'))
        username = input('username:').strip()
        password = input("password:").strip()

        verify = {"username":None,"password":None,'verify':False}
        verify['username'] = username
        verify['password'] = password
        verify = json.dumps(verify).encode()
        #print(verify)
        self.sock.send(verify)
        verify_data = self.sock.recv(1024)
        print(verify_data)
        verify_data = json.loads(verify_data.decode())

        if not verify_data['verify']:
            return False
        return True

client_addr = ("localhost",8888)
with FtpClient(client_addr) as fc:
    count = 3
    tag = False
    while count:
        auc_tag = fc.auc()
        if not auc_tag:
            count -= 1
            print("剩余%s次机会"%count)
        if auc_tag:
            tag = True
            print("鉴权成功")
            break
    if tag:
        while True:
            msg = input(">>").strip()
            if len(msg) == 0: continue
            fc.sock.send(msg.encode())             #第一次交互，发送用户端数据
            data = fc.sock.recv(8092)    #返回处理完后的数据
            msg = fc.msg_handle(data)     #对数据进行处理
    else:
        print("鉴权失败")



