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


def create_keypair(password:str) -> bytes:
    """
    Requests the server to create a new key pair using the ECSDA secp256k1
    algorithm. The private key will be protected with the given password.

    Returns the created public key.

    TxeConnectionError will be thrown if the connection couldn't be made,
    or is closed before receiving the public key.
    """

    pass


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

    This function may throw the following exceptions:
    * TxeMissingPrivateKeyError when the server couldn't find the key pair
    of this public key.
    * TxeWrongPasswordError when the password is incorrect.
    * TxeConnectionError when the connection couldn't be made or is
    closed before receiving the signature.
    """

    pass


class TxeException(Exception):
    pass


class TxeConnectionError(TxeException):
    pass


class TxeWrongPasswordError(TxeException):
    pass


class TxeMissingPrivateKeyError(TxeException):
    pass


