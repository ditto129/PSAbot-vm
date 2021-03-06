import time, socket, sys
import urllib.request

external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

print("This is your IP: ", external_ip)
 
new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
s_ip = socket.gethostbyname(host_name)
port = 55003

new_socket.bind((host_name, port))
print("Binding successful!")
print("This is your hostname: ", host_name)
print("This is your IP: ", s_ip)

name = input("Enter name: ")
new_socket.listen(1)

conn, add = new_socket.accept()
print("Received connection from", add[0])
print("Connection Established. Connected From", add[0])

client = (conn.recv(1024)).decode()
print(client + " has connected.")
conn.send(name.encode())

while True:
    message = input("Me: ")
    conn.send(message.encode())
    message = conn.recv(1024)
    message = message.decode()
    print(client, ":", message)
