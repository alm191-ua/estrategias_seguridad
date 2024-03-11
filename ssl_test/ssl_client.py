import socket
import ssl

IP = '127.0.0.1'
PORT = 4444


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(
        sock,
        ca_certs='certificates/certificate.pem')

    print("Connecting to server...")
    ssl_sock.connect((IP, PORT))
    print("Connected to server")

    try:
        while True:
            message = input("Enter message: ")

            if message:
                ssl_sock.write(message.encode())
                resp = ssl_sock.read()
                print("Response: ", resp.decode())

    except Exception as e:
        print(e)

    ssl_sock.close()
    sock.close()


if __name__ == '__main__':
    main()