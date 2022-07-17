def sign_transaction(self, tx: Transaction, password) -> Optional[PartialTransaction]:
    """Abstract_Wallet"""
    if self.is_watching_only():
        return
    if not isinstance(tx, PartialTransaction):
        return
    # note: swap signing does not require the password
    swap = self.lnworker.swap_manager.get_swap_by_tx(tx) if self.lnworker else None
    if swap:
        self.lnworker.swap_manager.sign_tx(tx, swap)
        return
    # add info to a temporary tx copy; including xpubs
    # and full derivation paths as hw keystores might want them
    tmp_tx = copy.deepcopy(tx)
    tmp_tx.add_info_from_wallet(self, include_xpubs=True)
    # sign. start with ready keystores.
    # note: ks.ready_to_sign() side-effect: we trigger pairings with potential hw devices.
    #       We only do this once, before the loop, however we could rescan after each iteration,
    #       to see if the user connected/disconnected devices in the meantime.
    for k in sorted(self.get_keystores(), key=lambda ks: ks.ready_to_sign(), reverse=True):
        try:
            if k.can_sign(tmp_tx):
                k.sign_transaction(tmp_tx, password)
        except UserCancelled:
            continue
    # remove sensitive info; then copy back details from temporary tx
    tmp_tx.remove_xpubs_and_bip32_paths()
    tx.combine_with_other_psbt(tmp_tx)
    tx.add_info_from_wallet(self, include_xpubs=False)
    return tx


def sign_transaction(self, tx, password):
    """Software_KeyStore"""
    if self.is_watching_only():
        return
    # Raise if password is not correct.
    self.check_password(password)
    # Add private keys
    keypairs = self._get_tx_derivations(tx)
    for k, v in keypairs.items():
        keypairs[k] = self.get_private_key(v, password)
    # Sign
    if keypairs:
        tx.sign(keypairs)


def sign(self, keypairs) -> None:
    """PartialTransaction"""
    # keypairs:  pubkey_hex -> (secret_bytes, is_compressed)
    bip143_shared_txdigest_fields = self._calc_bip143_shared_txdigest_fields()
    for i, txin in enumerate(self.inputs()):
        pubkeys = [pk.hex() for pk in txin.pubkeys]
        for pubkey in pubkeys:
            if txin.is_complete():
                break
            if pubkey not in keypairs:
                continue
            _logger.info(f"adding signature for {pubkey}")
            sec, compressed = keypairs[pubkey]
            sig = self.sign_txin(i, sec, bip143_shared_txdigest_fields=bip143_shared_txdigest_fields)
            self.add_signature_to_txin(txin_idx=i, signing_pubkey=pubkey, sig=sig)

    _logger.debug(f"is_complete {self.is_complete()}")
    self.invalidate_ser_cache()


def sign_txin(self, txin_index, privkey_bytes, *, bip143_shared_txdigest_fields=None) -> str:
    """PartialTransaction"""
    txin = self.inputs()[txin_index]
    txin.validate_data(for_signing=True)
    sighash = txin.sighash if txin.sighash is not None else Sighash.ALL
    sighash_type = sighash.to_bytes(length=1, byteorder="big").hex()
    pre_hash = sha256d(bfh(self.serialize_preimage(txin_index,
                                                   bip143_shared_txdigest_fields=bip143_shared_txdigest_fields)))
    privkey = ecc.ECPrivkey(privkey_bytes)
    sig = privkey.sign_transaction(pre_hash)
    sig = bh2u(sig) + sighash_type
    return sig
