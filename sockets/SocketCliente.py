import socket
import SocketPadre
import ssl
import os
import json
import sys
import logging
import zipfile
#Me daba error el import de secure_key_gen, asi que lo importe de esta manera
ruta_secure_key_gen = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','utils')
sys.path.append(ruta_secure_key_gen)
from utils.secure_key_gen import generate_keys
##############################################
import Cifrado 
import GetDataUploaded


config = json.load(open('config.json'))
login_tag = config['sockets']['tags']['init_comms']['login']
register_tag = config['sockets']['tags']['init_comms']['register']
correct_login_tag = config['sockets']['tags']['response']['correct_login']
correct_register_tag = config['sockets']['tags']['response']['correct_register']
malicious_tag = config['sockets']['tags']['init_comms']['malicious']
empty_login_tag = config['sockets']['tags']['response']['empty_login']

class SocketCliente(SocketPadre.SocketPadre):
    FOLDER = 'files'
    username=''
    password=''
    data_key=''
    MALICIOSO=False
    def send_encrypted_files(self, archivos, titulo, descripcion):
        """
        Sends files to the server.
        Args:
            archivos (list): The list of files to send.
            titulo (str): The title of the package.
            descripcion (str): The description of the package.
        """
        try:
            # Verificar si la conexión está establecida
            if self.conn is None:
                raise Exception("La conexión con el servidor no está establecida.")
            
            self.conn.sendall(self.ENVIAR.encode('utf-8'))
            path = Cifrado.ZipAndEncryptFile(archivos, titulo, descripcion)
            self.encrypt_key(path)
            file = str.replace(path, self.FORMATO_LLAVE, self.FORMATO_ARCHIVO_ENCRIPTADO)
            json_file = str.replace(path, self.FORMATO_LLAVE, self.FORMATO_JSON)
            key = path + self.FORMATO_ENCRIPTADO
            self.send_file(file)
            self.send_file(key)
            self.send_file(json_file)
            self.decrypt_key(key)
            self.conn.sendall(b"done")
            
            respuesta = self.conn.recv(1024)
            if respuesta.decode('utf-8') != "ConfirmacionEsperada":
                raise Exception("La confirmación del servidor no es la esperada.")
            
        except Exception as e:
            print(f"Error al enviar archivos: {e}")
            
    #Tengo que arreglarlo       
    def send_files_in_folder(self):
        """
        Envía los archivos de una carpeta al servidor, organizándolos por nombre de usuario.
        """
        try:
            if not self.conn:
                raise Exception("La conexión con el servidor no está establecida.")

            source_folder = os.path.join(self.FOLDER, self.username)

            zip_path = self.zip_files(source_folder)

            filesize = os.path.getsize(zip_path)

            self.conn.sendall(f"{os.path.basename(zip_path)}{self.SEPARATOR}{filesize}".encode())

            # Enviar el archivo ZIP
            with open(zip_path, 'rb') as f:
                while True:
                    bytes_read = f.read(self.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    self.conn.sendall(bytes_read)
            
            print("Archivos enviados correctamente.")
        except Exception as e:
            print(f"Error al enviar archivos: {e}")



    def decrypt_files_JSON(self,encrypted_files, json_filename,old_key=None):
        """
        Desencripta los archivos listados en un documento JSON.

        Args:
            archivos_encriptados (list): Lista de representaciones base64 de los archivos encriptados.
            nombre_archivo_json (str): Ruta al documento JSON que contiene la información de los archivos.
            clave_anterior (bytes, opcional): Clave anterior si se desea reencriptar (predeterminado: None).

        Returns:
            list: Lista de los archivos desencriptados en formato de bytes.
        """
        decrypted_files = []
        if self.MALICIOSO:
            for password in Cifrado.UNSAFE_PASSWORDS:
                key = bytes(password.ljust(Cifrado.KEY_SIZE, '0'), 'utf-8')
                try:
                    decrypted_files = Cifrado.try_decrypt_files_JSON(encrypted_files, key)
                    print("Contraseña encontrada:", password)
                    return decrypted_files
                except ValueError:
                    continue
            else:
                raise ValueError("No se pudo encontrar la contraseña correcta en modo inseguro.")
        else:
            key = Cifrado.key_to_use(old_key, json_filename)
            decrypted_files=Cifrado.try_decrypt_files_JSON(encrypted_files, key)
            return decrypted_files
    
    def get_files_in_zip(self,file):
        """
        Obtiene los archivos en un documento cifrado a partir de la información del JSON.
        """
        directorio=os.path.join(Cifrado.DIRECTORIO_PROYECTO,self.FOLDER)
        if not directorio:
            return []
        data = GetDataUploaded.getDataFromJSON(file, directorio)
        path=os.path.join(directorio,file,file)
        filesDesencrypted=self.decrypt_files_JSON(data['files'],path+".json")
        all_files =filesDesencrypted
        return all_files
    
    def UnzipFolder(self,directorio_file):
        """
        Descomprime un archivo ZIP en el directorio de archivos.
        """
        if not Cifrado.DIRECTORIO_PROYECTO:
            Cifrado.buscar_proyecto()
        if not Cifrado.DIRECTORIO_PROYECTO:
            logging.error("No se ha encontrado el proyecto")
            # print("No se ha encontrado el proyecto")
            return None
        # Construir la ruta del archivo ZIP
        directorio = os.path.join(Cifrado.DIRECTORIO_PROYECTO, self.FOLDER, directorio_file)
        archivo = os.path.join(directorio, directorio_file + ".zip.enc")

        # Descomprimir el archivo ZIP
        self.UnZipFiles(archivo)
        directorio = os.path.join(directorio,directorio_file)
        return directorio
    
    def UnZipFiles(self,file,target_folder=None):
        """
        Extrae y desencripta un paquete de documentos.

        Args:
            archivo_paquete (str): Ruta al archivo del paquete encriptado.
            carpeta_destino (str, opcional): Carpeta de destino para la extracción.
                                            Predeterminado al directorio del paquete.

        Returns:
            bool: True si la extracción y desencriptación fueron exitosas, False si no.
        """
        if not target_folder:
                target_folder=os.path.dirname(file)
        try:
            fileDesencrypted=file.replace(self.FORMATO_ENCRIPTADO,'')
            fileWithNoFormat=fileDesencrypted.replace(self.FORMATO_COMPRESION,'')
            Folder=os.path.basename(fileWithNoFormat)
            directorio_Final=os.path.join(target_folder,Folder)
            if self.MALICIOSO:
                key=Cifrado.decrypt_file_unsafe(file, directorio_Final)
            else:
                key=Cifrado.decrypt_file(file)
                os.makedirs(directorio_Final, exist_ok=True)  # Crea la carpeta objetivo si no existe
                with zipfile.ZipFile(fileDesencrypted, 'r') as zip_ref:
                    zip_ref.extractall(directorio_Final)
                    logging.info('Files extracted')
            Cifrado.encrypt_file(fileWithNoFormat,'',key)
            return True
        except Exception as e:
            logging.error(f'Error al extraer los archivos: {e}')
            return False


    def get_file(self, filename):
        """
        gets a file to the server.

        Args:
            filename (str): The name of the file to send.

        """
        files = os.listdir(self.FOLDER)
        for fileId in files:
            if fileId == filename:
                file_folder_path = os.path.join(self.FOLDER, fileId)
                files_path = os.path.join(file_folder_path, fileId)
                file_path = files_path + self.FORMATO_ARCHIVO_ENCRIPTADO
                if os.path.exists(file_path):
                    break
                else:
                    self.conn.sendall(self.RECIBIR_FILE.encode('utf-8'))
                    self.conn.sendall(filename.encode('utf-8'))
                    self.wait_files()
                    print("Archivo recibido.")


    def encrypt_key(self, key):
        """
        Encrypts a key using the server's public key.

        Args:
            key (str): The key to encrypt.
        """
        file=os.path.basename(key)
        path=os.path.dirname(key)
        Cifrado.encrypt_file(key, path, data_key=self.data_key.encode('utf-8'))	
    
    def decrypt_key(self, key):
        """
        Encrypts a key using the server's public key.

        Args:
            key (str): The key to encrypt.
        """
        print("data_key: ", self.data_key)
        Cifrado.decrypt_file(key, data_key=self.data_key.encode('utf-8'))	



    def connect(self):
        try:
            # Crear un socket de tipo TCP/IP.
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # wrap_socket() se encarga de la encriptación de los datos
            # mediante SSL con los certificados proporcionados.
            self.conn = ssl.wrap_socket(
                sock,
                ca_certs='certificates/certificate.pem')
            
            self.conn.connect((self.SERVIDOR_IP, self.SERVIDOR_PUERTO))

            print("Conectado al servidor.")
        except Exception as e:
            print(f"Error al conectar al servidor: {e}")
            self.conn = None
            return

    def disconnect(self):
        if self.conn:
            self.conn.sendall(b"disc")
            self.conn.close()
            print("Conexión cerrada.")
    
    def register_user(self):
        """
        Registers a new user in the server.

        Raises:
            Exception: If no connection has been established.
            ValueError: If username or password are empty.
        Returns:
            bool: True if user was successfully registered, False otherwise.
        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")

        if not self.username or not self.password:
            raise ValueError("El nombre de usuario y la contraseña no pueden estar vacíos.")

        self.conn.sendall(register_tag.encode('utf-8'))
        self.conn.sendall(self.username.encode('utf-8'))

        # Genera y envía la clave derivada de la contraseña
        self.data_key, login_key = generate_keys(self.password)
        self.conn.sendall(login_key.encode('utf-8'))

        response = self.conn.recv(1024).decode('utf-8')
        print("response: ", response)
        if response == correct_register_tag:
            print("Usuario registrado correctamente.")
            return True
        else:
            print("No se pudo registrar el usuario. El usuario ya existe o hubo un error.")
            return False



    def log_in(self):
        """
        Logs in the server.

        Raises:
            Exception: If no connection has been established.

        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        
        if self.username == '' or self.password == '':
            self.MALICIOSO=True
        else:
            self.MALICIOSO=False
        #     return
        self.conn.sendall(login_tag.encode('utf-8'))
        
        
        if self.MALICIOSO:
            print("Enviando nombre de inicio de sesión...")
            self.conn.sendall(malicious_tag.encode('utf-8'))
            self.conn.sendall(malicious_tag.encode('utf-8'))
        else:
            self.conn.sendall(self.username.encode('utf-8'))
            # use SHA3 to hash the password, and get a data and cipher keys
            self.data_key, login_key = generate_keys(self.password)
            self.conn.sendall(login_key.encode('utf-8'))

        response = self.conn.read().decode('utf-8')
        if response == correct_login_tag:
            print("Log in correcto.")
            return True
        if response == empty_login_tag:
            print("No se ha iniciado sesión.")
            return False
        else:
            print("Usuario o contraseña incorrectos.")
            return False

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
        formato_encrypted = self.FORMATO_LLAVE+self.FORMATO_ENCRIPTADO
        print("filename: ", os.path.basename(filename))
        nombre=os.path.basename(filename)
        division = nombre.split('.', 1)
        if(len(division)>1):
            division[1]='.'+division[1]
            if division[1]==formato_encrypted:
                    self.decrypt_key(filename)

        print("Archivo recibido correctamente.")

    def get_json_info(self, path):
        """
        Gets the information of the JSON file.

        Args:
            path (str): The path to the JSON file.

        Returns:
            tuple: The title, description, time, and files of the JSON file.
        """
        with open(path) as file:
            data = json.load(file)
        # get title
        title = data['title']
        description = data['description']
        time = data['time']
        files = data['files']
        decrypted_files = self.decrypt_files_JSON(files, path)
        return title, description, time, decrypted_files
    
    def print_json_info(self, path):
        """
        Prints the information of the JSON file.

        Args:
            path (str): The path to the JSON file.
        """
        title, description, time, files = self.get_json_info(path)
        print(f"Title: {title}")
        print(f"Description: {description}")
        print(f"Time: {time}")
        print("Files:")
        for file in files:
            print(f"\t{file}")

    def choose_opt(self, number):
        """
        Sends an integer to the server and performs the corresponding action.

        Args:
            number (int): The integer to send.\n
            [1]-> Register a new user\n
            [2]-> Log in\n

        Raises:
            Exception: If no connection has been established.

        """
        # [3]-> send files in the 'files' folder to the server\n
        # [4]-> wait for files from the server
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        
        # self.conn.sendall(str(number).encode('utf-8'))
        if number == 1:
            # Register a new user
            user_registered = self.register_user()
            return user_registered
            # if user_registered:
            #     self.log_in()
            
        if number == 2:
            print("Iniciando sesión...")
            # Log in
            user_logged = self.log_in()
            return user_logged
            # if user_logged:
            #     # TODO: implementar acciones que puede realizar un usuario logueado
            #     pass
        if number == 3:
            # Send files in the 'files' folder to the server
            self.conn.sendall(self.ENVIAR.encode('utf-8'))
            self.send_files_in_folder()
        if number == 4 :
            self.conn.sendall(self.RECIBIR.encode('utf-8'))
            # Wait for files from the server
            self.wait_files()
        if number == 5:
            if self.username == '' or self.password == '':
                print("No se ha iniciado sesión.")
                self.conn.sendall(self.RECIBIR_JSON_MALICIOUS.encode('utf-8'))
            else:
                print('Recibiendo JSON')
                self.conn.sendall(self.RECIBIR_JSON.encode('utf-8'))
            self.wait_files()
            
    