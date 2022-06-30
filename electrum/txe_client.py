"""
This module is a client that communicates with a TXE server
in order to securely sign data using ECDSA secp256k1 algorithm.

Usage:
1. Create a new wallet:
    pubkey = create_keypair(password)

2. Sign a transaction:
    try:
        sig = sign(transaction, password, pubkey)
        validate_sig(sig, pubkey) # Out of txe_client's responsibilities
    except TxeWrongPasswordException:
        # handle the exception
"""

def create_keypair(password:str) -> bytes:
    """
    Creates a new session with the TXE server
    in order to create a new key-pair.

    Returns the public key of the new wallet.
    """

    pass


def sign(data:bytes, password:str, pubkey:bytes) -> bytes:
    """
    Sends the data to be signed in the TXE using the ECDSA secp256k1 algorithm.
    Returns the data's digital signature given by the TXE.
    IMPORTANT: The digital signature is not validated.

    If the password is incorrect, then a TxeWrongPasswordException will be raised.
    """

    pass


class TxeWrongPasswordException(Exception):
    pass
