# client.py
import os
import socket
import struct
import sys

SERVIDOR_IP = 'localhost'
SERVIDOR_PUERTO = 12345
FOLDER_PATH = 'files'
FORMATO_ENCRIPTADO='.zip.enc'


def send_file(sck: socket.socket, filename):
    # Enviar el nombre del archivo al servidor.
    name = os.path.basename(filename)
    name_size = len(name)
    sck.sendall(struct.pack("<L", name_size))
    sck.sendall(name.encode('utf-8'))

    # Obtener el tamaño del archivo a enviar.
    filesize = os.path.getsize(filename)
    # Informar primero al servidor la cantidad
    # de bytes que serán enviados.
    sck.sendall(struct.pack("<Q", filesize))
    
    # Enviar el archivo en bloques de 1024 bytes.
    with open(filename, "rb") as f:
        while read_bytes := f.read(1024):
            sck.sendall(read_bytes)

# Crear un socket de tipo TCP/IP.
with socket.create_connection(("localhost", 6190)) as conn:
    print("Conectado al servidor.")
    
    for fileId in os.listdir(FOLDER_PATH):
            print("Enviando archivo...")
            file_folder_path = os.path.join(FOLDER_PATH, fileId)
            files_path = os.path.join(file_folder_path, fileId)
            file_path = files_path + FORMATO_ENCRIPTADO

            send_file(conn, file_path)

            print("Enviado.")
    conn.close()
print("Conexión cerrada.")