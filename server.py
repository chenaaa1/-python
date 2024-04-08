import socket
import threading
import queue
import json
import time
import os
import os.path
import sys

# 导入ftp的包
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# 用户所需输入信息分界线--------------------------------------
IP_server = '127.0.0.1'
PORT = 6666
FTP_PORT = 21

# 关于ftp的设置
username_server = 'mary'  # ftp登录用的用户名
password_server = '123456'
ftp_catalogue = 'C:/my_soft/python/code/lesson_code/ftp_test'  # ftp的目录
user_power = 'elradfmwMT'  # 权限
# 用户所需输入信息分界线--------------------------------------


que = queue.Queue()                             # 用于存放客户端发送的信息的队列
users = []                                      # 用于存放在线用户的信息  [conn, user, addr]
lock = threading.Lock()                         # 创建锁, 防止多个线程写入数据的顺序打乱


# ----------------------------------------显示在线列表1--------------------
# 将在线用户存入online列表并返回online这个集合
def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online
# ----------------------------------------显示在线列表2--------------------


# ----------------------------------------聊天服务器1--------------------
class ChatServer(threading.Thread):
    global users, que, lock

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.ADDR = ('', port)
        os.chdir(sys.path[0])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 用于接收所有客户端发送信息的函数
    def tcp_connect(self, conn, addr):
        # 连接后将用户信息添加到users列表
        user = conn.recv(1024)                                    # 接收用户名
        user = user.decode()

        for i in range(len(users)):
            if user == users[i][1]:
                print('User already exist')
                user = '' + user + '_2'

        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        print(' New connection:', addr, ':', user, end='')         # 打印用户名
        d = onlines()                                                   # 有新连接则刷新客户端的在线用户显示
        self.recv(d, addr)
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                self.recv(data, addr)                         # 保存信息到队列
            conn.close()
        except:
            print(user + ' Connection lose')
            self.delUsers(conn, addr)                             # 将断开用户移出users
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print(' Remaining online users: ', end='')         # 打印剩余在线用户(conn)
                d = onlines()
                self.recv(d, addr)
                print(d)
                break
            a += 1

    # 将接收到的信息(ip,端口以及发送的信息)存入que队列
    def recv(self, data, addr):
        lock.acquire()
        try:
            que.put((addr, data))
        finally:
            lock.release()

    # 将队列que中的消息发送给所有连接到的用户
    def sendData(self):
        while True:
            if not que.empty():
                data = ''
                reply_text = ''
                message = que.get()
                print('message')# 取出队列第一个元素
                # message收到的信息大概为(('127.0.0.1', 11590), 'hello world:;1:;2')
                print(message)
                if isinstance(message[1], str):                   # 如果data是str则返回Ture
                    for i in range(len(users)):
                        # user[i][1]是用户名, users[i][2]是addr, 将message[0]改为用户名
                        for j in range(len(users)):
                            if message[0] == users[j][2]:
                                # print(' this: message is from user[{}]'.format(j))
                                data = ' ' + users[j][1] + '：' + message[1]
                                print('data')
                                # data的信息大概为1：nice:;1:;2
                                print(data)

                                break
                        users[i][0].send(data.encode())

                if isinstance(message[1], list):  # 同上
                    # 如果是list则打包后直接发送  
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][0].send(data.encode())
                        except:
                            pass

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('聊天服务器启动成功')
        q = threading.Thread(target=self.sendData)
        q.start()
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()
# ----------------------------------------聊天服务器2--------------------------


# ----------------------------------------文件传输服务器1--------------------------
class FtpServer():
    # 新建一个用户组
    authorizer = DummyAuthorizer()
    # 将用户名，密码，指定目录，权限 添加到里面
    authorizer.add_user(username_server, password_server, ftp_catalogue, perm=user_power)  # adfmw
    # 这个是添加匿名用户,任何人都可以访问，如果去掉的话，需要输入用户名和密码，可以自己尝试
    authorizer.add_anonymous(ftp_catalogue)

    handler = FTPHandler
    handler.authorizer = authorizer

    def run(self):
        # 开启服务器
        server = FTPServer((IP_server, FTP_PORT), self.handler)
        server.serve_forever()
# ----------------------------------------文件传输服务器2--------------------------

if __name__ == '__main__':
    cserver = ChatServer(PORT)
    fserver = FtpServer()
    cserver.start()
    fserver.run()
    while True:
        time.sleep(1)
        if not cserver.isAlive():
            print("Chat connection lost...")
            sys.exit(0)
        if not fserver.isAlive():
            print("File connection lost...")
            sys.exit(0)
