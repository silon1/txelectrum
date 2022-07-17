import electrum
from types import MethodType

from electrum.gui.qt import ElectrumWindow
from electrum.plugin import BasePlugin, hook

from .overrided_funcs import _Abstract_Wallet
from electrum.i18n import _

from .send_trans import Data


class Plugin(BasePlugin):
    def __init__(self, parent, config: 'SimpleConfig', name):
        super().__init__(parent, config, name)

    @hook
    def load_wallet(self, wallet: electrum.wallet.Abstract_Wallet, main_window: ElectrumWindow):
        Data.main_window = main_window
        keys = wallet.keystore

        if any([keys.seed, keys.xprv]) or not wallet.is_watching_only():
            Data.main_window.show_error("This plugin effects only on watch only wallets.\n"
                                        "Create new watch only wallet and transfer your coins to it.")

    @hook
    def tc_sign_wrapper(self, wallet: electrum.wallet.Standard_Wallet, tx, on_success, on_failure):
        wallet.sign_transaction = MethodType(_Abstract_Wallet.sign_transaction, wallet)
