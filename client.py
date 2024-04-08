import os
import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText  # 导入多行文本框用到的包
from tkinter import *
from tkinter import filedialog

# email所需包
from smtplib import SMTP
from email.encoders import encode_base64
from email.utils import formatdate, make_msgid
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# ftp所需包
import ftplib
# 修改图片大小所需包
from PIL import Image

# Email需要用到的全局变量
fileName_mail = ''
fileName_mail_img = ''
fileName_mail_text = ''
fileName_mail_file = ''
fileName_mail_video = ''

# 初始登录框
# 下面这两行对应函数def login(*args):
IP = ''
PORT = ''

user = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '------群聊模式-------'  # 聊天对象, 默认为群聊

# 登陆窗口
root1 = tkinter.Tk()
# --这里我修改了界面和登录窗口大小
root1.title('登录界面')
root1['height'] = 170
root1['width'] = 300
root1.resizable(0, 0)  # 限制窗口大小

# 服务器信息
IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:6666')  # 默认显示的ip和端口
User = tkinter.StringVar()
User.set('')
# ftp所需信息
ftpUser = ''
ftpPassword = ''
ftpUser_tk = tkinter.StringVar()
ftpUser_tk.set('mary')  # 默认显示的ip和端口
ftpPassword_tk = tkinter.IntVar()
ftpPassword_tk.set('123456')

# 无关变量，用于后面的函数使用，这里使用者不用改
now_page = 0
image_name = ''
num = 0     # 用于给下面的list做下标，存储图片变量
list = ['aa', 'bb', 'cc', 'dd', 'ee', 'ff', 'gg', 'hh', 'jj', 'ii', 'kk']

# 这里的标签和上面的登录框都可以做大点，然后增加一些需要的美观(未做)
# 服务器标签
labelIP = tkinter.Label(root1, text='服务器的IP:')
labelIP.place(x=20, y=10, width=100, height=20)
entryIP = tkinter.Entry(root1, width=80, textvariable=IP1)
entryIP.place(x=120, y=10, width=130, height=20)

# 用户名标签
labelUser = tkinter.Label(root1, text='用户名:')
labelUser.place(x=30, y=40, width=80, height=20)
entryUser = tkinter.Entry(root1, width=80, textvariable=User)
entryUser.place(x=120, y=40, width=130, height=20)

# ftp用户名标签
labelFtpUser = tkinter.Label(root1, text='ftp用户名:')
labelFtpUser.place(x=30, y=70, width=80, height=20)
entryFtpUser = tkinter.Entry(root1, width=80, textvariable=ftpUser_tk)
entryFtpUser.place(x=120, y=70, width=130, height=20)

# ftp密码标签
labelFtpPassword = tkinter.Label(root1, text='ftp密码:')
labelFtpPassword.place(x=30, y=100, width=80, height=20)
entryFtpPassword = tkinter.Entry(root1, width=80, textvariable=ftpPassword_tk)
entryFtpPassword.place(x=120, y=100, width=130, height=20)


# 登录按钮
def login(*args):
    global IP, PORT, user, ftpUser, ftpPassword
    IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    PORT = int(PORT)  # 端口号需要为int类型
    user = entryUser.get()
    ftpUser = entryFtpUser.get()
    ftpPassword = entryFtpPassword.get()
    if not user:
        tkinter.messagebox.showerror('错误', message='请输入用户名')
    else:
        root1.destroy()  # 关闭登录窗口


root1.bind('<Return>', login)  # 回车绑定登录功能
but = tkinter.Button(root1, text='登录', command=login)
but.place(x=100, y=130, width=70, height=30)

# 让初始登录框一直存在不消失
root1.mainloop()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
if user:
    s.send(user.encode())  # 发送用户名
else:
    s.send('no'.encode())  # 没有输入用户名则标记no

# 如果没有用户名则将ip和端口号设置为用户名
addr = s.getsockname()  # 获取客户端ip和端口号
addr = addr[0] + ':' + str(addr[1])
if user == '':
    user = addr


