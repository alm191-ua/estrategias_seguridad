import sys
sys.path.append('./sockets')
#import SocketCliente
from sockets import SocketCliente
from Cifrado import ZipAndEncryptFile as encryptDoc
import os

def main():
    cliente = SocketCliente.SocketCliente()
    cliente.connect()
    options_not_logged = [0, 1, 2]
    while True:
        option = 3
        while option not in options_not_logged:
            option=input("0.Exit\n1. Register\n2. Login\n")
            option = int(option)
            if option==0:
                cliente.disconnect()
                return
            elif option==1:
                username = input("Username: ")
                password = input("Password: ")
                cliente.username = username
                cliente.password = password
                if cliente.register_user():
                    print("User registered")
                    continue
                else:
                    print("User not registered")
                    cliente.username = ''
                    cliente.password = ''

            elif option==2:
                username = input("Username: ")
                password = input("Password: ")
                cliente.username = username
                cliente.password = password
                if cliente.log_in():
                    print("User logged in")
                    login_options(cliente)
                    return
                else:
                    print("User not logged in")
                    cliente.username = ''
                    cliente.password = ''

            else:
                print("Invalid option")

def login_options(cliente: SocketCliente.SocketCliente):        
    # Logged options
    logged_options = [0, 1, 2] #exit, send file, receive file

    while True:
        option = 3
        while option not in logged_options:
            option=input("0.Exit\n1. Send document\n2. Receive files\n")
            option = int(option)
            if option==0:
                cliente.disconnect()
                return
            elif option==1:
                carpeta_con_files = "test"
                title = "Documento1"
                description = "Este es un documento de prueba"
                files = os.listdir(carpeta_con_files)
                cliente.send_encrypted_files(files, title, description)
                # encryptDoc(files, title, description)
                # # cliente.send_files()
                # cliente.conn.sendall(cliente.ENVIAR.encode('utf-8'))
                # cliente.send_files_in_folder()
            elif option==2:
                cliente.conn.sendall(cliente.RECIBIR.encode('utf-8'))
                # Wait for files from the server
                cliente.wait_files()
            else:
                print("Invalid option")




        # if cliente.username=='' or cliente.password=='':
            
        #     option=33
        #     while option!=10:
        #         option=input("1. Register\n2. Login\n5.Recibir JSON (malicioso)\n10. Exit\n")
        #         option = int(option)
        #         if option==10:
        #             cliente.disconnect()
        #             return
        #         elif option==1:
        #             username = input("Username: ")
        #             password = input("Password: ")
        #             cliente.username = username
        #             cliente.password = password
        #             if cliente.choose_opt(option):
        #                 print("User registered")
        #             else:
        #                 print("User not registered")
        #                 cliente.username = ''
        #                 cliente.password = ''
        #         elif option==2:
        #             username = input("Username: ")
        #             password = input("Password: ")
        #             cliente.username = username
        #             cliente.password = password
        #             if cliente.choose_opt(option):  
        #                 print("User logged in")
        #                 break
        #             else:
        #                 print("User not logged in")
        #                 cliente.username = ''
        #                 cliente.password = ''
        #         elif option==5:
        #             cliente.choose_opt(option)
        #         else:
        #             print("Invalid option")
        # else:
        #     option = input("3. Send files(no usar)\n4. Receive files\n5.Recibir JSONs\n8. add File\n10. Exit\n")
        #     option = int(option)
        #     print(option==5)
        #     if option==10:
        #         cliente.disconnect()
        #         return
        #     elif option==3 or option==4:
        #         cliente.choose_opt(option)
        #     elif option==5:
        #         cliente.choose_opt(option)
        #     elif option==8:
        #         archivos = ['archivo1.txt', 'archivo2.txt']
        #         # Definir el título y la descripción
        #         titulo = "Paquete de documentos"
        #         descripcion = "Este paquete contiene dos archivos de ejemplo."
        #         cliente.send_encrypted_files(archivos, titulo, descripcion)
        #     else:
        #         print(option)
        #         print("Invalid option")

if __name__ == "__main__":
    main()