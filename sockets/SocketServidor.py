import logging
import socket
import SocketPadre
import threading
import ssl
import os
import sys
import json

PROTOCOL = ssl.PROTOCOL_TLS_SERVER
if getattr(sys, 'frozen', False):
    DIRECTORIO_PROYECTO = sys._MEIPASS
else:
    DIRECTORIO_PROYECTO = os.getcwd()
PRIVATE_FILES = ["users.json", "public_keys.json", "private_key.pem.enc", "shared"]

ruta_base = os.path.join(os.path.dirname(__file__),'..')
config_file = os.path.join(ruta_base, 'config.json')

config = json.load(open(config_file))
file_does_not_exist_tag = config['sockets']['tags']['response']['file_does_not_exist']

PERSISTENT_SERVER = config["persistent_server"]

ruta_certs = os.path.join(ruta_base, 'certificates')
pub_cert = os.path.join(ruta_certs, 'certificate.pem')
priv_key = os.path.join(ruta_certs, 'key.pem')

if PERSISTENT_SERVER:
    SERVER_BASE_DIR = os.path.join(os.path.expanduser(os.getenv('USERPROFILE')), 'ES_practica')
else:
    SERVER_BASE_DIR = DIRECTORIO_PROYECTO
SERVER_ROOT_FOLDER = os.path.join(SERVER_BASE_DIR, 'server')
SHARED_FOLDER = 'shared'
class SocketServidor(SocketPadre.SocketPadre) :
    SERVER_FOLDER = SERVER_ROOT_FOLDER
    FOLDER = SERVER_ROOT_FOLDER
    print('Folder:', FOLDER)
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
                    print('Folder:', self.FOLDER)
                    print('File:', fileId)
                    print('File folder path:', file_folder_path)
                    files_path  = os.path.join(file_folder_path, fileId)
                    if os.path.exists(file_folder_path) and \
                        os.path.exists(files_path + self.FORMATO_JSON) and \
                        os.path.exists(files_path + self.FORMATO_LLAVE + self.FORMATO_ENCRIPTADO):

                        file_json   = files_path + self.FORMATO_JSON
                        file_key    = files_path + self.FORMATO_LLAVE + self.FORMATO_ENCRIPTADO
                    else:
                        raise FileNotFoundError("El archivo no existe.")
                except FileNotFoundError as e:
                    logging.warning(f"Error fichero no encontrado en la carpeta {file_folder_path}: {e}")
                    print("Error fichero no encontrado en la carpeta", file_folder_path, ":", e)
                    continue

                self.send_file(file_json)
                self.send_file(file_key)
                logging.info(f"Archivo JSON enviado al usuario {self.username}")
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
                    logging.info(f"Archivo JSON enviado sin verificar contraseña")
                    print("Enviado.")
                    
            self.conn.sendall(b"done")
            break
        return
    
    def send_enconded_file(self, folder,name, shared=False):
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
                    logging.warning(f"Error fichero no encontrado en la carpeta {folder}: {e}")
                    print("Error fichero no encontrado en la carpeta", folder, ":", e)
                    continue
                if not shared:
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
            logging.warning("Error al enviar las claves públicas:")
            print("Error al enviar las claves públicas:", e)
        except Exception as e:
            logging.warning("Error al enviar las claves públicas:")
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
                continue
            except Exception as e:
                logging.info("Archivo compartido recibido.")
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
            logging.warning(f"El usuario compartido {shared_user} no existe.")
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
        autor = self.conn.read().decode('utf-8')
        print(autor,' ',self.username)
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
                        logging.warning(f"Error al enviar desde la carpeta {folder_path}: {e}")
                        print("Error al enviar desde la carpeta", folder_path, ":", e)
                        continue  # Continuar con la siguiente iteración del ciclo
                else:
                    raise FileNotFoundError("El archivo no existe.")

            else:
                folder_path = self.FOLDER
                shared = False
                
                if autor != self.username:
                    print(name)
                    shared = True
                    folder_path = os.path.join(SERVER_ROOT_FOLDER,autor)
                    print(folder_path)
                try:
                    self.send_enconded_file(folder_path,name,shared)
                    return
                except Exception as e:
                    logging.warning(f"Archivo {name} no encontrado")
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
            except Exception as e:
                files=[]
            for fileId in files:
                if fileId=='shared':
                    path_shared_users=os.path.join(self.FOLDER,fileId)
                    propietarios=os.listdir(path_shared_users)
                    for propietario in propietarios:
                        if propietario in PRIVATE_FILES:
                            continue
                        archivos_path=os.path.join(path_shared_users,propietario)
                        archivos=os.listdir(archivos_path)
                        for archivo in archivos:
                            archivo_path=os.path.join(archivos_path,archivo)
                            camino_sin_extension=os.path.join(archivo_path,archivo)
                            camino_json=camino_sin_extension+self.FORMATO_JSON
                            camino_llave=camino_sin_extension+self.FORMATO_LLAVE+self.FORMATO_ENCRIPTADO
                            if os.path.exists(camino_json) and os.path.exists(camino_llave):
                                self.send_file(camino_json)
                                self.send_file(camino_llave)
                                logging.info(f"Archivo JSON y claves enviadas al usuario {self.username}")
                                print("Enviado.")
                        
                else:
                    continue
                
            self.conn.sendall(b"done")
            break
            
        return
    def createConnection(self,client):
        self.conn = ssl.wrap_socket(
            client, 
            server_side=True, 
            certfile=pub_cert, 
            keyfile=priv_key, 
            ssl_version=PROTOCOL)
                    

    def start(self, handle_client):
        while True:
            with socket.create_server((self.SERVIDOR_IP, self.SERVIDOR_PUERTO)) as server:
                print("Esperando al cliente...")
                try:
                    # Accept the connection
                    client, address = server.accept()
                    logging.info(f"Conexión establecida con {address}")

                    # Wrap the socket in an SSL context
                    
                except KeyboardInterrupt:
                    server.close()
                    print("\nInterrupción de teclado detectada, cerrando el servidor.")
                    break
                
                thread = threading.Thread(target=handle_client, args=(self, address))
                thread.start()
                print("Active threads: ", threading.active_count())
                        
