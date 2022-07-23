import inspect

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QMessageBox, QLabel, QVBoxLayout, QPushButton, QWidget, QGridLayout, QLineEdit, QHBoxLayout, \
    QPlainTextEdit, QTextEdit
import base58

import electrum
from types import MethodType

from electrum.gui.qt import ElectrumWindow
from electrum.plugin import BasePlugin, hook

from .keys import genaddr
from .overrided_funcs import _Abstract_Wallet, _SendTab
from electrum.i18n import _

from .send_trans import Pwd
from .txe_client import create_keypair
from ...gui.qt.password_dialog import PasswordDialog, PasswordLayout
from ...gui.qt.qrtextedit import ShowQRTextEdit
from ...gui.qt.util import WindowModalDialog, Buttons, CancelButton, OkButton, PasswordLineEdit, WWLabel
from ...transaction import PartialTransaction, Transaction


def add_pubkey(win):
    d = WindowModalDialog(win.top_level_window(), _('Add public key'))

    ok = QPushButton(_("Next"), d)
    ok.clicked.connect(d.accept)
    ok.setEnabled(False)

    pk = QTextEdit()
    pk.toPlainText()
    pk.textChanged.connect(lambda: ok.setEnabled(bool(pk.toPlainText())))

    vbox = QVBoxLayout()
    vbox.addWidget(pk)
    vbox.addLayout(Buttons(CancelButton(d), ok))
    d.setLayout(vbox)

    return d.exec_(), pk.toPlainText()


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
    dialog = WindowModalDialog(win.top_level_window(), _('Wallet info'))

    vbox = QVBoxLayout()

    pk = ShowQRTextEdit(pubkey, config=win.config)
    pk.setMaximumHeight(150)
    pk.addCopyButton()

    vbox.addWidget(WWLabel(_("Public Key")))
    vbox.addWidget(pk)

    addr = ShowQRTextEdit(genaddr(pubkey.encode(), 'testnet'), config=win.config)
    addr.setMaximumHeight(150)
    addr.addCopyButton()

    vbox.addWidget(WWLabel(_("Address")))
    vbox.addWidget(addr)

    vbox.addLayout(Buttons(CancelButton(dialog)))
    dialog.setLayout(vbox)
    dialog.exec_()
    dialog.close()


class Plugin(BasePlugin):
    def __init__(self, parent, config: 'SimpleConfig', name):
        super().__init__(parent, config, name)
        a = Transaction('020000000001016070f15c563238ee2e84ba795298407759fdb08df5ce4beb3c76a79079b6125b0100000000fdffffff0240420f00000000001976a91494b083576f267d1c1f076804be928b67a5ca2d7888aca8122200000000001600148ed861a1835027fcaf47b26c8ad9a2db93e31ece02473044022044f349e41df23b8e091f2953792ef2c8c991c566fcbbb97e65127e1eb0972d5402200ed168edbfe0f912508d5a2869d5e19c3c7f858d9c2eb636579856c3bd1c4e2e012103506b0e1d7a69f1919b39dd89dfda8abbe0e4ba3708a23021f20124f4254e190cdbe52200')
        b = a

    @hook
    def load_wallet(self, wallet: electrum.wallet.Abstract_Wallet, main_window: ElectrumWindow):
        keys = wallet.keystore

        if any([hasattr(keys, 'seed'), hasattr(keys, 'xprv')]):
            choice = main_window.question(_("This plugin affects only watch-only wallets.\n") +
                                          _("Notice that even though the wallet type is watch-only,"
                                            "you can send transactionsas usual because the TXE sign automatically.\n") +
                                          _("You can create new watch-only wallet and transfer your coins to it.\n") +
                                          _("Create new key pairs?"))
            # if choice:
            #     f, p = create_pwd(main_window)
            #     if not f:
            #         return
            #     pubkey = create_keypair(p)
            #     show_pubkey(main_window, pubkey)

        else:
            # p = '02f2dd109034c408433042ab0d237436ec62b5475ad87121ab607503c7d67d0895'
            # pk = {
            #     'type': 'imported',
            #     'keypairs': {p: p},
            # }
            # wallet.db.put('keystore', pk)
            if wallet.wallet_type == 'imported':
                wallet.txin_type = 'p2pkh'
                if not keys:
                    p = add_pubkey(main_window)
                    if p:
                        pk = {
                            'type': 'imported',
                            'keypairs': {p: p},
                        }
                        wallet.db.put('keystore', pk)


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
