import socket
import struct
import os
import ssl

PROTOCOL = ssl.PROTOCOL_TLS_SERVER

class SocketServidor:
    SERVIDOR_IP = 'localhost'
    SERVIDOR_PUERTO = 6190
    FOLDER="server"
    
    def buscar_server_folder(self):
        if not os.path.exists(self.FOLDER):
            os.makedirs(self.FOLDER)

    def create_folder_4_new_file(self, filename):
        filename = filename.split(".")[0]
        path=os.path.join(self.FOLDER, filename)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def receive_Name_size(self, sck: socket.socket):
        fmt="<L"
        expected_bytes = struct.calcsize(fmt)
        received_bytes = 0
        stream = bytes()
        while received_bytes < expected_bytes:
            chunk = sck.recv(expected_bytes - received_bytes)
            stream += chunk
            received_bytes += len(chunk)
            if(len(chunk) == 0):
                raise ConnectionResetError("Conexión cerrada por el cliente.")

        filesize = struct.unpack(fmt, stream)[0]
        return filesize

    def receive_file_size(self, sck: socket.socket):
        fmt = "<Q"
        expected_bytes = struct.calcsize(fmt)
        received_bytes = 0
        stream = bytes()
        while received_bytes < expected_bytes:
            chunk = sck.recv(expected_bytes - received_bytes)
            stream += chunk
            received_bytes += len(chunk)
        filesize = struct.unpack(fmt, stream)[0]
        return filesize

    def receive_file(self, sck: socket.socket):
        print("Esperando el tamaño del nombre del archivo...")
        try:
            NameSize = self.receive_Name_size(sck)
            file = sck.recv(NameSize)
            filename = file.decode('utf-8')
            print(f"Nombre de archivo recibido: {filename}")
            filesize = self.receive_file_size(sck)
            self.buscar_server_folder()
            folder = self.create_folder_4_new_file(filename)
            filename = os.path.join(folder, filename)
        except ConnectionResetError:
            raise ConnectionResetError("Conexión cerrada por el cliente.")

        print("Recibiendo archivo...")
        received_bytes = 0
        with open(filename, "wb") as f:
            while received_bytes < filesize:
                print(f"Recibidos {received_bytes} de {filesize} bytes.")
                try:
                    # remain_bytes = filesize - received_bytes
                    chunk = sck.recv(2048)
                    print(f"Recibidos {len(chunk)} bytes.")
                    if not chunk:
                        raise ConnectionResetError("Conexión cerrada por el cliente.")
                    f.write(chunk)
                    received_bytes += len(chunk)
                except ConnectionResetError:
                    raise ConnectionResetError("Conexión cerrada por el cliente.")

        print("Archivo recibido correctamente.")

    def close(self):
        self.server.close()
        print("Servidor cerrado.")
    

    def start(self):
        while True:
            with socket.create_server((self.SERVIDOR_IP, self.SERVIDOR_PUERTO)) as server:
                print("Esperando al cliente...")
                try:
                    conn, address = server.accept()
                    # conn = ssl.wrap_socket(
                    #     client, 
                    #     server_side=True, 
                    #     certfile='certificates/certificate.pem', 
                    #     keyfile='certificates/key.pem', 
                    #     ssl_version=PROTOCOL)
                    
                except KeyboardInterrupt:
                    print("\nInterrupción de teclado detectada, cerrando el servidor.")
                    server.close()
                    break
                print(f"{address[0]}:{address[1]} conectado.")
                while conn:
                    try:
                        self.receive_file(conn)
                        print("Recibiendo archivo...")
                    except ConnectionResetError:
                        print("Conexión cerrada por el cliente.")
                        conn.close()
                        break
                    print("Archivo recibido.")
