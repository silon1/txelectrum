import os, subprocess

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
    version = '02000000'
    txin_count = '01'
    txin_out_index = '00' * 4
    txin_sig_script_len = '49'
    push_72 = '48'
    seq_count = 'ff' * 4
    txout_count = '01'
    txout_sig_script_len = '19'
    dup = '76'
    hash_160 = 'a9'
    push_20 = '14'
    eq = '88'
    check_sig = 'ac'

    def __init__(self, txin_out_id, txin_sig, txout_sat, txout_pk_hash, lock_time):
        self.txin_out_id = txin_out_id
        self.txin_sig = txin_sig
        self.txout_sat = txout_sat
        self.txout_pk_hash = txout_pk_hash
        self.lock_time = lock_time

    @staticmethod
    def from_tx(tx: PartialTransaction):
        tx = tx.to_json()
        txin = tx['inputs'][0]
        txout = tx['outputs'][0]
        ith = lambda i: '0' * (len(s := hex(i)[2:]) % 2) + s
        return TX(txin['prevout_hash'],
                  [s for s in tx['inputs'][0]['part_sigs'].values()][0],
                  ith(txout['value_sats']).zfill(16),
                  txout['scriptpubkey'],
                  ith(tx['locktime']))

    def create(self):
        return TX.version + \
               TX.txin_count + \
               self.txin_out_id + \
               TX.txin_out_index + \
               TX.txout_sig_script_len + \
               TX.push_72 + \
               self.txin_sig + \
               TX.seq_count + \
               TX.txout_count + \
               self.txout_sat + \
               TX.txout_sig_script_len + \
               TX.dup + \
               TX.hash_160 + \
               TX.push_20 + \
               self.txout_pk_hash + \
               TX.eq + \
               TX.check_sig + \
               self.lock_time
