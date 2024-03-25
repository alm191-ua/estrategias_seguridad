import socket
import SocketPadre
import threading
import ssl

PROTOCOL = ssl.PROTOCOL_TLS_SERVER

def handle_client(serverSocket, address):
    print(f"{address[0]}:{address[1]} conectado.")
    while serverSocket.conn:
        option = serverSocket.conn.recv(1).decode('utf-8')
        if option == '1':
            serverSocket.wait_files()
        elif option == '2':
            serverSocket.send_files_in_folder()
            serverSocket.conn.sendall(b"done")
        else:
            break
        if serverSocket.conn:
            print("Esperando a que el cliente haga algo...")

class SocketServidor(SocketPadre.SocketPadre) :
    FOLDER="server"
                    
    def start(self):
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


                
