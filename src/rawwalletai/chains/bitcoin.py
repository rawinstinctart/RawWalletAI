"""Bitcoin chain adapter."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

from bech32 import bech32_encode, bech32_decode, convertbits

from rawwalletai.config.settings import WalletSettings


def _hash160(data: bytes) -> bytes:
    """RIPEMD160(SHA256(data))."""
    sha256 = hashlib.sha256(data).digest()
    ripemd160 = hashlib.new("ripemd160", sha256).digest()
    return ripemd160


def _base58_encode(data: bytes) -> str:
    """Encode data in Base58."""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    num = int.from_bytes(data, "big")
    result = ""
    while num > 0:
        num, mod = divmod(num, 58)
        result = alphabet[mod] + result
    for byte in data:
        if byte == 0:
            result = "1" + result
        else:
            break
    return result or "1"


def _checksum(data: bytes) -> bytes:
    """Double SHA256 checksum, first 4 bytes."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]


NETWORKS = {
    "bitcoin": {
        "p2pkh_version": b"\x00",
        "p2sh_version": b"\x05",
        "bech32_hrp": "bc",
    },
    "testnet": {
        "p2pkh_version": b"\x6f",
        "p2sh_version": b"\xc4",
        "bech32_hrp": "tb",
    },
}


@dataclass
class BitcoinAddress:
    address: str
    script_type: str
    path: Optional[str] = None


class BitcoinChain:
    """Bitcoin chain adapter."""

    def __init__(self, network: str = "bitcoin") -> None:
        if network not in NETWORKS:
            raise ValueError(f"Unknown network: {network}")
        self.network = network
        self.params = NETWORKS[network]

    def generate_address(
        self, public_key_bytes: bytes, script_type: str = "p2wpkh"
    ) -> BitcoinAddress:
        """Generate a Bitcoin address from public key bytes."""
        if script_type == "p2pkh":
            return BitcoinAddress(
                address=self._p2pkh(public_key_bytes),
                script_type="p2pkh",
            )
        if script_type == "p2wpkh":
            return BitcoinAddress(
                address=self._p2wpkh(public_key_bytes),
                script_type="p2wpkh",
            )
        if script_type == "p2sh":
            return BitcoinAddress(
                address=self._p2sh(public_key_bytes),
                script_type="p2sh",
            )
        raise ValueError(f"Unsupported script type: {script_type}")

    def _p2pkh(self, public_key_bytes: bytes) -> str:
        """Legacy Pay-to-Public-Key-Hash address."""
        pubkey_hash = _hash160(public_key_bytes)
        payload = self.params["p2pkh_version"] + pubkey_hash
        checksum = _checksum(payload)
        return _base58_encode(payload + checksum)

    def _p2wpkh(self, public_key_bytes: bytes) -> str:
        """Native SegWit Pay-to-Witness-Public-Key-Hash address."""
        pubkey_hash = _hash160(public_key_bytes)
        witness_program = [0x00] + list(pubkey_hash)
        bits5 = convertbits(witness_program, 8, 5)
        return bech32_encode(self.params["bech32_hrp"], bits5)

    def _p2sh(self, public_key_bytes: bytes) -> str:
        """Pay-to-Script-Hash wrapping P2WPKH."""
        pubkey_hash = _hash160(public_key_bytes)
        redeem_script = bytes([0x00, 0x14]) + pubkey_hash
        script_hash = hashlib.sha256(redeem_script).digest()[:20]
        payload = self.params["p2sh_version"] + script_hash
        checksum = _checksum(payload)
        return _base58_encode(payload + checksum)

    def estimate_fee(self, target_blocks: int = 6) -> int:
        """Estimate fee rate in satoshis per byte."""
        if target_blocks <= 2:
            return 15
        if target_blocks <= 6:
            return 10
        return 5
