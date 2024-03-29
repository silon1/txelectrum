import inspect

from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QTextEdit

import electrum
from types import MethodType

from electrum.gui.qt import ElectrumWindow
from electrum.plugin import BasePlugin, hook

from .keys import genaddr
from .overrided_funcs import _Abstract_Wallet, _SendTab
from electrum.i18n import _

from .send_trans import Pwd
from .txe_client import create_keypair
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

    addr = ShowQRTextEdit(genaddr(bytes.fromhex(pubkey), 'testnet'), config=win.config)
    addr.setMaximumHeight(150)
    addr.addCopyButton()

    vbox.addWidget(WWLabel(_("Address")))
    vbox.addWidget(addr)

    vbox.addLayout(Buttons(CancelButton(dialog)))
    dialog.setLayout(vbox)
    dialog.exec_()
    dialog.close()


class Plugin(BasePlugin):
    wallet_type = 'imported'

    def __init__(self, parent, config: 'SimpleConfig', name):
        super().__init__(parent, config, name)

    @staticmethod
    def use_plugin(wallet_type):
        return wallet_type == Plugin.wallet_type

    @hook
    def load_wallet(self, wallet: electrum.wallet.Abstract_Wallet, main_window: ElectrumWindow):
        keys = wallet.keystore
        wtype = wallet.wallet_type

        if any([hasattr(keys, 'seed'), hasattr(keys, 'xprv')]) or not self.use_plugin(wtype):
            choice = main_window.question(_("This plugin affects only on (address) imported wallets.\n") +
                                          _("You can create new a (address) imported wallet and transfer your coins to it.\n\n") +
                                          _("Notice that even though the wallet type is (address) imported, "
                                            "you will be able to send transactions as usual because of the TXE sign "
                                            "automatically.\n\n") +
                                          _("Create new key pairs?"))
            if choice:
                f, p = create_pwd(main_window)
                if not f:
                    return
                pubkey = create_keypair(p).lower()
                show_pubkey(main_window, pubkey)

        else:
            if self.use_plugin(wtype):
                wallet.txin_type = 'p2pkh'
                if not keys:
                    f, p = add_pubkey(main_window)
                    if f:
                        pk = {
                            'type': 'imported',
                            'keypairs': {p: p},
                        }
                        wallet.db.put('keystore', pk)
                wallet.is_watching_only = MethodType(_Abstract_Wallet.is_watching_only, wallet)

    @hook
    def abort_send(self, send_tab):
        if not self.use_plugin(send_tab.wallet.wallet_type):
            return
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
        if not self.use_plugin(wallet.wallet_type):
            return
        wallet.sign_transaction = MethodType(_Abstract_Wallet.sign_transaction, wallet)
