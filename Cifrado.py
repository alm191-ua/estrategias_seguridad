import zipfile
import os	
import sys
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import logging
from uuid import uuid4 as unique_id
import random
import json
from datetime import datetime
import base64
from utils.secure_key_gen import cipher_data, decipher_data

# Modo de cifrado
AES_MODE = AES.MODE_CTR

# directorio de los ficheros
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
KEY_SIZE = 32
IV_SIZE = 8 ##8 bytes
BLOCK_SIZE = 2048 #AES.block_size # in bytes 
DIRECTORIO=os.getcwd()
NOMBRE_PROYECTO="estrategias_seguridad"
DIRECTORIO_PROYECTO=None
log_directory=''

exec_dir = os.getcwd()
print('EXEC_DIR:', exec_dir)
DIRECTORIO_EJECUCION=exec_dir
if getattr(sys, 'frozen', False):
    DIRECTORIO_PROYECTO = sys._MEIPASS
else:
    DIRECTORIO_PROYECTO = os.getcwd()
    
# DIRECTORIO_PROYECTO = sys._MEIPASS
print('DIRECTORIO_TEMPORAL:', DIRECTORIO_PROYECTO)
# if(os.path.basename(exec_dir)==NOMBRE_PROYECTO):
#     DIRECTORIO_PROYECTO=exec_dir
# else:
#     DIRECTORIO_PROYECTO = os.path.dirname(exec_dir)
log_directory=os.path.join(DIRECTORIO_PROYECTO,'logs')


# Verificar si el directorio existe y, si no, crearlo
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configurar el registro con el directorio especificado
log_file_path = os.path.join(log_directory, 'logfile.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')
# logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')  # Formato con hora


def is_unsafe_mode(unsafe_mode):
    """
    Establece el modo seguro/inseguro.
    Args:
        unsafe_mode (bool): Modo seguro/inseguro.
    """
    global UNSAFE_MODE
    UNSAFE_MODE=unsafe_mode

def buscar_proyecto():
    """
    Busca la ruta del proyecto actual.

    Args:
        None.

    Returns:
        str o None: Ruta del proyecto si se encuentra, None si no.
    """

    global DIRECTORIO_PROYECTO
    # exec_dir = os.getcwd()
    # print('EXEC_DIR:', exec_dir)
    # DIRECTORIO_PROYECTO=exec_dir

    if getattr(sys, 'frozen', False):
        DIRECTORIO_PROYECTO = sys._MEIPASS
    else:
        DIRECTORIO_PROYECTO = os.getcwd()

    # if(os.path.basename(exec_dir)==NOMBRE_PROYECTO):
    #     DIRECTORIO_PROYECTO=exec_dir
    # else:
    #     DIRECTORIO_PROYECTO = os.path.dirname(exec_dir)

def Create_Dirs(filename,newdir=FILE_DIR):
    """
    Crea el directorio principal 'files/' y el subdirectorio para un archivo específico.

    Args:
        nombre_archivo (str): Nombre del archivo para el que se crea el subdirectorio.
        nuevo_directorio (str, optional): Nombre del directorio principal. Predeterminado: "files".

    Returns:
        str: Ruta del directorio del archivo.
    """
    if not DIRECTORIO_PROYECTO:
        buscar_proyecto()
    if DIRECTORIO_PROYECTO:
        DIRECTORIO=DIRECTORIO_PROYECTO
    else:
        DIRECTORIO=os.path.join(DIRECTORIO, NOMBRE_PROYECTO)
    # Primero, asegúrate de que el directorio principal 'files/' exista
    DIRECTORIO=os.path.join(DIRECTORIO, newdir)
    print(DIRECTORIO)
    os.makedirs(DIRECTORIO, exist_ok=True)# Usa os.makedirs() que crea directorios intermedios necesarios
    # Luego, procede a crear el subdirectorio para el archivo específico
    directory = os.path.join(DIRECTORIO, filename)  # Es más seguro usar os.path.join()
    if not os.path.exists(directory):
        os.makedirs(directory)  # Cambiado a os.makedirs() para coherencia y para evitar futuros errores
    return directory

