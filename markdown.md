##基于SocketFTP

###版本介绍
* 操作系统 windows 10
* python版本 python3.5

###作者介绍
* author：luxinjun
* myblog：[http://www.cnblogs.com/zj-luxj/]


###功能介绍
*  ftp_client.py文件，定义了一个ftp_client的类，里面包含上传文件，下载文件，对用户输入字符串进行处理
*  ftp_server.py文件，定义了一个ftp_server的类，提供接收客户端文件，客户端下载文件，验证的接口，定义处理客户端发送过来的请求方法
*  用户名和密码存储在db下的user.json文件下，里面还包含登陆ftp时所在的目录,lxj账户默认再c盘，sx账户默认再d盘

###运行说明
* 先运行ftp_server,再运行ftp_client。先进行鉴权，密码输错3次，退出，鉴权成功
输入rz接收文件，sz上传文件，dir查询ftp_server当前目录
