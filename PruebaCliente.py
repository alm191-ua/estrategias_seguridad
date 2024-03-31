import sys
sys.path.append('./sockets')
#import SocketCliente
from sockets import SocketCliente

def main():
    cliente = SocketCliente.SocketCliente()
    cliente.connect()
    while True:
        username = input("Username: ")
        password = input("Password: ")
        cliente.username = username
        cliente.password = password
        option=input("1. Register\n2. Login\n3. Exit\n")
        if option == '3':
            cliente.disconnect()
            break
        option = int(option)
        cliente.choose_opt(option)

if __name__ == "__main__":
    main()