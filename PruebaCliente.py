import SocketCliente

def main():
    cliente = SocketCliente.SocketCliente()
    cliente.connect()
    cliente.send_int(1)
    cliente.send_files_in_folder()
    cliente.disconnect()
if __name__ == "__main__":
    main()