import socket
import rsa
import threading

class Router:
    
    def __init__(self, host="127.0.0.1", port=7001, next_router=None, pervious_router= None, is_first=False, is_last=False, str_keys=""):
        self.host = host
        self.port = port
        self.next_router = next_router
        self.is_first = is_first
        self.is_last = is_last
        self.str_keys = str_keys
        self.pervious_router = pervious_router
        self.public_key, self.private_key = rsa.newkeys(512)
        

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            if(self.is_first):
                server.listen(5)
            else:
                server.listen(1)
            print(f"Router running on {self.host}:{self.port}")

            while True:
                conn, addr = server.accept()
                
                threading.Thread(target=self.handle_client, args=(conn,addr)).start()

    def handle_client(self, conn, addr):
        
        try:
            
            client_port = addr[1]
            # print(f"message received on port {self.port}")
            data = conn.recv(4096)
            data = data.decode()
            # print(f"port{self.port}  {data}")
            if "PUBLIC_KEY" in data:
                self.str_keys = data
                self.send_public_key()
                
            elif "REGISTER_CLIENT" in data:
                self.register_cilent(data)
                
                
            elif "CLIENT_RCV_KEYS" in data:
                self.send_keys_to_client(data)
                
        except Exception as e:
            print(f"Error in router {self.port}: {e}")
        finally:
            conn.close()

    def send_public_key(self):
        if self.is_first:
            self.str_keys = "PUBLIC_KEY"
            
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_conn:
            next_conn.connect(self.next_router)
            self.str_keys += str(self.public_key) + "#"
            # print(self.str_keys)
            # print(self.next_router)
            next_conn.send(self.str_keys.encode())


    def register_cilent(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_conn:
            next_conn.connect(self.next_router)
            next_conn.send(data.encode())

    def send_keys_to_client(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_conn:
            if self.pervious_router:
                next_conn.connect(self.pervious_router)
                next_conn.send(data.encode())
            else:
                port = data.split(",")[0]
                
                print(port)
                next_conn.connect(("127.0.0.1", int(port)))
                next_conn.send(data.encode())
                
        
        

if __name__ == "__main__":
    router1 = Router(port=7001, next_router=("127.0.0.1", 7002), is_first= True)
    router2 = Router(port=7002, next_router=("127.0.0.1", 7003),pervious_router =("127.0.0.1", 7001))
    router3 = Router(port=7003, next_router=("127.0.0.1", 5000), pervious_router =("127.0.0.1", 7002), is_last=True)

    threading.Thread(target=router1.start).start()
    threading.Thread(target=router2.start).start()
    threading.Thread(target=router3.start).start()
    router1.send_public_key()