def write_in_file_bytes(File, text):
    """
    Escribe bytes en un archivo.

    Args:
        archivo (str): Ruta del archivo.
        contenido (bytes): Contenido a escribir.

    Returns:
        None.
    """
    with open(File, 'wb') as f:
        f.write(text)

def generate_unique_id():
    """
    Genera un identificador único.

    Args:
        None.

    Returns:
        str: Identificador único.
    """
    return str(unique_id())

# ============= ZIP =============

def ZipFiles(directory, files, doc_id):
    """
    Comprime una lista de archivos en un directorio específico.

    Args:
        directorio (str): Directorio donde se encuentran los archivos.
        archivos (list): Lista de nombres de archivos.
        doc_id (str): Identificador único del documento.

    Returns:
        str: Ruta al archivo comprimido.
    """
    zip_path = os.path.join(directory, f"{doc_id}{FILES_COMPRESSION_FORMAT}")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:  # Itera sobre la lista de archivos
            if os.path.isfile(file):  # Verifica si el path es de un archivo
                zipf.write(file, os.path.basename(file))  # Añade el archivo al zip
    return zip_path



# ============= JSON ============

def _handle_JSON_decryption(files, json_filename, old_key):
    """
    Desencripta archivos si se proporciona una clave anterior,
    de lo contrario, los devuelve directamente.

    Args:
        archivos (list): Lista de nombres de archivos o contenidos codificados en base64.
        nombre_archivo_json (str): Ruta al documento JSON que contiene información de los archivos.
        clave_anterior (bytes, opcional): Clave anterior si se desea desencriptar y reencriptar (predeterminado: None).

    Returns:
        list: Lista de los archivos desencriptados en formato de bytes o los archivos originales.
    """
    if not old_key==None:
        return decrypt_files_JSON(files,json_filename,old_key)
    else:
        return files
    
#Lo he recuperado de la rama main
def decrypt_files_JSON(encrypted_files, json_filename,old_key=None):
    """
    Desencripta los archivos listados en un documento JSON.

    Args:
        archivos_encriptados (list): Lista de representaciones base64 de los archivos encriptados.
        nombre_archivo_json (str): Ruta al documento JSON que contiene la información de los archivos.
        clave_anterior (bytes, opcional): Clave anterior si se desea reencriptar (predeterminado: None).

    Returns:
        list: Lista de los archivos desencriptados en formato de bytes.
    """
    key=key_to_use(old_key,json_filename)
    decrypted_files = []
    for encrypted_file in encrypted_files:
        # Decodificar y separar el IV del texto cifrado
        iv_ctext = base64.b64decode(encrypted_file)
        iv = iv_ctext[:IV_SIZE]
        ctext = iv_ctext[IV_SIZE:]
        # Crear cifrador y desencriptar el archivo
        cipher = AES.new(key, AES.MODE_CTR, nonce=iv)
        decrypted_file = cipher.decrypt(ctext).decode()
        decrypted_files.append(decrypted_file)
    return decrypted_files

def encrypt_files_JSON(json_filename, key,old_key=None):
    """
    Encripta los archivos listados en un documento JSON y actualiza el documento en el mismo lugar.
    Utiliza RSA para encriptar los nombre de los archivos.
    
    Args:
        nombre_archivo_json (str): Ruta al documento JSON que contiene la información de los archivos.
        clave (bytes): Clave de encriptación.
        clave_anterior (bytes, opcional): Clave anterior si se desea desencriptar y reencriptar (predeterminado: None).

    Returns:
        None.
    """
    
    with open(json_filename, 'r') as file:
        doc_data = json.load(file)
    files = _handle_JSON_decryption(doc_data['files'], json_filename, old_key)
    encrypted_files = []
    for file in files:
        # iv = get_random_bytes(IV_SIZE)
        # cipher = AES.new(key, AES_MODE, nonce=iv)
        # ctext = cipher.encrypt(file.encode())
        # encrypted_files.append(base64.b64encode(iv + ctext).decode())
        ctext_hex = cipher_data(file, key)
        encrypted_files.append(bytes.fromhex(ctext_hex).decode('utf-8'))
    doc_data['files'] = encrypted_files
    with open(json_filename, 'w') as file:
        json.dump(doc_data, file)
 
