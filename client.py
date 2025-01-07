import socket
import rsa
import json
import pickle
from cryptography.hazmat.primitives import serialization
import threading


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
        threading.Thread(target=self.receive_messages, args=()).start()

        
       
        
        while True:
            choice = input("1. See client list\n2. connect ro someone\n3. Exit\nEnter choice: ")
            if choice == "1":
                self.request_peers()
            elif choice == "2":
                client_two_port = input("Enter port of client : ")
                self.connect_to_client(self.router_host ,client_two_port)
            elif choice == "3":
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
        message = message.encode()
        array_message = [message]
        chunks = self.split_strings_array_by_bytes(array_message, self.chunk_size)
        encrypted_chunks = []
        for chunk in chunks:
            encrypted_chunk = chunk
            key = self.public_keys[2]
            encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
            encrypted_chunks.append(encrypted_chunk)

        encrypted_chunks = self.split_strings_array_by_bytes(encrypted_chunks, self.chunk_size)
        for chunk in chunks:
            encrypted_chunk = chunk
            key = self.public_keys[1]
            encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
            encrypted_chunks.append(encrypted_chunk)

        encrypted_chunks = self.split_strings_array_by_bytes(encrypted_chunks, self.chunk_size)
        for chunk in chunks:
            encrypted_chunk = chunk
            key = self.public_keys[0]
            encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
            encrypted_chunks.append(encrypted_chunk)
        
        return encrypted_chunks
                
    def split_strings_array_by_bytes(self, strings_array, byte_size):
        
        result = []
        
        for input_string in strings_array:
            byte_data = input_string
            chunks = [byte_data[i:i + byte_size] for i in range(0, len(byte_data), byte_size)]
            result.extend([chunk for chunk in chunks])
        
        return result

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
                encrypted_chunks = pickle.dumps(encrypted_chunks)
                
                client.send(encrypted_chunks)
                
                response = client.recv(8192).decode()
                
                return response


    def request_peers(self):
        message = "REQUEST_PEERS"
        self.send_message(message)
        
        
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

if __name__ == "__main__":
    client = P2PClient(port=6001)  # پورت متفاوت برای کلاینت
    client.start()
