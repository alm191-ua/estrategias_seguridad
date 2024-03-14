# server.py
import socket
import struct
import time
import threading

def receive_Name_size(sck: socket.socket):
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

def receive_file_size(sck: socket.socket):
    # Esta función se asegura de que se reciban los bytes
    # que indican el tamaño del archivo que será enviado,
    # que es codificado por el cliente vía struct.pack(),
    # función la cual genera una secuencia de bytes que
    # representan el tamaño del archivo.
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


def receive_file(sck: socket.socket):
    print("Esperando el tamaño del nombre del archivo...")
    try:
        
        NameSize = receive_Name_size(sck)
        
        file = sck.recv(NameSize)
        
        filename = file.decode('utf-8')
        print(f"Nombre de archivo recibido: {filename}")
        filesize = receive_file_size(sck)
        print(f"Tamaño del archivo: {filesize}")
    except ConnectionResetError:
        raise ConnectionResetError("Conexión cerrada por el cliente.")
        return

    print("Recibiendo archivo...")
    received_bytes = 0
    with open(filename, "wb") as f:
        while received_bytes < filesize:
            try:
                remain_bytes = filesize - received_bytes
                chunk = sck.recv(min(remain_bytes, 2048))
                if not chunk:
                    raise ConnectionResetError("Conexión cerrada por el cliente.")
                    return
                f.write(chunk)
                received_bytes += len(chunk)
            except ConnectionResetError:
                raise ConnectionResetError("Conexión cerrada por el cliente.")
                return

    print("Archivo recibido correctamente.")

while True:
    with socket.create_server(("localhost", 6190)) as server:
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
                receive_file(conn)
                print("Recibiendo archivo...")
            except ConnectionResetError:
                print("Conexión cerrada por el cliente.")
                conn.close()
                break
            print("Archivo recibido.")
    

