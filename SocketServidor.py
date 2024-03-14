import socket
import struct
import os

FOLDER="server"

class SocketServidor:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def buscar_server_folder(self):
        if not os.path.exists(FOLDER):
            os.makedirs(FOLDER)


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
            filename = os.path.join(FOLDER, filename)
        except ConnectionResetError:
            raise ConnectionResetError("Conexión cerrada por el cliente.")

        print("Recibiendo archivo...")
        received_bytes = 0
        with open(filename, "wb") as f:
            while received_bytes < filesize:
                try:
                    remain_bytes = filesize - received_bytes
                    chunk = sck.recv(min(remain_bytes, 2048))
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
            with socket.create_server((self.host, self.port)) as server:
                print("Esperando al cliente...")
                try:
                    conn, address = server.accept()
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
