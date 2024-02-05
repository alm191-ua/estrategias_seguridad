import zipfile
import os	
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad ##usamos pks7 que es el padding que se usa en AES donde si se necesitan 4 bytes se añaden 4 bytes con el valor 4
from Crypto.Random import get_random_bytes



def ZipFile():
    global Fle_Indx
    Fle_Indx = 1
    FileName='File'+str(Fle_Indx)
    zipf = zipfile.ZipFile(FileName+'.zip', 'w')
    zipf.write('CrearZipYCodificar.py')
    zipf.close()
    encrypt_file(FileName+'.zip')
    decrypt_file(FileName+'.zip')
    print("Archivo Comprimido")
    Fle_Indx+=1

def encrypt_file(input_file):
    key=read_key_from_file(input_file)
    cipher = AES.new(key, AES.MODE_CBC) ##Se podría usar AES.MODE_ECB pero es poco seguro debido a que el bloque se cifra de la misma manera. CBC añade algo de alatoriedad
    with open(input_file, 'rb') as f:
        plaintext = f.read()
    padtext = pad(plaintext, AES.block_size)
    ctext = cipher.encrypt(padtext)
    with open(input_file, 'wb') as f:
        f.write(ctext)


def decrypt_file(input_file):
    key=read_key_from_file(input_file)
    cipher = AES.new(key, AES.MODE_CBC)
    with open(input_file, 'rb') as f:
        ciphertext = f.read()
    padded_plaintext = cipher.decrypt(ciphertext)
    print(padded_plaintext)
    plaintext = unpad(padded_plaintext, AES.block_size)
    print(plaintext)
    with open(input_file, 'wb') as f:
        f.write(plaintext)


def generate_and_save_key(filename):
    filename2 = filename+".bin"
    key = get_random_bytes(16)  # Generate a random 16-byte key
    with open(filename2, 'wb') as f:
        f.write(key)
    return key


def read_key_from_file(filename):
    filename2 = filename+".bin"
    with open(filename2, 'rb') as f:
        key = f.read()
    return key


ZipFile()




