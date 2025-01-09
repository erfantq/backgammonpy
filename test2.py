import rsa

public_key1, private_key1 = rsa.newkeys(512)
public_key2, private_key2 = rsa.newkeys(512)
public_key3, private_key3 = rsa.newkeys(512)

def split_into_chunks(data, chunk_size):
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def encrypt_message(message):

    message_bytes = message.encode()  

    chunks = split_into_chunks(message_bytes, 53)   
    encrypted_chunks = [rsa.encrypt(chunk, public_key1) for chunk in chunks]

    encrypted_chunks = [
        rsa.encrypt(chunk, public_key2)
        for chunk in split_into_chunks(b"".join(encrypted_chunks), 53)
    ]

    encrypted_chunks = [
        rsa.encrypt(chunk, public_key3)
        for chunk in split_into_chunks(b"".join(encrypted_chunks), 53)
    ]

    return encrypted_chunks

def decrypt_message(encrypted_chunks):

    decrypted_chunks = [rsa.decrypt(chunk, private_key3) for chunk in encrypted_chunks]

    decrypted_chunks = [
        rsa.decrypt(chunk, private_key2)
        for chunk in split_into_chunks(b"".join(decrypted_chunks), 64)
    ]

    decrypted_chunks = [
        rsa.decrypt(chunk, private_key1)
        for chunk in split_into_chunks(b"".join(decrypted_chunks), 64)
    ]

    return b"".join(decrypted_chunks).decode()

message = "REQUEST_PEERS"
print("Origin:", message)

encrypted_chunks = encrypt_message(message)
print("Encryp:", encrypted_chunks)

decrypted_message = decrypt_message(encrypted_chunks)
print("Decrypt:", decrypted_message)
