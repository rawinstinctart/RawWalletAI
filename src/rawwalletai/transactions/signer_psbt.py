"""PSBT signing with ECDSA."""

from __future__ import annotations

import hashlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from rawwalletai.transactions.psbt import PSBT


def _double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


class ECKey:
    """ECDSA private key wrapper for SECP256K1."""

    def __init__(self, private_key_bytes: bytes) -> None:
        if len(private_key_bytes) != 32:
            raise ValueError("Private key must be exactly 32 bytes")
        self._private_key = ec.derive_private_key(
            int.from_bytes(private_key_bytes, "big"),
            ec.SECP256K1(),
            default_backend()
        )
        self._public_key = self._private_key.public_key()

    def public_key_bytes(self) -> bytes:
        numbers = self._public_key.public_numbers()
        x = numbers.x.to_bytes(32, "big")
        prefix = b"\x02" if numbers.y % 2 == 0 else b"\x03"
        return prefix + x

    def sign(self, message_hash: bytes) -> bytes:
        return self._private_key.sign(
            message_hash,
            ec.ECDSA(hashes.SHA256())
        )

    @staticmethod
    def verify(public_key_bytes: bytes, message_hash: bytes, signature: bytes) -> bool:
        try:
            public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256K1(),
                public_key_bytes
            )
            public_key.verify(signature, message_hash, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False


class PSBTSigner:
    """Signs PSBTs with ECDSA for P2WPKH."""

    def __init__(self) -> None:
        pass

    def sign_psbt(self, psbt: PSBT, private_key_bytes: bytes) -> PSBT:
        """Sign all inputs in a PSBT."""
        ec_key = ECKey(private_key_bytes)
        public_key_bytes = ec_key.public_key_bytes()
        for i, inp in enumerate(psbt.inputs):
            sighash = self._sighash_all(psbt, i)
            signature = ec_key.sign(sighash)
            inp.signature = signature
            inp.public_key = public_key_bytes
        psbt._signed = True
        return psbt

    def _sighash_all(self, psbt: PSBT, input_index: int) -> bytes:
        tx_copy = self._serialize_tx_for_signing(psbt, input_index)
        return _double_sha256(tx_copy)

    def _serialize_tx_for_signing(self, psbt: PSBT, input_index: int) -> bytes:
        version = (1).to_bytes(4, "little")
        input_count = bytes([len(psbt.inputs)])
        inputs = b""
        for i, inp in enumerate(psbt.inputs):
            inputs += inp.txid[::-1] + inp.vout.to_bytes(4, "little")
            if i == input_index:
                inputs += b"\x00" * 34  # empty scriptSig
                inputs += (0xFFFFFFFF).to_bytes(4, "little")
            else:
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
