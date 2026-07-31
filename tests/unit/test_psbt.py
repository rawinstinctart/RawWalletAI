"""PSBT tests."""

from pathlib import Path

import pytest

from rawwalletai.chains.bitcoin import BitcoinChain
from rawwalletai.transactions.builder import TransactionBuilder
from rawwalletai.transactions.psbt import PSBT, PSBTInput, PSBTOutput


def test_psbt_creation_valid() -> None:
    inp = PSBTInput(txid=b"\xab" * 32, vout=0, amount_sats=1000, script_pubkey=b"\x00\x14" + b"\xaa" * 20)
    out = PSBTOutput(address="bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", amount_sats=500, script_pubkey=b"\x00\x14" + b"\xbb" * 20)
    psbt = PSBT(inputs=[inp], outputs=[out])
    raw = psbt.serialize()
    assert raw.startswith(b"psbt\xff")
    assert len(raw) > 10


def test_psbt_missing_input_raises() -> None:
    with pytest.raises(ValueError):
        PSBT(inputs=[], outputs=[PSBTOutput(address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", amount_sats=500, script_pubkey=b"")])


def test_psbt_negative_amount_rejected() -> None:
    with pytest.raises(ValueError):
        PSBTOutput(address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", amount_sats=-1, script_pubkey=b"")


def test_builder_valid_transaction() -> None:
    chain = BitcoinChain("bitcoin")
    builder = TransactionBuilder(chain)
    builder.add_input("a" * 64, 0, 100_000)
    builder.add_output("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", 50_000)
    tx = builder.build()
    assert tx.fee_sats >= 0
    assert tx.vsize > 0


def test_builder_empty_inputs_raise() -> None:
    chain = BitcoinChain("bitcoin")
    builder = TransactionBuilder(chain)
    builder.add_output("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", 50_000)
    with pytest.raises(ValueError):
        builder.build()


def test_builder_empty_outputs_raise() -> None:
    chain = BitcoinChain("bitcoin")
    builder = TransactionBuilder(chain)
    builder.add_input("a" * 64, 0, 100_000)
    with pytest.raises(ValueError):
        builder.build()