def encrypt_json_filenames(json_filename, key,old_key=None):
    """
    Encripta los archivos listados en un documento JSON y actualiza el documento en el mismo lugar.

    Args:
        nombre_archivo_json (str): Ruta al documento JSON que contiene la información de los archivos.
        clave (bytes): Clave de encriptación.
        clave_anterior (bytes, opcional): Clave anterior si se desea desencriptar y reencriptar (predeterminado: None).

    Returns:
        list: Lista de representaciones base64 de los archivos encriptados.
    """
    
    with open(json_filename, 'r') as file:
        doc_data = json.load(file)
    files = _handle_JSON_decryption(doc_data['files'], json_filename, old_key)
    encrypted_files = []
    for file in files:
        iv = get_random_bytes(IV_SIZE)
        cipher = AES.new(key, AES.MODE_CTR, nonce=iv)
        ctext = cipher.encrypt(file.encode())
        encrypted_files.append(base64.b64encode(iv + ctext).decode())
    doc_data['files'] = encrypted_files
    with open(json_filename, 'w') as file:
        json.dump(doc_data, file)

def create_and_save_document_json(directory, doc_id, title, description, files_names, author,size, json_name=None):
    """
    Crea un archivo JSON con los datos del documento y lo guarda en la ruta especificada.

    Args:
        directory (str): Directorio donde se guardará el archivo JSON.
        doc_id (str): Identificador único del documento.
        title (str): Título del documento.
        description (str): Descripción del documento.
        files_names (list[str]): Lista con los nombres de los archivos asociados al documento.
        author (str): Autor del documento.
        json_name (str, optional): Nombre personalizado para el archivo JSON.

    Returns:
        str: Ruta completa del archivo JSON creado.
    """

    logging.info(f"Creando archivo JSON para el documento {doc_id}")

    # Extraer los nombres base de los archivos para incluirlos en el JSON
    files_base_names = [os.path.basename(file) for file in files_names]

    size=round((size/1024)/1024,2)

    # Crear el diccionario con los datos del documento
    document_data = {
        "id": doc_id,
        "title": title,
        "description": description,
        "author": author,  # Añadir el autor al JSON
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": files_base_names,
        "size": str(size)+" MB"
    }

    # Crear un nombre de archivo JSON que incluya el título del documento
    if not json_name:
        json_filename = os.path.join(directory, f"{NAME_FILES}{doc_id}.json")
    else:
        json_filename = os.path.join(directory, json_name)

    # Guardar los datos del documento en formato JSON
    with open(json_filename, "w") as json_file:
        json.dump(document_data, json_file, indent=4)

    return json_filename



# ========= ENCRYPTION ==========

def encrypt_single_file(file_path, key, target_directory, change_name=False):
    """
    Encrypts a single file using AES-CTR.

    Args:
        file_path (str): Path to the file to encrypt.
        key (bytes): The key to use for encryption.
        target_directory (str): Path to the directory where the encrypted file will be saved.
        change_name (bool, optional): If True, the name of the directory includes the name of the file. Default: False.
        
    Returns:
        str: Path to the encrypted file.
    """
    iv = get_random_bytes(IV_SIZE)
    cipher = AES.new(key, AES_MODE, nonce=iv)
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    space = len(plaintext)
    ctext = cipher.encrypt(plaintext)
    if change_name:
        encrypted_path = target_directory
    else:
        encrypted_path = os.path.join(target_directory, os.path.basename(file_path) + FILES_ENCODE_FORMAT)
    write_in_file_bytes(encrypted_path, iv + ctext)
    delete_path=os.path.join(target_directory, os.path.basename(file_path))
    os.remove(delete_path)
    logging.info(f'File {file_path} encrypted')
    return encrypted_path,space

