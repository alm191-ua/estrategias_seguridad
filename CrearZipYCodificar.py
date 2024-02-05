import zipfile
import os	
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad ##usamos pks7 que es el padding que se usa en AES donde si se necesitan 4 bytes se añaden 4 bytes con el valor 4
from Crypto.Random import get_random_bytes



def ZipFile():
    global Fle_Indx
    Fle_Indx = 1
    FileName='File'+str(Fle_Indx)
    directory = 'files/'+FileName+'/'
    if(not os.path.exists(directory)):
        os.mkdir(directory)
    zip_path = os.path.join(directory, FileName + '.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write('CrearZipYCodificar.py')
    encrypt_file(FileName,directory)
    decrypt_file(FileName,directory)
    print("Archivo Comprimido")
    Fle_Indx+=1




def encrypt_file(input_file,directory):
    key=generate_and_save_key(input_file,directory)
    iv = get_random_bytes(16) 
    cipher = AES.new(key, AES.MODE_CBC, iv=iv) ##Se podría usar AES.MODE_ECB pero es poco seguro debido a que el bloque se cifra de la misma manera. CBC añade algo de alatoriedad
    with open(directory+input_file+'.zip', 'rb') as f:
        plaintext = f.read()
    padtext = pad(plaintext, AES.block_size)
    ctext = cipher.encrypt(padtext)
    with open(directory+input_file+'.zip', 'wb') as f:
        f.write(iv + ctext)




def decrypt_file(input_file,directory):
    key=read_key_from_file(input_file,directory)
    with open(directory+input_file+'.zip', 'rb') as f:
        iv = f.read(16)  # Read the first 16 bytes as the IV
        ciphertext = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded_plaintext = cipher.decrypt(ciphertext)
   
    plaintext = unpad(padded_plaintext, AES.block_size)

    with open(directory+input_file+'.zip', 'wb') as f:
        
        f.write(plaintext)


def generate_and_save_key(input_file,directory):
    key = get_random_bytes(16)  # Generate a random 16-byte key
    with open(directory+input_file+'.bin', 'wb') as f:
        f.write(key)
    return key


def read_key_from_file(input_file,directory):
    with open(directory+input_file+'.bin', 'rb') as f:
        key = f.read()
    return key


ZipFile()




