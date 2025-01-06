import socket
import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class P2PClient:
    def __init__(self, host="127.0.0.1", port=6000, server_host="127.0.0.1", server_port=7001, public_keys_str=[], public_keys = []):
        self.host = host
        self.port = port
        self.server_host = server_host
        self.server_port = server_port
        self.public_keys_str = public_keys_str
        self.public_keys = public_keys
       
        

    def start(self):
        self.register_with_server()
        
        
        while True:
            choice = input("1. See client list\n2. Exit\nEnter choice: ")
            if choice == "1":
                self.request_peers()
            elif choice == "2":
                break
            else:
                print("Invalid option!")

        
    def register_with_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((self.server_host, self.server_port))
            # ارسال پیام ثبت‌نام
            registration_message = f"REGISTER_CLIENT {self.port}"
            client.send(registration_message.encode())
            
            
            response = client.recv(2048).decode()
            # print(f"response is {response}")
            self.public_keys_str = response.split("PublicKey")
            del self.public_keys_str[0]
            for key in self.public_keys_str:
                newKey = "PublicKey"
                newKey += key
                
                
                public_key = serialization.load_pem_public_key(newKey.encode())
                self.public_keys.append(public_key)
            print(self.public_keys)
            
            
            
            

    def encrypt_message(self, message):
        encrypted_message = message.encode()

        for key in self.public_keys[::-1]:
            encrypted_message = rsa.encrypt(encrypted_message, key)
            
        return encrypted_message
            

    def send_message(self, message):
            """ارسال پیام به روتر اول"""
            encrypted_message = self.encrypt_message(message)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.router_host, self.router_port))
                # ارسال کلید عمومی و پیام
                client.send(encrypted_message)
                
                response = client.recv(2048).decode()


    def request_peers(self):
        message = "[CLIENT]REQUEST_PEERS"
        self.send_message(message)
        
        

if __name__ == "__main__":
    client = P2PClient(port=6001)  # پورت متفاوت برای کلاینت
    client.start()
