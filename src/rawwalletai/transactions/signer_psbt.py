"""PSBT signing with ECDSA."""

from __future__ import annotations

import hashlib
from typing import Optional

from rawwalletai.chains.bitcoin import BitcoinChain
from rawwalletai.core.keys import KeyManager
from rawwalletai.storage.encrypted import EncryptedStorage
from rawwalletai.transactions.psbt import PSBT, PSBTInput, PSBTOutput
from rawwalletai.transactions.signer import ECKey


def _double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


class PSBTSigner:
    """Signs PSBTs with ECDSA for P2WPKH."""

    def __init__(self, key_manager: KeyManager, chain: BitcoinChain) -> None:
        self.key_manager = key_manager
        self.chain = chain

    def sign_psbt(self, psbt: PSBT, private_key_bytes: bytes) -> PSBT:
        """Sign all inputs in a PSBT."""
        ec_key = ECKey(private_key_bytes)
        public_key_bytes = ec_key.public_key_bytes()
        for i, inp in enumerate(psbt.inputs):
            sighash = self._sighash_all(psbt, i)
            signature = ec_key.sign(sighash)
            # Append sighash type (0x01) to signature
            signature += b"\x01"
            inp.signature = signature
            inp.public_key = public_key_bytes
        psbt._signed = True
        return psbt

    def _sighash_all(self, psbt: PSBT, input_index: int) -> bytes:
        """Compute SIGHASH_ALL for a PSBT input."""
        tx_copy = self._serialize_tx_for_signing(psbt, input_index)
        return _double_sha256(tx_copy)

    def _serialize_tx_for_signing(self, psbt: PSBT, input_index: int) -> bytes:
        """Serialize transaction for signing (SIGHASH_ALL)."""
        version = (1).to_bytes(4, "little")
        input_count = bytes([len(psbt.inputs)])
        inputs = b""
        for i, inp in enumerate(psbt.inputs):
            if i == input_index:
                # Signing input: empty scriptSig, sequence = 0xFFFFFFFF
                inputs += inp.txid[::-1] + inp.vout.to_bytes(4, "little")
                inputs += b"\x00" * 34  # empty scriptSig
                inputs += (0xFFFFFFFF).to_bytes(4, "little")
            else:
                # Other inputs: empty scriptSig, keep sequence
                inputs += inp.txid[::-1] + inp.vout.to_bytes(4, "little")
                inputs += b"\x00" * 34
                inputs += (0xFFFFFFFF).to_bytes(4, "little")
        output_count = bytes([len(psbt.outputs)])
        outputs = b""
        for out in psbt.outputs:
            outputs += out.amount_sats.to_bytes(8, "little")
            outputs += bytes([len(out.script_pubkey)]) + out.script_pubkey
        locktime = (0).to_bytes(4, "little")
        sighash_all = (1).to_bytes(4, "little")
        return version + input_count + inputs + output_count + outputs + locktime + sighash_all
