import socket
import rsa
import rsa.key

public_key , private_key = rsa.newkeys(512)

message = "hello world".encode()

layer1 = rsa.encrypt(message, public_key)

# print(layer1)

dec = rsa.decrypt(layer1, private_key)

dec = dec.decode()

print(dec)



message = "44,222,222,3,"

keys = message.split(",")
print (keys)

str = "111111"

str += "22"
print(str)