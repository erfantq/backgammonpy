import socket
import signal
import threading
import time
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from router import Router
from board import Board
import random
import sys


class P2PClient:
    

    def __init__(self, host="127.0.0.1", port=6000, router_host="127.0.0.1", router_port=7001, keys=None):
        self.host = host
        self.port = port
        self.router_host = router_host
        self.router_port = router_port
        self.keys = keys
               
    def start(self):
        while True:
            
                
            choice = input("1. See client list\n2. connect to someone\n3. Exit\nEnter choice: ")
            
            if choice == "1":
                self.request_peers()
            elif choice == "2":
                client_two_port = input("Enter port of client : ")
                self.connect_to_client(self.host ,client_two_port)
            elif choice == "3":
                break
            
            
            else:
                print("Invalid option!")   
                                                         

    def encrypt_message(self, key, message):
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(message.encode())
        return base64.b64encode(nonce + ciphertext).decode()
      
    def decrypt_message(self, key, encrypted_message):
        data = base64.b64decode(encrypted_message.encode())
        nonce = data[:16]
        ciphertext = data[16:]
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt(ciphertext).decode()          

    def send_message(self, message):
        """send message to first router."""
        encrypted_message = message
        for key in reversed(self.keys):
            encrypted_message = self.encrypt_message(key, encrypted_message)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((self.router_host, self.router_port))
            client.sendall(encrypted_message.encode())
            response = client.recv(1024).decode()

        decrypted_response = response
        for key in self.keys:
            decrypted_response = self.decrypt_message(key, decrypted_response)
        
        print(f"Client received response: {decrypted_response}")        
        
        return decrypted_response    
            
    def request_peers(self):
        message = "REQUEST_PEERS"
        response = self.send_message(message)
    
    def connect_to_client(self,client_two_host, client_two_port):
        message = f"CONNECT TO CLIENT{self.port}:{client_two_port}"
        # response = self.send_message(message)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client.bind((self.host, self.port))
        client.connect((client_two_host, int(client_two_port)))
        # client.send("Starting game.".encode())
        client.send(f"CONNECTION_REQUEST{self.port}".encode())
        print(f"request for client {client_two_port}")
        response = client.recv(1024).decode()
        if response == "YES":
            print("Match accepted! Starting game.")        
            self.start_game(client)
            
        else:
            print("Match declined.")

    def receive_messages(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.host, int(self.port)))
            sock.listen(1)
            while True:
                conn, addr = sock.accept()
                try:
                    message = conn.recv(1024).decode()
                    # print(f"\n{message}")
                    
                    if message.startswith("CONNECTION_REQUEST"):
                        port = message.replace("CONNECTION_REQUEST", "")
                        while True:
                            print(f"want to connect you, do you agree?? ")
                            response = input(f"{port} want to connect you, do you agree?? (yes/no)")
                            if(response == "yes"):
                            
                                conn.sendall("YES".encode())
                                while True:
                                    message = conn.recv(1024).decode()
                                    print(message)
                                    if message.startswith("O, what do you want to do?") or message.startswith("You didn't roll that!") or message.startswith("YThat move is not allowed.  Please try again.") or message.startswith("the game is not over yet"):
                                        
                                        line = input()
                                        conn.sendall(line.encode())
                                        print("thanks")
                                        
                                    
                                    
                                
                            
                            elif(response == "no"):
                                conn.sendall("NO".encode())
                                break
                            else:
                                print("Wrong input")
                                
                                
                   
                        
                            
                            
                                
                
                                
                except:
                    print("Connection lost.")
                    break
        except Exception as e:
            print(f"Error in receive_messages: {e}")
        
       
    exitTerms = ("quit", "exit", "bye","q")
    def start_game(self, socket):
        b = Board()
        intro = open('readme.txt', 'r')
        
        # if(len(sys.argv[1]) > 1):
        #     if(sys.argv[1].lower() == "x"):
        #         SIDE = True
        #     else:
        #         SIDE = False			

        SIDE = True
        for line in intro:
            socket.send(line.encode())
            print(line)

        
        while (True):
            bo = str(b)
            socket.send(bo.encode())
            print(bo)
            
            # roll1 = random.randint(1,6)
            # roll2 = random.randint(1,6)
            roll1, roll2 = self.send_message("ASK_DICE").split(":")
    
            turnComplete = False
            roll1 = int(roll1)
            roll2 = int(roll2)
            total = roll1 + roll2
            if (roll1 == roll2):
                total *= 2
    
            if(SIDE):
                print("You rolled a " + str(roll1) + " and a " + str(roll2) + " giving you a total of " + str(total) + " moves.")
            else:
                socket.send(("You rolled a " + str(roll1) + " and a " + str(roll2) + " giving you a total of " + str(total) + " moves.").encode())
            if SIDE:
                print("X, what do you want to do?")
            else:
                socket.send("O, what do you want to do?".encode())
            line = ""
            while (not turnComplete and line not in self.exitTerms and int(total) > 0):
                if(SIDE):
                    line = input()
                else:
                    line = socket.recv(1024).decode()
                    
                if(line in self.exitTerms):
                    if SIDE:
                        print("you left the game. you lost!!")
                        socket.send("Your rival left the game, you win".encode())
                        break
                    else:
                        print("Your rival left the game, you win")
                        socket.send("you left the game. you lost!!".encode())
                        break
                elif line.capitalize() == "WON" :
                    if SIDE :
                        free = b.xFree
                    else:
                        free = b.oFree
                    result = self.ckeck_win(free)
                    
                    if result:
                        if SIDE:
                            print("The game is over, you win")
                            socket.send("The game is over, you lost".encode())
                            break
                        else:
                            print("he game is over, you lost")
                            socket.send("The game is over, you win".encode())
                            break
                        
                    else:
                        if SIDE:
                            print("the game is not over yet")
                        else:
                            socket.send("the game is not over yet".encode())
                        
                     
                    
                space,steps = self.parseInput(line)
                jailFreed = False
                jailCase = False
                if (SIDE and b.xJail > 0):
                    jailCase = True
                if (not SIDE and b.oJail > 0):
                    jailCase = True
                if (space == 100 and steps == 100):
                    total = 0
                    break
                if (space == 101 and steps == 101):
                    break
                if (steps != roll1 and steps != roll2 and steps != (roll1 + roll2) and steps != 100 and not jailCase):
                    if SIDE :
                        print("You didn't roll that!")
                    else: 
                        socket.send("You didn't roll that!".encode())
                    continue
                    # Must jump to beginning of loop
                space = space - 1
                if (steps == 0 and SIDE and b.xJail > 0):
                    tempSteps = space - 18
                    if (tempSteps != roll1 and tempSteps != roll2):
                        if SIDE :
                            print("You didn't roll that!")
                        else: 
                            socket.send("You didn't roll that!".encode())
                        continue
                    else:
                        jailFreed = True
                elif (steps == 0 and not SIDE and b.oJail > 0):
                    tempSteps = space + 1
                    if (tempSteps != roll1 and tempSteps != roll2):
                        if SIDE :
                            print("You didn't roll that!")
                        else: 
                            socket.send("You didn't roll that!".encode())
                        continue
                    else:
                        jailFreed = True
                if (space < 0 or space > 23 or steps < 0):
                    if SIDE :
                        print("That move is not allowed.  Please try again.")
                    else: 
                        socket.send("That move is not allowed.  Please try again.".encode())
                    continue
                    #Same deal here.
                move, response = b.makeMove(space, SIDE, steps)
                if SIDE :
                    print(response)
                else: 
                    socket.send(response.encode())
                if (move and jailFreed):
                    steps = tempSteps
                if move:
                    total = total - steps
                    if SIDE :
                        print(b)
                    else:
                        socket.send(b.encode())
                    if SIDE:
                        print("You have " + str(total) + " steps left.")
                    else:
                        socket.send(("You have " + str(total) + " steps left.").encode())
            SIDE = not SIDE

    #TODO: Include error management
    def parseInput(self, response):
        if response == "d" or response == "f" or response == "done" or response == "finish":
            return(100,100)
        if response in self.exitTerms:
            return (101, 101)
        # if type(response) == type("Sample string"):
        # 	return(101,101)
        loc = self.findSeparation(response)
        return(int(response[:loc]), int(response[loc+1:])) 

    def findSeparation(self, value):
        for i in range(len(value)):
            if (value[i] == ' ' or value[i] == ','):
                return i
        return 0   
    
    def ckeck_win(self, free):
        message = f"CHECK_WIN{free}"
        response = self.send_message(message)
        if response.startswith("YOU WIN"):
            return True
        else:
            return False
        
        


