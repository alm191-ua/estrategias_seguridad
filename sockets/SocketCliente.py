import socket
import SocketPadre
import ssl
import os
import json
import sys
import logging
import zipfile
import shutil
#Me daba error el import de secure_key_gen, asi que lo importe de esta manera
ruta_secure_key_gen = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','utils')
sys.path.append(ruta_secure_key_gen)
from utils.secure_key_gen import generate_keys
from utils.secure_key_gen import generate_pub_priv_keys
##############################################
import Cifrado 
import GetDataUploaded

# parámetros obtenidos del archivo de configuración
config = json.load(open('config.json'))
login_tag = config['sockets']['tags']['init_comms']['login']
register_tag = config['sockets']['tags']['init_comms']['register']
correct_login_tag = config['sockets']['tags']['response']['correct_login']
correct_register_tag = config['sockets']['tags']['response']['correct_register']
incorrect_register_tag = config['sockets']['tags']['response']['incorrect_register']
malicious_tag = config['sockets']['tags']['init_comms']['malicious']
empty_login_tag = config['sockets']['tags']['response']['empty_login']
enable_otp_tag = config['sockets']['tags']['init_comms']['enable_otp']
disable_otp_tag = config['sockets']['tags']['init_comms']['disable_otp']

class SocketCliente(SocketPadre.SocketPadre):
    """
    Clase que representa el socket del cliente.
    Se encarga del envío y recepción de archivos y mensajes al servidor.
    """
    FOLDER = 'files'
    SHARED_FOLDER = 'shared'
    username=''
    password=''
    data_key=''
    otp = True
    uri = ''
    MALICIOSO=False
    NAME_PREFIX  = 'File'
    PRIVATE_KEY=''

    def create_folder_4_new_file(self, filename,get_shared=False):
        """
        Crea una carpeta para un nuevo archivo.
        """
        filename = filename.split(".")[0]
        if get_shared:
            dir=os.path.join(self.FOLDER,self.SHARED_FOLDER)
            if not os.path.exists(dir):
                os.makedirs(dir)
            path=os.path.join(dir, filename)
        else:
            path=os.path.join(self.FOLDER, filename)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    def send_encrypted_files(self, archivos, titulo, descripcion,author, users=[], public_keys=[]):

        """
        Sends files to the server.
        Args:
            archivos (list): The list of files to send.
            titulo (str): The title of the package.
            descripcion (str): The description of the package.
        """

        print("--------------------")
        print("ENVIANDO ARCHIVOS")
        print("Archivos: ", archivos)
        print("Titulo: ", titulo)
        print("Descripcion: ", descripcion)
        print("Author: ", author)
        print("Users: ", users)
        print("Public keys: ", public_keys)
        print("--------------------")

        try:
            # Verificar si la conexión está establecida
            if self.conn is None:
                raise Exception("La conexión con el servidor no está establecida.")
            
            # Comunicar al servidor que se enviarán archivos
            self.conn.sendall(self.ENVIAR.encode('utf-8'))

            # Generar un identificador único para el documento
            doc_id = Cifrado.generate_unique_id()
            doc_id = self.NAME_PREFIX + doc_id
            # Crear los directorios necesarios
            directory = Cifrado.Create_Dirs(doc_id, self.FOLDER)
            # Comprimir los archivos
            zip_file_path = Cifrado.ZipFiles(directory, archivos, doc_id)

            # Generar y guardar la clave del archivo
            file_key = Cifrado.generate_and_save_key(doc_id, directory)
            # Cifrar el archivo comprimido
            encrypted_file_path = Cifrado.encrypt_single_file(zip_file_path, file_key, directory)

            # print("EEEEEEEEEEEEEEEE")

            # Cifrar el fichero con la clave publica de cada usuario compartido
            file_key_path = os.path.join(directory, doc_id + self.FORMATO_LLAVE)
            file_key_paths = []
            # print("Users: ", users)
            # print("Public keys: ", public_keys)
            for user, public_key in zip(users, public_keys):
                new_key_path = os.path.join(directory, doc_id + '_' + user + self.FORMATO_LLAVE + self.FORMATO_ENCRIPTADO)
                encrypted_file_key_path = Cifrado.encrypt_file_asimetric(file_key_path, public_key, new_key_path, change_name=True)
                file_key_paths.append(encrypted_file_key_path)

            # print("Algo")

            # Crear los ficheros json con los ficheros cifrados para cada usuario compartido
            json_files_paths = []
            for user, public_key in zip(users, public_keys):
                new_json_name = doc_id + '_' + user + '.json'
                new_json_path = Cifrado.create_and_save_document_json(directory, doc_id, titulo, descripcion, archivos, author, new_json_name)
                # print("AAAAAAAAAAAAAA")
                Cifrado.encrypt_json_filenames(new_json_path, file_key)
                # print("BBBBBBBBBBBBBB")
                json_files_paths.append(new_json_path)

            # archivos a enviar:
            # 1. archivos cifrados (id.zip.enc)
            # 2. claves cifradas (id_user1.key.enc, id_user2.key.enc, ...)
            # 3. json cifrados (id_user1.json, id_user2.json, ...)
            # en el servidor se distribuirán los archivos a los usuarios correspondientes
            # una clave y un json para el usuario que envía el documento
            # y un json y clave para cada usuario compartido

            

            # Enviar los archivos al servidor
            self.send_file(encrypted_file_path)
            self.conn.sendall(b"done")
            # self.send_one_file(encrypted_file_path)
            
            for file in file_key_paths:
                self.send_one_file(file)
            self.conn.sendall(b"done")

            for file in json_files_paths:
                self.send_one_file(file)
            self.conn.sendall(b"done")
            

            # Comprimir y cifrar los archivos
            # path = Cifrado.ZipAndEncryptFile(archivos, titulo, descripcion)
            # file = str.replace(path, self.FORMATO_LLAVE, self.FORMATO_ARCHIVO_ENCRIPTADO)
            # json_file = str.replace(path, self.FORMATO_LLAVE, self.FORMATO_JSON)
            # if not users:
            #     self.encrypt_key(path)
            #     key = path + self.FORMATO_ENCRIPTADO
            # else:
            #     keys_files = self.encrypt_multiple_keys(path, users, public_keys)

            # # Enviar los archivos al servidor
            # self.send_file(file)
            # self.send_file(key)
            # self.send_file(json_file)
            # self.decrypt_key(key)
            
            # Esperar confirmación del servidor
            respuesta = self.conn.read().decode('utf-8')
            if respuesta != "ConfirmacionEsperada":
                raise Exception("La confirmación del servidor no es la esperada.")
            
        except Exception as e:
            print(f"Error al enviar archivos: {e}")


    def encrypt_multiple_keys(self, path, users, public_keys):
        """
        Encrypts the key with the public keys of the users.

        Args:
            path (str): The path to the key file.
            users (list): The list of users.
            public_keys (list): The list of public keys.

        Returns:
            list: The list of key files.
        """
        keys_files = []
        for user, public_key in zip(users, public_keys):
            key_file = path + '_' + user + self.FORMATO_ENCRIPTADO
            Cifrado.encrypt_single_file(path, public_key, key_file, True)
            keys_files.append(key_file)
        return keys_files

    #TODO: Tengo que arreglarlo, aunque no sé el qué :(      
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



    def decrypt_files_JSON(self, encrypted_files, json_filename, old_key=None):
        """
        Desencripta los archivos listados en un documento JSON.

        Args:
            encrypted_files (list): Lista de representaciones base64 de los archivos encriptados.
            json_filename (str): Ruta al documento JSON que contiene la información de los archivos.
            old_key (bytes, opcional): Clave anterior si se desea reencriptar (predeterminado: None).

        Returns:
            list: Lista de los archivos desencriptados en formato de bytes.
        """
        decrypted_files = []
        if self.MALICIOSO:
            # trata de descifrar los archivos con contraseñas inseguras
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
    
    def get_files_in_zip(self, file,shared=False):
        """
        Obtiene los archivos en un documento cifrado a partir de la información del JSON.

        Args:
            file (str): Nombre del documento.

        Returns:
            list: Lista de los archivos desencriptados.
        """
        directorio=os.path.join(Cifrado.DIRECTORIO_PROYECTO,self.FOLDER)
        if shared:
            directorio=os.path.join(directorio,self.SHARED_FOLDER)
        print(directorio)
        if not directorio:
            return []
        data = GetDataUploaded.getDataFromJSON(file, directorio)
        path = os.path.join(directorio,file,file)
        filesDesencrypted = self.decrypt_files_JSON(data['files'],path+".json")
        print('HECHO')
        all_files = filesDesencrypted
        return all_files
    
    def UnzipFolder(self, directorio_file,shared=False):
        """
        Descomprime un archivo ZIP en el directorio de archivos.

        Args:
            directorio_file (str): Nombre del archivo a descomprimir.
        """
        if not Cifrado.DIRECTORIO_PROYECTO:
            Cifrado.buscar_proyecto()
        if not Cifrado.DIRECTORIO_PROYECTO:
            logging.error("No se ha encontrado el proyecto")
            # print("No se ha encontrado el proyecto")
            return None
        # Construir la ruta del archivo ZIP
        if shared:
            directorio = os.path.join(Cifrado.DIRECTORIO_PROYECTO, self.FOLDER, self.SHARED_FOLDER, directorio_file)
        else:
            directorio = os.path.join(Cifrado.DIRECTORIO_PROYECTO, self.FOLDER, directorio_file)
        archivo = os.path.join(directorio, directorio_file + ".zip.enc")
        print(archivo)

        # Descomprimir el archivo ZIP
        self.UnZipFiles(archivo)
        directorio = os.path.join(directorio,directorio_file)
        return directorio
    
    def UnZipFiles(self, file, target_folder=None):
        """
        Extrae y desencripta un paquete de documentos.

        Args:
            file (str): Ruta al archivo del paquete encriptado.
            target_folder (str, opcional): Carpeta de destino para la extracción.
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


    def get_file(self, filename,autor):
        """
        gets a document from the server.

        Args:
            filename (str): The name of the file to receive.

        """
        shared=False
        if autor!=self.username and not self.MALICIOSO:
            shared=True
        files = os.listdir(self.FOLDER)
        if shared:
            files = os.listdir(os.path.join(self.FOLDER,self.SHARED_FOLDER))
            for fileId in files:
                if fileId == autor:
                    file_folder_path = os.path.join(files, fileId,filename)
                    files_path = os.path.join(file_folder_path, filename)
                    file_path = files_path + self.FORMATO_ARCHIVO_ENCRIPTADO
                    if os.path.exists(file_path):
                        # En caso de que el archivo ya exista, no se descarga
                        break
                    else:
                        self.conn.sendall(self.RECIBIR_FILE.encode('utf-8'))
                        self.conn.sendall(filename.encode('utf-8'))
                        self.conn.sendall(autor.encode('utf-8'))

                        self.wait_files(shared)
                        print("Archivo recibido.")
        for fileId in files:
            if fileId == filename:
                file_folder_path = os.path.join(self.FOLDER, fileId)
                files_path = os.path.join(file_folder_path, fileId)
                file_path = files_path + self.FORMATO_ARCHIVO_ENCRIPTADO
                if os.path.exists(file_path):
                    # En caso de que el archivo ya exista, no se descarga
                    break
                else:
                    self.conn.sendall(self.RECIBIR_FILE.encode('utf-8'))
                    self.conn.sendall(filename.encode('utf-8'))
                    self.conn.sendall(autor.encode('utf-8'))

                    self.wait_files(shared)
                    print("Archivo recibido.")


    def get_public_keys(self):
        """
        Gets the file with the usernames and public keys of the users.

        Returns:
            list: The list of usernames.
            list: The list of public keys.
        """
        self.conn.sendall(self.RECIBIR_PUBLIC_KEYS.encode('utf-8'))
        print("Recibiendo archivo de claves públicas...")
        print("FOlder: ", self.FOLDER)
        self.receive_one_file() # lo almacena en la carpeta files_username/
        usuarios = []
        claves_publicas = []
        path = os.path.join(self.FOLDER, "public_keys.json")
        with open(path) as file:
            data = json.load(file)
        for user, data in data.items():
            usuarios.append(user)
            claves_publicas.append(data['public_key'])
        return usuarios, claves_publicas

    def decrypt_private_key(self, private_key_path):
        """
        Decrypts the private key with the public key of the user.

        Args:
            private_key (str): The public key of the user.

        Returns:
            str: The private key.
        """
        Cifrado.decrypt_file(private_key_path, data_key=self.data_key.encode('utf-8'))
        private_key_path = private_key_path.replace(self.FORMATO_ENCRIPTADO, '')
        with open(private_key_path, 'rb') as f:
            private_key_data = f.read()	
        self.PRIVATE_KEY = private_key_data
        return private_key_path


    def encrypt_key(self, key):
        """
        Encrypts a key using the user data key.

        Args:
            key (str): The key to encrypt.
        """
        file=os.path.basename(key)
        path=os.path.dirname(key)
        # Cifrado.encrypt_file(key, path, data_key=self.data_key.encode('utf-8'))
        Cifrado.encrypt_single_file(file_path=key, key=self.data_key.encode('utf-8'), target_directory=path)	
    
    def decrypt_key(self, path_key):
        """
        Decrypts a key using the user data key.

        Args:
            key (str): The key to encrypt.
        """
        taget_dir=os.path.dirname(path_key)
        Cifrado.decrypt_file_asimetric(path_key,self.PRIVATE_KEY,taget_dir)	
        os.remove(path_key)       



    def connect(self):
        """
        Connects to the server.
        """
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
        """
        Closes the connection with the server.
        """
        if self.conn:
            self.conn.sendall(b"disc")
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
            print("Conexión cerrada.")
    
    def register_user(self):
        """
        Registers a new user in the server.

        Raises:
            ConnectionError: If no connection has been established.
            ValueError: If username or password are empty.
        Returns:
            bool: True if user was successfully registered, False otherwise.
        """
        if not self.conn:
            raise ConnectionError("No se ha establecido una conexión.")

        if not self.username or not self.password:
            raise ValueError("El nombre de usuario y la contraseña no pueden estar vacíos.")

        self.conn.sendall(register_tag.encode('utf-8'))
        self.conn.sendall(self.username.encode('utf-8'))

        # Genera la clave de login derivada de la contraseña
        self.data_key, login_key = generate_keys(self.password)
        # genera las claves pública y privada
        public_key, private_key = generate_pub_priv_keys()

        # envía la clave de login y la clave pública
        self.conn.sendall(login_key.encode('utf-8'))
        self.conn.sendall(public_key)

        # send otp option
        if self.otp:
            self.conn.sendall(enable_otp_tag.encode('utf-8'))
        else:
            self.conn.sendall(disable_otp_tag.encode('utf-8'))

        response = self.conn.read().decode('utf-8')
        print("response: ", response)

        if response != incorrect_register_tag:
            if self.otp:
                self.uri = response

            self.FOLDER=self.FOLDER+'_'+self.username
            # save private key file
            # create self.FOLDER if not exist
            if not os.path.exists(self.FOLDER):
                os.makedirs(self.FOLDER)
            with open(os.path.join(self.FOLDER, 'private_key.pem'), 'wb') as f:
                f.write(private_key)
            
            # encrypt private key with data_key
            Cifrado.encrypt_single_file(os.path.join(self.FOLDER, 'private_key.pem'), self.data_key.encode('utf-8'), self.FOLDER)
            # send private_key.pem.enc file to server
            self.send_one_file(os.path.join(self.FOLDER, 'private_key.pem.enc'))

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
            # enviar como nombre de usuario y contraseña el tag de cliente malicioso
            self.conn.sendall(malicious_tag.encode('utf-8'))
            self.conn.sendall(malicious_tag.encode('utf-8'))
        else:
            # send username
            self.conn.sendall(self.username.encode('utf-8'))
            # get the data and cipher keys
            self.data_key, login_key = generate_keys(self.password)
            # send login key
            self.conn.sendall(login_key.encode('utf-8'))

                
            # private_key_folder = os.path.join(serverSocket.FOLDER, username)
            # serverSocket.receive_one_file(folder=private_key_folder)

        response = self.conn.read().decode('utf-8')
        if response == correct_login_tag:
            print("Log in correcto.")
            self.FOLDER=self.FOLDER+'_'+self.username
            print(self.MALICIOSO)
            if not os.path.exists(self.FOLDER):
                    os.makedirs(self.FOLDER)
            if not self.MALICIOSO:
                private_key_folder=self.receive_one_file(folder=self.FOLDER)
                self.decrypt_private_key(private_key_folder)
            
            return True
        if response == empty_login_tag:
            print("No se ha iniciado sesión.")
            return False
        else:
            print("Usuario o contraseña incorrectos.")
            return False
        
    def check_otp(self, otp):
        if otp == '':
            return False
        # send otp
        self.conn.sendall(otp.encode('utf-8'))
        response = self.conn.read().decode('utf-8')
        if response == correct_login_tag:
            print("Log in correcto.")
            return True
        else:
            print("OTP incorrecto.")
            return False


    def receive_file(self,shared_file=False):
        """
        Receives a file from the server.
        """
        print("Esperando el tamaño del nombre del archivo...")
        try:
            fmt = "<L"
            NameSize = self.receive_size(fmt)
            if NameSize == 0:
                raise ValueError("Everything sent correctly")
            file = self.conn.recv(NameSize)
            filename = file.decode('utf-8')
            print(f"Nombre de archivo recibido: {filename}")
            if filename == "done":
                raise ValueError("Everything sent correctly")
            fmt="<Q"
            
            filesize = self.receive_size(fmt)
            self.buscar_server_folder()
            if shared_file:
                folder = self.create_folder_4_new_file(filename,True)
            else:
                folder = self.create_folder_4_new_file(filename)
            print("folder: ", folder)
            filename = os.path.join(folder, filename)
        except ConnectionResetError:
            raise ConnectionResetError("Conexión cerrada por el cliente.")

        print("Recibiendo archivo...")
        received_bytes = 0
        with open(filename, "wb") as f:
            # receive the file divided in chunks of 2048 bytes
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
            [3]-> Send files in the 'files' folder to the server\n
            [4]-> Receive all files from the server (from the user logged)\n
            [5]-> Receive a JSON file from the server\n

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
            if self.MALICIOSO:
                print("No se ha iniciado sesión.")
                self.conn.sendall(self.RECIBIR_JSON_MALICIOUS.encode('utf-8'))
            else:
                print('Recibiendo JSON')
                self.conn.sendall(self.RECIBIR_JSON.encode('utf-8'))
            self.wait_files()
        if number == 6:
            self.conn.sendall(self.RECIBIR_JSON_SHARED.encode('utf-8'))
            self.wait_files(sharing=True)
    