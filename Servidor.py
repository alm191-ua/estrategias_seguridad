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
    start_time = time.time()
    NameSize = receive_Name_size(sck)
    file= sck.recv(NameSize)
    filename = file.decode('utf-8')
    filesize = receive_file_size(sck)
        
    def receive_data():
        with open(filename, "wb") as f:
            received_bytes = 0
            while received_bytes < filesize:
                remain_bytes = filesize - received_bytes
                chunk = sck.recv(min(remain_bytes, 1024))
                if chunk:
                    f.write(chunk)
                    received_bytes += len(chunk)
            f.close()

    # Create a thread to receive data
    thread = threading.Thread(target=receive_data)
    thread.start()

    # Wait for the thread to finish
    thread.join()

    end_time = time.time()
    print(f"Tiempo de ejecución: {end_time - start_time} segundos")
with socket.create_server(("localhost", 6190)) as server:
    print("Esperando al cliente...")
    conn, address = server.accept()
    print(f"{address[0]}:{address[1]} conectado.")
    while True:
        print("Recibiendo archivo...")
        receive_file(conn)
        print("Archivo recibido.")
  
    

