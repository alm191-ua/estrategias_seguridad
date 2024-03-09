import zipfile
import os	
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import logging
from uuid import uuid4 as unique_id
import random
import json
from datetime import datetime
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
log_directory = '../logs'

# Verificar si el directorio existe y, si no, crearlo
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configurar el registro con el directorio especificado
log_file_path = os.path.join(log_directory, 'logfile.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')  # Formato con hora


def is_unsafe_mode(unsafe_mode):
    """
    Establece el modo seguro/inseguro.
    Args:
        unsafe_mode (bool): Modo seguro/inseguro.
    """
    global UNSAFE_MODE
    UNSAFE_MODE=unsafe_mode

def buscar_directorio(nombre_directorio, ruta_inicio=os.path.abspath(os.sep)):
    """
    Recorre un directorio y sus subdirectorios buscando un directorio específico.

    Args:
        nombre_directorio (str): Nombre del directorio a buscar.
        ruta_inicio (str, optional): Ruta donde iniciar la búsqueda. Predeterminado: raíz del sistema.

    Returns:
        str o None: Ruta completa del directorio si se encuentra, None si no.
    """
    for root, dirs, files in os.walk(ruta_inicio):
        if nombre_directorio in dirs:
            return os.path.join(root, nombre_directorio)
    return None

def buscar_proyecto():
    """
    Busca la ruta del proyecto actual.

    Args:
        None.

    Returns:
        str o None: Ruta del proyecto si se encuentra, None si no.
    """

    global DIRECTORIO_PROYECTO
    exec_dir = os.getcwd()
    DIRECTORIO_PROYECTO = os.path.dirname(exec_dir)

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

# ============= ZIP =============

def ZipAndEncryptFile(files, title, description):
    """
    Crea un paquete comprimido de documentos con metadatos asociados y encriptación.

    Args:
        archivos (lista): Lista de archivos para incluir en el paquete.
        titulo (str): Título del documento.
        descripcion (str): Descripción del documento.

    Returns:
        str: Ruta al archivo del paquete creado.
    """
    doc_id = str(unique_id())
    FileName = f"{NAME_FILES}{doc_id}"
    directory = Create_Dirs(FileName)
    zip_path = os.path.join(directory, FileName + FILES_COMPRESSION_FORMAT)
    

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:  # Itera sobre la lista de archivos
            if os.path.isfile(file):  # Verifica si el path es de un archivo
                zipf.write(file, os.path.basename(file))  # Añade el archivo al zip

    create_and_save_document_json(directory,doc_id, title, description, files)
    encrypt_file(FileName, directory)

    logging.info('Files compressed')

def UnZipFiles(file,target_folder=None):
    """
    Extrae y desencripta un paquete de documentos.

    Args:
        archivo_paquete (str): Ruta al archivo del paquete encriptado.
        carpeta_destino (str, opcional): Carpeta de destino para la extracción.
                                        Predeterminado al directorio del paquete.

    Returns:
        bool: True si la extracción y desencriptación fueron exitosas, False si no.
    """
    if not target_folder:
            target_folder=os.path.dirname(file)
    try:
        key=decrypt_file(file)
        fileDesencrypted=file.replace(FILES_ENCODE_FORMAT,'')
        fileWithNoFormat=fileDesencrypted.replace(FILES_COMPRESSION_FORMAT,'')
        Folder=os.path.basename(fileWithNoFormat)
        directorio_Final=os.path.join(target_folder,Folder)
        os.makedirs(directorio_Final, exist_ok=True)  # Crea la carpeta objetivo si no existe
        with zipfile.ZipFile(fileDesencrypted, 'r') as zip_ref:
            zip_ref.extractall(directorio_Final)
            logging.info('Files extracted')
        encrypt_file(fileWithNoFormat,'',key)
        return True
    except Exception as e:
        logging.error(f'Error al extraer los archivos: {e}')
        return False

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

def encrypt_files_JSON(json_filename, key,old_key=None):
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
 
def create_and_save_document_json(directory, doc_id, title, description, files_names):
    """
    Crea un archivo JSON con los datos del documento y lo guarda en la ruta especificada.

    Args:
        directory (str): Directorio donde se guardará el archivo JSON.
        doc_id (str): Identificador único del documento.
        title (str): Título del documento.
        description (str): Descripción del documento.
        files_names (list[str]): Lista con los nombres de los archivos asociados al documento.

    Returns:
        str: Ruta completa del archivo JSON creado.
    """

    logging.info(f"Creando archivo JSON para el documento {doc_id}")

    # Extraer los nombres base de los archivos para incluirlos en el JSON
    files_base_names = [os.path.basename(file) for file in files_names]

    # Crear el diccionario con los datos del documento
    document_data = {
        "id": doc_id,
        "title": title,
        "description": description,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": files_base_names
    }

    # Crear un nombre de archivo JSON que incluya el título del documento
    json_filename = os.path.join(directory, f"{NAME_FILES}{doc_id}.json")

    # Guardar los datos del documento en formato JSON
    with open(json_filename, "w") as json_file:
        json.dump(document_data, json_file, indent=4)

    return json_filename


# ========= ENCRYPTION ==========

def encrypt_file(input_file, directory,old_key=None):
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
    
    key = generate_and_save_key(input_file, directory)
    iv = get_random_bytes(IV_SIZE)
    cipher = AES.new(key, AES_MODE, nonce=iv)
    path = os.path.join(directory, input_file + FILES_COMPRESSION_FORMAT)
    json_filename = os.path.join(directory, input_file + '.json')
    with open(path, 'rb') as f:
        plaintext = f.read()
    
    ctext = cipher.encrypt(plaintext)
    encrypted_path = path +FILES_ENCODE_FORMAT
    write_in_file_bytes(encrypted_path, iv + ctext)
    os.remove(path)
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
    # Crear cifrador y desencriptar el texto
    cipher = AES.new(key, AES_MODE, nonce=iv)
    plaintext = cipher.decrypt(ciphertext)

    return plaintext, key

def decrypt_file(input_file, key = None):
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
            return
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
        key = bytes(random.choice(UNSAFE_PASSWORDS).ljust(KEY_SIZE, '0'), 'utf-8')
    else:
        key = get_random_bytes(KEY_SIZE)  # Generate a random 16-byte key
    path=os.path.join(directory,input_file)
    path+=KEYS_FORMAT
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
    with open(file, 'rb') as f:
        key = f.read()
    return key



'''


parser = argparse.ArgumentParser(description='Save documents in a secure way')
parser.add_argument('-u', '--unsafe', help='Use unsafe mode', action='store_true')
parser.add_argument('-d', '--decrypt', help='Start to decrypt a file (must be followed by File (-f))', action='store_true')
parser.add_argument('-f', '--file', help='Indicates the file [put the directory eg: "python3 Cifrado.py -d -f files/File2e47b658-6cdc-46ae-aa15-b3344bb3cbfd/]"')
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


