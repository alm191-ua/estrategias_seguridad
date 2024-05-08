import struct
import os
import json


config = json.load(open('config.json'))
file_does_not_exist_tag = config['sockets']['tags']['response']['file_does_not_exist']
chunk_size = config['sockets']['chunk_size']

class SocketPadre:
    """
    Clase padre para la comunicación entre el servidor y el cliente.
    Permite ralizar el envío y recepción de archivos, ya sea desde el servidor al cliente o viceversa.
    """
    SERVIDOR_IP = config['sockets']['host']
    SERVIDOR_PUERTO = config['sockets']['port']
    ENVIAR=config['sockets']['tags']['init_comms']['send']
    RECIBIR=config['sockets']['tags']['init_comms']['receive']
    RECIBIR_JSON=config['sockets']['tags']['init_comms']['receive_json']
    RECIBIR_FILE=config['sockets']['tags']['init_comms']['receive_file']
    RECIBIR_PUBLIC_KEYS=config['sockets']['tags']['init_comms']['receive_public_keys']
    RECIBIR_JSON_MALICIOUS=config['sockets']['tags']['init_comms']['recieve_json_malicious']
    RECIBIR_JSON_SHARED=config['sockets']['tags']['init_comms']['receive_shared_json']
    correct_sent=config['sockets']['tags']['response']['correct_sent']
    FORMATO_ARCHIVO_ENCRIPTADO='.zip.enc'
    FORMATO_LLAVE='.key'
    FORMATO_JSON='.json'
    FORMATO_ENCRIPTADO='.enc'
    FORMATO_COMPRESION='.zip'
    conn=None
    FOLDER=None

    def buscar_server_folder(self):
        """
        Busca la carpeta del servidor en la que se guardarán los archivos.
        Si no existe, la crea.
        """
        if not os.path.exists(self.FOLDER):
            os.makedirs(self.FOLDER)

    def create_folder_4_new_file(self, filename):
        """
        Crea una carpeta para un nuevo archivo.
        """
        filename = filename.split(".")[0]
        path=os.path.join(self.FOLDER, filename)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    def receive_size(self, fmt):
        """
        Recibe el tamaño de un archivo.
        
        Args:
            fmt (str): El formato del tamaño del archivo.

        Returns:
            int: El tamaño del archivo.
        """
        expected_bytes = struct.calcsize(fmt)
        received_bytes = 0
        stream = bytes()
        while received_bytes < expected_bytes:
            chunk = self.conn.recv(expected_bytes - received_bytes)       
            if chunk == file_does_not_exist_tag.encode('utf-8'):
                raise FileNotFoundError("El archivo no existe.")
            try:
                if chunk.decode('utf-8') == "done":
                    return 0
                
                if chunk.decode('utf-8') == "disc":
                    raise ConnectionResetError("Conexión cerrada por el cliente.")

            except UnicodeDecodeError:
                pass
            stream += chunk
            received_bytes += len(chunk)
            

        filesize = struct.unpack(fmt, stream)[0]
        return filesize
    
    def receive_file(self,sharing=False):
        """
        Recibe un archivo.
        """
        print("Esperando el tamaño del nombre del archivo...")
        try:
            fmt = "<L"
            NameSize = self.receive_size(fmt)
            if NameSize == 0:
                raise ValueError("Everything sent correctly")
            file = self.conn.recv(NameSize)
            filename = file.decode('utf-8')
            fmt="<Q"
            print(f"Nombre de archivo recibido: {filename}")
            filename = 'File'+filename
            filesize = self.receive_size(fmt)
            self.buscar_server_folder()
            folder = self.create_folder_4_new_file(filename)
            filename = os.path.join(folder, filename)
        except ConnectionResetError:
            raise ConnectionResetError("Conexión cerrada por el cliente.")

        print("Recibiendo archivo...")
        received_bytes = 0
        with open(filename, "wb") as f:
            while received_bytes < filesize:
                try:
                    remain_bytes = filesize - received_bytes
                    chunk = self.conn.recv(min(remain_bytes, 2048))
                    if not chunk:
                        raise ConnectionResetError("Conexión cerrada por el cliente.")
                    f.write(chunk)
                    received_bytes += len(chunk)
                except ConnectionResetError:
                    raise ConnectionResetError("Conexión cerrada por el cliente.")
            f.close()

        print("Archivo recibido correctamente.")

    def wait_files(self,sharing=False):
        """
        Espera a recibir archivos.
        """
        while self.conn:
            try:
                self.receive_file(sharing)
            except ConnectionResetError:
                print("Conexión cerrada.")
                self.conn.close()
                self.conn=None
                break
            except ValueError as e:
                print("Archivos recibidos correctamente.")
                break
            except FileNotFoundError as e:
                print(e)
                break
            print("Archivo recibido.")


    def send_one_file(self, filename):
        """
        Envia un archivo.

        Args:
            filename (str): La ruta del archivo a enviar.
        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        
        if not os.path.exists(filename):
            print(f"El archivo {filename} no existe.")
            raise FileNotFoundError("El archivo no existe.")
        
        # send filename
        name = os.path.basename(filename)
        self.conn.write(name.encode('utf-8'))

        with open(filename, "rb") as f:
            while read_bytes := f.read(chunk_size):
                self.conn.write(read_bytes)
            self.conn.sendall(b"EOF")
                
    def receive_one_file(self, filename=None, folder=None, receive_file_name=True):
        """
        Recibe un archivo.

        Args:
            filename (str): El nombre del archivo.
            folder (str): La carpeta en la que se guardará el archivo.
        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        
        if (not receive_file_name) and (not filename):
            raise ValueError("Se debe especificar un nombre de archivo o recibirlo del cliente.")
            
        # receive filename
        if receive_file_name:
            _filename = self.conn.read().decode('utf-8')
        if filename:
            _filename = filename

        base_filename = os.path.basename(_filename)
        print("Recibiendo archivo...", base_filename)

        if folder:
            _path = folder
            file_path = os.path.join(_path, base_filename)
        else:
            _path = self.FOLDER
            file_path = os.path.join(_path, base_filename)
        print("Guardando archivo en:", file_path)
            
        if not os.path.exists(_path):
            os.makedirs(_path)

        with open(file_path, "wb") as f:
            while True:
                #Problema
                chunk = self.conn.read(chunk_size)
                if chunk == b"EOF":
                    break
                f.write(chunk)
            f.close()
        return file_path

    def send_file(self, filename):
        """
        Envia un archivo.
        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        
        # Enviar el nombre del archivo al servidor.
        name = os.path.basename(filename)
        print("filename, name: ", filename, name)
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
        """
        Envia los archivos en el directorio seleccionado.
        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        while self.conn:
            files = os.listdir(self.FOLDER)
            for fileId in files:
                if fileId != "users.json":
                    print("Enviando archivo...")
                    try:
                        file_folder_path = os.path.join(self.FOLDER, fileId)
                        files_path  = os.path.join(file_folder_path, fileId)
                        if os.path.exists(file_folder_path) and \
                            os.path.exists(files_path + self.FORMATO_ARCHIVO_ENCRIPTADO) and \
                            os.path.exists(files_path + self.FORMATO_LLAVE + self.FORMATO_ENCRIPTADO) and \
                            os.path.exists(files_path + self.FORMATO_JSON):
                        
                            file_path   = files_path + self.FORMATO_ARCHIVO_ENCRIPTADO
                            file_key    = files_path + self.FORMATO_LLAVE + self.FORMATO_ENCRIPTADO
                            file_json   = files_path + self.FORMATO_JSON
                        else:
                            raise FileNotFoundError(f"El archivo {fileId} no existe.")
                    except FileNotFoundError as e:
                        print("Error faltan ficheros en la carpeta", file_folder_path, ":", e)
                        continue
                    
                    self.send_file(file_path)
                    self.send_file(file_key)
                    self.send_file(file_json)
                    print("Enviado.")
                
            self.conn.sendall(b"done")
            break
            
        return

