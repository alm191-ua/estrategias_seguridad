import socket
import SocketPadre
import threading
import ssl
import os
import json

PROTOCOL = ssl.PROTOCOL_TLS_SERVER
SERVER_ROOT_FOLDER = "server"
SHARED_FOLDER = "shared"
PRIVATE_FILES = ["users.json", "public_keys.json", "private_key.pem.enc", "shared"]

config = json.load(open('config.json'))
file_does_not_exist_tag = config['sockets']['tags']['response']['file_does_not_exist']

class SocketServidor(SocketPadre.SocketPadre) :
    FOLDER = SERVER_ROOT_FOLDER
    username = ''

    def send_json(self):
        """
        Sends a JSON file to the client.
        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        while self.conn:    
            try:
                files = os.listdir(self.FOLDER)
            except Exception as e:
                files=[]
            for fileId in files:
                if fileId in PRIVATE_FILES:
                    continue

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
                if folderId in PRIVATE_FILES:
                    continue

                files=os.listdir(os.path.join(self.FOLDER,folderId))
                for fileId in files:
                    if fileId in ["private_key.pem.enc"]:
                        continue

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
                        os.path.exists(files_path + self.FORMATO_ARCHIVO_ENCRIPTADO) and \
                        os.path.exists(files_path + self.FORMATO_JSON) and \
                        os.path.exists(files_path + self.FORMATO_LLAVE + self.FORMATO_ENCRIPTADO):

                        file_path   = files_path + self.FORMATO_ARCHIVO_ENCRIPTADO
                        file_json   = files_path + self.FORMATO_JSON
                        file_key    = files_path + self.FORMATO_LLAVE + self.FORMATO_ENCRIPTADO
                    else:
                        raise FileNotFoundError("El archivo no existe.")
                    # print(file_path)
                    self.send_file(file_path)
                    self.send_file(file_json)
                    self.send_file(file_key)
                    print("Enviado.")
                except FileNotFoundError as e:
                    print("Error fichero no encontrado en la carpeta", folder, ":", e)
                    continue
                
                self.conn.sendall(b"done")
                return
        raise Exception("El archivo no existe.")
        
    def send_public_keys(self):
        """
        Sends the public keys to the client.
        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        try:
            public_keys_file_path = os.path.join(SERVER_ROOT_FOLDER, "public_keys.json")
            self.send_one_file(public_keys_file_path)
        except FileNotFoundError as e:
            print("Error al enviar las claves públicas:", e)
        except Exception as e:
            print("Error al enviar las claves públicas:", e)

    def wait_shared(self,):
        """
        Espera a recibir los ficheros compartidos (.key y .json) cifrados con las claves publicas de los usuarios.
        También los almacena en los directorios de cada usuario.
        """
        while self.conn:
            try:
                self.receive_shared_file()
            except FileNotFoundError as e:
                print(e)
                continue
            except Exception as e:
                print(e)
                print("Archivos recibidos correctamente.")
                break

            print("Archivo recibido.")

    def receive_one_document(self):
        """
        Recibe un documento del cliente y lo almacena en su directorio correspondiente.
        """
        file_name = self.conn.read().decode('utf-8')
        prev_folder = self.FOLDER
        self.FOLDER = os.path.join(self.FOLDER, file_name)
        self.receive_one_file(filename=file_name, receive_file_name=False)
        self.FOLDER = prev_folder

    
    def receive_shared_file(self):
        """
        Recibe un archivo compartido.

        Returns:
            str: The name of the user with whom the file was shared.
        """
        filename = self.conn.read().decode('utf-8')
        if filename == 'done':
            raise Exception("No se ha recibido ningún archivo.")
        # filename received is in format: "doc-id_user1_hola.some-ext.enc"
        # we need to split it to get the filename and extension
        file_name_base = filename.split('_', maxsplit=1)[0]
        file_ext = filename.split('.', maxsplit=1)[1]
        file_name = file_name_base + '.' + file_ext
        shared_user = filename.split('_', maxsplit=1)[1].split('.', maxsplit=1)[0]

        # check if the shared user exists
        if not os.path.exists(os.path.join(SERVER_ROOT_FOLDER, shared_user)):
            raise FileNotFoundError("El usuario compartido no existe.")

        # server/user_shared/shared/user_owner/filename
        # TODO: comprobar si funciona con el malicioso
        if shared_user == self.username:
            folder = os.path.join(self.FOLDER, file_name_base)
        else:
            folder = os.path.join(SERVER_ROOT_FOLDER, shared_user, SHARED_FOLDER, self.username, file_name_base)
        
        print("Receiving shared file...", file_name, "from", self.username, "to", shared_user, "in", folder)

        if not os.path.exists(folder):
            os.makedirs(folder)
            
        self.receive_one_file(file_name, folder, receive_file_name=False)

        return shared_user

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
                    self.conn.sendall(file_does_not_exist_tag.encode('utf-8'))
                    print(e)   
            break
        return
        
    def send_shared_json(self):
        """
        Sends a JSON file to the client.
        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        while self.conn:    
            try:
                files = os.listdir(self.FOLDER)
                print(files)
            except Exception as e:
                files=[]
            for fileId in files:
                if fileId == "shared":
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
                        
