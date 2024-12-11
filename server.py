# server.py
import socket
import threading
import random

clients = {}
lock = threading.Lock()

def handle_client(client_socket, address):
    global clients
    try:
        client_socket.send("Welcome to Backgammon! Enter your username: ".encode())
        username = client_socket.recv(1024).decode().strip()
        with lock:
            clients[username] = client_socket
        
        while True:
            client_socket.send("Commands: \n1. List players\n2. Select player\n3. Exit\n".encode())
            command = client_socket.recv(1024).decode().strip()
            
            if command == '1':
                with lock:
                    players_list = "\n".join(clients.keys())
                client_socket.send(f"Available players:\n{players_list}".encode())
            elif command == '2':
                client_socket.send("Enter the username of the player you want to play with: ".encode())
                opponent = client_socket.recv(1024).decode().strip()
                if opponent in clients:
                    client_socket.send("Requesting match...".encode())
                    clients[opponent].send(f"{username} wants to play with you. Accept? (yes/no): ".encode())
                    response = clients[opponent].recv(1024).decode().strip()
                    if response.lower() == 'yes':
                        client_socket.send("Match accepted! Starting game.".encode())
                        clients[opponent].send("Match accepted! Starting game.".encode())
                        peer_to_peer_game(username, opponent)
                    else:
                        client_socket.send("Match declined.".encode())
                else:
                    client_socket.send("Player not found.".encode())
            elif command == '3':
                client_socket.send("Goodbye!".encode())
                break
    except ConnectionError:
        pass
    finally:
        with lock:
            if username in clients:
                del clients[username]
        client_socket.close()

def peer_to_peer_game(player1, player2):
    p1_socket = clients[player1]
    p2_socket = clients[player2]
    
    threading.Thread(target=peer_to_peer_chat, args=(p1_socket, p2_socket)).start()
    threading.Thread(target=peer_to_peer_chat, args=(p2_socket, p1_socket)).start()

def peer_to_peer_chat(sender_socket, receiver_socket):
    while True:
        try:
            message = sender_socket.recv(1024).decode()
            receiver_socket.send(message.encode())
        except:
            break

def dice_roll():
    return random.randint(1, 6), random.randint(1, 6)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    print("Server started. Waiting for connections...")
    
    while True:
        client_socket, address = server.accept()
        print(f"Connection from {address}")
        threading.Thread(target=handle_client, args=(client_socket, address)).start()

if __name__ == "__main__":
    main()
