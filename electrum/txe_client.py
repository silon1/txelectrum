"""
This module implements functions that communicate with a TXE server.
By using this module an application can create a key pair and sign
data using the ECDSA secp256k1 algorithm. Signing data is protected
with a password. Each function creates a new socket to communicate
with the server and closes it.

Example Usage:
* Create a new wallet:
    try:
        pubkey = create_keypair(password)
    except TxeException:
        # handle the exception

* Sign a transaction:
    try:
        sig = sign(transaction, TXE_SHA256, password, pubkey)
    except TxeWrongPasswordError:
        # handle the exception
    except TxeException:
        # handle other exceptions
"""

TXE_SHA1 = 0
TXE_SHA256 = 1
TXE_SHA512 = 2

"""
Number of times to request the server to sign again and validate the response
when the first validation failed.
"""
__TXE_NUM_VALIDATIONS = 10

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
    and a selected hash function. This function validates the digital signature
    before returning it.

    The parameters for this function are the following:
    1. buffer to be signed
    2. hash function to use when signed
    3. password to unlock the key pair
    4. public key to identify the key pair to use

    hash_func must be one of the following:
    * txe_client.TXE_SHA1
    * txe_client.TXE_SHA256
    * txe_client.TXE_SHA512

    Returns the buffer's digital signature.

    This function may throw the following exceptions:
    * TxeMissingPrivateKey when the server couldn't find the key pair of
    this public key.
    * TxeWrongPasswordError when the password is incorrect.
    * TxeValidationError when this function failed to validate the digital
    signature.
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


class TxeMissingPrivateKey(TxeException):
    pass


class TxeValidationError(TxeException):
    pass

