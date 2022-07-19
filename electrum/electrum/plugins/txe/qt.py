import inspect

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QMessageBox, QLabel, QVBoxLayout, QPushButton, QWidget, QGridLayout
import base58

import electrum
from types import MethodType

from electrum.gui.qt import ElectrumWindow
from electrum.plugin import BasePlugin, hook

from .overrided_funcs import _Abstract_Wallet, _SendTab
from electrum.i18n import _

from .send_trans import Pwd
from .txe_client import create_keypair
from ...gui.qt.password_dialog import PasswordDialog, PasswordLayout
from ...gui.qt.qrtextedit import ShowQRTextEdit
from ...gui.qt.util import WindowModalDialog, Buttons, CancelButton, OkButton, PasswordLineEdit, WWLabel


def create_pwd(win):
    d = WindowModalDialog(win.top_level_window())

    ok = QPushButton(_("Next"), d)
    ok.clicked.connect(d.accept)
    ok.setEnabled(False)
    pl = PasswordLayout(_('Please create new password'), None, ok)
    pl.encrypt_cb.setChecked(False)
    pl.encrypt_cb.setVisible(False)
    pl.new_pw.textChanged.connect(lambda: ok.setEnabled(ok.isEnabled() and bool(pl.new_pw.text())))

    vbox = QVBoxLayout()
    vbox.addLayout(pl.layout())
    vbox.addLayout(Buttons(CancelButton(d), ok))
    d.setLayout(vbox)

    return d.exec_(), pl.new_pw.text()


def show_pubkey(win, pubkey):
    dialog = WindowModalDialog(win.top_level_window())

    vbox = QVBoxLayout()

    mpk_text = ShowQRTextEdit(pubkey, config=win.config)
    mpk_text.setMaximumHeight(150)
    mpk_text.addCopyButton()

    vbox.addWidget(WWLabel(_("Master Public Key")))
    vbox.addWidget(mpk_text)

    vbox.addLayout(Buttons(CancelButton(dialog)))
    dialog.setLayout(vbox)
    dialog.exec_()
    dialog.close()


class Plugin(BasePlugin):
    def __init__(self, parent, config: 'SimpleConfig', name):
        super().__init__(parent, config, name)

    @hook
    def load_wallet(self, wallet: electrum.wallet.Abstract_Wallet, main_window: ElectrumWindow):
        Pwd.main_window = main_window
        Pwd.pwd_d = PasswordDialog(main_window)
        keys = wallet.keystore

        if any([keys.seed, keys.xprv]) or not wallet.is_watching_only():
            choice = Pwd.main_window.question("This plugin effects only on watch only wallets.\n"
                                              "Create new watch only wallet and transfer your coins to it.\n"
                                              "Create new key pairs?")
            if choice:
                f, p = create_pwd(main_window)
                if not f:
                    return
                pubkey = create_keypair(p)
                # pubkey = base58.b58decode(pubkey)
                show_pubkey(main_window, pubkey)

        wallet.is_watching_only = MethodType(_Abstract_Wallet.is_watching_only, wallet)

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
    def tc_sign_wrapper(self, wallet: electrum.wallet.Standard_Wallet, tx, on_success, on_failure):
        wallet.sign_transaction = MethodType(_Abstract_Wallet.sign_transaction, wallet)
