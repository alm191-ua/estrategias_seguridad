import struct
import os
import json

config = json.load(open('config.json'))

class SocketPadre:
    SERVIDOR_IP = config['sockets']['host']
    SERVIDOR_PUERTO = config['sockets']['port']
    FORMATO_ENCRIPTADO='.zip.enc'
    FORMATO_LLAVE='.key'
    FORMATO_JSON='.json'
    conn=None
    FOLDER=None
    def buscar_server_folder(self):
        if not os.path.exists(self.FOLDER):
            os.makedirs(self.FOLDER)

    def create_folder_4_new_file(self, filename):
        filename = filename.split(".")[0]
        path=os.path.join(self.FOLDER, filename)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    def receive_size(self, fmt):

        expected_bytes = struct.calcsize(fmt)
        received_bytes = 0
        stream = bytes()
        while received_bytes < expected_bytes:
            chunk = self.conn.recv(expected_bytes - received_bytes)
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
    
    def receive_file(self,):
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

    def wait_files(self):
        while self.conn:
            try:
                self.receive_file()
            except ConnectionResetError:
                print("Conexión cerrada por el cliente.")
                self.conn.close()
                self.conn=None
                break
            except ValueError:
                print("Archos recibidos correctamente.")
                return
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
        while self.conn:
            files = os.listdir(self.FOLDER)
            legnth = len(files)
            i=0
            for fileId in files:
                
                if fileId != "users.json":
                    print("Enviando archivo...")
                    file_folder_path = os.path.join(self.FOLDER, fileId)
                    files_path = os.path.join(file_folder_path, fileId)
                    file_path = files_path + self.FORMATO_ENCRIPTADO
                    file_key=files_path+self.FORMATO_LLAVE
                    file_json=files_path+self.FORMATO_JSON
                    self.send_file(file_path)
                    self.send_file(file_key)
                    self.send_file(file_json)
                    print("Enviado.")
                i+=1
                if i==legnth:
                    break
            break
        return