from PyQt5.QtWidgets import QMessageBox
import base58

import electrum
from types import MethodType

from electrum.gui.qt import ElectrumWindow
from electrum.plugin import BasePlugin, hook

from .overrided_funcs import _Abstract_Wallet
from electrum.i18n import _

from .send_trans import Data
from .txe_client import create_keypair


class Plugin(BasePlugin):
    def __init__(self, parent, config: 'SimpleConfig', name):
        super().__init__(parent, config, name)

    @hook
    def load_wallet(self, wallet: electrum.wallet.Abstract_Wallet, main_window: ElectrumWindow):
        Data.main_window = main_window
        keys = wallet.keystore

        if any([keys.seed, keys.xprv]) or not wallet.is_watching_only():
            choise = Data.main_window.question("This plugin effects only on watch only wallets.\n"
                                               "Create new watch only wallet and transfer your coins to it.\n"
                                               "Create new key pairs?")
            if choise:
                pubkey = create_keypair()
                pubkey = base58.b58decode(pubkey)
                Data.main_window.show_message(pubkey, title='New master pubkey')

    @hook
    def tc_sign_wrapper(self, wallet: electrum.wallet.Standard_Wallet, tx, on_success, on_failure):
        wallet.sign_transaction = MethodType(_Abstract_Wallet.sign_transaction, wallet)
