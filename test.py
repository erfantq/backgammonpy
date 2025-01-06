def split_string_by_bytes(input_string, byte_size):
    # تبدیل رشته به بایت
    byte_data = input_string.encode('utf-8')
    # تقسیم بایت‌ها به قسمت‌های مشخص
    chunks = [byte_data[i:i + byte_size] for i in range(0, len(byte_data), byte_size)]
    # تبدیل هر بخش به رشته (در صورت نیاز)
    string_chunks = [chunk.decode('utf-8', errors='ignore') for chunk in chunks]
    return string_chunks

# مثال
input_string = "REQUEST_PEERS"
byte_size = 53
result = split_string_by_bytes(input_string, byte_size)

for i, chunk in enumerate(result):
    print(f"قسمت {i+1}: {chunk}")
    print(len(chunk.encode('utf-8')))