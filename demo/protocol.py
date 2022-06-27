from typing import Tuple
import socket

# crc-16 of 'txelectrum'
SERVER_PORT = 51841

EXIT = 0
CREATE_KEYS = 1
SIGN_DATA = 2
PARSE_ERROR = 3

_VER = 1
_ENDIANESS = 'little'

_VER_BYTES = 4
_MSG_TYPE_BYTES = 1
_SIZE_BYTES = 4


def read(sock: socket.socket) -> Tuple['type', 'data']:
    version = sock.recv(_VER_BYTES)
    if version == b'':
        return EXIT, None
    version = int.from_bytes(version, byteorder=_ENDIANESS)
    if version != _VER:
        return PARSE_ERROR, None

    msg_type = int.from_bytes(sock.recv(_MSG_TYPE_BYTES), byteorder=_ENDIANESS)
    if msg_type not in (CREATE_KEYS, SIGN_DATA):
        return PARSE_ERROR, None

    size = int.from_bytes(sock.recv(_SIZE_BYTES), byteorder=_ENDIANESS)
    return msg_type, sock.recv(size)


def write(sock: socket.socket, msg_type: int, data: bytes) -> None:
    if msg_type not in (CREATE_KEYS, SIGN_DATA):
        raise ValueError("msg_type must be one of CREATE_KEYS, SIGN_DATA")

    version = _VER.to_bytes(_VER_BYTES, byteorder=_ENDIANESS)
    msg_type_bytes = msg_type.to_bytes(_MSG_TYPE_BYTES, byteorder=_ENDIANESS)
    size = len(data).to_bytes(_SIZE_BYTES, byteorder=_ENDIANESS)

    sock.send(version + msg_type_bytes + size + data)
