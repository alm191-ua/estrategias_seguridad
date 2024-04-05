import socket
import SocketPadre
import ssl
import hashlib
import os
import json
import sys
sys.path.append('utils')
from secure_key_gen import generate_keys
import Cifrado 


config = json.load(open('config.json'))
login_tag = config['sockets']['tags']['init_comms']['login']
register_tag = config['sockets']['tags']['init_comms']['register']
correct_login_tag = config['sockets']['tags']['response']['correct_login']
correct_register_tag = config['sockets']['tags']['response']['correct_register']

class SocketCliente(SocketPadre.SocketPadre):
    FOLDER = 'files'
    username=''
    password=''
    data_key=''
    MALICIOSO=False
    def ZipAndEncryptFile(self, archivos, titulo, descripcion):
        """
        Sends files to the server.
        Args:
            archivos (list): The list of files to send.\n
            titulo (str): The title of the package.\n
            descripcion (str): The description of the package.
        
        """
        self.conn.sendall(self.ENVIAR.encode('utf-8'))
        path = Cifrado.ZipAndEncryptFile(archivos, titulo, descripcion)
        self.encrypt_key(path)
        file = str.replace(path, self.FORMATO_LLAVE,self.FORMATO_ARCHIVO_ENCRIPTADO)
        json_file = str.replace(path, self.FORMATO_LLAVE,self.FORMATO_JSON)
        key = path+self.FORMATO_ENCRIPTADO
        self.send_file(file)
        self.send_file(key)
        self.send_file(json_file)
        self.decrypt_key(key)
        self.conn.sendall(b"done")
    
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
                print("file_path: ", file_path)
                if os.path.exists(file_path):
                    break
                else:
                    self.conn.sendall(self.RECIBIR_FILE.encode('utf-8'))
                    print("Nombre enviado.")
                    self.conn.sendall(filename.encode('utf-8'))
                    print("Nombre enviado.")
                    self.receive_file()
                    print("Archivo recibido.")
        return


        
        

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

        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        self.conn.sendall(register_tag.encode('utf-8'))
        self.conn.sendall(self.username.encode('utf-8'))

        # use SHA3 to hash the password, and get a data and cipher keys
        self.data_key, login_key = generate_keys(self.password)
        self.conn.sendall(login_key.encode('utf-8'))

        response = self.conn.read().decode('utf-8')
        if response == correct_register_tag:
            print("Usuario registrado correctamente.")
            return True
        else:
            print("El usuario ya existe.")
            return False


    def log_in(self):
        """
        Logs in the server.

        Raises:
            Exception: If no connection has been established.

        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        
        self.conn.sendall(login_tag.encode('utf-8'))
        self.conn.sendall(self.username.encode('utf-8'))

        # use SHA3 to hash the password, and get a data and cipher keys
        self.data_key, login_key = generate_keys(self.password)
        self.conn.sendall(login_key.encode('utf-8'))

        response = self.conn.read().decode('utf-8')
        if response == correct_login_tag:
            print("Log in correcto.")
            return True
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
                print('Enviando JSON')
                self.conn.sendall(self.RECIBIR_JSON.encode('utf-8'))
            self.wait_files()
            
    