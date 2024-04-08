import socket
import SocketPadre
import threading
import ssl
import os
import json

PROTOCOL = ssl.PROTOCOL_TLS_SERVER
SERVER_ROOT_FOLDER = "server"

config = json.load(open('config.json'))

class SocketServidor(SocketPadre.SocketPadre) :
    FOLDER = SERVER_ROOT_FOLDER

    def send_json(self):
        """
        Sends a JSON file to the client.
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
                            os.path.exists(files_path + self.FORMATO_JSON) and \
                            os.path.exists(files_path + self.FORMATO_LLAVE + self.FORMATO_ENCRIPTADO):

                            file_json   = files_path + self.FORMATO_JSON
                            file_key    = files_path + self.FORMATO_LLAVE + self.FORMATO_ENCRIPTADO
                        else:
                            raise FileNotFoundError("El archivo no existe.")
                    except FileNotFoundError as e:
                        print("Error fichero no encontrado en la carpeta", file_folder_path, ":", e)
                        continue

                    self.send_file(file_json)
                    self.send_file(file_key)
                    print("Enviado.")
                
            self.conn.sendall(b"done")
            break
            
        return
    def send_json_malicious(self):
        """
        Sends a JSON file to the client.
        """
        self.FOLDER = SERVER_ROOT_FOLDER
        
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        while self.conn:
            folders = os.listdir(self.FOLDER)
            for folderId in folders:
                if folderId != "users.json":
                    files=os.listdir(os.path.join(self.FOLDER,folderId))
                    for fileId in files:
                        print("Enviando archivo...")
                        try:
                            file_folder_path = os.path.join(self.FOLDER, folderId,fileId)
                            files_path = os.path.join(file_folder_path, fileId)
                            if os.path.exists(file_folder_path) and \
                                os.path.exists(files_path + self.FORMATO_JSON):

                                file_json=files_path+self.FORMATO_JSON
                            else:
                                raise FileNotFoundError("El archivo no existe.")
                        except FileNotFoundError as e:
                            print("Error fichero no encontrado en la carpeta", file_folder_path, ":", e)
                            continue

                        self.send_file(file_json)
                        print("Enviado.")
                    
            self.conn.sendall(b"done")
            break
        return
    
    def send_enconded_file(self, folder,name):
        """
        Sends an encoded file to the client.

        Args:
            folder (str): The folder where the file is located.
            name (str): The name of the file to send.

        """
        files = os.listdir(folder)
        for fileId in files:
            if fileId == name:
                print("Enviando archivo...")
                try:
                    file_folder_path = os.path.join(folder, fileId)
                    files_path = os.path.join(file_folder_path, fileId)
                    if os.path.exists(file_folder_path) and \
                        os.path.exists(files_path + self.FORMATO_ARCHIVO_ENCRIPTADO):

                        file_path = files_path + self.FORMATO_ARCHIVO_ENCRIPTADO
                    else:
                        raise FileNotFoundError("El archivo no existe.")
                    # print(file_path)
                    self.send_file(file_path)
                    print("Enviado.")
                except FileNotFoundError as e:
                    print("Error fichero no encontrado en la carpeta", folder, ":", e)
                    continue
                
                self.conn.sendall(b"done")
                return
        raise Exception("El archivo no existe.")
        
        
    def send_encoded(self):
        name = self.conn.read().decode('utf-8')
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        while self.conn:
            if self.FOLDER == SERVER_ROOT_FOLDER:
                print("MALICIOSO")
                for folderId in os.listdir(self.FOLDER):
                    folder_path = os.path.join(self.FOLDER, folderId)
                    print(folder_path)
                    try:
                        self.send_enconded_file(folder_path, name)
                        return
                    except Exception as e:
                        print("Error al enviar desde la carpeta", folder_path, ":", e)
                        continue  # Continuar con la siguiente iteración del ciclo
                else:
                    raise FileNotFoundError("El archivo no existe.")

            else:
                folder_path = self.FOLDER
                try:
                    self.send_enconded_file(folder_path,name)
                    return
                except Exception as e:
                    print(e)   
            break
        return
        
          
    def start(self, handle_client):
        while True:
            with socket.create_server((self.SERVIDOR_IP, self.SERVIDOR_PUERTO)) as server:
                print("Esperando al cliente...")
                try:
                    # Accept the connection
                    client, address = server.accept()

                    # Wrap the socket in an SSL context
                    self.conn = ssl.wrap_socket(
                        client, 
                        server_side=True, 
                        certfile='certificates/certificate.pem', 
                        keyfile='certificates/key.pem', 
                        ssl_version=PROTOCOL)
                    
                except KeyboardInterrupt:
                    server.close()
                    print("\nInterrupción de teclado detectada, cerrando el servidor.")
                    break
                
                thread = threading.Thread(target=handle_client, args=(self, address))
                thread.start()
                print("Active threads: ", threading.active_count())
                        
