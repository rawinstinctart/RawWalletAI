import tempfile
from pathlib import Path

import pytest

from rawwalletai.config.settings import WalletSettings
from rawwalletai.core.keys import KeyManager
from rawwalletai.storage.encrypted import EncryptedStorage


def test_settings_creates_dirs(tmp_path: Path) -> None:
    settings = WalletSettings(data_dir=tmp_path / ".rawwalletai")
    assert settings.data_dir.exists()
    assert (settings.data_dir / "wallets").exists()


def test_key_manager_generates_mnemonic() -> None:
    settings = WalletSettings()
    manager = KeyManager(settings)
    mnemonic = manager.generate_mnemonic()
    words = mnemonic.split()
    assert len(words) == 24


def test_key_manager_validate_mnemonic() -> None:
    settings = WalletSettings()
    manager = KeyManager(settings)
    mnemonic = manager.generate_mnemonic()
    assert manager.validate_mnemonic(mnemonic) is True
    assert manager.validate_mnemonic("invalid mnemonic test here") is False


def test_encrypted_storage_roundtrip(tmp_path: Path) -> None:
    settings = WalletSettings(data_dir=tmp_path)
    storage = EncryptedStorage(settings=settings, key=b"0" * 32)
    payload = {"mnemonic": "test", "network": "bitcoin"}
    storage.save("test-wallet", payload)
    loaded = storage.load("test-wallet")
    assert loaded == payload
