import argparse
import logging
import sys
import os
import json
import bcrypt
import socket
import ssl
import threading
sys.path.append('./sockets')
sys.path.append('./utils')
#import SocketServidor
from sockets import SocketServidor

ruta_secure_key_gen = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','utils')
sys.path.append(ruta_secure_key_gen)
from utils.secure_key_gen import hash_password
from utils.secure_key_gen import check_password
#from secure_key_gen import hash_password
#from secure_key_gen import check_password

NOMBRE_PROYECTO="estrategias_seguridad"
DIRECTORIO_PROYECTO=None
log_directory=''
PROTOCOL = ssl.PROTOCOL_TLS_SERVER


config = json.load(open('config.json'))
class Server:
    SERVIDOR_IP = config['sockets']['host']
    SERVIDOR_PUERTO = config['sockets']['port']
    def start(self, handle_client):
        while True:
            with socket.create_server((self.SERVIDOR_IP, self.SERVIDOR_PUERTO)) as server:
                print("Esperando al cliente...")
                try:
                    # Accept the connection
                    self.client, address = server.accept()
                except KeyboardInterrupt:
                    server.close()
                    print("\nInterrupción de teclado detectada, cerrando el servidor.")
                    break
                
                thread = threading.Thread(target=handle_client, args=(self, address))
                thread.start()
                print("Active threads: ", threading.active_count())


exec_dir = os.getcwd()
if(os.path.basename(exec_dir)==NOMBRE_PROYECTO):
    DIRECTORIO_PROYECTO=exec_dir
else:
    DIRECTORIO_PROYECTO = os.path.dirname(exec_dir)
log_directory=os.path.join(DIRECTORIO_PROYECTO,'logs')


# Verificar si el directorio existe y, si no, crearlo
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configurar el registro con el directorio especificado
log_file_path = os.path.join(log_directory, 'logfile_server.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')


config = json.load(open('config.json'))

register_tag = config['sockets']['tags']['init_comms']['register']
login_tag = config['sockets']['tags']['init_comms']['login']
correct_login_tag = config['sockets']['tags']['response']['correct_login']
incorrect_login_tag = config['sockets']['tags']['response']['incorrect_login']
correct_register_tag = config['sockets']['tags']['response']['correct_register']
incorrect_register_tag = config['sockets']['tags']['response']['incorrect_register']
incorrect_tag = config['sockets']['tags']['response']['incorrect_tag']
malicious_tag = config['sockets']['tags']['init_comms']['malicious']
empty_login_tag = config['sockets']['tags']['response']['empty_login']
send_shared_json = config['sockets']['tags']['init_comms']['receive_shared_json']

server_action_tags = [register_tag, login_tag, malicious_tag]

FORBIDDEN_USERNAMES = ["admin", "root", "superuser", "sysadmin", "system"] + server_action_tags

USERS_FILE = "server/users.json"
PUBLIC_KEYS_FILE = "server/public_keys.json"
MIN_USERNAME_LENGTH = 4
MIN_PASSWORD_LENGTH = 8
INSECURE_MODE = False

def exists_user(username):
    print(f"Comprobando si el usuario {username} existe...")
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as file:
            users = json.load(file)
            # print(users)
            if username in users:
                return True
    return False

def login_user(username, password):
    """
    Comprueba si existe el usuario y si la contrseña es la adecuada.
    Si ambas condiciones se cumplen, devuelve True, de lo contrario, False.

    Args:
        socket (SocketServidor.SocketServidor): El socket del servidor.

    Returns:
        bool: True si el usuario y la contraseña son correctos, de lo contrario, False.
    """

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as file:
            users = json.load(file)
            if username in users and check_password(password, users[username]['password']):
                logging.info(f"Usuario {username} ha iniciado sesion.")
                return True
    return False  