# --------------------------聊天窗口---------------------------
# 聊天窗口
# 创建图形界面
root = tkinter.Tk()
root.title(user)  # 窗口命名为用户名
root['height'] = 400
root['width'] = 580
root.resizable(0, 0)  # 限制窗口大小

# 创建多行文本框
listbox = ScrolledText(root)
listbox.place(x=5, y=0, width=570, height=320)
# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')
listbox.insert(tkinter.END, 'Welcome to the chat room!', 'blue')

# -----------------------------------------------------------

# -------------------------图片发送功能1---------------------------------------
def image():
    # 进行ftp登录
    global IP
    server_address = IP
    # 创建FTP实例，并显示欢迎界面
    ftp = ftplib.FTP(server_address)
    # 这里要改下格式，因为ftplib默认的格式不支持中文
    ftp.encoding = 'UTF-8'
    # print(ftp.getwelcome())
    # 登录，输入服务器里添加过的用户名和口令
    global ftpUser
    global ftpPassword
    ftp.login(ftpUser, ftpPassword)
    global image_name

    # 首先先打开文件选择界面，获取对应的文件所在位置
    image_path = tkinter.filedialog.askopenfilename()
    image_name = image_path.split('/')[-1]

    # 这里我还要对图片的大小进行一下调整，放到代码同目录下即可
    # 修改图片大小函数
    def ResizeImage(filein, fileout, width, height, type):
        img = Image.open(filein)
        out = img.resize((width, height), Image.ANTIALIAS)
        # resize image with high-quality
        out.save(fileout, type)

    filein = image_path   # 图片原始位置
    fileout = image_name # 修改后的图片位置
    width = 250
    height = 200
    type = 'png'
    ResizeImage(filein, fileout, width, height, type)

    # 将图片利用ftp传到服务器上（利用了ftp函数里的upload功能）
    # fd = open(image_path, 'rb')
    fd = open(image_name, 'rb')
    # 以二进制的形式上传
    ftp.storbinary("STOR %s" % image_name, fd)
    fd.close()
    print("upload image finished")

    # 然后给服务器发个图片的信息，提示它把图片发给对应的用户
    # mes = exp + ':;' + user + ':;' + chat
    mes = 'image' + ':;' + user + ':;' + chat + ':;' + image_name
    print(mes)
    s.send(mes.encode())
    # 这里利用了ftp函数里的download功能


# 创建图片按钮
image_button = tkinter.Button(root, text='图片', command=image)
image_button.place(x=120, y=320, width=60, height=30)

# -------------------------图片发送功能2---------------------------------------


# --------------------------------------------显示当前在线用户功能1------------------
# 创建多行文本框, 显示在线用户
listbox1 = tkinter.Listbox(root)
listbox1.place(x=445, y=0, width=130, height=320)

def users():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        ii = 1

# 查看在线用户按钮
button1 = tkinter.Button(root, text='当前在线人数', command=users)
button1.place(x=485, y=320, width=90, height=30)

# --------------------------------------------显示当前在线用户功能2------------------


# ------------------------------------------最下方的聊天输入框1--------------
# 创建输入文本框和关联变量
a = tkinter.StringVar()
a.set('')
entry = tkinter.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=350, width=570, height=40)

# ------------------------------------------最下方的聊天输入框2--------------

# ------------------------------------------发送信息给服务器1--------------
def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    users.append('------群聊模式-------')
    print(chat)
    if chat not in users:
        tkinter.messagebox.showerror('Send error', message='There is nobody to talk to!')
        return
    if chat == user:
        tkinter.messagebox.showerror('Send error', message='Cannot talk with yourself in private!')
        return
    mes = entry.get() + ':;' + user + ':;' + chat  # 添加聊天对象标记
    s.send(mes.encode())
    a.set('')  # 发送后清空文本框


