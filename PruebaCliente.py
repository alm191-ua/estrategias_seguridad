import sys
sys.path.append('./sockets')
#import SocketCliente
from sockets import SocketCliente

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
            while option!=10:
                option=input("1. Register\n2. Login\n10. Exit\n")
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
            option = input("3. Send files(no usar)\n4. Receive files\n5.Recibir JSONs\n6. add File\n10. Exit\n")
            option = int(option)
            print(option==5)
            if option==10:
                cliente.disconnect()
                break
            if option==3 or option==4:
                cliente.choose_opt(option)
            elif option==5:
                cliente.choose_opt(option)
            if option==8:
                archivos = ['archivo1.txt', 'archivo2.txt']
                # Definir el título y la descripción
                titulo = "Paquete de documentos"
                descripcion = "Este paquete contiene dos archivos de ejemplo."
                cliente.ZipAndEncryptFile(archivos, titulo, descripcion)
            else:
                print(option)
                print("Invalid option")

if __name__ == "__main__":
    main()