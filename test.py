import rsa
import rsa.key
import pickle

public_key1 , private_key1 = rsa.newkeys(512)
public_key2 , private_key2 = rsa.newkeys(512)
public_key3 , private_key3 = rsa.newkeys(512)

def encrypt_message(message):
    message = message.encode()
    array_message = [message]
    chunks = split_strings_array_by_bytes(array_message, 53)
    encrypted_chunks = []
    for chunk in chunks:
        encrypted_chunk = chunk
        key = public_key3
        encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
        encrypted_chunks.append(encrypted_chunk)

    encrypted_chunks = split_strings_array_by_bytes(encrypted_chunks, 53)
    for chunk in chunks:
        encrypted_chunk = chunk
        key = public_key2
        encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
        encrypted_chunks.append(encrypted_chunk)

    encrypted_chunks = split_strings_array_by_bytes(encrypted_chunks, 53)
    for chunk in chunks:
        encrypted_chunk = chunk
        key = public_key1
        encrypted_chunk = rsa.encrypt(encrypted_chunk, key)
        encrypted_chunks.append(encrypted_chunk)
    
    return encrypted_chunks

def decrypt(data):
    encrypted_chunks = data
    # encrypted_chunks = pickle.loads(encrypted_chunks)
    decrypted_chunks = []
    for encrypted_chunk in encrypted_chunks:
        print("Decrypting...")
        print(encrypted_chunk)
        decrypted_chunk = rsa.decrypt(encrypted_chunk, private_key1)
        decrypted_chunks.append(decrypted_chunk)
    for encrypted_chunk in decrypted_chunks:
        print("Decrypting...")
        print(encrypted_chunk)
        decrypted_chunk = rsa.decrypt(encrypted_chunk, private_key2)
        decrypted_chunks.append(decrypted_chunk)
    for encrypted_chunk in decrypted_chunks:
        print("Decrypting...")
        print(encrypted_chunk)
        decrypted_chunk = rsa.decrypt(encrypted_chunk, private_key3)
        decrypted_chunks.append(decrypted_chunk)
        
    return decrypted_chunks


def split_strings_array_by_bytes(strings_array, byte_size):    
    result = []
    
    for input_string in strings_array:
        byte_data = input_string
        chunks = [byte_data[i:i + byte_size] for i in range(0, len(byte_data), byte_size)]
        result.extend([chunk for chunk in chunks])
    
    return result



message = "REQUEST_PEERS"
encrypted_chunks = encrypt_message(message)
decrypted_chunks = decrypt(encrypted_chunks)
print(decrypted_chunks)
