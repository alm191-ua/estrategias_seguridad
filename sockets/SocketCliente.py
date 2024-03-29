import socket
import SocketPadre
import ssl
import hashlib
    
class SocketCliente(SocketPadre.SocketPadre):
    FOLDER = 'files'
    USER=None
    PASSWD=None

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
        pass
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        user = input("Nombre de usuario: ")
        passwd = input("Contraseña: ")
        self.conn.sendall(user.encode('utf-8'))
        # use SHA3 to hash the password, and get a data and cipher keys


    def log_in(self):
        """
        Logs in the server.

        Raises:
            Exception: If no connection has been established.

        """
        pass
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        user = input("Nombre de usuario: ")
        passwd = input("Contraseña: ")
        self.conn.sendall(user.encode('utf-8'))
        self.conn.sendall(passwd.encode('utf-8'))
        response = self.conn.recv(1).decode('utf-8')
        if response == '1':
            self.USER=user
            self.PASSWD=passwd
            print("Log in correcto.")
        else:
            print("Usuario o contraseña incorrectos.")

    def choose_opt(self, number):
        """
        Sends an integer to the server and performs the corresponding action.

        Args:
            number (int): The integer to send.\n
            [1]-> Register a new user\n
            [2]-> Log in\n
            [3]-> send files in the 'files' folder to the server\n
            [4]-> wait for files from the server

        Raises:
            Exception: If no connection has been established.

        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        self.conn.sendall(str(number).encode('utf-8'))
        if number == 1:
            # Register a new user
            self.register_user()
        if number == 2:
            # Log in
            self.log_in()
        if number == 3:
            # Send files in the 'files' folder to the server
            self.send_files_in_folder()
            self.conn.sendall(b"done")
        if number == 4:
            # Wait for files from the server
            self.wait_files()
    
    