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
AES_MODE = AES.MODE_CBC

FILE_DIR='files/'
NAME_FILES='File'
FILES_COMPRESSION_FORMAT='.zip'
CYPHER_FORMAT='.enc'
KEYS_FORMAT='.bin' # TODO: Cambiar a .key
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
BLOCK_SIZE = 1024 # in bytes 
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


def writeText(File, text):
    with open(File, 'wb') as f:
        f.write(text)
    

def ZipFile(files, title, description):
    doc_Id = str(unique_id())
    FileName = NAME_FILES + str(doc_Id)
    directory = Create_Dirs(FileName)
    zip_path = os.path.join(directory, FileName + FILES_COMPRESSION_FORMAT)
    Json_File=CreateJSON(directory,doc_Id, title, description, files)
    files.append(Json_File)

    #Primero, crea el archivo JSON con los metadatos
    files_names = [os.path.basename(file) for file in files]
    doc_data = {
        'id': doc_Id,
        'title': title,
        'description': description,
        'files': files_names
    }
    json_path = os.path.join(directory, f"{FileName}.json")
    with open(json_path, 'w') as json_file:
        json.dump(doc_data, json_file)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:  # Itera sobre la lista de archivos
            if os.path.isfile(file):  # Verifica si el path es de un archivo
                zipf.write(file, os.path.basename(file))  # Añade el archivo al zip
    os.remove(Json_File)
    
    encrypt_file(FileName, directory)
    logging.info('Files compressed')
    os.remove(json_path)

def UnZipFile(file):
    inicio=buscar_directorio('estrategias_seguridad')
    directory = buscar_directorio(file, inicio)

    decrypt_file(file,directory)
    zip_path = os.path.join(directory, file + FILES_COMPRESSION_FORMAT)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
      zip_ref.extractall(directory)

def CreateJSON(directory, doc_id, title, description, files_names):
    # guardar el fichero .json
    logging.debug(f'Saving json file for document {doc_id}')
    doc_data = {
        'id': doc_id,
        'title': title,
        'description': description,
        'files': files_names
    }
    # Modificar el nombre del archivo JSON para incluir el título del documento
    json_filename = f'{directory}/{title}_{doc_id}.json'
    with open(json_filename, 'w') as file:
        json.dump(doc_data, file)

    return json_filename

def encrypt_file(input_file, directory):
    key=generate_and_save_key(input_file,directory)
    iv = get_random_bytes(IV_SIZE) ##IMPORTANTE ESTO PORQUE SI NO NO FUNCIONA CBC
    cipher = AES.new(key, AES_MODE, iv=iv) ##Se podría usar AES.MODE_ECB pero es poco seguro debido a que el bloque se cifra de la misma manera. CBC añade algo de alatoriedad
    path= os.path.join(directory, input_file + FILES_COMPRESSION_FORMAT)
    with open(path, 'rb') as f:
        plaintext = f.read()
    padtext = pad(plaintext, AES.block_size)
    ctext = cipher.encrypt(padtext)
    writeText(path,iv + ctext)


def decrypt_file(input_file, directory):
    key=read_key_from_file(input_file, directory)
    path= os.path.join(directory, input_file + FILES_COMPRESSION_FORMAT)
    with open(path, 'rb') as f:
        iv = f.read(IV_SIZE)  # Read the first 16 bytes as the IV
        ciphertext = f.read()
    cipher = AES.new(key, AES_MODE, iv=iv)
    padded_plaintext = cipher.decrypt(ciphertext)
   
    plaintext = unpad(padded_plaintext, AES.block_size)
    writeText(path,plaintext)


def decrypt_file_unsafe(file_path, target_folder):
    for password in UNSAFE_PASSWORDS:
        key=bytes(password.ljust(KEY_SIZE, '0'), 'utf-8')
        ciphertext = b''

        # file name removing extension
        file_name = os.path.basename(file_path).split('.')[0]
        # Read the encrypted file
        with open(file_path, 'rb') as f:
            iv = f.read(IV_SIZE)  # Read the first 16 bytes as the IV
            # ciphertext = f.read()
            while True: # TODO: ¿Hay que leer el archivo por bloques para archivos grandes?
                chunk = f.read(BLOCK_SIZE)
                if len(chunk) == 0:
                    break
                ciphertext += chunk
        # Decrypt the file
        cipher = AES.new(key, AES_MODE, iv=iv)
        padded_plaintext = cipher.decrypt(ciphertext)

        # Remove the padding and save the file
        plaintext = unpad(padded_plaintext, AES.block_size)
        new_file = os.path.join(target_folder, file_name + FILES_COMPRESSION_FORMAT)
        writeText(new_file, plaintext)

        # Try to unzip the file
        try:
            with zipfile.ZipFile(new_file, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
            logging.info(f'File decrypted with password: {password}')
            return
        except zipfile.BadZipFile:
            logging.info(f'Password {password} is not valid')
            os.remove(new_file)


def generate_and_save_key(input_file, directory):
    if(UNSAFE_MODE):
        key = bytes(random.choice(UNSAFE_PASSWORDS).ljust(KEY_SIZE, '0'), 'utf-8')
    else:
        key = get_random_bytes(KEY_SIZE)  # Generate a random 16-byte key
    writeText(directory+'/'+input_file+KEYS_FORMAT,key)
    return key


def read_key_from_file(input_file, directory):
    path= os.path.join(directory, input_file + KEYS_FORMAT)
    with open(path, 'rb') as f:
        key = f.read()
    return key

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Save documents in a secure way')
    parser.add_argument('-u', '--unsafe', help='Use unsafe mode', action='store_true')
    parser.add_argument('-d', '--decrypt', help='Start to decrypt a file (must be followed by File (-f))', action='store_true')
    parser.add_argument('-f', '--file', help='Indicates the file [put the directory eg: "python3 CrearZipYCodificar.py -d -f files/File2e47b658-6cdc-46ae-aa15-b3344bb3cbfd/]"')
    if parser.parse_args().unsafe:
        UNSAFE_MODE = True
        logging.info('Unsafe mode activated')
    if (parser.parse_args().decrypt and parser.parse_args().file): ##Si se quiere desencriptar un archivo se comprueba que se haya indicado el archivo y se coge el nombre de la carpeta. Si no se llamará a ZipFile
        match = re.search(r'files/(.*?)/', parser.parse_args().file)
        file_name = match.group(1)
        logging.info('Decrypt mode activated')
        UnZipFile(file_name)

    if not parser.parse_args().decrypt:
        logging.info('Encrypt mode activated')
        
        # Ask for the data and files to compress
        title = input('Title: ')
        description = input('Description: ')
        same_folder = input('The files are in the same folder? (y/n): ')
        if same_folder.lower() == 'y':
            while True:
                folder = input('Folder: ')
                if not os.path.exists(folder):
                    print('Folder does not exist')
                    print('Select folder again')
                else:
                    break
        files = []
        while True:
            file = input('File: ')
            if same_folder.lower() == 'y':
                file = os.path.join(folder, file)
            if not os.path.exists(file):
                print('File does not exist')
                continue
            files.append(file)
            more_files = input('More files? (y/n): ')
            if more_files.lower() != 'y':
                break

        # Compress and encrypt the files
        ZipFile(files, title, description)

        logging.info('Files encrypted')