def encrypt_file_asimetric(file_path, key, target_directory, change_name=False):
    """
    Encrypts a single file using RSA.
    
    Args:
        file_path (str): Path to the file to encrypt.
        key (bytes): The key to use for encryption.
        target_directory (str): Path to the directory where the encrypted file will be saved.
        change_name (bool, optional): If True, the name of the directory includes the name of the file. Default: False.
    
    Returns:
        str: Path to the encrypted file.
    """

    # use cipher_data to encrypt the file (RSA)
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    ctext_hex = cipher_data(plaintext, key)
    if change_name:
        encrypted_path = target_directory
    else:
        encrypted_path = os.path.join(target_directory, os.path.basename(file_path) + FILES_ENCODE_FORMAT)
    write_in_file_bytes(encrypted_path, bytes.fromhex(ctext_hex))
    logging.info(f'File {file_path} encrypted with public key')
    return encrypted_path

def decrypt_file_asimetric(file_path, key, target_directory, change_name=False):
    """
    Decrypts a single file using RSA.
    
    Args:
        file_path (str): Path to the file to decrypt.
        key (bytes): The key to use for decryption.
        target_directory (str): Path to the directory where the decrypted file will be saved.
        change_name (bool, optional): If True, the name of the directory includes the name of the file. Default: False.
    
    Returns:
        str: Path to the decrypted file.
    """
    # use decipher_data to decrypt the file (RSA)
    with open(file_path, 'rb') as f:
        ctext = f.read()
    plaintext = decipher_data(ctext.hex(), key)
    if change_name:
        decrypted_path = target_directory
    else:
        decrypted_path = os.path.join(target_directory, os.path.basename(file_path)[:-4])
    write_in_file_bytes(decrypted_path, plaintext)
    logging.info(f'File {file_path} decrypted with private key')
    return decrypted_path

def encrypt_file(input_file, directory,old_key=None,data_key=None):
    """
    Encripta un archivo y lo guarda en la ruta especificada.
    Actualiza el archivo JSON con la información de encriptación.

    Args:
        input_file (str): Ruta del archivo a encriptar.
        directory (str): Directorio donde se guardará el archivo encriptado.
        old_key (bytes, optional): Clave anterior del archivo (para desencriptación y reencriptación).

    Returns:
        None.
    """
    if data_key:
        print('Data key provided')
        key = data_key
    elif not old_key:
        key = generate_and_save_key(input_file, directory)
        print(key)
    if old_key:
        key=old_key
    iv = get_random_bytes(IV_SIZE)
    cipher = AES.new(key, AES_MODE, nonce=iv)
    if data_key:
        path = os.path.join(directory, input_file)
    else:  
        path = os.path.join(directory, input_file + FILES_COMPRESSION_FORMAT)
        json_filename = os.path.join(directory, input_file + '.json')
    with open(path, 'rb') as f:
        plaintext = f.read()
    
    ctext = cipher.encrypt(plaintext)
    encrypted_path = path +FILES_ENCODE_FORMAT
    write_in_file_bytes(encrypted_path, iv + ctext)
    os.remove(path)
    if not data_key:
        encrypt_files_JSON(json_filename, key,old_key)
    logging.info('File encrypted')

def key_to_use(old_key,json_filename):
    """
    Determina la clave adecuada a usar para operaciones criptográficas.

    Args:
        clave_anterior (bytes, opcional): Clave anterior si se proporciona (predeterminado: None).

    Returns:
        bytes: La clave a utilizar.
    """
    path=json_filename.replace('.json','')
    if old_key==None:
        return read_key_from_file(path)
    else:
        return old_key


def try_decrypt_files_JSON(encrypted_files,key):

    decrypted_files = []
    for encrypted_file in encrypted_files:
        # Decodificar y separar el IV del texto cifrado
        iv_ctext = base64.b64decode(encrypted_file)
        iv = iv_ctext[:IV_SIZE]
        ctext = iv_ctext[IV_SIZE:]
        # Crear cifrador y desencriptar el archivo
        cipher = AES.new(key, AES_MODE, nonce=iv)
        decrypted_file = cipher.decrypt(ctext).decode()
        decrypted_files.append(decrypted_file)
    return decrypted_files


