import socket
import signal
import threading
import time
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from router import Router


class P2PClient:

    def __init__(self, host="127.0.0.1", port=6000, router_host="127.0.0.1", router_port=7001, keys=None):
        self.host = host
        self.port = port
        self.router_host = router_host
        self.router_port = router_port
        self.keys = keys
       
    def start(self):
        while True:
            choice = input("1. See client list\n2. connect to someone\n3. Exit\nEnter choice: ")
            if choice == "1":
                self.request_peers()
            elif choice == "2":
                client_two_port = input("Enter port of client : ")
                self.connect_to_client(self.router_host ,client_two_port)
            elif choice == "3":
                break
            else:
                print("Invalid option!")                                            

    def encrypt_message(self, key, message):
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(message.encode())
        return base64.b64encode(nonce + ciphertext).decode()
      
    def decrypt_message(self, key, encrypted_message):
        data = base64.b64decode(encrypted_message.encode())
        nonce = data[:16]
        ciphertext = data[16:]
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt(ciphertext).decode()          

    def send_message(self, message):
        """send message to first router."""
        encrypted_message = message
        for key in reversed(self.keys):
            encrypted_message = self.encrypt_message(key, encrypted_message)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((self.router_host, self.router_port))
            client.sendall(encrypted_message.encode())
            response = client.recv(1024).decode()

        decrypted_response = response
        for key in self.keys:
            decrypted_response = self.decrypt_message(key, decrypted_response)
        
        print(f"Client received response: {decrypted_response}")        
        
        return decrypted_response    
            
    def request_peers(self):
        message = "REQUEST_PEERS"
        response = self.send_message(message)
    
    def connect_to_client(self,client_two_host, client_two_port):
        message = f"CONNECT TO CLIENT{client_two_port}"
        response = self.send_message(message)
        if response == "YES":        
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(client_two_host, client_two_port)

    def receive_messages(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.router_host, self.router_port))
        while True:
            try:
                message = client.recv(1024).decode()
                print(f"\n{message}")
                if message.startswith("CONNECTION_REQUEST"):
                    port = message.replace("CONNECTION_REQUEST", "")
                    while True:
                        response = input(f"{port} want to connect you, do you agree?? (yes/no)")
                        if(response == "yes"):
                            client.send("YES".encode())
                            break
                        elif(response == "no"):
                            client.send("NO".encode())
                            break
                        else:
                            print("Wrong input")
            except:
                print("Connection lost.")
                break


def handle_sigint(signal_number, frame):
    os.remove("first_run.lock")
    exit(0)

def start_router(port, next_port=None, key=None):
    router = Router(port=port, next_router=next_port, key=key)
    router.start()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)

    # keys = [get_random_bytes(16) for _ in range(3)]  # Three random keys for encryption layers
    keys = [b'\xbd_+\xa2\xf0\x7f\xd8\x0c\xce\xf3\xfe\x0f`8E\xd0', b'\x0b\x8be\xce\xe3\xfa9\xfb4o\xe4\x05\xb7\xda\x89\xc2', b'\xed\xfa\xcf\x16@\x909/\x80o\xd2\xadupET']
    
    
    status_file = "first_run.lock"
    if not os.path.exists(status_file):
        threading.Thread(target=start_router, args=(7001, ("127.0.0.1", 7002), keys[0]), daemon=True).start()
        threading.Thread(target=start_router, args=(7002, ("127.0.0.1", 7003), keys[1]), daemon=True).start()
        threading.Thread(target=start_router, args=(7003, ("127.0.0.1", 5000), keys[2]), daemon=True).start()
        with open(status_file, "w") as file:
            file.write("Executed")    
    
    port = input("Enter the port number:(6000-6010)")
    client = P2PClient(port=port, keys=keys)  # پورت متفاوت برای کلاینت
    client.send_message(f"REGISTER_CLIENT {client.port}")
    client.start()
