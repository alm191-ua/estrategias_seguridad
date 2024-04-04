import socket
import SocketPadre
import ssl
import hashlib
import os
import json
import sys
sys.path.append('utils')
from secure_key_gen import generate_keys
from Cifrado import encrypt_file, decrypt_file


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
# def encrypt_file(input_file, directory,old_key=None,data_key=None)
    def encrypt_key(self, key):
        """
        Encrypts a key using the server's public key.

        Args:
            key (str): The key to encrypt.

        Returns:
            str: The encrypted key.

        """
        file=os.path.basename(key)
        path=os.path.dirname(key)
        print("data_key: ", self.data_key)
        encrypt_file(key, path, data_key=self.data_key.encode('utf-8'))	
    def decrypt_key(self, key):
        """
        Encrypts a key using the server's public key.

        Args:
            key (str): The key to encrypt.

        Returns:
            str: The encrypted key.

        """

        print("data_key: ", self.data_key)
        decrypt_file(key, data_key=self.data_key.encode('utf-8'))	



    def connect(self):
        # Crear un socket de tipo TCP/IP.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # wrap_socket() se encarga de la encriptación de los datos
        # mediante SSL con los certificados proporcionados.
        self.conn = ssl.wrap_socket(
            sock,
            ca_certs='certificates/certificate.pem')
        
        self.conn.connect((self.SERVIDOR_IP, self.SERVIDOR_PUERTO))

        print("Conectado al servidor.")

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
        if number == 4:
            self.conn.sendall(self.RECIBIR.encode('utf-8'))
            # Wait for files from the server
            self.wait_files()
    