"""BIP-32 master key derivation tests."""

from pathlib import Path

import pytest

from rawwalletai.core.keys import KeyManager
from rawwalletai.config.settings import WalletSettings


def test_bip32_master_key_derivation() -> None:
    km = KeyManager(WalletSettings())
    seed = bytes(range(64))
    priv, chain = km.derive_master_key(seed)
    assert len(priv) == 32
    assert len(chain) == 32


def test_bip32_deterministic() -> None:
    km1 = KeyManager(WalletSettings())
    km2 = KeyManager(WalletSettings())
    seed = bytes(range(64))
    priv1, chain1 = km1.derive_master_key(seed)
    priv2, chain2 = km2.derive_master_key(seed)
    assert priv1 == priv2
    assert chain1 == chain2


def test_bip32_different_seeds() -> None:
    km = KeyManager(WalletSettings())
    priv1, _ = km.derive_master_key(bytes(range(64)))
    priv2, _ = km.derive_master_key(bytes(range(64, 128)))
    assert priv1 != priv2
