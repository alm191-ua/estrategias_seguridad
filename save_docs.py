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

unsafe_mode = False
unsafe_passwords = ['123456',
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
tmp_dir = 'tmp'
# directorio de los ficheros
files_dir = 'files'
compression_format = 'zip'
key_size = 16
aes_mode = AES.MODE_EAX

# crear directorio de documentos
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

# crear directorio de ficheros
if not os.path.exists(files_dir):
    os.makedirs(files_dir)

# test data
test_dir = 'test'
if not os.path.exists(test_dir):
    os.makedirs(test_dir)

def save_document(title, description, files):
    # crear id único para el documento
    doc_id = str(unique_id())

    # crear directorio para el documento
    doc_dir = f'{files_dir}/{doc_id}'
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)

    # copiar los ficheros al directorio temporal
    for file in files:
        shutil.copy(file, tmp_dir)

    # guardar el fichero .json
    files_names = os.listdir(tmp_dir)
    doc_data = {
        'id': doc_id,
        'title': title,
        'description': description,
        'files': files_names
    }
    with open(f'{tmp_dir}/{doc_id}.json', 'w') as file:
        json.dump(doc_data, file)

    # comprimir los ficheros que hay en el directorio temporal
    name = shutil.make_archive(f'./{tmp_dir}/{doc_id}', compression_format, tmp_dir)
    encoded_name = name.encode('utf-8')

    # generar y almacenar clave de encriptación aleatoria
    if unsafe_mode:
        key = bytes(random.choice(unsafe_passwords).ljust(key_size, '0'), 'utf-8')
    else:
        key = generate_key(key_size)
    with open(f'./{doc_dir}/{doc_id}.key', 'wb') as file:
        file.write(key)

    # encriptar el fichero comprimido con AES
    cipher = AES.new(key, aes_mode)
    ciphertext, tag = cipher.encrypt_and_digest(encoded_name)
    with open(f'{name}.enc', 'wb') as file:
        [file.write(x) for x in (cipher.nonce, tag, ciphertext)]

    # mover el fichero encriptado al directorio del documento
    shutil.move(f'{name}.enc', doc_dir)

    # eliminar el directorio temporal
    shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    document1_title = 'documento1'
    document1_description = 'descripcion del documento 1'
    document1_files = [f'./{test_dir}/file1.txt', f'./{test_dir}/file2.txt']
    save_document(document1_title, document1_description, document1_files)


