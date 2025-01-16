--- SERVER ---
Server is runnig on port 5000
It waits for an request from client
When it takes a request it processes the request and then sends a response to the client with routers
--- ROUTER --- 
Each router takes its key from client 
If a message is from client it decryptes it once and sends it to the next router
Else if a message is from the server then it encrypts it in each router with its key and sends it to previous router
--- CLIENT --- 
When the client wants to send message to another client the message will be encrypted 3 times and will be sent to the first router
When a client wants to connect to another client he enters the port number of the client that he wants to connect then if the second
  client accepts the match then they will play the game with P2P connection and the dice and turn is managed by the server.
Clients use AES for encrypte and decrypt.

