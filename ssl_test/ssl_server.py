import socket
import ssl
import time
import threading

IP = '127.0.0.1'
PORT = 4444
WITH_THREADS = True
PROTOCOL = ssl.PROTOCOL_TLS_SERVER

def handle_client(client, address):
	"""
	Handle client connection
	"""
	print("Connected to: ", address)
	while True:
		try:
			# read client data
			data = client.read(1024)
			if data:
				print("Received: ", data.decode())
				client.write(data)
			else:
				print("Client disconnected")
				break
		except Exception as e:
			print(e)
			break
	client.close()

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((IP, PORT))
	sock.listen(5)

	print("Listening on port: ", PORT)
	while True:
		client, address = sock.accept()

		ssl_sock = ssl.wrap_socket(
			client, 
			server_side=True, 
			certfile='certificates/certificate.pem', 
			keyfile='certificates/key.pem', 
			ssl_version=PROTOCOL)

		if not WITH_THREADS:
			handle_client(ssl_sock, address)
		else:
			thread = threading.Thread(target=handle_client, args=(ssl_sock, address))
			thread.start()
			print("Active threads: ", threading.active_count())
	

if __name__ == '__main__':
	main()