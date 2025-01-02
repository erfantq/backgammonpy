import socket
import rsa

class P2PClient:
    def __init__(self, host="127.0.0.1", port=6000, server_host="127.0.0.1", server_port=5000):
        self.host = host
        self.port = port
        self.server_host = server_host
        self.server_port = server_port
        self.public_key, self.private_key = rsa.newkeys(512)

    def start(self):
        self.fetch_server_public_key()  # دریافت کلید عمومی سرور
        self.register_with_server()
        
        while True:
            choice = input("1. See client list\n2. Exit\nEnter choice: ")
            if choice == "1":
                self.request_peers()
            elif choice == "2":
                break
            else:
                print("Invalid option!")

    def fetch_server_public_key(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((self.server_host, self.server_port))
            client.send("GET_PUBLIC_KEY".encode())
            server_key_data = client.recv(2048)
            print(f"Received data:\n{server_key_data.decode()}")
            if b"-----BEGIN RSA PUBLIC KEY-----" in server_key_data:
                try:
                    self.server_public_key = rsa.PublicKey.load_pkcs1(server_key_data, "PEM")
                except ValueError:
                    print("Invalid public key format received from server.")
                    raise
            else:
                print("Invalid data received: Not a PEM formatted public key.")
                raise ValueError("Public key not in PEM format.")

    def register_with_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((self.server_host, self.server_port))
            # ارسال پیام ثبت‌نام
            registration_message = f"REGISTER_CLIENT {self.port}"
            client.send(registration_message.encode())
            
            # ارسال کلید عمومی
            public_key_data = self.public_key.save_pkcs1(format="PEM")
            client.send(public_key_data)

            # دریافت پاسخ رمزنگاری‌شده
            encrypted_response = client.recv(2048)
            response = rsa.decrypt(encrypted_response, self.private_key).decode()
            print(f"Server Response: {response}")


    # def request_peers(self):
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    #         client.connect((self.server_host, self.server_port))
    #         encrypted_message = rsa.encrypt("GET_PEERS".encode(), self.server_public_key)
    #         client.send(encrypted_message)
    #         response = rsa.decrypt(client.recv(2048), self.private_key).decode()
    #         peers = response.split("\n")
    #         print("Available Clients:")
    #         for idx, peer in enumerate(peers):
    #             print(f"{idx+1}. {peer}")
            
    #         choice = int(input("Enter the number of the client to connect to: ")) - 1
    #         if choice >= 0 and choice < len(peers):
    #             target_ip, target_port = peers[choice].split(":")
    #             target_port = int(target_port)
    #             self.send_connection_request(target_ip, target_port)

    def request_peers(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((self.server_host, self.server_port))
            client.send("GET_PEERS".encode())
            encrypted_response = client.recv(2048)
            print(f"Encrypted response from server: {encrypted_response}")
            try:
                response = rsa.decrypt(encrypted_response, self.private_key).decode()
                print("Available Clients:")
                print(response)
            except rsa.DecryptionError:
                print("Failed to decrypt the response from the server.")
                raise


    def send_connection_request(self, target_ip, target_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((target_ip, target_port))
            message = f"CONNECTION_REQUEST {self.host}:{self.port}"
            encrypted_message = rsa.encrypt(message.encode(), self.server_public_key)
            client.send(encrypted_message)
            response = rsa.decrypt(client.recv(2048), self.private_key).decode()
            print(f"Response from target client: {response}")

if __name__ == "__main__":
    client = P2PClient(port=6001)  # پورت متفاوت برای کلاینت
    client.start()
