# Client-Server Protocol Design-Note

Version: 1

## Introduction

The client and server implementation can be in different files with different
languages. Hence, we need a central place to explain the design. In this
design note, I will explain the interface design between the client and the server.

## Purpose

The purpose of the protocol is to allow the client to create a bitcoin wallet on
a remote server. Therefore, the server must provide the following funcitonality:

1. Request the server to create a seckp256k1 key pair protected with a password.
2. Receive the public key of the key pair from the server.
3. Send a hashed buffer to sign with the private key.
4. Receive the digital signature of the hashed buffer.

## Start a Connection

The server will serve clients using a TCP socket on `localhost:51841`. (The port 51841
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
client must add in the payload a hashed password with SHA-1 algorithm. The server then
will create a key pair protected with the password and response with the created public
key.

The server must send the public key uncompressed in SEC format[^1]. Therefore, the public
key size must be 65 bytes. 

[^1]: https://bitcoin.stackexchange.com/a/92683.

The following table summarizes the fields' content:

|                  | Version Number | Message Type | Payload's Length | Payload         |
|------------------|----------------|--------------|------------------|-----------------|
| client to server | 1              | 1            | 20               | hashed password |
| server to client | 1              | 1            | 65               | public key      |

## Sign a Buffer

The client requests with Message Type 2 and adds the following fields in the paylod:
1. The public key uncompressed in SEC format (65 bytes)[^1].
2. The hash of the password with SHA-1 algorithm (20 bytes).
3. The hash of the buffer to sign with SHA-256 algorithm (32 bytes)[^2].

[^2]: [Bitcoin uses SHA-256 algorithm for transactions](https://bitcoin.stackexchange.com/a/9216)

The server's response differs according to the client's request and the TXE state. The
server can response in the following ways:

* In normal flow, the server responses with Message Type 2 and the digital signature
in the payload in DER format[^1].
* In error flow, the response must be with Message Type 3 and a 2-bytes payload with
one of the following error codes:
    * On missing private key, the error code is 0x0200.
    * On wrong password, the error code is 0x0201.

The following table summarizes the fields' content in every possible flow:

|                  | Flow                | Version Number | Message Type | Payload's Length | Payload                                              |
|------------------|---------------------|----------------|--------------|------------------|------------------------------------------------------|
| client to server | -                   | 1              | 2            | 117              | public key + hashed password + hashed buffer to sign |
| server to client | normal              | 1              | 2            | variable length  | digital signature                                    |
| server to client | missing private key | 1              | 3            | 2                | 0x0200                                               |
| server to client | wrong password      | 1              | 3            | 2                | 0x0201                                               |

## General Errors

Sometimes the server may incounter in an error not specific to a message type. For
example, consider the following errors:
* The client sent a badly formed message.
* The server incountered an internal error.
* The client'd waited too long until it sent the whole message.

When a server incouters a general error, it must send a response with Message
Type 3 and a 2-bytes payload with one of the following error codes:
* On badly formed message, the error code is 0x0000.
* On internal error, the error code is 0x0001.
* On timeout error, the error code is 0x0002.
* On unkown error, the error code is 0x00FF.

The following table summarizes the fields' content in every possible general error response:

| Error                | Version Number | Message Type | Payload's Length | Payload |
|----------------------|----------------|--------------|------------------|---------|
| badly formed message | 1              | 3            | 2                | 0x0000  |
| internal error       | 1              | 3            | 2                | 0x0001  |
| timeout error        | 1              | 3            | 2                | 0x0002  |
| unkown error         | 1              | 3            | 2                | 0x00FF  |
