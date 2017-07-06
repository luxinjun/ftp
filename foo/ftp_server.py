from ftp_base import FtpBase
import socket,subprocess,os,sys
import json
en_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(en_path)
path = os.path.join(en_path,r'conf\db\user.json')

# os.chdir("c:")
# print(os.listdir())
import struct
server_addr = ("localhost",8888)

class FtpServer(object):

    def __init__(self, address, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.sock = socket.socket(family,type)
        self.sock.bind(address)
        self.sock.listen(5)

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.close()

    def ftp_conn(self):

        conn,addr = self.sock.accept()
        return conn,addr

    def client_auc(self,conn):
        # verify = {"username":None,"password":None,'verify':False}
        # verify = json.dumps(verify).encode()
        # conn.send(verify)
        verify_data = json.loads(conn.recv(1024).decode())
        #print(verify_data)
        tag = False
        with open(path,'r') as f:
            data = json.load(f)
            print(data)
            for k in data:
                if k['username'] == verify_data.get('username') and k['password'] == verify_data.get('password'):
                    verify_data['verify'] = True
                    print(k['path'])
                    os.chdir(k['path'])
                    tag = True

        if not tag:
            verify_data['verify'] = False

        verify = json.dumps(verify_data).encode()
        conn.send(verify)

        return verify_data['verify']


    def msg_handle(self,conn,msg):
        """
        对msg进行处理
        :param conn: 用户端套接字实例
        :param msg: str
        :return: 
        """
        if hasattr(self,msg):
            conn.send(msg.encode())
            func = getattr(self,msg)
            func(conn)
        else:
            msg = subprocess.run(msg,shell=True,stdout = subprocess.PIPE,stderr=subprocess.PIPE)
            print(msg)
            if msg.stdout:
                # msg_dict = dict(msg=msg.stdout,size = len(msg.stdout))
                # f = json.loads(msg_dict)
                # conn.send()
                conn.sendall(msg.stdout)
            elif msg.stderr:
                conn.sendall(msg.stderr)
            else:
                conn.sendall(str(msg.returncode).encode())

    def rz(self,conn):
        """
        用户端下载文件
        :param conn: 用户端套接字实例
        :return: 
        """
        """
                生成一个字典形式{"filename":filename,"file_size":size,"file":True}
        """
        file_dict = conn.recv(1024)     #接收用户端文件信息
        file_dict = json.loads(file_dict.decode())
        filename = file_dict.get('filename')
        print(filename)
        if os.path.isfile(filename):
            # filename = os.path.join("c:",filename)
            f_size = os.stat(filename).st_size
            print("文件大小",f_size)
            file_dict['file_size'] = f_size
            file_dict = json.dumps(file_dict).encode()
            pack_size = struct.pack('i', len(file_dict))
            conn.send(pack_size)  # 发送文件大小
            conn.send(file_dict) #发送新的文件信息字典

            with open(filename, "rb") as f:
                for line in f:
                    conn.send(line)  # 发送文件
            print("发送成功".ljust(10, '.'))
        else:
            file_dict['file'] = False

            file_dict = json.dumps(file_dict).encode()
            pack_size = struct.pack('i', len(file_dict))
            conn.send(pack_size)  # 发送文件大小
            conn.send(file_dict)


    def sz(self,conn):
        """
        用户端上传文件
        :param conn: 用户端套接字实例
        :return: 
        """
        pack_size = conn.recv(4)  # 接收包头长度
        pack_size, = struct.unpack('i',pack_size)
        print("pack_size:%s"%pack_size)
        if pack_size == 0:
            return

        pack = conn.recv(pack_size)  #接收包头
        print(pack)
        msg = json.loads(pack.decode())  #解析json
        filename = msg.get('filename')   #得到用户名
        file_size = msg.get('size')         #得到文件大小
        print(filename,file_size)

        recv_size = 1024
        total_size = 0
        with open(filename,"wb") as f:
            while file_size > total_size:  # 中文字节长度和字符串字节长度不一样
                if file_size - total_size >1024:
                    recv_size = file_size - total_size
                data = conn.recv(recv_size)  # 接收文件

                f.write(data)
                total_size += len(data)

        print("接收成功,文件大小%s..." % total_size)

with FtpServer(server_addr) as fs:

    while True:
        conn,addr = fs.ftp_conn()
        count = 3
        tag = False
        while count:
            auc_tag = fs.client_auc(conn)
            if not auc_tag:
                count -= 1
                print("剩余%s次机会" % count)
            if auc_tag:
                tag = True
                print("鉴权成功")
                break

        print(conn,addr)
        if tag:
            while True:
                data = conn.recv(8092).decode()  # 接收数据
                if not data:
                    print("client is lost...")
                    break
                print("收到指令>>:",data)
                fs.msg_handle(conn,data)


