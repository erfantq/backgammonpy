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
           
           

            message = conn.recv(4096).decode()
            
            # print(f"message is {message}")
            
            if "PUBLIC_KEY" in message:
                message = message.replace("PUBLIC_KEY", "")
                self.router_keys = message.split("#")
                print(f" client with request router")

                # print(self.router_keys)
                
            elif "GET_PUBLIC_KEY" in message:
                send_message = self.router_keys
                self.send_message(send_message)
                
            elif message.startswith("REGISTER_CLIENT"):
                # دریافت کلید عمومی کلاینت
                self.register_client(conn, message)
                print(f" client with request register")

            


           
        except Exception as e:
            print(f"Error in server: {e}")
        finally:
            conn.close()
            
            
            
    def send_message(self, send_message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as router_conn:
            
            send_message = send_message.encode()
            for key in self.router_keys:
                if(key == ''):
                    continue
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
            
        self.send_public_keys(client_port)
            
          
    def send_public_keys(self, client_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as router_conn:
            print(f"client_port {client_port}")
            router_keys = "" +client_port + ","
            router_keys += "CLIENT_RCV_KEYS"
            router_keys += "#".join(self.router_keys)
                # print(router_keys)
            router_keys = router_keys.encode()
            router_conn.connect(("127.0.0.1", 7003))  # روتر آخر
            router_conn.send(router_keys)
            print(router_conn)
            # client_socket.raddr=(("127.0.0.1", 7003))
            # print(client_socket)
            # client_socket.send(router_keys)
            

        
        
        
if __name__ == "__main__":
    server = Server()
    server.start()
    
    