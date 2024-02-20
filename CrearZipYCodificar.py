import zipfile
import os	
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import logging
from uuid import uuid4 as unique_id
import argparse
import random
import re
import json
from datetime import datetime
from Logs import LoggerConfigurator 
import base64

# directorio de los ficheros
AES_MODE = AES.MODE_CTR

FILE_DIR='files'
NAME_FILES='File'
FILES_COMPRESSION_FORMAT='.zip'
FILES_ENCODE_FORMAT='.enc'
KEYS_FORMAT='.key'
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
IV_SIZE = 8 ##8 bytes
BLOCK_SIZE = AES.block_size # in bytes 
DIRECTORIO=os.getcwd()
NOMBRE_PROYECTO="estrategias_seguridad"
DIRECTORIO_PROYECTO=None


def is_unsafe_mode(unsafe_mode):
    if unsafe_mode == True:
        return UNSAFE_MODE == True
    else:
        return UNSAFE_MODE == False


def buscar_directorio(nombre_directorio, ruta_inicio=os.path.abspath(os.sep)):


    # Recorre todos los directorios y archivos en la ruta_inicio
    for root, dirs, files in os.walk(ruta_inicio):
        
        # Busca el directorio deseado en la lista de directorios
        if nombre_directorio in dirs:
            # Si lo encuentra, devuelve la ruta completa del directorio
            return os.path.join(root, nombre_directorio)
            
    # Si no lo encuentra, devuelve None
    return None


def buscar_proyecto():
    global DIRECTORIO_PROYECTO
    DIRECTORIO_PROYECTO=buscar_directorio(NOMBRE_PROYECTO)
    return DIRECTORIO_PROYECTO

def buscar_directorio_archivo_comprimido(nombre_archivo_sin_extension):
    if not DIRECTORIO_PROYECTO:
        buscar_proyecto()
    if DIRECTORIO_PROYECTO:
       return buscar_directorio(nombre_archivo_sin_extension, DIRECTORIO_PROYECTO)
    return None
    



def Create_Dirs(filename,newdir=FILE_DIR):
    if not DIRECTORIO_PROYECTO:
        buscar_proyecto()
    if DIRECTORIO_PROYECTO:
        DIRECTORIO=DIRECTORIO_PROYECTO
    else:
        DIRECTORIO=os.path.join(DIRECTORIO, NOMBRE_PROYECTO)
    # Primero, asegúrate de que el directorio principal 'files/' exista
    DIRECTORIO=os.path.join(DIRECTORIO, newdir)
    if not os.path.exists(DIRECTORIO):
        os.makedirs(DIRECTORIO)  # Usa os.makedirs() que crea directorios intermedios necesarios
        logging.info('Main directory created')

    # Luego, procede a crear el subdirectorio para el archivo específico
    directory = os.path.join(DIRECTORIO, filename)  # Es más seguro usar os.path.join()
    if not os.path.exists(directory):
        os.makedirs(directory)  # Cambiado a os.makedirs() para coherencia y para evitar futuros errores
        LoggerConfigurator.Subdirectory("Interfaz")
    return directory


def writeText(File, text):
    with open(File, 'wb') as f:
        f.write(text)
    

def ZipFile(files, title, description):
    doc_Id = str(unique_id())
    FileName = NAME_FILES + str(doc_Id)
    directory = Create_Dirs(FileName)
    zip_path = os.path.join(directory, FileName + FILES_COMPRESSION_FORMAT)
    


    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:  # Itera sobre la lista de archivos
            if os.path.isfile(file):  # Verifica si el path es de un archivo
                zipf.write(file, os.path.basename(file))  # Añade el archivo al zip

    CreateJSON(directory,doc_Id, title, description, files)
    encrypt_file(FileName, directory)
    
    logging.info('Files compressed')




def UnZipFiles(file,target_folder=None):
    if not target_folder:
            target_folder=os.path.dirname(file)
    try:
        decrypt_file(file)
        fileDesencrypted=file.replace(FILES_ENCODE_FORMAT,'')
        fileWithNoFormat=fileDesencrypted.replace(FILES_COMPRESSION_FORMAT,'')
        Folder=os.path.basename(fileWithNoFormat)
        directorio_Final=os.path.join(target_folder,Folder)
        if not os.path.exists(directorio_Final):
            os.makedirs(directorio_Final)
        with zipfile.ZipFile(fileDesencrypted, 'r') as zip_ref:
            zip_ref.extractall(directorio_Final)
            logging.info('Files extracted')
        encrypt_file(fileWithNoFormat,'')
        return True
    except Exception as e:
        logging.error(f'Error al extraer los archivos: {e}')
        return False




def encrypt_files_JSON(json_filename, key):
    with open(json_filename, 'r') as file:
        doc_data = json.load(file)
    files=doc_data['files']
    encrypted_files = []
    for file in files:
        iv = get_random_bytes(IV_SIZE)
        cipher = AES.new(key, AES.MODE_CTR, nonce=iv)
        ctext = cipher.encrypt(file.encode())
        encrypted_files.append(base64.b64encode(iv + ctext).decode())
    doc_data['files'] = encrypted_files
    with open(json_filename, 'w') as file:
        json.dump(doc_data, file)
 
