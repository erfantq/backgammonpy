import socket
import rsa
import json
import pickle
from cryptography.hazmat.primitives import serialization

class P2PClient:
    def __init__(self, host="127.0.0.1", port=6000, router_host="127.0.0.1", router_port=7001, public_keys_str=[], public_keys = [], chunk_size=53):
        self.host = host
        self.port = port
        self.router_host = router_host
        self.router_port = router_port
        self.public_keys_str = public_keys_str
        self.public_keys = public_keys
        self.chunk_size = chunk_size
       
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
            client.connect((self.router_host, self.router_port))
            # ارسال پیام ثبت‌نام
            registration_message = f"REGISTER_CLIENT {self.port}"
            client.send(registration_message.encode())
            
            response = client.recv(8192)
            received_keys = pickle.loads(response)
            print(f"reseived_keys is {received_keys}")
            self.public_keys = received_keys
                                            

    def encrypt_message(self, message):
        # encrypted_message = message.encode()

        # encrypted_message = rsa.encrypt(encrypted_message, self.public_keys[0])

        # for key in self.public_keys[::-1]:
        #     chunks = self.split_message(encrypted_message, self.chunk_size)
        #     encrypted_message = [rsa.encrypt(chunk, key) for chunk in chunks]
        #     # print(type(key))
        #     # signature = rsa.sign(encrypted_message, key, 'SHA-256')
        #     # signatures.append(signature)
        chunks = self.split_message(message, self.chunk_size)
        encrypted_chunks = []
        for chunk in message:
            encrypted_chunk = chunk.encode()
            for key in self.public_keys[::-1]:  # رمزنگاری از کلید عمومی 3 به 1
                encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
            encrypted_chunks.append(encrypted_chunk)
        return encrypted_chunks
                
            
    def split_message(self, message, chunk_size):
        return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

    def send_message(self, message):
            """ارسال پیام به روتر اول"""
            encrypted_chunks = self.encrypt_message(message)
            # print(f"signatures_len: {len(signatures)}")
            # bytes_data = pickle.dumps(signatures)
            # data_to_send = encrypted_message + b'||' + bytes_data
            # print(f"data_to_send: {encrypted_message}")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.router_host, self.router_port))
                # ارسال کلید عمومی و پیام
                # data_to_send = b'REQUEST_PEERS||b8\xf9q\x03\xa8/.J\xdfAd\t\xd8\tC=\x9b|`)\xf0\x8e\xfd\xdc\xd6/\x19J\xbf\xfe]\x85~\xc8\xb4r\xae\x8f\r\x92\x9d\xbb\xb4f\x10\xce\xe3\xf3\xbd\xbf\xa3\xcd\x7f\xf6\xa0\xf0\xc3\x18\xf6:\xf5\x90\xad||\x1e\xdf\xc8\x96\xcc*R82\x02jv\x1dA\xd7MO\xa6;\x7f\xc0Dz\xf0\x9aNv\xf1\x05<\x04<\xe6\xb2\xf7\xb4$;\x8fP;)\x89\xee\x18\x9e\x03CgL\x92xyn\x99eFE\x1c)\xd5\x92^?||\x82wx\x1e?{\xd7\x9d\xc1\x9c\xcc\xa1(\xfd,Y\xd5\xd8\x1d@\xdd\xe4"\x9c\xae>\x0f\x1b1\x8b\x92\xb7\x86\xa7k3\x03\x8c\xd4\xdc\x8eo\xb70\xfe%\xd0\xa6F)?\xaa\xbb3\x1e\xac\x7f\xa6\xd3rk\xbcH\xd5'
                # print(type(data_to_send))
                # for chunk in encrypted_chunks:
                    # chunk_list = [chunk]
                    
                client.send(encrypted_chunks)
                
                response = client.recv(8192).decode()


    def request_peers(self):
        message = "REQUEST_PEERS"
        self.send_message(message)
        
        

if __name__ == "__main__":
    client = P2PClient(port=6001)  # پورت متفاوت برای کلاینت
    client.start()
