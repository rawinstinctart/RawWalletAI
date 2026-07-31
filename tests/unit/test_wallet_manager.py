"""Wallet manager tests."""



from rawwalletai.chains.bitcoin import BitcoinChain
from rawwalletai.config.settings import WalletSettings
from rawwalletai.core.keys import KeyManager
from rawwalletai.core.wallet import WalletManager
from rawwalletai.storage.encrypted import EncryptedStorage


def test_create_wallet_returns_no_mnemonic() -> None:
    manager = WalletManager(
        KeyManager(WalletSettings()),
        EncryptedStorage(settings=WalletSettings(), key=b"\x00" * 32),
        BitcoinChain("bitcoin"),
    )
    wallet = manager.create_wallet("test", "")
    assert "mnemonic" not in str(wallet)


def test_create_wallet_generates_valid_address() -> None:
    manager = WalletManager(
        KeyManager(WalletSettings()),
        EncryptedStorage(settings=WalletSettings(), key=b"\x00" * 32),
        BitcoinChain("bitcoin"),
    )
    wallet = manager.create_wallet("test", "")
    assert wallet.address.address.startswith("bc1q")
    assert len(wallet.address.script_pubkey) == 22


def test_load_wallet_roundtrip() -> None:
    manager = WalletManager(
        KeyManager(WalletSettings()),
        EncryptedStorage(settings=WalletSettings(), key=b"\x00" * 32),
        BitcoinChain("bitcoin"),
    )
    wallet = manager.create_wallet("roundtrip", "")
    wallet_id = wallet.wallet_id

    manager2 = WalletManager(
        KeyManager(WalletSettings()),
        EncryptedStorage(settings=WalletSettings(), key=b"\x00" * 32),
        BitcoinChain("bitcoin"),
    )
    loaded = manager2.load_wallet(wallet_id)
    assert loaded is not None
    assert loaded.name == "roundtrip"
    assert loaded.address.address == wallet.address.address
