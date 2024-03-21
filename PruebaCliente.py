import SocketCliente

def main():
    cliente = SocketCliente.SocketCliente()
    cliente.connect()
    while True:
        option=input("1. Enviar archivos\n2. Recibir archivos\n3. Salir\n")
        if option == '3':
            cliente.disconnect()
            break
        option = int(option)
        cliente.choose_opt(option)

if __name__ == "__main__":
    main()