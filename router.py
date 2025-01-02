import socket
import rsa
import threading

class Router:
    def __init__(self, host="127.0.0.1", port=7001, next_router=None):
        self.host = host
        self.port = port
        self.next_router = next_router
        self.private_key, self.public_key = rsa.newkeys(512)

    def start(self):
        router_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        router_socket.bind((self.host, self.port))
        router_socket.listen(5)
        print(f"Router running on {self.host}:{self.port}")

        while True:
            client_socket, addr = router_socket.accept()
            encrypted_message = client_socket.recv(2048)
            decrypted_message = rsa.decrypt(encrypted_message, self.private_key).decode()
            print(f"Router {self.port} decrypted message: {decrypted_message}")

            if self.next_router:
                next_router_ip, next_router_port = self.next_router.split(":")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_router_socket:
                    encrypted_forward_message = rsa.encrypt(decrypted_message.encode(), self.public_key)
                    next_router_socket.connect((next_router_ip, int(next_router_port)))
                    next_router_socket.send(encrypted_forward_message)
            else:
                print(f"Message delivered to final destination: {decrypted_message}")
                response = rsa.encrypt("Message delivered successfully.".encode(), self.public_key)
                client_socket.send(response)
            client_socket.close()

    def set_next_router(self, next_router):
        self.next_router = next_router

if __name__ == "__main__":
    router1 = Router(port=7001)
    router2 = Router(port=7002)
    router3 = Router(port=7003)
    router1.set_next_router("127.0.0.1:7002")
    router2.set_next_router("127.0.0.1:7003")

    threading.Thread(target=router1.start).start()
    threading.Thread(target=router2.start).start()
    threading.Thread(target=router3.start).start()