def _handle_decrypt_file(input_file, key = None):
    """
    Desencripta un archivo individual usando AES-CTR.

    Args:
        archivo_entrada (str): Ruta al archivo encriptado.

    Returns:
        bytes: Contenido desencriptado del archivo.
        bytes: Clave utilizada para la desencriptación.
    """

    # Extraer nombre base del archivo y recuperar la clave
    file = input_file.replace(FILES_COMPRESSION_FORMAT + FILES_ENCODE_FORMAT, '')
    if key == None:
        key = read_key_from_file(file)
    # Leer el archivo por fragmentos para manejar archivos grandes
    chunks = []
    with open(input_file, 'rb') as f:
        iv = f.read(IV_SIZE)  # Read first 8 bytes as IV
        while True:
            chunk = f.read(BLOCK_SIZE)
            if len(chunk) == 0:
                break
            chunks.append(chunk)
    ciphertext = b''.join(chunks)
    try:
    # Crear cifrador y desencriptar el texto
        cipher = AES.new(key, AES_MODE, nonce=iv)
        plaintext = cipher.decrypt(ciphertext)
    except Exception as e:
        print(e)
    print(len(plaintext))
    return plaintext, key

def decrypt_file(input_file, key = None,data_key=None):
    """
    Desencripta un archivo individual y guarda la versión con texto plano.

    Args:
        archivo_entrada (str): Ruta al archivo encriptado.

    Returns:
        bytes: Clave utilizada para la desencriptación (para usos posteriores).
    """
    if key:
        global UNSAFE_MODE
        UNSAFE_MODE = True
    if data_key:
        key=data_key
    plaintext, key = _handle_decrypt_file(input_file, key)
    encrypted_path = input_file[:-4]  # Elimina la extensión ".enc"
    write_in_file_bytes(encrypted_path, plaintext)
    if not UNSAFE_MODE:
        os.remove(input_file)
    return key

def decrypt_file_unsafe(file_path, target_folder):
    """
    Descifra un archivo inseguro individual y guarda la versión con texto plano.

    Args:
        archivo_entrada (str): Ruta al archivo cifrado.

    Returns:
        bytes: Clave utilizada para la descifrado (para usos posteriores).
    """
    decrypted = False
    for password in UNSAFE_PASSWORDS:
        key=bytes(password.ljust(KEY_SIZE, '0'), 'utf-8')

        decrypt_file(file_path, key)
        new_file = file_path[:-4]  # Elimina la extensión ".enc"
        # Try to unzip the file
        try:
            with zipfile.ZipFile(new_file, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
            logging.info(f'File decrypted')
            decrypted = True
            return key
        except zipfile.BadZipFile:
            # logging.info(f'Password {password} is not valid')
            pass
        finally:
            os.remove(new_file)
    if not decrypted:
        logging.error('File could not be decrypted')
        raise Exception('File could not be decrypted')

def generate_and_save_key(input_file,directory):
    """
    Genera una clave aleatoria segura y la guarda en un archivo.

    Args:
        nombre_archivo (str): Nombre del archivo de la clave.
        directorio (str): Directorio donde guardar el archivo.

    Returns:
        bytes: Clave generada.
    """
    if(UNSAFE_MODE):
        # gets random password from the list and pads it with zeros to match the key size
        key = bytes(random.choice(UNSAFE_PASSWORDS).ljust(KEY_SIZE, '0'), 'utf-8')
    else:
        key = get_random_bytes(KEY_SIZE)  # Generate a random 16-byte key
    path = os.path.join(directory,input_file)
    path += KEYS_FORMAT
    # cypher key
    # path += KEYS_FORMAT + FILES_ENCODE_FORMAT
    # iv = get_random_bytes(IV_SIZE)
    # cipher = AES.new(key, AES_MODE, nonce=iv)
    # ctext = cipher.encrypt(key)
    # write_in_file_bytes(path, iv + ctext)
    write_in_file_bytes(path,key)
    return key

def read_key_from_file(input_file):
    """
    Lee una clave del archivo especificado.

    Args:
        nombre_archivo (str): Nombre del archivo de la clave.

    Returns:
        bytes: Clave leída del archivo.
    """
    file=input_file+KEYS_FORMAT
    try:
        with open(file, 'rb') as f:
            key = f.read()
    except FileNotFoundError:
        logging.error(f'Key file not found: {file}')
        raise
    # decyper key
    # iv = key[:IV_SIZE]
    # ctext = key[IV_SIZE:]
    # cipher = AES.new(key, AES_MODE, nonce=iv)
    # key = cipher.decrypt(ctext)
    return key