def handle_sigint(signal_number, frame):
    os.remove("first_run.lock")
    exit(0)

def start_router(port, next_port=None, key=None):
    router = Router(port=port, next_router=next_port, key=key)
    router.start()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)

    # keys = [get_random_bytes(16) for _ in range(3)]  # Three random keys for encryption layers
    keys = [b'\xbd_+\xa2\xf0\x7f\xd8\x0c\xce\xf3\xfe\x0f`8E\xd0', b'\x0b\x8be\xce\xe3\xfa9\xfb4o\xe4\x05\xb7\xda\x89\xc2', b'\xed\xfa\xcf\x16@\x909/\x80o\xd2\xadupET']
    
    
    status_file = "first_run.lock"
    if not os.path.exists(status_file):
        threading.Thread(target=start_router, args=(7001, ("127.0.0.1", 7002), keys[0]), daemon=True).start()
        threading.Thread(target=start_router, args=(7002, ("127.0.0.1", 7003), keys[1]), daemon=True).start()
        threading.Thread(target=start_router, args=(7003, ("127.0.0.1", 5000), keys[2]), daemon=True).start()
        with open(status_file, "w") as file:
            file.write("Executed")    
    
    port = input("Enter the port number:(6000-6010)")
    client = P2PClient(port=port, keys=keys)  # پورت متفاوت برای کلاینت
    client.send_message(f"REGISTER_CLIENT {client.port}")
    threading.Thread(target=client.start, args=()).start()
    threading.Thread(target=client.receive_messages, args=()).start() 
