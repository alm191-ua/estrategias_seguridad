import os
import socket
import struct
import ssl

class SocketCliente:
    SERVIDOR_IP = 'localhost'
    SERVIDOR_PUERTO = 6190
    FOLDER_PATH = 'files'
    FORMATO_ENCRIPTADO='.zip.enc'
    FORMATO_LLAVE='.key'
    FORMATO_JSON='.json'

    def __init__(self):
        self.conn = None

    def connect(self):
        # Crear un socket de tipo TCP/IP.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = ssl.wrap_socket(
                        sock,
                        ca_certs='certificates/certificate.pem')
        
        self.conn.connect((self.SERVIDOR_IP, self.SERVIDOR_PUERTO))
        print("Conectado al servidor.")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print("Conexión cerrada.")

    def send_file(self, filename):
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")

        # Enviar el nombre del archivo al servidor.
        name = os.path.basename(filename)
        name_size = len(name)
        self.conn.sendall(name_size.to_bytes(4, byteorder='big'))
        self.conn.sendall(name.encode('utf-8'))

        # Obtener el tamaño del archivo a enviar.
        filesize = os.path.getsize(filename)
        # Informar primero al servidor la cantidad
        # de bytes que serán enviados.
        print("Enviando tamaño del archivo...")
        self.conn.sendall(struct.pack("<Q", filesize))

        # Enviar el archivo en bloques de 2048 bytes.
        with open(filename, "rb") as f:
            print("Enviando archivo...")
            while read_bytes := f.read(2048):
                print(f"Enviados {len(read_bytes)} bytes.")
                self.conn.sendall(read_bytes)

    def send_files_in_folder(self):
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")

        for fileId in os.listdir(self.FOLDER_PATH):
            print("Enviando archivo...")
            file_folder_path = os.path.join(self.FOLDER_PATH, fileId)
            files_path = os.path.join(file_folder_path, fileId)
            file_path = files_path + self.FORMATO_ENCRIPTADO
            file_key = files_path+self.FORMATO_LLAVE
            file_json = files_path+self.FORMATO_JSON

            print("Enviando enc")
            self.send_file(file_path)
            print("Enviando key")
            self.send_file(file_key)
            print("Enviando json")
            self.send_file(file_json)

            print("Enviado.")