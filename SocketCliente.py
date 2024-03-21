import os
import socket
import struct

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
        self.conn = socket.create_connection((self.SERVIDOR_IP, self.SERVIDOR_PUERTO))
        print("Conectado al servidor.")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print("Conexión cerrada.")




    def buscar_server_folder(self):
        if not os.path.exists(self.FOLDER_PATH):
            os.makedirs(self.FOLDER_PATH)

    def create_folder_4_new_file(self, filename):
        filename = filename.split(".")[0]
        path=os.path.join(self.FOLDER_PATH, filename)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def receive_size(self,fmt):

        expected_bytes = struct.calcsize(fmt)
        received_bytes = 0
        stream = bytes()
        while received_bytes < expected_bytes:
            chunk = self.conn.recv(expected_bytes - received_bytes)
            stream += chunk
            received_bytes += len(chunk)
            if(len(chunk) == 0):
                raise ConnectionResetError("Conexión cerrada por el servidor.")

        filesize = struct.unpack(fmt, stream)[0]
        return filesize
    
    def receive_file(self):
        print("Esperando el tamaño del nombre del archivo...")
        try:
            fmt="<L"
            NameSize = self.receive_size(fmt)
            file = self.conn.recv(NameSize)
            filename = file.decode('utf-8')
            fmt="<Q"
            print(f"Nombre de archivo recibido: {filename}")
            filesize = self.receive_size(fmt)
            self.buscar_server_folder()
            folder = self.create_folder_4_new_file(filename)
            filename = os.path.join(folder, filename)
        except ConnectionResetError:
            raise ConnectionResetError("Conexión cerrada por el servidor.")

        print("Recibiendo archivo...")
        received_bytes = 0
        with open(filename, "wb") as f:
            while received_bytes < filesize:
                try:
                    remain_bytes = filesize - received_bytes
                    chunk = self.conn.recv(min(remain_bytes, 2048))
                    if not chunk:
                        raise ConnectionResetError("Conexión cerrada por el servidor.")
                    f.write(chunk)
                    received_bytes += len(chunk)
                except ConnectionResetError:
                    raise ConnectionResetError("Conexión cerrada por el servidor.")

        print("Archivo recibido correctamente.")
    
    def wait_files(self):
        while self.conn:
            try:
                self.receive_file()
            except ConnectionResetError:
                print("Conexión cerrada.")
                self.disconnect()
                break
            print("Archivo recibido.")

    def send_file(self, filename):
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")

        # Enviar el nombre del archivo al servidor.
        name = os.path.basename(filename)
        name_size = len(name)
        self.conn.sendall(struct.pack("<L", name_size))
        self.conn.sendall(name.encode('utf-8'))

        # Obtener el tamaño del archivo a enviar.
        filesize = os.path.getsize(filename)
        # Informar primero al servidor la cantidad
        # de bytes que serán enviados.
        self.conn.sendall(struct.pack("<Q", filesize))

        # Enviar el archivo en bloques de 2048 bytes.
        with open(filename, "rb") as f:
            while read_bytes := f.read(2048):
                self.conn.sendall(read_bytes)

    def send_files_in_folder(self):
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")

        for fileId in os.listdir(self.FOLDER_PATH):
            print("Enviando archivo...")
            file_folder_path = os.path.join(self.FOLDER_PATH, fileId)
            files_path = os.path.join(file_folder_path, fileId)
            file_path = files_path + self.FORMATO_ENCRIPTADO
            file_key=files_path+self.FORMATO_LLAVE
            file_json=files_path+self.FORMATO_JSON
            self.send_file(file_path)
            self.send_file(file_key)
            self.send_file(file_json)
            print("Enviado.")
            os.remove(file_path)
            os.remove(file_key)
            os.remove(file_json)
            os.rmdir(file_folder_path)
            os.rmdir(files_path)

    def choose_opt(self, number):
        """
        Sends an integer to the server and performs the corresponding action.

        Args:
            number (int): The integer to send.
            [1]-> send files in the 'files' folder to the server
            [2]-> wait for files from the server

        Raises:
            Exception: If no connection has been established.

        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        self.conn.sendall(str(number).encode('utf-8'))
        if number == 1:
            # Send files in the 'files' folder to the server
            self.send_files_in_folder()
            self.disconnect()
        if number == 2:
            # Wait for files from the server
            self.wait_files()
            self.disconnect()
    
    