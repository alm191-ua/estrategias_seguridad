import argparse
import logging
import sys
import os
import json
import bcrypt
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

USERS_FILE = "server/users.json"
MIN_USERNAME_LENGTH = 4
MIN_PASSWORD_LENGTH = 8
INSECURE_MODE=False

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
                logging.info(f"Usuario {username} ha iniciado sesión.")
                return True
    return False  

def register_user(username, password):
    """
    Registra un usuario.

    Args:
        username (str): El nombre de usuario.\n
        password (str): La contraseña.

    Returns:
        bool: True si el usuario ha sido registrado correctamente, de lo contrario, False.
    """
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

    logging.info(f"Usuario {username} ha sido registrado.")
    return True

def handle_user_logged(serverSocket: SocketServidor.SocketServidor,username):
    while serverSocket.conn:
        option = serverSocket.conn.read().decode('utf-8')
        if option == serverSocket.ENVIAR:
            logging.info("Recibiendo archivos...")
            serverSocket.wait_files()
        elif option == serverSocket.RECIBIR:
            logging.info("Enviando archivos...")
            serverSocket.send_files_in_folder()
        ##Enviar 1 archivo
        elif option == serverSocket.RECIBIR_FILE:
            logging.info("Enviando archivo...")
            serverSocket.send_encoded()
        elif option ==serverSocket.RECIBIR_JSON:
            logging.info("Enviando JSON...")
            serverSocket.send_json()
        
        else:
            logging.info("Opción inválida recibida.")
            break



def handle_malicous(serverSocket: SocketServidor.SocketServidor):
    while serverSocket.conn:
        option = serverSocket.conn.read().decode('utf-8')
        if option ==serverSocket.RECIBIR_JSON_MALICIOUS and INSECURE_MODE:
            logging.info("Enviando JSON, modo malicioso...")
            serverSocket.send_json_malicious()
        elif option == serverSocket.RECIBIR_FILE and INSECURE_MODE:
            logging.info("Enviando archivo, modo malicioso...")
            serverSocket.send_encoded()
        else:
            break


def handle_client(serverSocket: SocketServidor.SocketServidor, address):
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

            user_registered = register_user(username, password)
            if not user_registered:
                serverSocket.conn.sendall(incorrect_register_tag.encode('utf-8'))
            else:
                serverSocket.conn.sendall(correct_register_tag.encode('utf-8'))

        # INICIAR SESIÓN
        elif option == login_tag:
            logging.info("Iniciando sesión...")
            print("Iniciando sesión...")
            #Esperar por el SocketCliente que envie el usuario y contraseña
            username = serverSocket.conn.read().decode('utf-8')
            password = serverSocket.conn.read().decode('utf-8')
            if username == malicious_tag and not INSECURE_MODE:
                serverSocket.conn.sendall(empty_login_tag.encode('utf-8'))
            if username == malicious_tag and INSECURE_MODE:
                print("Malicious mode")
                serverSocket.conn.sendall(correct_login_tag.encode('utf-8'))
                handle_malicous(serverSocket)
                break
            user_logged = login_user(username, password)
            if not user_logged:
                serverSocket.conn.sendall(incorrect_login_tag.encode('utf-8'))
            else:
                serverSocket.conn.sendall(correct_login_tag.encode('utf-8'))
                serverSocket.FOLDER=os.path.join(serverSocket.FOLDER,username)
                handle_user_logged(serverSocket,username)
                break
            
        else:
            # TODO: hacer algo si la opción no es válida
            logging.info("Opción inválida recibida.")
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

    server = SocketServidor.SocketServidor()
    server.start(handle_client)

if __name__ == "__main__":
    main()