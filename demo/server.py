from typing import List
import socket
import select
import argparse

import protocol

def main(args: List) -> None:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((args.ip_addr, args.port))
    server_sock.listen()
    print(f"Server is listening on ({args.ip_addr}, {args.port})")

    client_socks = []
    messages = []
    try:
        while True:
            read_list = client_socks + [server_sock]
            ready_to_read, ready_to_write, in_error = select.select(read_list, client_socks, [])

            for sock in ready_to_read:
                if sock is server_sock:
                    client_sock, client_address = server_sock.accept()
                    print(client_address, "New client joined!")
                    client_socks.append(client_sock)
                    continue

                sock_addr = sock.getpeername()

                if sock in in_error:
                    print(sock_addr, "Client connection closed with error!")
                    client_socks.remove(sock)
                    sock.close()
                    continue
                
                msg_type, data = protocol.read(sock)
                if msg_type == protocol.EXIT:
                    print(sock_addr, "Client connection closed!")
                    client_socks.remove(sock)
                    sock.close()
                elif msg_type == protocol.CREATE_KEYS:
                    print(sock_addr, "Creating new keys")
                    messages.append((sock, protocol.CREATE_KEYS, b'public key'))
                elif msg_type == protocol.SIGN_DATA:
                    print(sock_addr, "Signing data:", data.decode())
                    messages.append((sock, protocol.SIGN_DATA, b'signed ' + data))
                else:
                    print(sock_addr, "Unexpected Message Type")
                    client_socks.remove(sock)
                    sock.close()

            for message in messages:
                sock, msg_type, data = message
                if sock not in ready_to_write:
                    continue
                print("writing to", sock.getpeername())
                protocol.write(sock, msg_type, data)
                messages.remove(message)

    finally:
        server_sock.close()

def create_parser():
    parser = argparse.ArgumentParser(description='txelectrum demo server')
    parser.add_argument('-ip', '--ip-addr', default='0.0.0.0', help='server\'s ip address')
    parser.add_argument('-p', '--port', default=protocol.SERVER_PORT, type=int, help='server\'s port')
    return parser


if __name__ == '__main__':
    main(create_parser().parse_args())
