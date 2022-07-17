import os, subprocess

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel, QPushButton
from electrum.gui.qt import ElectrumWindow
from electrum.gui.qt.util import PasswordLineEdit
from electrum.i18n import _
from electrum.transaction import PartialTransaction


class Data:
    main_window: ElectrumWindow = None
    pwd = None

    @staticmethod
    def get_pwd():
        PwdForm.new()
        pwd = Data.pwd
        Data.pwd = None
        return pwd


class PwdForm(QWidget):
    @staticmethod
    def new():
        app = QApplication([1])
        f = PwdForm()
        f.show()
        app.exec_()

    def __init__(self):
        super().__init__()
        self.resize(200, 120)
        grid = QGridLayout()

        self.pwd_label = QLabel('Password')
        self.pwd = PasswordLineEdit()
        grid.addWidget(self.pwd_label)
        grid.addWidget(self.pwd)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.on_send)
        grid.addWidget(self.send_button)

        self.setLayout(grid)

    def on_send(self):
        Data.pwd = self.pwd.text()
        self.close()


def send_trans(tx: PartialTransaction):
    # c = Commands(config=Data.main_window.config,
    #              daemon=Data.main_window.gui_object.daemon,
    #              network=Data.main_window.network)
    # res = c.broadcast(tx)

    try:
        p = '\\'.join(os.path.abspath(__file__).split('\\')[:-1])
        print(tx)
        res = subprocess.check_output(fr"python {p}\..\..\..\run_electrum broadcast --testnet {tx}", shell=True)
    except subprocess.CalledProcessError as e:
        Data.main_window.show_message(_(f"{e.stdout}"))
        res = e.stdout
    finally:
        return res