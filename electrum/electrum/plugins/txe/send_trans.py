import os, subprocess
import textwrap

from electrum.transaction import PartialTransaction


class Pwd:
    p = None


def send_trans(tx):
    # c = Commands(config=Pwd.main_window.config,
    #              daemon=Pwd.main_window.gui_object.daemon,
    #              network=Pwd.main_window.network)
    # res = c.broadcast(tx)

    try:
        p = '\\'.join(os.path.abspath(__file__).split('\\')[:-1])
        print(tx)
        res = subprocess.check_output(fr"python {p}\..\..\..\run_electrum broadcast --testnet {tx}", shell=True)
    except subprocess.CalledProcessError as e:
        res = e.stdout
        print(res)
    finally:
        return res


class TX:
    version_zf = 4 * 2
    sat_zf = 8 * 2
    txin_index_zf = 4 * 2
    flags = 'fdffffff'
    locktime_zf = 4 * 2

    def __init__(self, version, txins, txouts, lock_time):
        self.version = ith(version, True, TX.version_zf)
        self.txins = txins
        self.txouts = txouts
        self.lock_time = ith(lock_time, True, TX.locktime_zf)

    def _in(self):
        utxo = ith(len(self.txins))
        for i in self.txins:
            utxo += lendian(i['prevout_hash'])
            utxo += ith(i['prevout_n'], True, zf=TX.txin_index_zf)
            sig = ''
            for k, s in i['part_sigs'].items():
                sig += lth(s)
                sig += s
                sig += lth(k)
                sig += k
                sig = lth(sig) + sig
            utxo += sig
            utxo += TX.flags
        return utxo

    def _out(self):
        s = ith(len(self.txouts))
        for o in self.txouts:
            s += ith(o['value_sats'], True, TX.sat_zf)
            s += lth(o['scriptpubkey'], zf=2)
            s += o['scriptpubkey']
        return s

    @staticmethod
    def from_tx(tx: PartialTransaction):
        tx = tx.to_json()
        version = tx['version']
        txins = tx['inputs']
        txouts = tx['outputs']
        locktime = tx['locktime']
        return TX(version, txins, txouts, locktime)

    def create(self):
        return self.version + self._in() + self._out() + self.lock_time


def lendian(x):
    return ''.join(textwrap.wrap(x, 2)[::-1])


def ith(i, little=False, zf=0):
    x = '0' * (len(s := hex(i)[2:]) % 2) + s
    x = x.zfill(zf) if zf else x
    return lendian(x) if little else x


def lth(s, zf=2):
    return ith(int(len(s) // 2), True, zf)
