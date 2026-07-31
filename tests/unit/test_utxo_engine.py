"""UTXO engine tests."""

from pathlib import Path

import pytest

from rawwalletai.chains.utxo_backends import UTXO, MockUTXOBackend
from rawwalletai.chains.utxo_engine import UTXOEngine


def make_utxo(address: str, txid: str, amount_sats: int, confirmed: bool = True) -> UTXO:
    return UTXO(txid=txid, vout=0, amount_sats=amount_sats, script_pubkey="", address=address, confirmed=confirmed)


@pytest.mark.asyncio
async def test_select_coins_single_utxo() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 100_000))
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", 50_000, fee_rate=1)
    assert result.total_amount == 100_000
    assert len(result.utxos) == 1


@pytest.mark.asyncio
async def test_select_coins_insufficient_funds() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 10_000))
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", 50_000, fee_rate=1)
    assert result.error is not None


@pytest.mark.asyncio
async def test_select_coins_no_utxos() -> None:
    backend = MockUTXOBackend()
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", 50_000, fee_rate=1)
    assert result.error == "No UTXOs available"


@pytest.mark.asyncio
async def test_double_spend_protection() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 100_000))
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", 50_000, fee_rate=1)
    assert result.utxos
    engine.mark_used(result.utxos[0].txid)
    assert await engine.check_double_spend(result.utxos[0].txid)


@pytest.mark.asyncio
async def test_fee_calculation() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", 100_000, fee_rate=5)
    assert result.fee > 0


@pytest.mark.asyncio
async def test_change_output() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", 100_000, fee_rate=1)
    assert result.change_amount > 0
    assert result.change_address is None


@pytest.mark.asyncio
async def test_select_multiple_utxos() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 30_000))
    backend.add_utxo(make_utxo("addr1", "b" * 64, 40_000))
    backend.add_utxo(make_utxo("addr1", "c" * 64, 50_000))
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", 70_000, fee_rate=1)
    assert len(result.utxos) == 3
    assert result.total_amount == 120_000


@pytest.mark.asyncio
async def test_negative_amount_rejected() -> None:
    backend = MockUTXOBackend()
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", -1, fee_rate=1)
    assert result.error == "Amount must be positive"


@pytest.mark.asyncio
async def test_unconfirmed_utxos_accepted() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 50_000, confirmed=False))
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", 40_000, fee_rate=1)
    assert result.total_amount == 50_000
    assert len(result.utxos) == 1


@pytest.mark.asyncio
async def test_mark_used_prevents_reuse() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 200_000))
    backend.add_utxo(make_utxo("addr1", "b" * 64, 100_000))
    engine = UTXOEngine(backend)
    result = await engine.select_coins("addr1", 80_000, fee_rate=1)
    used_txid = result.utxos[0].txid
    engine.mark_used(used_txid)
    result2 = await engine.select_coins("addr1", 70_000, fee_rate=1)
    assert used_txid not in [u.txid for u in result2.utxos]
    assert len(result2.utxos) == 1


@pytest.mark.asyncio
async def test_balance_aggregation() -> None:
    backend = MockUTXOBackend()
    backend.add_utxo(make_utxo("addr1", "a" * 64, 100_000, confirmed=True))
    backend.add_utxo(make_utxo("addr1", "b" * 64, 50_000, confirmed=False))
    engine = UTXOEngine(backend)
    balance = await engine.get_balance("addr1")
    assert balance["confirmed"] == 100_000
    assert balance["unconfirmed"] == 50_000
    assert balance["total"] == 150_000