def CreateJSON(directory, doc_id, title, description, files_names):
    # guardar el fichero .json
    logging.debug(f'Saving json file for document {doc_id}')
    for i, file in enumerate(files_names):
        files_names[i] = os.path.basename(file)

    doc_data = {
        'id': doc_id,
        'title': title,
        'description': description,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Formato 'YYYY-MM-DD HH:MM:SS
        'files': files_names
    }
    # Modificar el nombre del archivo JSON para incluir el título del documento
    json_filename = os.path.join(directory, f'File{doc_id}.json')
    with open(json_filename, 'w') as file:
        json.dump(doc_data, file)

    return json_filename






def encrypt_file(input_file, directory):
    key = generate_and_save_key(input_file, directory)
    iv = get_random_bytes(IV_SIZE)
    cipher = AES.new(key, AES_MODE, nonce=iv)
    path = os.path.join(directory, input_file + FILES_COMPRESSION_FORMAT)
    json_filename = os.path.join(directory, input_file + '.json')
    with open(path, 'rb') as f:
        plaintext = f.read()
    
    ctext = cipher.encrypt(plaintext)
    encrypted_path = path +FILES_ENCODE_FORMAT
    writeText(encrypted_path, iv + ctext)
    os.remove(path)
    encrypt_files_JSON(json_filename, key)



def decrypt_files_JSON(json_filename):
    path=json_filename.replace('.json','')

    with open(json_filename, 'r') as file:
        doc_data = json.load(file)
    encrypted_files=doc_data['files']
    key=read_key_from_file(path)
    decrypted_files = []
    for encrypted_file in encrypted_files:
        iv_ctext = base64.b64decode(encrypted_file)
        iv = iv_ctext[:IV_SIZE]
        ctext = iv_ctext[IV_SIZE:]
        cipher = AES.new(key, AES.MODE_CTR, nonce=iv)
        decrypted_file = cipher.decrypt(ctext).decode()
        decrypted_files.append(decrypted_file)
    doc_data['files'] = decrypted_files
    with open(json_filename, 'w') as file:
        json.dump(doc_data, file)
    return doc_data




def decrypt_file(input_file):
    file=input_file.replace(FILES_COMPRESSION_FORMAT+FILES_ENCODE_FORMAT, '')
    key = read_key_from_file(file)
    chunks = []
    with open(input_file, 'rb') as f:
        iv = f.read(IV_SIZE)  # Lee los primeros 8 bytes como IV
        while True:
            chunk = f.read(BLOCK_SIZE)
            if len(chunk) == 0:
                break
            chunks.append(chunk)
    ciphertext = b''.join(chunks)
    cipher = AES.new(key, AES_MODE, nonce=iv)
    plaintext = cipher.decrypt(ciphertext)
    encrypted_path = input_file[:-4]  # Elimina la extensión ".enc"
    writeText(encrypted_path, plaintext)
    os.remove(input_file)



def decrypt_file_unsafe(file_path, target_folder):
    for password in UNSAFE_PASSWORDS:
        key=bytes(password.ljust(KEY_SIZE, '0'), 'utf-8')

        chunks = []
        with open(file_path, 'rb') as f:
            iv = f.read(IV_SIZE)  # Lee los primeros 16 bytes como IV
            while True:
                chunk = f.read(BLOCK_SIZE)
                if len(chunk) == 0:
                    break
                chunks.append(chunk)
        ciphertext = b''.join(chunks)
        cipher = AES.new(key, AES_MODE, nonce=iv)
        plaintext = cipher.decrypt(ciphertext)
        # file name removing extension
        file_name = os.path.basename(file_path).split('.')[0]
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


def generate_and_save_key(input_file,directory):
    if(UNSAFE_MODE):
        key = bytes(random.choice(UNSAFE_PASSWORDS).ljust(KEY_SIZE, '0'), 'utf-8')
    else:
        key = get_random_bytes(KEY_SIZE)  # Generate a random 16-byte key
    path=os.path.join(directory,input_file)
    path+=KEYS_FORMAT
    writeText(path,key)
    return key



def read_key_from_file(input_file):
    file=input_file+KEYS_FORMAT
    with open(file, 'rb') as f:
        key = f.read()
    return key


#encrypt_file("Filee52fd474-21c0-4115-b515-ce963d43f621", "files\Filee52fd474-21c0-4115-b515-ce963d43f621")
#encrypt_file("Filedbce936b-2f98-4f73-a078-1d2ca5558586", "files\Filedbce936b-2f98-4f73-a078-1d2ca5558586")
#decrypt_file("files\Filedbce936b-2f98-4f73-a078-1d2ca5558586\Filedbce936b-2f98-4f73-a078-1d2ca5558586.zip.enc")
#decrypt_file("files\Filee52fd474-21c0-4115-b515-ce963d43f621\Filee52fd474-21c0-4115-b515-ce963d43f621.zip.enc")


'''


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
    UnZipJSON(file_name)

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
'''


