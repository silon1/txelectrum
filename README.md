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

Create/open a standard wallet, activates the plugin, and reopen Electrum.  
