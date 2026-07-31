"""ECDSA signing for Bitcoin transactions."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def _double_sha256(data: bytes) -> bytes:
    """Double SHA256 hash."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def _sha256(data: bytes) -> bytes:
    """Single SHA256 hash."""
    return hashlib.sha256(data).digest()


class ECKey:
    """ECDSA private key wrapper for SECP256K1."""

    def __init__(self, private_key_bytes: bytes) -> None:
        """Initialize from 32-byte private key."""
        if len(private_key_bytes) != 32:
            raise ValueError("Private key must be exactly 32 bytes")
        self._private_key = ec.derive_private_key(
            int.from_bytes(private_key_bytes, "big"),
            ec.SECP256K1(),
            default_backend()
        )
        self._public_key = self._private_key.public_key()

    def sign(self, message_hash: bytes) -> bytes:
        """Sign a 32-byte message hash with ECDSA."""
        signature = self._private_key.sign(
            message_hash,
            ec.ECDSA(hashes.SHA256())
        )
        return signature

    def public_key_bytes(self) -> bytes:
        """Get the compressed public key (33 bytes)."""
        numbers = self._public_key.public_numbers()
        x = numbers.x.to_bytes(32, "big")
        prefix = b"\x02" if numbers.y % 2 == 0 else b"\x03"
        return prefix + x

    @staticmethod
    def verify(public_key_bytes: bytes, message_hash: bytes, signature: bytes) -> bool:
        """Verify an ECDSA signature."""
        try:
            public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256K1(),
                public_key_bytes
            )
            public_key.verify(signature, message_hash, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False
