import socket
import struct
import os



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

    def receive_size(self, sck: socket.socket,fmt):

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
    
    def receive_file(self, sck: socket.socket):
        print("Esperando el tamaño del nombre del archivo...")
        try:
            fmt="<L"
            NameSize = self.receive_size(sck,fmt)
            file = sck.recv(NameSize)
            filename = file.decode('utf-8')
            fmt="<Q"
            print(f"Nombre de archivo recibido: {filename}")
            filesize = self.receive_size(sck,fmt)
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
                    chunk = sck.recv(min(remain_bytes, 2048))
                    if not chunk:
                        raise ConnectionResetError("Conexión cerrada por el cliente.")
                    f.write(chunk)
                    received_bytes += len(chunk)
                except ConnectionResetError:
                    raise ConnectionResetError("Conexión cerrada por el cliente.")

        print("Archivo recibido correctamente.")

    def close(self):
        if self.server:
            self.server.close()
            print("Servidor cerrado.")
    
    def wait_files(self, conn: socket.socket):
        while conn:
            try:
                self.receive_file(conn)
            except ConnectionResetError:
                print("Conexión cerrada por el cliente.")
                conn.close()
                break
            print("Archivo recibido.")
    
    

    def start(self):
        while True:
            with socket.create_server((self.SERVIDOR_IP, self.SERVIDOR_PUERTO)) as server:
                print("Esperando al cliente...")
                try:
                    conn, address = server.accept()
                except KeyboardInterrupt:
                    print("\nInterrupción de teclado detectada, cerrando el servidor.")
                    server.close()
                    break
                print(f"{address[0]}:{address[1]} conectado.")
                option = conn.recv(1).decode('utf-8')
                print(f"Opción seleccionada: {option}")
                if option == '1':
                    self.wait_files(conn)
                elif option == '2':
                    files = os.listdir(self.FOLDER)
                    print(f'Enviando {len(files)} archivos al cliente...')

                
