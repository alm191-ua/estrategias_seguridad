import socket
import Socket



class SocketServidor(Socket.Socekt) :
    FOLDER="server"
                    

    def start(self):
        while True:
            with socket.create_server((self.SERVIDOR_IP, self.SERVIDOR_PUERTO)) as server:
                print("Esperando al cliente...")
                try:
                    self.conn, address = server.accept()
                except KeyboardInterrupt:
                    server.close()
                    print("\nInterrupción de teclado detectada, cerrando el servidor.")
                    break
                print(f"{address[0]}:{address[1]} conectado.")
                while self.conn:
                    option = self.conn.recv(1).decode('utf-8')
                    if option == '1':
                        self.wait_files()
                    elif option == '2':
                        self.send_files_in_folder()
                        self.conn.sendall(b"done")
                    else:
                        break
                    if self.conn:
                        print("Esperando a que el cliente haga algo...")

                
