import socket
import SocketPadre
import threading
import ssl
import os
import json

PROTOCOL = ssl.PROTOCOL_TLS_SERVER

config = json.load(open('config.json'))

class SocketServidor(SocketPadre.SocketPadre) :
    FOLDER="server"

    def send_json(self):
        """
        Sends a JSON file to the client.
        """
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        while self.conn:
            files = os.listdir(self.FOLDER)
            legnth = len(files)
            i=0
            for fileId in files:
                
                if fileId != "users.json":
                    print("Enviando archivo...")
                    file_folder_path = os.path.join(self.FOLDER, fileId)
                    files_path = os.path.join(file_folder_path, fileId)
                    file_json=files_path+self.FORMATO_JSON
                    file_key=files_path+self.FORMATO_LLAVE+self.FORMATO_ENCRIPTADO
                    self.send_file(file_json)
                    self.send_file(file_key)
                    print("Enviado.")
                i+=1
                if i==legnth:
                    break
            self.conn.sendall(b"done")
            break
            
        return
    def send_encoded(self):
        name = self.conn.read().decode('utf-8')
        print(name)
        if not self.conn:
            raise Exception("No se ha establecido una conexión.")
        while self.conn:
            files = os.listdir(self.FOLDER)
            for fileId in files:
                if fileId == name:
                    print("Enviando archivo...")
                    file_folder_path = os.path.join(self.FOLDER, fileId)
                    files_path = os.path.join(file_folder_path, fileId)
                    file_path = files_path + self.FORMATO_ARCHIVO_ENCRIPTADO
                    print(file_path)
                    self.send_file(file_path)
                    print("Enviado.")
                    break
            self.conn.sendall(b"done")
            break
            
        return
        
          
    def start(self, handle_client):
        while True:
            with socket.create_server((self.SERVIDOR_IP, self.SERVIDOR_PUERTO)) as server:
                print("Esperando al cliente...")
                try:
                    client, address = server.accept()

                    self.conn = ssl.wrap_socket(
                        client, 
                        server_side=True, 
                        certfile='certificates/certificate.pem', 
                        keyfile='certificates/key.pem', 
                        ssl_version=PROTOCOL)
                    
                except KeyboardInterrupt:
                    server.close()
                    print("\nInterrupción de teclado detectada, cerrando el servidor.")
                    break
                
                thread = threading.Thread(target=handle_client, args=(self, address))
                thread.start()
                print("Active threads: ", threading.active_count())
                        
