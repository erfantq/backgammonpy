# client.py
import socket
import threading

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            print(f"\n{message}")
        except:
            print("Connection lost.")
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 9999))
    
    threading.Thread(target=receive_messages, args=(client,)).start()
    
    while True:
        try:
            message = input(">> ")
            client.send(message.encode())
        except:
            break

if __name__ == "__main__":
    main()
