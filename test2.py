import rsa

message = "test"

public, private = rsa.newkeys(512)

encrypted = rsa.encrypt(message.encode(), public)

decrypted = rsa.decrypt(encrypted, private)

print(decrypted)