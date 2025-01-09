import socket
import rsa
import threading
import json
import pickle

class Server: 
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.clients = []        
        
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
            message = conn.recv(1024).decode()
            print(f"This is message {message}")
            
            if "REGISTER_CLIENT" in message:
                self.register_client(conn, message)
            elif "REQUEST_PEERS" in message:
                message = ""
                for item in self.clients:
                    message += item
            elif message.startswith("CONNECT TO CLIENT"):
                client_port, client_two_port = message.replace("CONNECT TO CLIENT", "").split(":")
                
                print(f"client_port is {client_port}")
                # print(client_port)
                message = self.connect_two_client(client_two_port, client_port)
            


            conn.sendall(message.encode())
            
            
            # if b"-----BEGIN RSA PUBLIC KEY-----" in message:
            #     self.receive_public_keys(message)

            # elif b"REQUEST_PEERS" in message:
            #     print(f"REQUEST_PEERS_MESSAGE: {message}")
            #     clients_list_str = "".join(self.clients)
            #     self.respose_client_request(clients_list_str)
                            
            
                
            # elif message.startswith("CONNECT TO CLIENT"):
            #     client_two_port = message.replace("CONNECT TO CLIENT", "")
                

        except Exception as e:
            print(f"Error in server: {e}")
        finally:
            conn.close()

    def register_client(self, conn, message):
        client_port = message.split()[1]
        client_address = conn.getpeername()
        client_ip = client_address[0]
            
        self.clients.append((f"{client_ip}:{client_port}"))
        print(f"Registered client: {client_ip}:{client_port} .")
            
            
    def connect_two_client(self, client_two_port, client_port):
        if client_two_port in self.clients:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.host, client_two_port))
                client.sendall(f"CONNECTION_REQUEST{client_port}".encode())
                response = client.recv(1024).decode()

            # self.clients[client_two_port].sendall(f"CONNECTION_REQUEST{client_port}".encode())
            # response = self.clients[client_two_port].recv(1024).decode()
            return response
        
        
if __name__ == "__main__":
    server = Server()
    server.start()
