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
from ...gui.qt.password_dialog import PasswordLayout
from ...gui.qt.qrtextedit import ShowQRTextEdit
from ...gui.qt.util import WindowModalDialog, Buttons, CancelButton, WWLabel


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
                    _, p = add_pubkey(main_window)
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
