import socket
import sys
import time

new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
new_socket.connect(("8.8.8.8", 80))
s_ip = new_socket.getsockname()[0]
print(s_ip)
new_socket.close()
#host_name = socket.gethostname()
#port = 55003
#
#new_socket.bind((s_ip, port))
#print("Binding successful!")
#print("This is your hostname: ", host_name)
#print("This is your IP: ", s_ip)
#
#name = input("Enter name:")
#new_socket.listen(1)
#
#conn, add = new_socket.accept()
#print("Received connection from", add[0])
#print("Connection Established. Connected From", add[0])
#
#client = (conn.recv(1024)).decode()
#print(client + "has connected.")
#conn,send(name.encode())
#
#while True:
#    message = input("Me: ")
#    conn.send(message.encode())
#    message = conn.recv(1024)
#    message = message.decode()
#    print(client, ":", message)