# 创建发送按钮
button = tkinter.Button(root, text='发送', command=send)
button.place(x=515, y=353, width=60, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息
# ------------------------------------------发送信息给服务器2--------------


# --------------------------------------私聊功能1---------------------------
def private(*args):
    global chat
    # 获取点击的索引然后得到内容(用户名)
    indexs = listbox1.curselection()
    index = indexs[0]
    if index > 0:
        chat = listbox1.get(index)
        # 修改客户端名称
        if chat == '------群聊模式-------':
            root.title(user + ' 的群聊窗口')
            return
        # 下面这两行用于在标题头处显示目前是谁和谁在聊天
        ti = user + '  与  ' + chat + ' 的聊天窗口'
        root.title(ti)


# 在显示用户列表框上设置绑定事件
listbox1.bind('<ButtonRelease-1>', private)

# --------------------------------------私聊功能2---------------------------


# --------------------------------------邮件功能1---------------------------
def emailTest():
    # 先像ftp一样创建一个界面出来
    root['height'] = 400
    root['width'] = 1000
    # 下面这个是在多出来的宽度中加一个白色列表框
    list_mail = tkinter.Listbox(root, bg='#f0f0f0')
    list_mail.place(x=580, y=25, width=400, height=325)

    # 创建信息输入框（包括发送者邮箱，收件者邮箱，主题，内容）
    # 发送者邮箱标签
    sender_mail = tkinter.Label(root, text='发送者邮箱:')
    sender_mail.place(x=590, y=30, height=30, width=70)
    sender_box = tkinter.StringVar()
    sender_box.set('example@163.com')
    entry_sender = tkinter.Entry(root, width=80, textvariable=sender_box)
    entry_sender.place(x=680, y=30, height=30, width=250)

    # 发送者电子邮箱密码 / 授权码：
    sender_passwd = tkinter.Label(root, text='邮箱密码/授权码:')
    sender_passwd.place(x=590, y=70, height=30, width=130)
    sender_passwd_content = tkinter.StringVar()
    sender_passwd_content.set('password')
    entry_sender_passwd = tkinter.Entry(root, width=80, textvariable=sender_passwd_content)
    entry_sender_passwd.place(x=730, y=70, height=30, width=200)

    # 接收者邮箱标签
    recipients_mail = tkinter.Label(root, text='接收者邮箱:')
    recipients_mail.place(x=590, y=110, height=30, width=70)
    recipients_box = tkinter.StringVar()
    recipients_box.set('')
    entry_recipients = tkinter.Entry(root, width=80, textvariable=recipients_box)
    entry_recipients.place(x=680, y=110, height=30, width=250)

    # 主题标签
    mail_topic = tkinter.Label(root, text='主题:')
    mail_topic.place(x=590, y=150, height=30, width=70)
    mail_topic_content = tkinter.StringVar()
    mail_topic_content.set('')
    entry_mail_topic = tkinter.Entry(root, width=80, textvariable=mail_topic_content)
    entry_mail_topic.place(x=680, y=150, height=30, width=250)

    # body标签
    mail_body = tkinter.Label(root, text='内容:')
    mail_body.place(x=590, y=190, height=30, width=70)
    mail_body_content = tkinter.StringVar()
    mail_body_content.set('')
    entry_mail_body = tkinter.Text(root)  # 这里用Text文本框来保存信息
    entry_mail_body.place(x=680, y=190, height=150, width=270)

    # 添加附件功能模块
    # 让用户选择文件，然后获取对应文件名
    def put():
        # 选择对话框
        global fileName_mail
        global fileName_mail_img
        global fileName_mail_text
        global fileName_mail_file
        global fileName_mail_video
        fileName_mail = tkinter.filedialog.askopenfilename(title='Select upload file')

        # 这里对名字再做一个判断，然后为对应的文件赋值对应变量名，最后再用if来判断文件是否存在
        # 记得先要在开头初始化变量，初步选择文件为txt,jpg,exe,看看支持什么类型把
        # print(fileName_mail)
        # 这里判断一下文件类型，赋予不同的文件名(这里的判断应该会比较繁琐，但我暂时找不到更好的办法)
        if fileName_mail.split('.')[-1] == 'jpg' or fileName_mail.split('.')[-1] == 'png':
            fileName_mail_img = fileName_mail
        elif fileName_mail.split('.')[-1] == 'txt' or fileName_mail.split('.')[-1] == 'docx' \
                or fileName_mail.split('.')[-1] == 'pdf' or fileName_mail.split('.')[-1] == 'doc' \
                or fileName_mail.split('.')[-1] == 'epub':
            fileName_mail_text = fileName_mail
        elif fileName_mail.split('.')[-1] == 'exe' or fileName_mail.split('.')[-1] == 'zip' \
                or fileName_mail.split('.')[-1] == 'rar':
            fileName_mail_file = fileName_mail
        elif fileName_mail.split('.')[-1] == 'mp3' or fileName_mail.split('.')[-1] == 'mp4' \
                or fileName_mail.split('.')[-1] == 'avi':
            fileName_mail_video = fileName_mail
        else:
            fileName_mail_file = fileName_mail

    # 创建上传按钮, 并绑定上传文件功能
    upload_mail_attachment = tkinter.Button(root, text='附件', command=put)
    upload_mail_attachment.place(x=610, y=353, height=30, width=80)

    # 给发送邮件做个按钮
    def send_mail():
        global fileName_mail_img
        global fileName_mail_file
        global fileName_mail_text
        global fileName_mail_video
        # 然后给对应变量赋值即可
        sender = entry_sender.get()
        # sender = input('请输入一个电子邮箱地址（163/QQ）：')
        username, domain = sender.split('@')
        if domain == '163.com':
            host = 'smtp.163.com'
        elif domain == 'qq.com':
            host = 'smtp.qq.com'
        else:
            # print('当前代码只识别163和QQ邮箱，请检查邮箱地址或修改代码。')
            exit()
        port = 25

        body = entry_mail_body.get("1.0", "end")  # 这个get里面的参数是获得所有信息的

        # 输入密码，无回显，需要在cmd或PowerShell运行程序
        userpwd = entry_sender_passwd.get()
        # 要群发的电子邮件地址
        recipients = entry_recipients.get()

        # 登录邮箱服务器
        with SMTP(host, port) as server:
            server.starttls()
            server.login(username, userpwd)

            # 如果发给每个收件人的内容一样，可以不用循环
            # 如果发给每个收件人的内容有所不同，可以使用循环
            # for recipient in recipients.split(';'):
            # 如果使用循环的话，下面的代码需要再缩进一层
            # 创建邮件
            msg = MIMEMultipart()
            msg.set_charset('utf-8')
            # 回复地址与发信地址可以不同
            # 但是大部分邮件系统在回复时会提示
            msg['Reply-to'] = sender
            # 设置发信人、收信人和主题
            msg.add_header('From', sender)
            msg.add_header('To', recipients)
            msg.add_header('Subject', entry_mail_topic.get())
            msg['Date'] = formatdate()
            msg['Message-Id'] = make_msgid()
            # 设置邮件文字内容
            msg.attach(MIMEText(body, 'plain', _charset='utf-8'))

            # ---------------------------------这里为添加附件功能-------------------
            # 首先是要打开一个窗口，然后获取到对应的文件名
            # 添加图片
            fn = fileName_mail_img
            print(fn)
            if fn :
                with open(fn, 'rb') as fp:
                    attachment = MIMEImage(fp.read())
                    attachment.add_header('content-disposition',
                                          'attachment', filename=fn.split('/')[-1])
                    msg.attach(attachment)

            # 添加文本文件
            fn = fileName_mail_text
            print(fn)
            if fn:
                with open(fn, 'rb') as fp:
                    attachment = MIMEBase('text', 'txt')
                    attachment.set_payload(fp.read())
                    encode_base64(attachment)
                    attachment.add_header('content-disposition',
                                          'attachment',
                                          filename=fn.split('/')[-1])
                    msg.attach(attachment)

            # 添加可执行程序
            fn = fileName_mail_file
            print(fn)
            if fn:
                with open(fn, 'rb') as fp:
                    attachment = MIMEApplication(fp.read(),
                                                 _encoder=encode_base64)
                    attachment.add_header('content-disposition',
                                          'attachment', filename=fn.split('/')[-1])
                    msg.attach(attachment)

            # 添加音乐文件
            fn = fileName_mail_video
            print(fn)
            if fn:
                with open(fn, 'rb') as fp:
                    attachment = MIMEAudio(fp.read(), 'plain',
                                           _encoder=encode_base64)
                    attachment.add_header('content-disposition',
                                          'attachment', filename=fn.split('/')[-1])
                    msg.attach(attachment)
            # 发送邮件
            server.send_message(msg)

            # 每次发完清空附件
            fileName_mail_file = ''
            fileName_mail_text = ''
            fileName_mail_video = ''
            fileName_mail_img = ''

    # 创建发送邮件按钮
    close_mail = tkinter.Button(root, text='发送', command=send_mail)
    close_mail.place(x=800, y=353, height=30, width=90)

    # 再加个close按钮，即添加close功能
    def closeFile_mail():
        root['height'] = 390
        root['width'] = 580

    # 创建关闭按钮
    close_mail = tkinter.Button(root, text='退出', command=closeFile_mail)
    close_mail.place(x=910, y=353, height=30, width=70)

# 创建email按钮
mBut = tkinter.Button(root, text='邮件', command=emailTest)
mBut.place(x=5, y=320, width=60, height=30)

# --------------------------------------邮件功能2---------------------------

list2 = ''  # 列表框
# --------------------------------------ftp功能1---------------------------
def fileClient():
    # 首先在下面创建出一个界面
    root['height'] = 650
    root['width'] = 580
    # 下面这个是在多出来的高度中加一个白色列表框
    list_ftp= tkinter.Listbox(root, bg='#f0f0f0')
    list_ftp.place(x=580, y=25, width=400, height=325)

    # 进行ftp登录
    global IP
    server_address = IP
    # 创建FTP实例，并显示欢迎界面
    ftp = ftplib.FTP(server_address)
    # 这里要改下格式，因为ftplib默认的格式不支持中文
    ftp.encoding = 'UTF-8'
    # print(ftp.getwelcome())
    # 登录，输入服务器里添加过的用户名和口令
    global ftpUser
    global ftpPassword
    ftp.login(ftpUser, ftpPassword)

    # 创建展示ftp目录文件的列表框--------------
    # 创建列表框（list2是被初始化过的，在上面大概二十行可以找到）
    list2 = tkinter.Listbox(root)
    list2.place(x=330, y=390, width=230, height=325)

    # 展示ftp目录当前存在的文件
    def show_ftp():
        global now_page
        # 将打印出来的数据截取出对应的文件名(这个有点巧妙）
        dir_res = []
        ftp.dir('.', dir_res.append)  # 对当前目录进行dir()，将结果放入列表
        # print(dir_res)
        print(len(dir_res))     # 打印列表长度
        # 由文件名判断名称是文件还是目录
        for i in range(14):
            # 防止数组越界
            if (now_page*14)+i <= len(dir_res)-1:
                name = dir_res[(now_page*14)+i].split(' ')[-1]
                # print(name)
                # 将名称插入列表
                list2.insert(tkinter.END, name)
                # 通过.号判断是否为文件或文件夹，从而赋予不同的颜色(暂时未测试过文件夹)
                if '.' not in name:
                    list2.itemconfig(tkinter.END, fg='orange')
                else:
                    list2.itemconfig(tkinter.END, fg='blue')
        # print(dir_res[1])
        # 列表里最多展示14个文件名称,考虑下能不能改动做分页展示(可以考虑做两个函数来解决,已解决)

    # 第一次先展示ftp界面，也顺手清一下列表框
    list2.delete(0, tkinter.END)  # 清空列表框
    show_ftp()

    # 下一页,一页最多显示14条数据
    def next_page():
        global now_page
        now_page += 1
        list2.delete(0, tkinter.END)  # 清空列表框
        show_ftp()

    # 上一页
    def pre_page():
        global now_page
        if(now_page >=1):
            now_page -= 1
        print('pre: now_page -->' + str(now_page))
        list2.delete(0, tkinter.END)  # 清空列表框
        show_ftp()

    # 上一页按钮
    pre_page_button = tkinter.Button(root, text='上一页', command=pre_page)
    pre_page_button.place(x=250, y=450, width=60, height=30)
    # 下一页按钮
    next_page_button = tkinter.Button(root, text='下一页', command=next_page)
    next_page_button.place(x=250, y=500, width=60, height=30)

    def upload_ftp():
        # 思路：先获取到对应文件名，然后以二进制形式上传,ftp的目录信息是在服务端进行设置的
        # 这里获取到的是一个数组,所以下面我用遍历的方式解决
        fileName_ftp = tkinter.filedialog.askopenfilenames()
        for name in fileName_ftp:
            print('ftp--->'+name)
            fd = open(name, 'rb')
            # 因为fileName_ftp包含绝对路径，所以这里我们要提取出最后的名字
            new_name = name.split('/')[-1]
            # 以二进制的形式上传
            ftp.storbinary("STOR %s" % new_name, fd)
        fd.close()
        # 上传完文件后刷新一遍目录窗口,首先要清空目录，再重载
        list2.delete(0, tkinter.END)  # 清空列表框
        show_ftp()
        print("upload finished")

    def upload_ftpdir():
        # 思路：先获取到对应文件名，然后以二进制形式上传,ftp的目录信息是在服务端进行设置的
        # 获取文件夹名,并判断ftp目录里是否存在该文件夹
        fileName_ftp = tkinter.filedialog.askdirectory()
        fileName_ftp_end = fileName_ftp.split('/')[-1]
        dir = []
        ftp.dir('.', dir.append)  # 对当前目录进行dir()，将结果放入列表
        # 将打印信息拼接成字符串，方便后面的not in 判断
        rubbish = ''
        for i in dir:
            rubbish = rubbish + i
            # print(rubbish)
        if fileName_ftp_end not in rubbish:
            # 不存在则创建文件夹
            ftp.mkd(fileName_ftp_end)
            # 然后进行下载
            ftp.cwd(fileName_ftp_end)
            dir_res = []
            files = os.listdir(fileName_ftp)
            print(files)
            for i in files:
                dir_res.append(i)
            print(dir_res)
            for name in dir_res:
                print(fileName_ftp + '/' + name)
                fd = open(fileName_ftp + '/' + name, 'rb')
                # 以二进制的形式上传
                ftp.storbinary("STOR %s" % name, fd)
                fd.close()
        else:
            ftp.cwd(fileName_ftp_end)
            dir_res = []
            files = os.listdir(fileName_ftp)
            print(files)
            for i in files:
                dir_res.append(i)
            print(dir_res)
            # ftp.dir(fileName_ftp_end, dir_res.append)  # 对当前目录进行dir()，将结果放入列表
            # print(dir_res)
            for name in dir_res:
                print(fileName_ftp + '/' + name)
                fd = open(fileName_ftp + '/' + name, 'rb')
                # 以二进制的形式上传
                ftp.storbinary("STOR %s" % name, fd)
                fd.close()
        # 传完文件后再把目录切回原目录，再刷新界面
        ftp.cwd('..')
        # 上传完文件后刷新一遍目录窗口,首先要清空目录，再重载
        list2.delete(0, tkinter.END)  # 清空列表框
        show_ftp()
        print("upload finished")

    def download_ftp():
        # 获取到要下载到本地的文件名(只需要名字就行)
        fileName_ftp = list2.get(list2.curselection())
        print(fileName_ftp)
        # 对文件名做判断
        if '.' not in fileName_ftp:
            # 如果是文件夹的话就切换ftp目录进该文件夹，再下载，最后返回源目录
            ftp.cwd(fileName_ftp)
            dir_res = []
            # 将目录内文件信息保存到dir_res中
            ftp.dir('.', dir_res.append)  # 对当前目录进行dir()，将结果放入列表
            # print(dir_res)
            # 从dir_res中取出文件名放入files数组中
            files = []
            for i in dir_res:
                files.append(i.split(' ')[-1])
            # print(files)
            # 设置文件存储路径（路径为文件夹类型）
            dir_path = tkinter.filedialog.askdirectory()
            os.mkdir(dir_path + '\\' + fileName_ftp)
            # print(dir_path_end)
            for j in files:
                # 是文件的话就直接下载
                # 这里要对目录路径进行一些小替换以符合格式
                dir_path_end = dir_path.replace("/", '\\') + '\\' + fileName_ftp + '\\' + j
                fd = open(dir_path_end, 'wb')
                # 以二进制形式下载，注意第二个参数是fd.write，上传时是fd
                ftp.retrbinary("RETR %s" % j, fd.write)
                fd.close()
            ftp.cwd('..')
        else:
            # 是文件的话就直接下载
            # 设置文件存储路径（路径为文件夹类型）
            dir_path = tkinter.filedialog.askdirectory()
            # 这里要对目录路径进行一些小替换以符合格式
            dir_path_end = dir_path.replace("/", '\\') + '\\' + fileName_ftp
            print(dir_path_end)
            fd = open(dir_path_end, 'wb')
            # 以二进制形式下载，注意第二个参数是fd.write，上传时是fd
            ftp.retrbinary("RETR %s" % fileName_ftp, fd.write)
            fd.close()
        print("download finished")

    def join():
        # 获取到要下载到本地的文件名(只需要名字就行)
        fileName_ftp = list2.get(list2.curselection())
        ftp.cwd(fileName_ftp)
        # 刷新一遍目录窗口,首先要清空目录，再重载
        list2.delete(0, tkinter.END)  # 清空列表框
        show_ftp()

    def Back():
        ftp.cwd('..')
        # 刷新一遍目录窗口,首先要清空目录，再重载
        list2.delete(0, tkinter.END)  # 清空列表框
        show_ftp()

    def delete_ftp():
        # 获取到要下载到本地的文件名(只需要名字就行)
        fileName_ftp = list2.get(list2.curselection())
        print(fileName_ftp)
        # 通过.号判断是否为文件或文件夹，从而赋予不同的颜色
        if '.' not in fileName_ftp:
            # 因为rmd命令只能删空目录
            # 所以我们要先递归删除目录里的文件
            dir_res = []
            ftp.dir(fileName_ftp, dir_res.append)  # 对当前目录进行dir()，将结果放入列表
            print(dir_res)
            for i in dir_res:
                name = i.split(' ')[-1]
                print(name)
                ftp.delete(fileName_ftp + '/' + name)
            ftp.rmd(fileName_ftp)
        else:
            ftp.delete(fileName_ftp)
        print("delete finished")
        # 上传完文件后刷新一遍目录窗口,首先要清空目录，再重载
        list2.delete(0, tkinter.END)  # 清空列表框
        show_ftp()

    def close_ftp():
        root['height'] = 390
        root['width'] = 580

    # 创建按钮（包含上传文件，下载目录，退出）
    # 上传按钮
    upload_button_ftp = tkinter.Button(root, text='上传文件', command=upload_ftp)
    upload_button_ftp.place(x=0, y=450, width=60, height=30)
    upload_button_ftp = tkinter.Button(root, text='上传目录', command=upload_ftpdir)
    upload_button_ftp.place(x=100, y=450, width=60, height=30)
    # 下载按钮
    download_button_ftp = tkinter.Button(root, text='下载', command=download_ftp)
    download_button_ftp.place(x=0, y=500, width=60, height=30)
    # 子目录按钮
    download_button_ftp = tkinter.Button(root, text='进入目录', command=join)
    download_button_ftp.place(x=100, y=500, width=60, height=30)
    # 返回上一层目录按钮
    download_button_ftp = tkinter.Button(root, text='返回上一层目录', command=Back)
    download_button_ftp.place(x=100, y=550, width=105, height=30)
    # 删除按钮
    download_button_ftp = tkinter.Button(root, text='删除', command=delete_ftp)
    download_button_ftp.place(x=0, y=550, width=60, height=30)
    # 退出按钮
    close_button_ftp = tkinter.Button(root, text='退出', command=close_ftp)
    close_button_ftp.place(x=0, y=600, width=60, height=30)

# 创建ftp按键
fBut = tkinter.Button(root, text='传输文件', command=fileClient)
fBut.place(x=65, y=320, width=60, height=30)
# --------------------------------------ftp功能2---------------------------


# --------------------------------------接收服务器的信息并打印1---------------------------
# 用于时刻接收服务端发送的信息并打印
def recv():
    global users
    while True:
        data = s.recv(1024)
        data = data.decode()
        print('data')
        print(data)
        # 没有捕获到异常则表示接收到的是在线用户列表
        try:
            data = json.loads(data)
            users = data
            listbox1.delete(0, tkinter.END)  # 清空列表框
            number = ('   当前在线人数: ' + str(len(data)))
            listbox1.insert(tkinter.END, number)
            listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
            listbox1.insert(tkinter.END, '------群聊模式-------')
            # listbox1.insert(tkinter.END, 'Robot')
            listbox1.itemconfig(tkinter.END, fg='green')
            for i in range(len(data)):
                listbox1.insert(tkinter.END, (data[i]))
                listbox1.itemconfig(tkinter.END, fg='green')
        except:
            data = data.split(':;')
            print(data[0])
            # print('data')
            # print(data)
            data1 = data[0].strip()  # 消息，格式大概为：[' 1：hello', '1', '2']
            # print('data1')
            # print(data1)
            data2 = data[1]  # 发送信息的用户名
            # print('data2')
            # print(data2)
            data3 = data[2]  # 聊天对象名
            # print('data3')
            # print(data3)

            # 判断是否为图片,是的话就把图片下载到聊天对象那里所处的目录即./
            # 地址为：E:\python\code\lesson_code\failQQ\emoji  这种类型
            if(data[0].split('：')[-1] == 'image'):
                # 进行ftp登录
                global IP
                server_address = IP
                # 创建FTP实例，并显示欢迎界面
                ftp = ftplib.FTP(server_address)
                # 这里要改下格式，因为ftplib默认的格式不支持中文
                ftp.encoding = 'UTF-8'
                # print(ftp.getwelcome())
                # 登录，输入服务器里添加过的用户名和口令
                global ftpUser
                global ftpPassword
                ftp.login(ftpUser, ftpPassword)

                # print('download_image:   ' + image_name)
                image_name = data[3]
                dir_path = '.\\' + image_name
                # print(dir_path)
                fd = open(dir_path, 'wb')
                # 以二进制形式下载，注意第二个参数是fd.write，上传时是fd
                ftp.retrbinary("RETR %s" % image_name, fd.write)
                fd.close()
                print("download image finished")

                # 图片下载成功后将其打开设置为变量，然后插入对话框即可

            # 如果接收到的信息里含有图片，则取出图片赋给变量，再打开
            if(data[0].split('：')[-1] == 'image'):
                listbox.insert(tkinter.END, '\n')
                print('data3')
                print(data[3])
                global num
                image_path_temp = './' + data[3]
                print(image_path_temp)
                # 这里只能发png类型的图片，而且还要限制一下图片大小才行
                list[num] = tkinter.PhotoImage(file=image_path_temp)
                # list[num].resize((220, 220))
                listbox.image_create(tkinter.END, image=list[num])
                num += 1

            else:
                data1 = data1
                # 群聊模式
                if data3 == '------群聊模式-------':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, '\n' + data1, 'blue')
                    else:
                        listbox.insert(tkinter.END, '\n' + data1, 'green')  # END将信息加在最后一行
                    if len(data) == 4:  # 这个好像没用可以删
                        listbox.insert(tkinter.END, '\n' + data[3], 'pink')
                # 私聊模式
                elif data2 == user or data3 == user:  # 显示私聊
                    # listbox.insert(tkinter.END, data1, 'red')  # END将信息加在最后一行
                    listbox.insert(tkinter.END, '\n' + data2 + '-->' + data3 + ': ' + data1.split('：')[-1], 'red')  # END将信息加在最后一行
            listbox.see(tkinter.END)  # 显示在最后


r = threading.Thread(target=recv)
r.start()  # 开始线程接收信息

root.mainloop()
s.close()  # 关闭图形界面后关闭TCP连接
# --------------------------------------接收服务器的信息并打印2---------------------------
