import rsa
import rsa.key
import pickle
from Crypto.Cipher import AES
import base64




# def encrypt_message(message):
#     message = message.encode()
#     array_message = [message]
#     chunks = split_strings_array_by_bytes(array_message, 53)
#     encrypted_chunks = []
#     for chunk in chunks:
#         encrypted_chunk = chunk
#         key = public_key3
#         encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
#         encrypted_chunks.append(encrypted_chunk)

#     print(f"before split1: {encrypted_chunks}\n\n\n\n")

#     encrypted_chunks = [b"".join(encrypted_chunks)]
#     print(f"before split2: {encrypted_chunks}\n\n\n")
    
#     encrypted_chunks = split_strings_array_by_bytes(encrypted_chunks, 53)

#     for chunk in chunks:
#         encrypted_chunk = chunk
#         key = public_key2
#         encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
#         encrypted_chunks.append(encrypted_chunk)

#     # print(f"after split: {encrypted_chunks}")

#     # encrypted_chunks = split_strings_array_by_bytes(encrypted_chunks, 53)
#     # for chunk in chunks:
#     #     encrypted_chunk = chunk
#     #     key = public_key1
#     #     encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
#     #     encrypted_chunks.append(encrypted_chunk)
    
#     return encrypted_chunks

# def decrypt(data):
#     encrypted_chunks = data
#     # print(encrypted_chunks)
#     # encrypted_chunks = pickle.loads(encrypted_chunks)
#     decrypted_chunks = []
#     # for encrypted_chunk in encrypted_chunks:
#     #     print("Decrypting...")
#     #     print(encrypted_chunk)
#     #     decrypted_chunk = rsa.decrypt(encrypted_chunk, private_key1)
#     #     decrypted_chunks.append(decrypted_chunk)
#     for encrypted_chunk in encrypted_chunks:
#         print("Decrypting...")
#         # print(encrypted_chunk)
#         decrypted_chunk = rsa.decrypt(encrypted_chunk, private_key2)
#         decrypted_chunks.append(decrypted_chunk)
    
#     print(f"Decrypted: {decrypted_chunks}")
#     for encrypted_chunk in decrypted_chunks:
#         print("Decrypting...")
#         decrypted_chunk = rsa.decrypt(encrypted_chunk, private_key3)
#         decrypted_chunks.append(decrypted_chunk)
        
#     return decrypted_chunks


# def split_strings_array_by_bytes(strings_array, byte_size):    
#     result = []
    
#     for input_string in strings_array:
#         byte_data = input_string
#         chunks = [byte_data[i:i + byte_size] for i in range(0, len(byte_data), byte_size)]
#         result.extend([chunk for chunk in chunks])
    
#     return result


public_key1 , private_key1 = rsa.newkeys(512)
public_key2 , private_key2 = rsa.newkeys(512)
public_key3 , private_key3 = rsa.newkeys(512)

# Utility functions for encryption and decryption
def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return base64.b64encode(nonce + ciphertext).decode()

def decrypt_message(key, encrypted_message):
    data = base64.b64decode(encrypted_message.encode())
    nonce = data[:16]
    ciphertext = data[16:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(ciphertext).decode()



message = "REQUEST_PEERS"
encrypted_chunks = encrypt_message(public_key1, message)
encrypted_chunks = encrypt_message(public_key2, encrypted_chunks)
encrypted_chunks = encrypt_message(public_key3, encrypted_chunks)
decrypted_chunks = decrypt_message(private_key3, encrypted_chunks)
decrypted_chunks = decrypt_message(private_key2, encrypted_chunks)
decrypted_chunks = decrypt_message(private_key1, encrypted_chunks)
print(decrypted_chunks)
