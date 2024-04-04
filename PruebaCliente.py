import sys
sys.path.append('./sockets')
#import SocketCliente
from sockets import SocketCliente
from Cifrado import ZipAndEncryptFile

def main():
    cliente = SocketCliente.SocketCliente()
    cliente.connect()
    while True:
        if cliente.username=='' or cliente.password=='':
            username = input("Username: ")
            password = input("Password: ")
            cliente.username = username
            cliente.password = password
            option=33
            while option!=5:
                option=input("1. Register\n2. Login\n5. Exit\n")
                option = int(option)
                if option==5:
                    cliente.disconnect()
                    break
                if option==1:
                    if cliente.choose_opt(option):
                        print("User registered")
                    else:
                        print("User not registered")
                        cliente.username = ''
                        cliente.password = ''
                if option==2:
                    if cliente.choose_opt(option):  
                        print("User logged in")
                        break
                    else:
                        print("User not logged in")
                        cliente.username = ''
                        cliente.password = ''
                else:
                    print("Invalid option")
        else:
            option = input("3. Send files\n4. Receive files\n8. add File\n6. Exit\n")
            option = int(option)
            if option==6:
                cliente.disconnect()
                break
            if option==3:
                cliente.choose_opt(option)
            if option==4:
                cliente.choose_opt(option)
            if option==8:
                archivos = ['archivo1.txt', 'archivo2.txt']
                # Definir el título y la descripción
                titulo = "Paquete de documentos"
                descripcion = "Este paquete contiene dos archivos de ejemplo."
                cliente.ZipAndEncryptFile(archivos, titulo, descripcion)
            else:
                print("Invalid option")

if __name__ == "__main__":
    main()