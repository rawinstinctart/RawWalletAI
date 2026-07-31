"""Encrypted file storage."""

from __future__ import annotations

import json
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from pydantic import BaseModel

from rawwalletai.config.settings import WalletSettings


class EncryptedStorage(BaseModel):
    """AES-256-GCM encrypted file storage."""

    settings: WalletSettings
    key: bytes

    def _encrypt(self, data: bytes) -> bytes:
        """Encrypt data with AES-256-GCM."""
        aesgcm = AESGCM(self.key)
        nonce = HKDF(
            algorithm=hashes.SHA256(),
            length=12,
            salt=None,
            info=b"rawwalletai-nonce",
        ).derive(self.key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def _decrypt(self, encrypted: bytes) -> bytes:
        """Decrypt data with AES-256-GCM."""
        aesgcm = AESGCM(self.key)
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]
        return aesgcm.decrypt(nonce, ciphertext, None)

    def save(self, wallet_id: str, data: dict[str, Any]) -> None:
        """Save encrypted wallet data."""
        path = self.settings.data_dir / "wallets" / f"{wallet_id}.wallet"
        plaintext = json.dumps(data).encode()
        encrypted = self._encrypt(plaintext)
        path.write_bytes(encrypted)

    def load(self, wallet_id: str) -> dict[str, Any]:
        """Load and decrypt wallet data."""
        path = self.settings.data_dir / "wallets" / f"{wallet_id}.wallet"
        encrypted = path.read_bytes()
        plaintext = self._decrypt(encrypted)
        return json.loads(plaintext.decode())

    def delete(self, wallet_id: str) -> None:
        """Delete wallet file."""
        path = self.settings.data_dir / "wallets" / f"{wallet_id}.wallet"
        if path.exists():
            path.unlink()
