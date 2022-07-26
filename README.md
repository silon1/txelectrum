# txelectrum

## Getting Started

This project is built from two parts:
1. Electrum plugin.
2. secp256k1 signer server.

### Build and run the secp256k1 signer server & applet

**We assume you have already installed DAL.**

To run the TXE signer server, you have to complete the following steps:
1. Open the applet project in Eclipse. (Project directory `./txe/secp256k1_signer`.)
2. Build the applet. (Press on the shield button with the play icon.)
3. Open the host project in Visual Studio. (Project directory `./txe/secp256k1_signer_server`.)
4. Change the build configuration from `Debug` to `Amulet`.
5. Build and run the host. (Press the play button.)

### Build and run the electrum TXE plugin

You have the following options to run the electrum TXE plugin:
* Build and run the repository's electrum.
* Use already installed electrum. (Note: it's not working on portable electrum.)

#### Build and run electrum
To bulid and run electrum, you have to complete the following steps:
1. Create python virtual environment at `./electrum`. (Optional)
2. Follow the steps in [Electrum's Readme](./electrum/README.md).
3. Install the requirements file at `./requirements.txt`.
4. Install the requirements file at `./electrum/contrib/requirements/requirements.txt`.
5. Run `$ python ./electrum/run_electrum [--testnet]`

#### Use already installed electrum
Just copy the files at `./electrum/electrum/plugins/txe` into the instalation folder. (**Note: This wasn't tested.**)

---
## How to use
This project implements the following features:
* Create a wallet in the TXE.
* Sign a transaction from the TXE.

**Note: The plugin is a proof of concept, hence we haven't developed the user experience.**

### Create a wallet
Complete the following steps to create a new wallet:
1. Create a new dummy standard wallet.
2. Press `yes` button on the new window to create a new wallet inside the TXE.
3. Enter a new password for the new wallet.
4. Copy the public key and the bitcoin address from the new window.
5. Create a new imported address wallet (`File > New/Restore`).
6. Paste the copied bitcoin address.

### Sign a transaction
Complete the following steps to sign and broadcast a transaction:
1. Go to `Send` tab.
2. Insert the reciever bitcoin address and the amount to pay.
3. Press `Pay` button.
4. Enter the password.
5. Press `Send` to sign and broadcast the transaction.
6. Press `Close` on the new opened window.
