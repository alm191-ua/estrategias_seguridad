import ssl
import socket

if __name__ == "__main__":
    # Create a context, just like as for the server
    context = ssl.create_default_context()
    # Load the server's CA
    context.load_verify_locations("certificates\certificate.pem")
    
    # Wrap the socket, just as like in the server.
    conn = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname="localhost")
    
    # Connect and send data! Standard python socket stuff can go here.
    conn.connect(("localhost", 1234))
    conn.sendall(b"Hello, server! This was encrypted.")