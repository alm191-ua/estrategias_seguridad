# codigo que permita guardar los documentos en el directorio files
# con una estructura de un subdirectorio por cada documento
# y dentro de cada subdirectorio se guardan los archivos de cada documento
# además se guarda un fichero .json con el título, descripción y ficheros asociados
# a cada documento en el directorio documents

import os
import json
import shutil
from uuid import uuid4 as unique_id
from Crypto.Cipher import AES
from secure_key_gen import generate_key
import random
import argparse
import logging

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

# directorio temporal
TMP_DIR = 'tmp'
# directorio de los ficheros
FILES_DIR = 'files'
COMPRESSION_FORMAT = 'zip'
KEY_SIZE = 16
AES_MODE = AES.MODE_EAX

# crear directorio de documentos
if not os.path.exists(TMP_DIR):
    logging.debug('Creating tmp directory')
    os.makedirs(TMP_DIR)

# crear directorio de ficheros
if not os.path.exists(FILES_DIR):
    logging.debug('Creating files directory')
    os.makedirs(FILES_DIR)

# test data
test_dir = 'test'
if not os.path.exists(test_dir):
    logging.debug('Creating test directory')
    os.makedirs(test_dir)

def save_document(title, description, files):
    # crear id único para el documento
    doc_id = str(unique_id())

    # crear directorio para el documento
    doc_dir = f'{FILES_DIR}/{doc_id}'
    if not os.path.exists(doc_dir):
        logging.debug(f'Creating directory for document {doc_id}')
        os.makedirs(doc_dir)

    # copiar los ficheros al directorio temporal
    logging.debug(f'Copying files to tmp directory')
    for file in files:
        shutil.copy(file, TMP_DIR)

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

    # comprimir los ficheros que hay en el directorio temporal
    logging.debug(f'Compressing files for document {doc_id}')
    name = shutil.make_archive(f'./{TMP_DIR}/{doc_id}', COMPRESSION_FORMAT, TMP_DIR)
    encoded_name = name.encode('utf-8')

    # generar y almacenar clave de encriptación aleatoria
    if UNSAFE_MODE:
        logging.debug(f'Generating unsafe key for document {doc_id}')
        key = bytes(random.choice(UNSAFE_PASSWORDS).ljust(KEY_SIZE, '0'), 'utf-8')
    else:
        logging.debug(f'Generating safe key for document {doc_id}')
        key = generate_key(KEY_SIZE)
    with open(f'./{doc_dir}/{doc_id}.key', 'wb') as file:
        file.write(key)

    # encriptar el fichero comprimido con AES
    logging.debug(f'Encrypting file for document {doc_id}')
    cipher = AES.new(key, AES_MODE)
    ciphertext, tag = cipher.encrypt_and_digest(encoded_name)
    with open(f'{name}.enc', 'wb') as file:
        [file.write(x) for x in (cipher.nonce, tag, ciphertext)]

    # mover el fichero encriptado al directorio del documento
    shutil.move(f'{name}.enc', doc_dir)

    # eliminar el directorio temporal
    shutil.rmtree(TMP_DIR)

    logging.info(f'Document {doc_id} saved successfully')

# main with arguments
def main():
    parser = argparse.ArgumentParser(description='Save documents in a secure way')
    parser.add_argument('-u', '--unsafe', help='Use unsafe mode', action='store_true')
    parser.add_argument('-t', '--test_document', help='Create a test document', action='store_true')
    args = parser.parse_args()

    global UNSAFE_MODE
    UNSAFE_MODE = args.unsafe
    if args.test_document:
        document1_title = 'documento1'
        document1_description = 'descripcion del documento 1'
        document1_files = [f'./{test_dir}/file1.txt', f'./{test_dir}/file2.txt']
        save_document(document1_title, document1_description, document1_files)
    
    print('Program finished successfully!')


if __name__ == '__main__':
    main()


