import socket
import SocketPadre
import ssl

class SocketCliente(SocketPadre.SocketPadre):
    FOLDER = 'files'

    def connect(self):
        # Crear un socket de tipo TCP/IP.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    



    def choose_opt(self, number):
        """
        Sends an integer to the server and performs the corresponding action.

        Args:
            number (int): The integer to send.
            [1]-> send files in the 'files' folder to the server
            [2]-> wait for files from the server

        Raises:
            Exception: If no connection has been established.

        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        self.conn.sendall(str(number).encode('utf-8'))
        if number == 1:
            # Send files in the 'files' folder to the server
            self.send_files_in_folder()
            self.conn.sendall(b"done")
        if number == 2:
            # Wait for files from the server
            self.wait_files()
    
    