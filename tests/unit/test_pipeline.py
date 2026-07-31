"""Transaction pipeline tests."""


import pytest

from rawwalletai.chains.broadcast import MockBroadcastBackend
from rawwalletai.chains.utxo_backends import UTXO, MockUTXOBackend
from rawwalletai.config.settings import WalletSettings
from rawwalletai.core.keys import KeyManager
from rawwalletai.transactions.pipeline import TransactionPipeline, TransactionRequest


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
    assert result.txid is not None
    assert result.tx_hex is not None
    assert result.fee_sats > 0
    assert result.inputs_used == 1
    assert result.outputs_created == 1


@pytest.mark.asyncio
async def test_multiple_inputs() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 50_000))
    backend.add_utxo(make_utxo("addr1", "b" * 64, 60_000))
    backend.add_utxo(make_utxo("addr1", "c" * 64, 70_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=120_000,
        private_key_bytes=b"\x01" * 32,
    ))
    assert result.success
    assert result.inputs_used == 3


@pytest.mark.asyncio
async def test_multiple_outputs() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=50_000,
        fee_rate=10,
        change_address="bc1qchange000000000000000000000000000000000",
        private_key_bytes=b"\x01" * 32,
    ))
    assert result.success
    assert result.change_sats > 0


@pytest.mark.asyncio
async def test_exact_balance_spend() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 100_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=100_000,
        fee_rate=1,
        private_key_bytes=b"\x01" * 32,
    ))
    assert not result.success
    assert result.error is not None


@pytest.mark.asyncio
async def test_dust_handling() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 500))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=1000,
        fee_rate=1,
        private_key_bytes=b"\x01" * 32,
    ))
    assert not result.success


@pytest.mark.asyncio
async def test_invalid_destination_address() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bad",
        amount_sats=50_000,
        private_key_bytes=b"\x01" * 32,
    ))
    assert not result.success


@pytest.mark.asyncio
async def test_invalid_private_key_length() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=50_000,
        private_key_bytes=b"\x01" * 31,
    ))
    assert not result.success
    assert result.error is not None


@pytest.mark.asyncio
async def test_invalid_utxo_negative_amount() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(UTXO(txid="a" * 64, vout=0, amount_sats=-100, script_pubkey="", address="addr1", confirmed=True))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=50_000,
        fee_rate=1,
        private_key_bytes=b"\x01" * 32,
    ))
    assert not result.success


@pytest.mark.asyncio
async def test_duplicate_utxo_detection() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 100_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result1 = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=10_000,
        fee_rate=1,
        private_key_bytes=b"\x01" * 32,
    ))
    assert result1.success
    result2 = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=10_000,
        fee_rate=1,
        private_key_bytes=b"\x01" * 32,
    ))
    assert not result2.success
    assert result2.error is not None


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
    assert result.error is not None


@pytest.mark.asyncio
async def test_large_transaction() -> None:
    backend = MockUTXOBackend()
    for i in range(20):
        backend.add_utxo(make_utxo("addr1", f"{i:064x}", 10_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=100_000,
        fee_rate=5,
        private_key_bytes=b"\x01" * 32,
    ))
    assert result.success
    assert result.inputs_used > 1


@pytest.mark.asyncio
async def test_fee_validation() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline = TransactionPipeline(backend, broadcast, key_manager)
    result = await pipeline.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=50_000,
        fee_rate=3000,
        private_key_bytes=b"\x01" * 32,
    ))
    assert not result.success
    assert result.error is not None


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
async def test_raw_transaction_generation() -> None:
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
    assert isinstance(result.tx_hex, str)
    assert len(result.tx_hex) > 0
    int(result.tx_hex, 16)


@pytest.mark.asyncio
async def test_deterministic_transaction() -> None:
    backend1 = MockUTXOBackend()
    backend1.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    backend2 = MockUTXOBackend()
    backend2.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    broadcast = MockBroadcastBackend()
    key_manager = KeyManager(WalletSettings())
    pipeline1 = TransactionPipeline(backend1, broadcast, key_manager)
    pipeline2 = TransactionPipeline(backend2, broadcast, key_manager)
    result1 = await pipeline1.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=50_000,
        fee_rate=10,
        private_key_bytes=b"\x01" * 32,
    ))
    result2 = await pipeline2.execute(TransactionRequest(
        from_address="addr1",
        to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        amount_sats=50_000,
        fee_rate=10,
        private_key_bytes=b"\x01" * 32,
    ))
    assert result1.success and result2.success
    assert result1.tx_hex == result2.tx_hex
