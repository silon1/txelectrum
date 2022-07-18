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
        sig = sign(transaction, password, pubkey)
        validate_sig(sig) # Out of txe_client's responsibilities
    except TxeWrongPasswordError:
        # handle the exception
    except TxeException:
        # handle other exceptions
"""

# The REST api is explained at `/openapi.yaml`.

import requests
import hashlib

__BASE_URL = "http://localhost:51841"


def create_keypair(password:str) -> bytes:
    """
    Requests the server to create a new key pair using the secp256k1
    algorithm. The private key will be protected with the given password.

    Returns the created public key.

    This function will raise TxeException if it cannot recieve the public
    key from the server.
    """

    hashed_password = hashlib.sha1(password.encode()).hexdigest()
    req_body = { "hashed_password": hashed_password }

    try:

        response = requests.post(f"{__BASE_URL}/create_keypair", json=req_body)
        response.raise_for_status()
        pubkey = response.json()["public_key"]
        return bytes.fromhex(pubkey)

    except Exception as e:

        raise TxeException(e)


def txe_sign(buffer:bytes, password:str, pubkey:bytes) -> bytes:
    print(password)
    exit()
    """
    Requests the server to sign the buffer with the pair of the public key
    and a selected hash function.

    The parameters for this function are the following:
    1. Buffer to be signed.
    2. Password to unlock the key pair.
    3. Public key to identify the key pair to use.

    Returns the buffer's digital signature in DER format. This function
    doesn't validate the digital signautre. The caller MUST validate the
    digital signature for security.

    This function may raise the following exceptions:
    * TxeMissingPrivateKeyError when the server couldn't find the key pair
    of this public key.
    * TxeWrongPasswordError when the password is incorrect.
    * TxeException if this function cannot recieve the digital signature
    from the server.
    """

    hashed_password = hashlib.sha1(password.encode()).hexdigest()
    hashed_buffer = hashlib.sha256(buffer).hexdigest()

    req_body = {
        "public_key": pubkey.hex(),
        "hashed_password": hashed_password,
        "hashed_buffer": hashed_buffer,
    }

    try:

        response = requests.post(f"{__BASE_URL}/sign_buffer", json=req_body)
        response.raise_for_status()
        signature = response.json()["signature"]
        return bytes.fromhex(signature)

    except requests.HTTPError as e:

        if e.response.status_code == 404:
            raise TxeMissingPrivateKeyError(e)
        if e.response.status_code == 401:
            raise TxeWrongPasswordError(e)
        raise TxeException(e)

    except Exception as e:

        raise TxeException(e)


class TxeException(Exception):
    pass


class TxeWrongPasswordError(TxeException):
    pass


class TxeMissingPrivateKeyError(TxeException):
    pass


