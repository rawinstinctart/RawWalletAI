"""Schnorr signatures for Bitcoin (BIP-340)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

import secp256k1


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


@dataclass
class SchnorrSignature:
    """Schnorr signature (64 bytes)."""

    r: bytes  # 32 bytes
    s: bytes  # 32 bytes

    def serialize(self) -> bytes:
        """Return the 64-byte signature."""
        return self.r + self.s


class SchnorrSigner:
    """Schnorr signing for Bitcoin (BIP-340)."""

    def __init__(self, private_key_bytes: bytes) -> None:
        """Initialize from 32-byte private key."""
        if len(private_key_bytes) != 32:
            raise ValueError("Private key must be exactly 32 bytes")
        self._private_key_bytes = private_key_bytes
        self._key = secp256k1.PrivateKey(private_key_bytes)
        self._public_key_bytes = self._key.pubkey.serialize()

    def public_key_bytes(self) -> bytes:
        """Get the compressed public key (33 bytes)."""
        return self._public_key_bytes

    def sign(self, message: bytes, tag: bytes = b"raw_signing") -> SchnorrSignature:
        """Sign a message with Schnorr."""
        sig_bytes = self._key.schnorr_sign(message, tag)
        r = sig_bytes[:32]
        s = sig_bytes[32:64]
        return SchnorrSignature(r=r, s=s)

    def verify(self, message: bytes, signature: SchnorrSignature, tag: bytes = b"raw_signing") -> bool:
        """Verify a Schnorr signature."""
        try:
            pubkey = secp256k1.PublicKey(self._public_key_bytes, raw=True)
            return pubkey.schnorr_verify(signature.serialize(), message, tag)
        except Exception:
            return False
