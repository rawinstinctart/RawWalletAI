"""Transaction pipeline tests."""

from pathlib import Path

import pytest

from rawwalletai.chains.utxo_backends import UTXO, MockUTXOBackend
from rawwalletai.chains.utxo_engine import UTXOEngine
from rawwalletai.chains.broadcast import MockBroadcastBackend
from rawwalletai.transactions.pipeline import TransactionPipeline, TransactionRequest, TransactionResult
from rawwalletai.config.settings import WalletSettings
from rawwalletai.core.keys import KeyManager
from rawwalletai.transactions.signer_psbt import PSBTSigner


def make_utxo(address: str, txid: str, amount_sats: int, confirmed: bool = True) -> UTXO:
    return UTXO(txid=txid, vout=0, amount_sats=amount_sats, script_pubkey="", address=address, confirmed=confirmed)


@pytest.mark.asyncio
async def test_normal_payment() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=50_000,
        private_key_bytes=b"\x01" * 32,
    ))
    assert result.success


@pytest.mark.asyncio
async def test_insufficient_balance() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 10_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=50_000,
        private_key_bytes=b"\x01" * 32,
    ))
    assert not result.success
    assert result.error is not None


@pytest.mark.asyncio
async def test_empty_wallet() -> None:
    backend = MockUTXOBackend()
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=50_000,
        private_key_bytes=b"\x01" * 32,
    ))
    assert not result.success
