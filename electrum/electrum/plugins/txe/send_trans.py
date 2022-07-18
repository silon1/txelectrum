import os, subprocess

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel, QPushButton
from electrum.gui.qt import ElectrumWindow
from electrum.gui.qt.util import PasswordLineEdit
from electrum.i18n import _
from electrum.transaction import PartialTransaction

from electrum.gui.qt.password_dialog import PasswordDialog


class Pwd:
    p = None


def send_trans(tx: PartialTransaction):
    # c = Commands(config=Pwd.main_window.config,
    #              daemon=Pwd.main_window.gui_object.daemon,
    #              network=Pwd.main_window.network)
    # res = c.broadcast(tx)

    try:
        p = '\\'.join(os.path.abspath(__file__).split('\\')[:-1])
        print(tx)
        res = subprocess.check_output(fr"python {p}\..\..\..\run_electrum broadcast --testnet {tx}", shell=True)
    except subprocess.CalledProcessError as e:
        Pwd.main_window.show_message(_(f"{e.stdout}"))
        res = e.stdout
    finally:
        return res