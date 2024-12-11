import socket
import threading

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
print(SERVER)
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a new socket (First arg is family, Second is type)
server.bind(ADDR)





