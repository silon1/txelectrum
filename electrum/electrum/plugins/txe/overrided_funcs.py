import copy
from types import MethodType
from typing import List, Sequence

import electrum.wallet
from electrum.crypto import sha256d
from electrum.keystore import Software_KeyStore
from electrum.transaction import PartialTransaction, Sighash
from electrum.util import UserCancelled, bfh, bh2u

from .send_trans import send_trans, Pwd, TX
from .txe_client import txe_sign
from ...gui.qt.confirm_tx_dialog import ConfirmTxDialog
from ...gui.qt.transaction_dialog import PreviewTxDialog
from ...i18n import _
from ...transaction import PartialTxInput, PartialTxOutput
from ...util import parse_max_spend


class _ConfirmTxDialog:
    """
    Override ConfirmTxDialog on_send
    """

    @staticmethod
    def on_send(self):
        self.is_send = True
        self.accept()


class PublicKeyNotFoundException(Exception):
    def __init__(self, msg="publickey not found"):
        super().__init__(msg)


class _SendTab:
    """
    Override SendTab pay_onchain_dialog
    """

    @staticmethod
    def pay_onchain_dialog(
            self, inputs: Sequence[PartialTxInput],
            outputs: List[PartialTxOutput], *,
            external_keypairs=None) -> None:
        is_sweep = bool(external_keypairs)
        make_tx = lambda fee_est: self.wallet.make_unsigned_transaction(
            coins=inputs,
            outputs=outputs,
            fee=fee_est,
            is_sweep=is_sweep)
        output_values = [x.value for x in outputs]
        if any(parse_max_spend(outval) for outval in output_values):
            output_value = '!'
        else:
            output_value = sum(output_values)

        conf_dlg = ConfirmTxDialog(window=self.window, make_tx=make_tx, output_value=output_value, is_sweep=is_sweep)
        conf_dlg.password_required = True
        conf_dlg.pw_label.setVisible(True)
        conf_dlg.pw.setVisible(True)

        conf_dlg.message_label.setText(_('Enter your password to proceed'))

        conf_dlg.send_button.clicked.disconnect(conf_dlg.on_send)
        conf_dlg.on_send = MethodType(_ConfirmTxDialog.on_send, conf_dlg)
        conf_dlg.send_button.clicked.connect(conf_dlg.on_send)

        if conf_dlg.not_enough_funds:
            # Check if we had enough funds excluding fees,
            # if so, still provide opportunity to set lower fees.
            if not conf_dlg.have_enough_funds_assuming_zero_fees():
                text = self.get_text_not_enough_funds_mentioning_frozen()
                self.show_message(text)
                return

        # shortcut to advanced preview (after "enough funds" check!)
        if self.config.get('advanced_preview'):
            preview_dlg = PreviewTxDialog(
                window=self.window,
                make_tx=make_tx,
                external_keypairs=external_keypairs,
                output_value=output_value)
            preview_dlg.show()
            return

        cancelled, is_send, password, tx = conf_dlg.run()
        Pwd.p = password
        if is_send:
            self.save_pending_invoice()

            def sign_done(success):
                if success:
                    self.window.broadcast_or_show(tx)

            self.window.sign_tx_with_password(
                tx,
                callback=sign_done,
                password=password,
                external_keypairs=external_keypairs,
            )
        else:
            preview_dlg = PreviewTxDialog(
                window=self.window,
                make_tx=make_tx,
                external_keypairs=external_keypairs,
                output_value=output_value)
            preview_dlg.show()


class _Abstract_Wallet:
    @staticmethod
    def is_watching_only(self):
        """
        Override Abstract_Wallet is_watching_only
        """
        return False

    @staticmethod
    def sign_transaction(self: electrum.wallet.Abstract_Wallet, tx: PartialTransaction, password):
        """
        Override Abstract_Wallet sign_transaction
        """

        if not isinstance(tx, PartialTransaction):
            return

        pk = self.db.get('keystore').get('keypairs')
        if not pk:
            raise PublicKeyNotFoundException()
        for i in tx.inputs():
            i.pubkeys = [bytes.fromhex(k) for k in pk.keys()]

        swap = self.lnworker.swap_manager.get_swap_by_tx(tx) if self.lnworker else None
        if swap:
            self.lnworker.swap_manager.sign_tx(tx, swap)
            return

        tmp_tx = copy.deepcopy(tx)
        tmp_tx.add_info_from_wallet(self, include_xpubs=True)

        for k in sorted(self.get_keystores(), key=lambda ks: ks.ready_to_sign(), reverse=True):
            try:
                k.sign_transaction = MethodType(_Software_KeyStore.sign_transaction, k)
                k.sign_transaction(tmp_tx, password)
            except UserCancelled:
                continue

        tmp_tx.remove_xpubs_and_bip32_paths()
        tx.combine_with_other_psbt(tmp_tx)
        tx.add_info_from_wallet(self, include_xpubs=False)
        send_trans(TX.from_tx(tx).create())


class _Software_KeyStore:
    @staticmethod
    def sign_transaction(self: Software_KeyStore, tx, _):
        """
        Override Software_KeyStore sign_transaction
        """
        keypairs = self._get_tx_derivations(tx)
        if keypairs:
            tx.sign = MethodType(_PartialTransaction.sign, tx)
            tx.sign(keypairs)


class _PartialTransaction:
    @staticmethod
    def sign(self: PartialTransaction, keypairs) -> None:
        """
        Override PartialTransaction sign
        """
        # keypairs:  pubkey_hex -> (0, 0)
        bip143_shared_txdigest_fields = self._calc_bip143_shared_txdigest_fields()
        for i, txin in enumerate(self.inputs()):
            pubkeys = [pk.hex() for pk in txin.pubkeys]
            for pubkey in pubkeys:
                if txin.is_complete():
                    break
                if pubkey not in keypairs:
                    continue
                # _logger.info(f"adding signature for {pubkey}")\
                self.sign_txin = MethodType(_PartialTransaction.sign_txin, self)
                sig = self.sign_txin(i, pubkey, bip143_shared_txdigest_fields=bip143_shared_txdigest_fields)
                self.add_signature_to_txin(txin_idx=i, signing_pubkey=pubkey, sig=sig)

        # _logger.debug(f"is_complete {self.is_complete()}")
        self.invalidate_ser_cache()

    @staticmethod
    def sign_txin(self: PartialTransaction, txin_index, pubkey, *, bip143_shared_txdigest_fields=None) -> str:
        """
        Override PartialTransaction sign_txin
        """
        txin = self.inputs()[txin_index]
        txin.validate_data(for_signing=True)
        txin.script_type = 'p2pkh'
        sighash = txin.sighash if txin.sighash is not None else Sighash.ALL
        sighash_type = sighash.to_bytes(length=1, byteorder="big").hex()
        pre_hash = sha256d(bfh(self.serialize_preimage(txin_index,
                                                       bip143_shared_txdigest_fields=bip143_shared_txdigest_fields)))
        sig = txe_sign(pre_hash, Pwd.p, pubkey)
        sig = bh2u(sig) + sighash_type
        return sig
