"""Key management for RawWalletAI."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from mnemonic import Mnemonic

from rawwalletai.config.settings import WalletSettings


@dataclass
class KeyPair:
    """Represents a derived key pair."""

    private_key_bytes: bytes
    public_key_bytes: bytes
    chain_code: bytes
    address: str
    path: str


class KeyManager:
    """Manages HD wallet keys according to BIP-39/32/44."""

    def __init__(self, settings: WalletSettings) -> None:
        self.settings = settings
        self._master_key: bytes | None = None
        self._master_chain_code: bytes | None = None
        self._mnemonic: str | None = None

    def generate_mnemonic(self, strength: int = 256) -> str:
        """Generate a new BIP-39 mnemonic phrase."""
        mnemo = Mnemonic("english")
        return mnemo.generate(strength=strength)

    def validate_mnemonic(self, mnemonic: str) -> bool:
        """Validate a BIP-39 mnemonic phrase."""
        mnemo = Mnemonic("english")
        return mnemo.check(mnemonic)

    def mnemonic_to_seed(self, mnemonic: str, passphrase: str = "") -> bytes:
        """Convert mnemonic to BIP-39 seed."""
        mnemo = Mnemonic("english")
        return mnemo.to_seed(mnemonic, passphrase=passphrase)

    def derive_master_key(self, seed: bytes) -> tuple[bytes, bytes]:
        """Derive master private key and chain code from seed (BIP-32)."""
        # BIP-32 master key derivation
        hmac = hashlib.pbkdf2_hmac(
            "sha512",
            b"Bitcoin seed",
            seed,
            2048,
            dklen=64,
        )
        master_private_key = hmac[:32]
        master_chain_code = hmac[32:]
        self._master_key = master_private_key
        self._master_chain_code = master_chain_code
        return master_private_key, master_chain_code

    def derive_key(self, path: str) -> KeyPair:
        """Derive a key for a specific BIP-44 path."""
        raise NotImplementedError("Key derivation not yet implemented")

    def initialize_from_mnemonic(
        self, mnemonic: str, passphrase: str = ""
    ) -> None:
        """Initialize key manager from mnemonic."""
        if not self.validate_mnemonic(mnemonic):
            raise ValueError("Invalid mnemonic phrase")
        self._mnemonic = mnemonic
        seed = self.mnemonic_to_seed(mnemonic, passphrase)
        self.derive_master_key(seed)
