import inspect

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QMessageBox, QLabel, QVBoxLayout, QPushButton
import base58

import electrum
from types import MethodType

from electrum.gui.qt import ElectrumWindow
from electrum.plugin import BasePlugin, hook

from .overrided_funcs import _Abstract_Wallet, _SendTab
from electrum.i18n import _

from .send_trans import Pwd
from .txe_client import create_keypair
from ...gui.qt.password_dialog import PasswordDialog
from ...gui.qt.util import WindowModalDialog, Buttons, CancelButton, OkButton, PasswordLineEdit


class Plugin(BasePlugin):
    def __init__(self, parent, config: 'SimpleConfig', name):
        super().__init__(parent, config, name)

    @hook
    def password_dialog(self, pw, grid, a):
        pass

    @hook
    def transaction_dialog(self, d: 'TxDialog'):
        pass

    @hook
    def transaction_dialog_update(self, d: 'TxDialog'):
        pass

    @hook
    def abort_send(self, send_tab):
        Pwd.send_tab = send_tab
        try:
            f = inspect.stack()[2]
            if f[3] != 'pay_onchain_dialog':
                return
            params = f.frame.f_locals
            send_tab = params['self']
            inputs = params['inputs']
            outputs = params['outputs']
            external_keypairs = params['external_keypairs']

            send_tab.pay_onchain_dialog = MethodType(_SendTab.pay_onchain_dialog, send_tab)
            send_tab.pay_onchain_dialog(inputs, outputs, external_keypairs=external_keypairs)
        except:
            pass
        return 1


    @hook
    def load_wallet(self, wallet: electrum.wallet.Abstract_Wallet, main_window: ElectrumWindow):
        Pwd.main_window = main_window
        Pwd.pwd_d = PasswordDialog(main_window)
        keys = wallet.keystore


        # dialog = WindowModalDialog(main_window.top_level_window(), _("Enter PIN"))
        #
        # vbox = QVBoxLayout()
        # pos = vbox.geometry()
        #
        # p = PasswordLineEdit()
        # vbox.addWidget(QLabel('Password'))
        # vbox.addWidget(p)
        #
        # send_button = QPushButton('Send')
        # send_button.clicked.connect(lambda : print(p.text()))
        # vbox.addWidget(send_button)
        #
        # vbox.addLayout(Buttons(CancelButton(dialog), OkButton(dialog)))
        # dialog.setLayout(vbox)
        # dialog.exec_()
        # dialog.close()



        if any([keys.seed, keys.xprv]) or not wallet.is_watching_only():
            choise = Pwd.main_window.question("This plugin effects only on watch only wallets.\n"
                                               "Create new watch only wallet and transfer your coins to it.\n"
                                               "Create new key pairs?")
            # if choise:
            #     pubkey = create_keypair()
            #     pubkey = base58.b58decode(pubkey)
            #     Pwd.main_window.show_message(pubkey, title='New master pubkey')

    @hook
    def tc_sign_wrapper(self, wallet: electrum.wallet.Standard_Wallet, tx, on_success, on_failure):
        wallet.sign_transaction = MethodType(_Abstract_Wallet.sign_transaction, wallet)
