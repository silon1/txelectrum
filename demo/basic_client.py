import protocol
import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect(('127.0.0.1', protocol.SERVER_PORT))

while True:
    print('c - creating keys')
    print('s - signing data')
    print('q - exit')
    msg = input()

    if msg == 'q':
        break
    if msg != 's' and msg != 'c':
        continue
    if msg == 'c':
        protocol.write(my_socket, protocol.CREATE_KEYS, b'')
    elif msg == 's':
        data = input('enter data: ').encode()
        protocol.write(my_socket, protocol.SIGN_DATA, data)

    msg_type, data = protocol.read(my_socket)
    if msg_type == protocol.EXIT:
        print("Server connection closed")
        break
    elif msg_type in (protocol.CREATE_KEYS, protocol.SIGN_DATA):
        print(data.decode())
    else:
        print("Unexpected Message Type")
        break

my_socket.close()
