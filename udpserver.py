import socket

host = '127.0.0.1'
port = 9999

udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind((host, port))
print '..waiting for message..'
while True:
    data, address = udp_server.recvfrom(1024)
    print 'Received data %s for %s:%d' %(data, address[0], address[1])
    udp_server.sendto('success', address)
udp_server.close()
