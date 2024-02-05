from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter

def encrypt_file(input_file, output_file):
    key = generate_and_save_key()
    iv = get_random_bytes(16)  # Initialization vector
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    with open(input_file, 'rb') as f:
        plaintext = f.read()
    padtext = pad(plaintext, AES.block_size)
    ctext = cipher.encrypt(padtext)
    with open(output_file, 'wb') as f:
        f.write(iv + ctext)

def decrypt_file(input_file, output_file):
    key = read_key_from_file()
    with open(input_file, 'rb') as f:
        iv = f.read(16)  # Read the first 16 bytes as the IV
        ciphertext = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded_plaintext = cipher.decrypt(ciphertext)
    plaintext = unpad(padded_plaintext, AES.block_size)
    with open(output_file, 'wb') as f:
        f.write(plaintext)

def generate_and_save_key():
    filename = 'encryption_key.bin'
    key = get_random_bytes(16)  # Generate a random 16-byte key
    with open(filename, 'wb') as f:
        f.write(key)
    return key

def read_key_from_file():
    filename = 'encryption_key.bin'
    with open(filename, 'rb') as f:
        key = f.read()
    return key

input_file = 'File1.zip'
encrypted_file = 'File1_encrypted.zip'
decrypted_file = 'decrypted_File1.zip'

# Encrypt file
encrypt_file(input_file, encrypted_file)
print("File encrypted.")

# Decrypt file
decrypt_file(encrypted_file, decrypted_file)
print("File decrypted.")
