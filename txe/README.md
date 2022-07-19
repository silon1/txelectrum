# Host-Applet Protocol

Version: 1.

The host is the application that runs in the untrusted OS, and communicates with the applet. The host 
is the REST api server. The applet is the application that runs in the TXE and is in charge of the
secure computations and storage.

The communication between the host and the applet is as the following:
1. The host sends a `commandId` and an `inputBuffer`.
2. The applet responses with a `responseId` and a `outputBuffer`.

The protocol defines the following functions the applet will perform:
* Create a secp256k1 key pair and protect it with a password.
* Sign a hashed buffer with ECDSA secp256k1 algorithm.

## Create key pair

To create a key pair, the host must send a request with `commandId = 0` and a hashed password with SHA-1 algorithm (20 bytes length) in the `inputBuffer`.

The applet must return one of the following responses:
* Response with `responseId = 0` and the public key in SEC's compressed format (33 bytes length) in the `outputBuffer`, if the hashed password's length is 20 bytes.
* Response with `responseId = 1` and empty `outputBuffer`, if the hashed password's length is not 20 bytes (meaning bad request).
* Response with `responseId = 2` and empty `outputBuffer`, if the applet incountered an internal error.

## Sign buffer

To sign a buffer, the host must send a request with `commandId = 2` and an `inputBuffer` with the following concatenated parameters:
1. The public key of the key pair to use in SEC's compressed format (33 bytes length).
2. The hashed password with SHA-1 algorithm (20 bytes length).
3. The hashed buffer to sign with SHA-256 algorithm (32 bytes length).
Overall, the length of `inputBuffer` must be 85 bytes.

The applet must retunr one of the following responses:
* Response with `responseId = 0` and the digital signature in DER format in `outputBuffer`, if `inputBuffer` meets the following conditions:
    * The overall length is 85 bytes.
    * The private key paired with the public key in the `inputBuffer` exists in the secure storage.
    * The hashed password in the `inputBuffer` matches the hashed password protecting the private key.
* Response with `responseId = 1` and empty `outputBuffer`, if the `inputBuffer`'s length is not 80 bytes (meaning bad request).
* Response with `responseId = 2` and empty `outputBuffer`, if the applet incountered an internal error.
* Response with `responseId = 3` and empty `outputBuffer`, if the private key pairing the public key is not in the secure storage.
* Response with `responseId = 4` and empty `outputBuffer`, if the hashed password doesn't match the hashed password protecting the private key.
