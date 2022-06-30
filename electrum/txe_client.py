"""
This module implements functions that communicate with a TXE server.
By using this module an application can create a key-pair and sign
data using the ECDSA secp256k1 algorithm. Signing data is protected
with a password. Each function creates a new socket to communicate
with the server and closes it.

Example Usage:
1. Create a new wallet:
    try:
        pubkey = create_keypair(password)
    except TxeConnectionError:
        # handle the exception

2. Sign a transaction:
    try:
        sig = sign(transaction, password, pubkey)
        validate_sig(sig, pubkey) # Out of txe_client's responsibilities
    except TxeWrongPasswordError:
        # handle the exception
    except TxeConnectionError:
        # handle the exception
"""

def create_keypair(password:str) -> bytes:
    """
    Creates a new session with the TXE server and requests to create
    a new key-pair using the ECSDA secp256k1 algorithm. The private key
    will be protected with the given password.

    Returns the created public key.

    TxeConnectionError will be thrown if the connection couldn't be made,
    or is closed before receiving the public key.
    """

    pass


def sign(data:bytes, password:str, pubkey:bytes) -> bytes:
    """
    Sends the data to the TXE server for it to be signed with the
    private key.
    IMPORTANT: The digital signature is not validated.

    Returns the data's digital signature given by the TXE.

    TxeWrongPasswordError will be thrown if the password is incorrect.
    TxeConnectionError will be thrown if the connection couldn't be made,
    or is closed before receiving the signature.
    """

    pass


class TxeWrongPasswordError(Exception):
    pass


class TxeWrongPasswordError(Exception):
    pass
