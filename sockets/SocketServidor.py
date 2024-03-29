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
                        
