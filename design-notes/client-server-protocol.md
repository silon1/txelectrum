# Client-Server Protocol Design-Note

Version: 1

## Introduction

The client and server implementation can be in different files with different
languages. Hence, we need a central place to explain the design. In this
design note, I will explain the interface design between the client and the server.

## Purpose

The purpose of the protocol is to allow the client to perform the following tasks:

1. Request the server to create a seckp256k1 key pair in the TXE protected with a
password.
2. Receive the public key of the key pair from the TXE.
3. Send a buffer to sign with the private key located in the TXE.
4. Receive the digital signature of the buffer.

## Start a Connection

The server will serve clients using a TCP socket on ```localhost:51841```. (The port 51841
was chosen because it equals to crc-16 of 'txelectrum'.)

## Message Structure

### Endianess

The endianess of this protocol is little-endian.

### Header

Every message between the client and the server will start with this
header. The header will contain following fields:

1. Version Number, 4 bytes, must be 1.
2. Message Type, 1 byte, contains one of the following values:
    * 1 for creating a key pair.
    * 2 for signing a payload.
    * 3 for singaling an error by the server.
3. Payload's Length, 4 bytes.

## Create Key Pair

The client asks the server to create a key pair. The algorithm must be ECDSA secp256k1.
Therefore, the Message Type in the headers of request and response must be 1. The
client must add in the payload a password digest using SHA-1 algorithm. The server then
will create a key pair protected with the password and response with the created public
key.

The following table summarizes the fields' content:

|                  | Version Number | Message Type | Payload's Length | Payload         |
|------------------|----------------|--------------|------------------|-----------------|
| client to server | 1              | 1            | 20               | password digest |
| server to client | 1              | 1            | 32               | public key      |

## Sign a Buffer

The client requests with Message Type 2 and adds the following fields in the paylod:
1. public key (32 bytes)
2. password digest (20 bytes)
3. hash function to use (1 byte)
4. buffer to sign (variable length)

The hash function field in the payload can have the following values:
* 1 for SHA-1
* 2 for SHA-256
* 3 for SHA-512

The server's response differs according to the client's request and the TXE state. The
server can response in the following ways:

* In normal flow, the server responses with Message Type 2 and the digital signature
in the payload.
* In error flow, the response must be with Message Type 3 and payload with one of the
following error types:
    * On missing private key, the error type is 0.
    * On wrong password, the error type is 1.

The following table summarizes the fields' content in every possible flow:

|                  | Flow                | Version Number | Message Type | Payload's Length | Payload         |
|------------------|---------------------|----------------|--------------|------------------|-----------------|
| client to server | -                   | 1              | 2            | variable length  | public key + password digest + hash function + buffer to sign |
| server to client | normal              | 1              | 2            | variable length  | digital signature |
| server to client | missing private key | 1              | 3            | 1                | 0                 |
| server to client | wrong password      | 1              | 3            | 1                | 1                 |
