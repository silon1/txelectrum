"""
This module implements functions that communicate with a TXE server.
By using this module an application can create a key pair and sign
data using the ECDSA secp256k1 algorithm. Signing data is protected
with a password.

Example Usage:
* Create a new wallet:
    try:
        pubkey = create_keypair(password)
    except TxeException:
        # handle the exception
* Sign a transaction:
    try:
        sig = sign(transaction, TXE_SHA256, password, pubkey)
        validate_sig(sig) # Out of txe_client's responsibilities
    except TxeWrongPasswordError:
        # handle the exception
    except TxeException:
        # handle other exceptions
"""


TXE_SHA1 = 0
TXE_SHA256 = 1
TXE_SHA512 = 2


# The design notes for the client-server protocol is found at ```design-notes/client-server-protocol.md```.


from typing import Tuple
import hashlib
import socket


__IP = '127.0.0.1'
__PORT = 51841

__CREATE_KEYS = 1
__SIGN_BUFFER = 2
__ERROR = 3

__VERSION = 1
__ENDIANESS = 'little'
__VERSION_LENGTH = 4
__MESSAGE_TYPE_LENGTH = 1
__PAYLOAD_LENGTH_LENGTH = 4
__PUBKEY_LENGTH = 32
__HASH_FUNC_LENGTH = 1


def create_keypair(password:str) -> bytes:
    """
    Requests the server to create a new key pair using the ECSDA secp256k1
    algorithm. The private key will be protected with the given password.

    Returns the created public key.

    This function will raise TxeException if it cannot recieve the public
    key from the server.
    """

    password_digest = hashlib.sha1(password.encode()).digest()
    message_type, payload = __send_recv(__CREATE_KEYS, password_digest)

    if message_type != __CREATE_KEYS:
        raise TxeException(f"The server sent the message type {message_type} and not {__CREATE_KEYS}.")

    if len(payload) != __PUBKEY_LENGTH:
        raise TxeException(f"The server sent a payload with the length {len(payload)} and not {__PUBKEY_LENGTH}.")

    return payload


def sign(buffer:bytes, hash_func:int, password:str, pubkey:bytes) -> bytes:
    """
    Requests the server to sign the buffer with the pair of the public key
    and a selected hash function.

    The parameters for this function are the following:
    1. buffer to be signed
    2. hash function to use when signed
    3. password to unlock the key pair
    4. public key to identify the key pair to use

    hash_func must be one of the following:
    * txe_client.TXE_SHA1
    * txe_client.TXE_SHA256
    * txe_client.TXE_SHA512

    Returns the buffer's digital signature. This function doesn't validate
    the digital signautre. The caller MUST validate the digital signature
    for security.

    This function may raise the following exceptions:
    * TxeMissingPrivateKeyError when the server couldn't find the key pair
    of this public key.
    * TxeWrongPasswordError when the password is incorrect.
    * TxeException if this function cannot recieve the digital signature
    from the server.
    """

    if hash_func not in (TXE_SHA1, TXE_SHA256, TXE_SHA512):
        raise ValueError(f"Invalid hash func {hash_func}")

    password_digest = hashlib.sha1(password.encode()).digest()
    encoded_hash_func = hash_func.to_bytes(__HASH_FUNC_LENGTH, byteorder=__ENDIANESS)
    payload = pubkey + password_digest + encoded_hash_func + buffer
    
    message_type, payload = __send_recv(__SIGN_BUFFER, payload)

    if message_type == __SIGN_BUFFER:
        # normal flow, the payload is the digital signature
        return payload

    if message_type == __ERROR:
        # error flow, the payload contains the reason for the error
        error_reason = int.from_bytes(payload, byteorder=__ENDIANESS)
        if error_reason == 0:
            raise TxeMissingPrivateKeyError()
        if error_reason == 1:
            raise TxeWrongPasswordError()
        raise TxeException(f"The server sent an unexpected error reason {error_reason}")
    
    raise TxeException(f"The server sent an unexpected message type {message_type}")


class TxeException(Exception):
    pass


class TxeWrongPasswordError(TxeException):
    pass


class TxeMissingPrivateKeyError(TxeException):
    pass


def __send_recv(message_type:int, payload:bytes) -> Tuple[int, bytes]:
    """
    This function sends a message to the server and returns the answer
    from the server. The messages are according to the client-server
    protocol (see the comment at top.) The returned values are the message
    type and the payload.

    This function may raise TxeException if the server sent a header not
    according to the protocol.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((__IP, __PORT))

        # sending the message
        encoded_version = __VERSION.to_bytes(__VERSION_LENGTH, byteorder=__ENDIANESS)
        encoded_message_type = message_type.to_bytes(__MESSAGE_TYPE_LENGTH, byteorder=__ENDIANESS)
        encoded_length = len(payload).to_bytes(__PAYLOAD_LENGTH_LENGTH, byteorder=__ENDIANESS)
        header = encoded_version + encoded_message_type + encoded_length

        sock.send(header + payload)

        # receiving the message
        encoded_version = sock.recv(__VERSION_LENGTH)
        version = int.from_bytes(encoded_version, byteorder=__ENDIANESS)

        if version != __VERSION:
            raise TxeException(f"The server sent the version {version} and not {__VERSION}")

        encoded_message_type = sock.recv(__MESSAGE_TYPE_LENGTH)
        message_type = int.from_bytes(encoded_message_type, byteorder=__ENDIANESS)

        encoded_length = sock.recv(__PAYLOAD_LENGTH_LENGTH)
        length = int.from_bytes(encoded_length, byteorder=__ENDIANESS)

        payload = sock.recv(length)

        return message_type, payload

