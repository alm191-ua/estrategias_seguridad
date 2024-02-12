import zipfile
import os	
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad ##usamos pks7 que es el padding que se usa en AES donde si se necesitan 4 bytes se añaden 4 bytes con el valor 4
from Crypto.Random import get_random_bytes
import logging
from uuid import uuid4 as unique_id
import argparse
import random
import re
import json


TMP_DIR = 'tmp'
# directorio de los ficheros
AES_MODE = AES.MODE_EAX

FILE_DIR='files/'
NAME_FILES='File'
FILES_COMPRESSION_FORMAT='.zip'
KEYS_FORMAT='.bin'
UNSAFE_MODE = False
UNSAFE_PASSWORDS = ['123456',
                    'admin',
                    'password',
                    '12345678',
                    '1234',
                    '123',
                    'Aa123456',
                    '111111',
                    'Password',
                    'qwerty',]
KEY_SIZE = 16
IV_SIZE = 16
DIRECTORIO=os.getcwd()


def buscar_directorio(nombre_directorio, ruta_inicio='/'):
    # Recorre todos los directorios y archivos en la ruta_inicio
    for root, dirs, files in os.walk(ruta_inicio):
        # Busca el directorio deseado en la lista de directorios
        if nombre_directorio in dirs:
            # Si lo encuentra, devuelve la ruta completa del directorio
            return os.path.join(root, nombre_directorio)
    # Si no lo encuentra, devuelve None
    return None

##logging.basicConfig(filename='logfile.log', level=logging.INFO, format='%(asctime)s - %(message)s')  # Formato con hora

def Create_Dirs(filename):
    nombre_directorio_buscado = "estrategias_seguridad"
    resultado = buscar_directorio(nombre_directorio_buscado)
    if resultado:
        DIRECTORIO=resultado
    else:
        DIRECTORIO += '/estrategias_seguridad'
    # Primero, asegúrate de que el directorio principal 'files/' exista
    DIRECTORIO += '/files/'
    if not os.path.exists(DIRECTORIO):
        os.makedirs(DIRECTORIO)  # Usa os.makedirs() que crea directorios intermedios necesarios
        logging.info('Main directory created')

    # Luego, procede a crear el subdirectorio para el archivo específico
    directory = os.path.join(DIRECTORIO, filename)  # Es más seguro usar os.path.join()
    if not os.path.exists(directory):
        os.makedirs(directory)  # Cambiado a os.makedirs() para coherencia y para evitar futuros errores
        logging.info('Subdirectory created for: ' + filename)
    return directory


def writeText(File,text):
    with open(File, 'wb') as f:
        f.write(text)
    

def ZipFile(files):
    doc_Id = str(unique_id())
    FileName = NAME_FILES + str(doc_Id)
    directory = Create_Dirs(FileName)
    zip_path = os.path.join(directory, FileName + FILES_COMPRESSION_FORMAT)

    # Crea un archivo zip y añade todos los archivos de la lista
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:  # Itera sobre la lista de archivos
            if os.path.isfile(file):  # Verifica si el path es de un archivo
                zipf.write(file, os.path.basename(file))  # Añade el archivo al zip
    encrypt_file(FileName, directory)
    logging.info('Files compressed')

def UnZipFile(file):
    inicio=buscar_directorio('estrategias_seguridad')
    directory = buscar_directorio(file, inicio)

    decrypt_file(file,directory)
    zip_path = os.path.join(directory, file + FILES_COMPRESSION_FORMAT)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
      zip_ref.extractall(directory)

def CreateJSON(doc_id, title, description):
    # guardar el fichero .json
    logging.debug(f'Saving json file for document {doc_id}')
    files_names = os.listdir(TMP_DIR)
    doc_data = {
        'id': doc_id,
        'title': title,
        'description': description,
        'files': files_names
    }
    with open(f'{TMP_DIR}/{doc_id}.json', 'w') as file:
        json.dump(doc_data, file)


def encrypt_file(input_file,directory):
    key=generate_and_save_key(input_file,directory)
    iv = get_random_bytes(IV_SIZE) ##IMPORTANTE ESTO PORQUE SI NO NO FUNCIONA CBC
    cipher = AES.new(key, AES.MODE_CBC, iv=iv) ##Se podría usar AES.MODE_ECB pero es poco seguro debido a que el bloque se cifra de la misma manera. CBC añade algo de alatoriedad
    path= os.path.join(directory, input_file + FILES_COMPRESSION_FORMAT)
    with open(path, 'rb') as f:
        plaintext = f.read()
    padtext = pad(plaintext, AES.block_size)
    ctext = cipher.encrypt(padtext)
    writeText(path,iv + ctext)


def decrypt_file(input_file,directory):
    key=read_key_from_file(input_file,directory)
    path= os.path.join(directory, input_file + FILES_COMPRESSION_FORMAT)
    with open(path, 'rb') as f:
        iv = f.read(IV_SIZE)  # Read the first 16 bytes as the IV
        ciphertext = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded_plaintext = cipher.decrypt(ciphertext)
   
    plaintext = unpad(padded_plaintext, AES.block_size)
    writeText(path,plaintext)


def decrypt_file_unsafe(input_file,directory):
    for password in UNSAFE_PASSWORDS:
        key=bytes(password.ljust(KEY_SIZE, '0'), 'utf-8')
        with open(directory+input_file+FILES_COMPRESSION_FORMAT, 'rb') as f:
            iv = f.read(IV_SIZE)  # Read the first 16 bytes as the IV
            ciphertext = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        padded_plaintext = cipher.decrypt(ciphertext)
    
        plaintext = unpad(padded_plaintext, AES.block_size)
        writeText(directory+input_file+FILES_COMPRESSION_FORMAT,plaintext)


def generate_and_save_key(input_file,directory):
    if(UNSAFE_MODE):
        key = bytes(random.choice(UNSAFE_PASSWORDS).ljust(KEY_SIZE, '0'), 'utf-8')
    else:
        key = get_random_bytes(KEY_SIZE)  # Generate a random 16-byte key
    writeText(directory+'/'+input_file+KEYS_FORMAT,key)
    return key


def read_key_from_file(input_file,directory):
    path= os.path.join(directory, input_file + KEYS_FORMAT)
    with open(path, 'rb') as f:
        key = f.read()
    return key

parser = argparse.ArgumentParser(description='Save documents in a secure way')
parser.add_argument('-u', '--unsafe', help='Use unsafe mode', action='store_true')
parser.add_argument('-d', '--decrypt', help='Start to decrypt a file (must be followed by File (-f))', action='store_true')
parser.add_argument('-f', '--file', help='Indicates the file [put the directory eg: "python3 CrearZipYCodificar.py -d -f files/File2e47b658-6cdc-46ae-aa15-b3344bb3cbfd/]"')
if(parser.parse_args().unsafe):
    UNSAFE_MODE = True
    logging.info('Unsafe mode activated')
if(parser.parse_args().decrypt and parser.parse_args().file): ##Si se quiere desencriptar un archivo se comprueba que se haya indicado el archivo y se coge el nombre de la carpeta. Si no se llamará a ZipFile
    match = re.search(r'files/(.*?)/', parser.parse_args().file)
    file_name = match.group(1)
    logging.info('Decrypt mode activated')
    UnZipFile(file_name)





