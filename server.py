import socket
import threading
import rsa
import threading

lock = threading.Lock()

class CentralServer:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.clients = []
        # self.private_key, self.public_key = rsa.newkeys(512)
        self.public_key, self.private_key = rsa.newkeys(512)

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Server running on {self.host}:{self.port}")

        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            # دریافت پیام ثبت‌نام
            data = client_socket.recv(2048).decode()
            if data == "GET_PUBLIC_KEY":
                # فراخوانی متد ارسال کلید عمومی
                self.send_public_key(client_socket)
            elif data.startswith("REGISTER_CLIENT"):
                # دریافت کلید عمومی کلاینت
                client_public_key_data = client_socket.recv(2048)  # دریافت کلید عمومی
                client_public_key = rsa.PublicKey.load_pkcs1(client_public_key_data, "PEM")
                self.register_client(client_socket, data, client_public_key)
            elif data == "GET_PEERS":
                self.send_peers(client_socket)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()


    def send_public_key(self, client_socket):
        """ارسال کلید عمومی به کلاینت"""
        try:
            public_key_pem = self.public_key.save_pkcs1(format="PEM")  # تبدیل کلید به فرمت PEM
            print(f"Sending Public Key:\n{public_key_pem.decode()}")
            client_socket.send(public_key_pem)  # ارسال کلید عمومی به کلاینت
        except Exception as e:
            print(f"Error sending public key: {e}")
            
    # def register_client(self, client_socket, data, client_public_key):
    #     client_port = data.split()[1]
    #     # ذخیره اطلاعات کلاینت همراه با کلید عمومی
    #     self.clients.append((f"127.0.0.1:{client_port}", client_public_key))
    #     response = "Client registered successfully."
    #     # رمزنگاری پاسخ با کلید عمومی کلاینت
    #     encrypted_response = rsa.encrypt(response.encode(), client_public_key)
    #     client_socket.send(encrypted_response)
        
    def register_client(self, client_socket, data, client_public_key):
        client_port = data.split()[1]
        client_address = client_socket.getpeername()
        client_ip = client_address[0]
        # ذخیره اطلاعات کلاینت به همراه کلید عمومی
        self.clients.append((f"{client_ip}:{client_port}", client_public_key))
        print(f"Registered client: {client_ip}:{client_port} with public key.")
        response = "Client registered successfully."
        encrypted_response = rsa.encrypt(response.encode(), client_public_key)
        client_socket.send(encrypted_response)

    # def send_peers(self, client_socket):
    #     peers = "\n".join(self.clients)
    #     response = rsa.encrypt(peers.encode(), self.public_key)
    #     client_socket.send(response)
        
    # def send_peers(self, client_socket):
    #     # پیدا کردن کلید عمومی کلاینت درخواست‌دهنده
    #     client_address = client_socket.getpeername()
    #     client_ip, client_port = client_address
    #     client_entry = next((entry for entry in self.clients if entry[0] == f"{client_ip}:{client_port}"), None)

    #     if client_entry:
    #         client_public_key = client_entry[1]
    #         peers = "\n".join([entry[0] for entry in self.clients])  # فقط آدرس کلاینت‌ها
    #         encrypted_response = rsa.encrypt(peers.encode(), client_public_key)
    #         client_socket.send(encrypted_response)
    #     else:
    #         print("Client public key not found for encryption.")
    #         client_socket.send(b"Error: Public key not found.")


    def send_peers(self, client_socket):
        # پیدا کردن آدرس کلاینت درخواست‌دهنده
        client_address = client_socket.getpeername()
        client_ip, client_port = client_address

        # تطابق با کلاینت‌های ذخیره‌شده
        # client_entry = next((entry for entry in self.clients if entry[0] == f"{client_ip}:{client_port}"), None)
        client_entry = next((entry for entry in self.clients if entry[0].startswith(client_ip)), None)

        print(f'client entry: {client_entry}')
        
        if client_entry:
            client_public_key = client_entry[1]
            peers = "\n".join([entry[0] for entry in self.clients])  # فقط آدرس کلاینت‌ها
            print(f"Peers sent to {client_ip}:{client_port}: {peers}")
            encrypted_response = rsa.encrypt(peers.encode(), client_public_key)
            client_socket.send(encrypted_response)
        else:
            print(f"Public key not found for client {client_ip}:{client_port}")
            client_socket.send(b"Error: Public key not found.")


if __name__ == "__main__":
    server = CentralServer()
    threading.Thread(target=server.start).start()
