import zipfile
import os	
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad ##usamos pks7 que es el padding que se usa en AES donde si se necesitan 4 bytes se añaden 4 bytes con el valor 4
from Crypto.Random import get_random_bytes
import logging
from uuid import uuid4 as unique_id



FILE_DIR='files/'
NAME_FILES='File'
FILES_COMPRESSION_FORMAT='.zip'
KEYS_FORMAT='.bin'
logging.basicConfig(filename='logfile.log', level=logging.INFO)  # Guardar registros en un archivo

def Create_Dirs(filename):
    directory = FILE_DIR+filename+'/'
    if(not os.path.exists(directory)):
        os.mkdir(directory)
        logging.info('Directory created')
    return directory

def writeText(File,text):
    with open(File, 'wb') as f:
        f.write(text)
    

def ZipFile():
    doc_Id = str(unique_id())
    FileName=NAME_FILES+str(doc_Id)
    directory = Create_Dirs(FileName)
    zip_path = os.path.join(directory, FileName + FILES_COMPRESSION_FORMAT)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write('CrearZipYCodificar.py')
    encrypt_file(FileName,directory)
    decrypt_file(FileName,directory)
    logging.info('Directory created')


def encrypt_file(input_file,directory):
    key=generate_and_save_key(input_file,directory)
    iv = get_random_bytes(16) ##IMOORTANTE ESTO PORQUE SI NO NO FUNCIONA CBC
    cipher = AES.new(key, AES.MODE_CBC, iv=iv) ##Se podría usar AES.MODE_ECB pero es poco seguro debido a que el bloque se cifra de la misma manera. CBC añade algo de alatoriedad
    with open(directory+input_file+FILES_COMPRESSION_FORMAT, 'rb') as f:
        plaintext = f.read()
    padtext = pad(plaintext, AES.block_size)
    ctext = cipher.encrypt(padtext)
    writeText(directory+input_file+FILES_COMPRESSION_FORMAT,iv + ctext)


def decrypt_file(input_file,directory):
    key=read_key_from_file(input_file,directory)
    with open(directory+input_file+FILES_COMPRESSION_FORMAT, 'rb') as f:
        iv = f.read(16)  # Read the first 16 bytes as the IV
        ciphertext = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded_plaintext = cipher.decrypt(ciphertext)
   
    plaintext = unpad(padded_plaintext, AES.block_size)
    writeText(directory+input_file+FILES_COMPRESSION_FORMAT,plaintext)



def generate_and_save_key(input_file,directory):
    key = get_random_bytes(16)  # Generate a random 16-byte key
    writeText(directory+input_file+KEYS_FORMAT,key)
    return key


def read_key_from_file(input_file,directory):
    with open(directory+input_file+KEYS_FORMAT, 'rb') as f:
        key = f.read()
    return key


ZipFile()




