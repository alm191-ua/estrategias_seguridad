import sys
sys.path.append('./sockets')
#import SocketServidor
from sockets import SocketServidor

def main():
    server = SocketServidor.SocketServidor()
    server.start()

if __name__ == "__main__":
    main()