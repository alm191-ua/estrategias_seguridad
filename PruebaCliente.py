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
        option = -1
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
    logged_options = [0, 1, 2, 3] #exit, send file, receive file

    while True:
        option = -1
        while option not in logged_options:
            option=input("0.Exit\n1. Send document\n2. Receive files\n3. List documents\n")
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
            elif option == 2:
                cliente.conn.sendall(cliente.RECIBIR.encode('utf-8'))
                # Wait for files from the server
                cliente.wait_files()

            elif option == 3:
                cliente.conn.sendall(cliente.RECIBIR_JSON.encode('utf-8'))
                # get the documents in jsons
                cliente.wait_files()
                # for every File in files
                files = os.listdir("files")
                for file in files:
                    json_path = os.path.join("files", file, file + ".json")
                    cliente.print_json_info(json_path)
                # NOTA para Alex: cuando vayas a hacer la interfaz puedes usar
                # el método de SocketCliente get_json_info para obtener los
                # campos del json. El método print_json_info llama a ese
                # método y además lo imprimer por terminal.

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