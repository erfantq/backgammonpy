import socket
import rsa
import pickle
import time
import threading
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytesc
import base64


class Router:
    
    def __init__(self, host="127.0.0.1", port=7001, next_router=None, pervious_router= None, is_first=False, is_last=False, str_keys="", received_keys=[], chenk_size=53):
        self.host = host
        self.port = port
        self.next_router = next_router
        self.is_first = is_first
        self.is_last = is_last
        self.str_keys = str_keys
        self.pervious_router = pervious_router
        self.public_key, self.private_key = None, None
        self.received_keys = received_keys
        self.chunk_size = chenk_size
        self.router1_handshake = 0
        self.router2_handshake = 0
        
        
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            server.listen(5)
            print(f"Router running on {self.host}:{self.port}")

            while True:
                conn, addr = server.accept()
                
                threading.Thread(target=self.handle_requests, args=(conn,addr)).start()
    
    def handle_requests(self, conn, addr):
        try:
            client_port = addr[1]
            # print(f"message received on port {self.port}")
            data = conn.recv(1024)
            print(f"Router {self.port} received keys from previous router: {self.received_keys}")
            # data = data.decode()
            # print(f"port{self.port}  {data}")
            if b"-----BEGIN RSA PUBLIC KEY-----" in data:
                self.received_keys = data.split(b"||")
                self.send_public_key()   
            elif b"REGISTER_CLIENT" in data:
                self.register_cilent(data, conn)
            else:
                if(self.port == 7001):
                    if(self.router1_handshake == 0):
                        self.public_key, self.private_key = pickle.loads(data)
                    elif(self.router1_handshake == 1):
                        pass
                    
                elif(self.port == 7002):
                    pass
                encrypted_chunks = data
                encrypted_chunks = pickle.loads(encrypted_chunks)
                decrypted_chunks = []
                for encrypted_chunk in encrypted_chunks:
                    print("Decrypting...")
                    print(encrypted_chunk)
                    decrypted_chunk = rsa.decrypt(encrypted_chunk, self.private_key)
                    decrypted_chunks.append(decrypted_chunk)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_conn:
                    encrypted_chunks = pickle.dumps(encrypted_chunks)
                    next_conn.connect(self.next_router)
                    next_conn.send(decrypted_chunks)
            # elif(b"[SERVER]" in data):
            #     pass
        except Exception as e:
            print(f"Error in router {self.port}: {e}")
        finally:
            conn.close() 
           
    def decrypt_message(key, encrypted_message):
        data = base64.b64decode(encrypted_message.encode())
        nonce = data[:16]
        ciphertext = data[16:]
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt(ciphertext).decode()
                
    def split_message(self, message, chunk_size):
        return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

    def send_public_key(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_conn:
            next_conn.connect(self.next_router)
            all_keys = b"||".join(self.received_keys + [self.public_key.save_pkcs1()])
            # print(f"all_keys: {all_keys}")
            next_conn.send(all_keys)
        print(f"Router {self.port} sent keys to next router.")

    def register_cilent(self, data, conn):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_conn:
            next_conn.connect(self.next_router)
            next_conn.send(data)
            
            response = next_conn.recv(8192)
            # print(f"response router is {response.decode()}")
            conn.send(response)

if __name__ == "__main__":
    router1 = Router(port=7001, next_router=("127.0.0.1", 7002), is_first= True)
    router2 = Router(port=7002, next_router=("127.0.0.1", 7003),pervious_router =("127.0.0.1", 7001))
    router3 = Router(port=7003, next_router=("127.0.0.1", 5000), pervious_router =("127.0.0.1", 7002), is_last=True)

    threading.Thread(target=router1.start).start()
    threading.Thread(target=router2.start).start()
    threading.Thread(target=router3.start).start()
    
    router1.send_public_key()
