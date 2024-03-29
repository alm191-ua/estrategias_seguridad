import sys
import os
import json
import bcrypt
sys.path.append('./sockets')
sys.path.append('./utils')
import SocketServidor
from secure_key_gen import hash_password
from secure_key_gen import check_password

config = json.load(open('config.json'))

register_tag = config['sockets']['tags']['init_comms']['register']
login_tag = config['sockets']['tags']['init_comms']['login']
correct_login_tag = config['sockets']['tags']['response']['correct_login']
incorrect_login_tag = config['sockets']['tags']['response']['incorrect_login']
correct_register_tag = config['sockets']['tags']['response']['correct_register']
incorrect_register_tag = config['sockets']['tags']['response']['incorrect_register']
incorrect_tag = config['sockets']['tags']['response']['incorrect_tag']

USERS_FILE = "server/users.json"
MIN_USERNAME_LENGTH = 4
MIN_PASSWORD_LENGTH = 8

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
            users = {username: hashed}
            json.dump(users, file)

    return True

def handle_user_logged(username):
    # TODO: gestionar lo que puede hacer un usuario logueado
    pass

def handle_client(serverSocket: SocketServidor.SocketServidor, address):
    print(f"{address[0]}:{address[1]} conectado.")
    while serverSocket.conn:
        option = serverSocket.conn.read().decode('utf-8')

        # REGISTRAR USUARIO
        if option == register_tag:
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
            print("Iniciando sesión...")
            #Esperar por el SocketCliente que envie el usuario y contraseña
            username = serverSocket.conn.read().decode('utf-8')
            password = serverSocket.conn.read().decode('utf-8')

            user_logged = login_user(username, password)
            if not user_logged:
                serverSocket.conn.sendall(incorrect_login_tag.encode('utf-8'))
            else:
                serverSocket.conn.sendall(correct_login_tag.encode('utf-8'))
                handle_user_logged(username)
            
        else:
            # TODO: hacer algo si la opción no es válida
            break
            # serverSocket.conn.sendall(incorrect_tag.encode('utf-8'))
        
    print(f"{address[0]}:{address[1]} desconectado.")


def main():
    server = SocketServidor.SocketServidor()
    server.start(handle_client)

if __name__ == "__main__":
    main()