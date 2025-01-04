import socket
import rsa
import threading

class Server: 
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.clients = []
        self.routers = []
        self.router_keys= []
        
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
           
           
            print(f"new client with {conn.host} {conn.port}")

            message = conn.recv(4096).decode()
            
            if "PUBLIC_KEY" in message:
                message = message.replace("PUBLIC_KEY", "")
                self.router_keys = message.split(",")
                
            elif "GET_PUBLIC_KEY" in message:
                send_message = self.router_keys
                self.send_message(send_message)
                
            elif message.startswith("REGISTER_CLIENT"):
                # دریافت کلید عمومی کلاینت
                self.register_client(conn, message)
            


           
        except Exception as e:
            print(f"Error in server: {e}")
        finally:
            conn.close()
            
            
            
    def send_message(self, send_message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as router_conn:
            
                send_message = send_message.encode()
                for key in self.router_keys:
                    send_message = rsa.encrypt(send_message, key)
                
                router_conn.connect(("127.0.0.1", 7003))  # روتر آخر
                router_conn.send(send_message)


    def register_client(self, client_socket, data):
            client_port = data.split()[1]
            client_address = client_socket.getpeername()
            client_ip = client_address[0]
            
            
            
            
            # # ذخیره اطلاعات کلاینت به همراه کلید عمومی
            self.clients.append((f"{client_ip}:{client_port}"))
            print(f"Registered client: {client_ip}:{client_port} .")
            response = "Client registered successfully."
            
            
            self.send_message(response)
            
          
if __name__ == "__main__":
    server = Server()
    server.start()
    
    