import SocketCliente

def main():
    cliente = SocketCliente.SocketCliente()
    cliente.connect()
    cliente.choose_opt(2)
    cliente.disconnect()
if __name__ == "__main__":
    main()