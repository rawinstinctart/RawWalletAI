"""PSBT tests."""

from pathlib import Path

import pytest

from rawwalletai.chains.bitcoin import BitcoinChain
from rawwalletai.transactions.builder import TransactionBuilder
from rawwalletai.transactions.psbt import PSBT, PSBTInput, PSBTOutput


def _sample_utxo(amount_sats: int = 50000) -> dict:
    return {
        "txid": "abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd",
        "vout": 0,
        "amount_sats": amount_sats,
        "script": "0014" + "ab" * 20,
    }


def test_psbt_serialization_roundtrip() -> None:
    inp = PSBTInput(
        txid=_sample_utxo()["txid"].encode()[:32],
        vout=0,
        amount_sats=50000,
        script_pubkey=bytes([0x00, 0x14] + [0xAB] * 20),
    )
    out = PSBTOutput(
        address="bc1qxxx",
        amount_sats=25000,
        script_pubkey=bytes([0x00, 0x14] + [0xCD] * 20),
    )
    psbt = PSBT(inputs=[inp], outputs=[out])
    serialized = psbt.serialize()
    assert isinstance(serialized, bytes)
    assert len(serialized) > 0


def test_psbt_unsigned_tx_includes_all_inputs_outputs() -> None:
    inputs = [
        PSBTInput(
            txid=b"a" * 32,
            vout=i,
            amount_sats=50000,
            script_pubkey=bytes([0x00, 0x14] + [0xAB] * 20),
        )
        for i in range(3)
    ]
    outputs = [
        PSBTOutput(
            address=f"bc1q{i:040x}"[:42],
            amount_sats=10000 * (i + 1),
            script_pubkey=bytes([0x00, 0x14] + [i] * 20),
        )
        for i in range(2)
    ]
    psbt = PSBT(inputs=inputs, outputs=outputs)
    serialized = psbt.serialize()
    assert len(serialized) > 100


def test_psbt_missing_input_raises() -> None:
    with pytest.raises(ValueError):
        PSBT(inputs=[], outputs=[PSBTOutput("bc1qxxx", 1000, b"\x00" * 22)])


def test_psbt_negative_amount_rejected() -> None:
    with pytest.raises(ValueError):
        PSBTOutput(address="bc1qxxx", amount_sats=-1, script_pubkey=b"\x00" * 22)


def test_psbt_zero_amount_allowed() -> None:
    out = PSBTOutput(address="bc1qxxx", amount_sats=0, script_pubkey=b"\x00" * 22)
    assert out.amount_sats == 0


def test_psbt_builder_integration() -> None:
    builder = TransactionBuilder(None)
    utxo = _sample_utxo()
    builder.add_input(utxo["txid"], utxo["vout"], utxo["amount_sats"])
    builder.add_output("bc1qrecipient", 25000)
    builder.set_fee_rate(10)
    raw = builder.build()
    assert raw.fee_sats >= 0
    assert raw.vsize > 0


def test_psbt_fee_cannot_exceed_input() -> None:
    builder = TransactionBuilder(None)
    builder.add_input("abcd" * 8, 0, 1000)
    builder.add_output("bc1qrecipient", 1)
    builder.set_fee_rate(1)
    raw = builder.build()
    assert raw.fee_sats <= 1000


def test_psbt_invalid_script_type_rejected() -> None:
    chain = BitcoinChain("bitcoin")
    with pytest.raises(ValueError):
        chain.generate_address(b"\x02" * 33, "unknown")


def test_psbt_address_formats() -> None:
    chain = BitcoinChain("bitcoin")
    pubkey = b"\x02" * 33
    assert chain.generate_address(pubkey, "p2wpkh").address.startswith("bc1q")
    assert chain.generate_address(pubkey, "p2pkh").address.startswith("1")
    assert chain.generate_address(pubkey, "p2sh").address.startswith("3")


def test_psbt_testnet_address_format() -> None:
    chain = BitcoinChain("testnet")
    pubkey = b"\x02" * 33
    assert chain.generate_address(pubkey, "p2wpkh").address.startswith("tb1q")


def test_psbt_fee_estimation_levels() -> None:
    chain = BitcoinChain("bitcoin")
    assert chain.estimate_fee(1) == 15
    assert chain.estimate_fee(2) == 15
    assert chain.estimate_fee(6) == 10
    assert chain.estimate_fee(25) == 5
