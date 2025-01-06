import socket
import rsa
import threading
import json
import pickle

class Server: 
    def __init__(self, host="127.0.0.1", port=5000, router1_public_key=None, router2_public_key=None, router3_public_key=None):
        self.host = host
        self.port = port
        self.clients = []
        self.routers = []
        self.router_keys= []
        self.router1_public_key = router1_public_key
        self.router2_public_key = router2_public_key
        self.router3_public_key = router3_public_key
        
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            server.listen(5)
            print(f"Server running on {self.host}:{self.port}")
            while True:
                conn, addr = server.accept()
                threading.Thread(target=self.handle_client, args=(conn,)).start()

        
    def handle_client(self, conn):
        try:
            message = conn.recv(8192)
            # print(f"This is message {message}")
            
            if b"-----BEGIN RSA PUBLIC KEY-----" in message:
                self.receive_public_keys(message)

            elif b"REQUEST_PEERS" in message:
                print(f"REQUEST_PEERS_MESSAGE: {message}")
                clients_list_str = "".join(self.clients)
                self.respose_client_request(clients_list_str)
                            
            elif b"REGISTER_CLIENT" in message:
                # دریافت کلید عمومی کلاینت
                self.register_client(conn, message)
                print("Client with request register")

        except Exception as e:
            print(f"Error in server: {e}")
        finally:
            conn.close()
       
    def receive_public_keys(self, message):
        router1_public_key_data, router2_public_key_data, router3_public_key_data = message.split(
        b"||")
        self.router1_public_key = rsa.PublicKey.load_pkcs1(router1_public_key_data)
        self.router2_public_key = rsa.PublicKey.load_pkcs1(router2_public_key_data)
        self.router3_public_key = rsa.PublicKey.load_pkcs1(router3_public_key_data)

        print("Received Public Keys:")
        print(f"Router 1: {self.router1_public_key}")
        print(f"Router 2: {self.router2_public_key}")
        print(f"Router 3: {self.router3_public_key}")
            
            
    def send_message(self, send_message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as router_conn:
            
            send_message = send_message.encode()
            for key in self.router_keys:
                if(key == ''):
                    continue
                send_message = rsa.encrypt(send_message, key)
            
            router_conn.connect(("127.0.0.1", 7003))  # روتر آخر
            router_conn.send(send_message)


    def register_client(self, conn, message):
        client_port = message.split()[1]
        client_address = conn.getpeername()
        client_ip = client_address[0]
            
        # ذخیره اطلاعات کلاینت به همراه کلید عمومی
        self.clients.append((f"{client_ip}:{client_port}"))
        print(f"Registered client: {client_ip}:{client_port} .")
            
        self.send_public_keys(conn)
          
    def send_public_keys(self, conn):
        router_keys = [self.router1_public_key, self.router2_public_key, self.router3_public_key]
        # router_keys = router_keys.encode()
        serialized_data = pickle.dumps(router_keys)
        conn.send(serialized_data)

    def respose_client_request(self, client_socket, message):
        client_socket.send(message.encode())
    
        
if __name__ == "__main__":
    server = Server()
    server.start()
