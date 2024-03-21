import ssl
import socket

BUFF_SIZE = 1024

if __name__ == "__main__":
    # First, create a context. The default settings are probably the best here. 
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # Load the CA (self-signed, in this case) and the corresponding private key (also self-signed, in this case)
    context.load_cert_chain(certfile="certificates\certificate.pem", 
        keyfile="certificates\key.pem")

    # Create a standard TCP socket, bind it to an address, and listen for connections
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 1234))
    s.listen()

    # Start accepting incoming connections
    accepting = True 
    try:
        while accepting:
            # conn is a standard python socket, addr is where it originated
            conn, addr = s.accept()
            # wrap the standard socket with the SSLContext, now it is a secure connection
            with context.wrap_socket(conn, server_side=True) as secure_conn:
                # data can be read/sent just like as in standard sockets
                data = secure_conn.recv(BUFF_SIZE)
    except socket.timeout:
        pass