def register_user(username, password, public_key):
    """
    Registra un usuario.

    Args:
        username (str): El nombre de usuario.\n
        password (str): La contraseña.

    Returns:
        bool: True si el usuario ha sido registrado correctamente, de lo contrario, False.
    """
    if username in FORBIDDEN_USERNAMES:
        return False

    if len(username) < MIN_USERNAME_LENGTH or len(password) < MIN_PASSWORD_LENGTH:
        return False

    if exists_user(username):
        return False

    hashed = hash_password(password)

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as file:
            users = json.load(file)
        users[username] = {"password": hashed}
        with open(USERS_FILE, "w") as file:
            # TODO: esto reescribe el fichero entero, buscar alternativa
            json.dump(users, file, indent=4)
    else:
        with open(USERS_FILE, "w") as file:
            users = {username: {"password": hashed}}
            json.dump(users, file, indent=4)

    if os.path.exists(PUBLIC_KEYS_FILE):
        with open(PUBLIC_KEYS_FILE) as file:
            users = json.load(file)
        users[username] = {"public_key": public_key}
        with open(PUBLIC_KEYS_FILE, "w") as file:
            # TODO: esto reescribe el fichero entero, buscar alternativa
            json.dump(users, file, indent=4)
    else:
        with open(PUBLIC_KEYS_FILE, "w") as file:
            users = {username: {"public_key": public_key}}
            json.dump(users, file, indent=4)

    # crear directorio de usuario
    user_folder = os.path.join("server", username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    logging.info(f"Usuario {username} ha sido registrado.")
    return True

def handle_user_logged(serverSocket: SocketServidor.SocketServidor, username):
    """
    Maneja las opciones del usuario una vez que ha iniciado sesion.
    
    Args:
        serverSocket (SocketServidor.SocketServidor): El socket del servidor.\n
        username (str): El nombre del usuario que ha iniciado sesion.
    """
    while serverSocket.conn:
        option = serverSocket.conn.read().decode('utf-8')
        # Recibir archivos del cliente
        if option == serverSocket.ENVIAR:
            logging.info(f"Recibiendo archivos del usuario {username}")
            # receive .zip.enc
            # lo almacena en la carpeta server/usuario/file/
            filename = serverSocket.conn.read().decode('utf-8')
            base_filename = os.path.basename(filename)
            filename_without_ext = base_filename.split('.')[0]
            folder = os.path.join(serverSocket.FOLDER, filename_without_ext)
            serverSocket.receive_one_file(filename, folder, receive_file_name=False) 
            # receive .key.enc 
            serverSocket.wait_shared() # distribuye los archivos a los usuarios a los que se comparten
            # receive .json.enc
            serverSocket.wait_shared()
            serverSocket.conn.sendall("ConfirmacionEsperada".encode('utf-8'))

        # Enviar archivos al cliente
        elif option == serverSocket.RECIBIR:
            logging.info(f"Enviando archivos al usuario {username}")
            serverSocket.send_files_in_folder()

        # Enviar 1 archivo al cliente
        elif option == serverSocket.RECIBIR_FILE:
            logging.info(f"Enviando archivo al usuario {username}")
            serverSocket.send_encoded()

        # Enviar los JSON al cliente
        elif option ==serverSocket.RECIBIR_JSON:
            logging.info(f"Enviando JSON al usuario {username}")
            serverSocket.send_json()

        elif option == serverSocket.RECIBIR_PUBLIC_KEYS:
            logging.info(f"Enviando claves publicas al usuario {username}")
            serverSocket.send_public_keys()
        
        elif option == serverSocket.RECIBIR_JSON_SHARED:
            logging.info(f"Enviando JSON compartido al usuario {username}")
            serverSocket.send_shared_json()
        
        else:
            logging.info("Opcion invalida recibida.")
            break



def handle_malicous(serverSocket: SocketServidor.SocketServidor):
    """
    Maneja las opciones del usuario malicioso.
    """
    while serverSocket.conn:
        option = serverSocket.conn.read().decode('utf-8')
        print(option)
        if option ==serverSocket.RECIBIR_JSON_MALICIOUS and INSECURE_MODE:
            logging.info("Enviando JSON, modo malicioso...")
            serverSocket.send_json_malicious()
            print("Enviado Todo")
        elif option == serverSocket.RECIBIR_FILE and INSECURE_MODE:
            logging.info("Enviando archivo, modo malicioso...")
            serverSocket.send_encoded()
        else:
            break


def handle_client(server: Server, address):
    """
    Maneja las opciones del cliente.
    
    Args:
        serverSocket (SocketServidor.SocketServidor): El socket del servidor.\n
        address (tuple): La dirección del cliente.
    """
    serverSocket = SocketServidor.SocketServidor()
    serverSocket.createConnection(server.client)
    serverSocket.FOLDER="server"
    print(f"{address[0]}:{address[1]} conectado.")
    logging.info(f"{address[0]}:{address[1]} conectado.")
    while serverSocket.conn:
        print("Esperando opción...")
        option = serverSocket.conn.read().decode('utf-8')

        # REGISTRAR USUARIO
        if option == register_tag:
            logging.info("Registrando usuario...")
            print("Registrando usuario...")
            username = serverSocket.conn.read().decode('utf-8')
            password = serverSocket.conn.read().decode('utf-8')
            public_key = serverSocket.conn.read().decode('utf-8')

            user_registered = register_user(username, password, public_key)
            if not user_registered:
                serverSocket.conn.sendall(incorrect_register_tag.encode('utf-8'))
            else:
                serverSocket.conn.sendall(correct_register_tag.encode('utf-8'))
                # Private key
                private_key_folder = os.path.join(serverSocket.FOLDER, username)
                serverSocket.receive_one_file(folder=private_key_folder)

        # INICIAR SESION
        elif option == login_tag:
            logging.info("Iniciando sesion...")
            print("Iniciando sesion...")
            #Esperar por el SocketCliente que envie el usuario y contraseña
            username = serverSocket.conn.read().decode('utf-8')
            password = serverSocket.conn.read().decode('utf-8')

            if username == malicious_tag and not INSECURE_MODE:
                serverSocket.conn.sendall(empty_login_tag.encode('utf-8'))
            if username == malicious_tag and INSECURE_MODE:
                serverSocket.conn.sendall(correct_login_tag.encode('utf-8'))
                handle_malicous(serverSocket)
                break

            # Comprobar si el usuario y la contraseña son correctos
            user_logged = login_user(username, password)
            if not user_logged:
                serverSocket.conn.sendall(incorrect_login_tag.encode('utf-8'))
            else:
                serverSocket.conn.sendall(correct_login_tag.encode('utf-8'))
                serverSocket.send_one_file(os.path.join(serverSocket.FOLDER,username, 'private_key.pem.enc')) # AÑADIDO AHORA
                serverSocket.FOLDER = os.path.join(serverSocket.FOLDER,username)
                serverSocket.username = username
                # Manejar las opciones del usuario
                handle_user_logged(serverSocket,username)
                logging.info(f"Usuario {username} ha cerrado sesion.")
                break
            
        else:
            # TODO: hacer algo si la opción no es válida
            logging.info("Opcion invalida recibida.")
            # serverSocket.conn.sendall(incorrect_tag.encode('utf-8'))
            break
        
    print(f"{address[0]}:{address[1]} desconectado.")
    logging.info(f"{address[0]}:{address[1]} desconectado.")


def main():
    parser = argparse.ArgumentParser(description='Save documents in a secure way')
    parser.add_argument('-u', '--unsafe', help='Use unsafe mode', action='store_true')
    if(parser.parse_args().unsafe):
        global INSECURE_MODE
        INSECURE_MODE = True
        logging.info('Unsafe mode activated :(')
        print("HABILITADO MODO INSEGURO")

    server = Server()
    server.start(handle_client)

if __name__ == "__main__":
    main()