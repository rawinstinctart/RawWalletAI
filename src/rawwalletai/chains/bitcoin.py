"""Bitcoin chain adapter with UTXO backend."""

from __future__ import annotations

import hashlib

from bech32 import bech32_encode, convertbits

from rawwalletai.chains.utxo_backends import UTXOBackend


def _double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


class BitcoinAddress:
    def __init__(self, address: str, script_type: str, script_pubkey: bytes, path: str | None = None):
        self.address = address
        self.script_type = script_type
        self.script_pubkey = script_pubkey
        self.path = path


class BitcoinChain:
    """Bitcoin chain adapter with UTXO backend."""

    def __init__(self, network: str, backend: UTXOBackend | None = None):
        self.network = network
        self.backend = backend
        if network == "bitcoin":
            self.bech32_hrp = "bc"
        elif network == "testnet":
            self.bech32_hrp = "tb"
        else:
            raise ValueError(f"Unknown network: {network}")

    def generate_address(self, public_key_bytes: bytes, script_type: str = "p2wpkh") -> BitcoinAddress:
        if script_type == "p2wpkh":
            pubkey_hash = hashlib.sha256(public_key_bytes).digest()[:20]
            witness_version = 0
            data = [witness_version] + list(pubkey_hash)
            bits5 = convertbits(data, 8, 5)
            address = bech32_encode(self.bech32_hrp, bits5)
            script_pubkey = bytes([0, 20]) + pubkey_hash
        elif script_type == "p2pkh":
            pubkey_hash = hashlib.sha256(public_key_bytes).digest()[:20]
            address = self._encode_base58(pubkey_hash, version=0)
            script_pubkey = bytes([0, 20]) + pubkey_hash
        elif script_type == "p2sh":
            pubkey_hash = hashlib.sha256(public_key_bytes).digest()[:20]
            redeem_script_hash = hashlib.sha256(hashlib.sha256(bytes([0, 20]) + pubkey_hash).digest()).digest()[:20]
            address = self._encode_base58(redeem_script_hash, version=5)
            script_pubkey = bytes([0, 20]) + redeem_script_hash
        else:
            raise ValueError(f"Unsupported script type: {script_type}")
        return BitcoinAddress(address=address, script_type=script_type, script_pubkey=script_pubkey)

    def _encode_base58(self, data: bytes, version: int | None = None) -> str:
        import base58
        if version is not None:
            data = bytes([version]) + data
        checksum = _double_sha256(data)[:4]
        return base58.b58encode(data + checksum).decode()
