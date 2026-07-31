"""Transaction tests."""

from pathlib import Path

import pytest

from rawwalletai.transactions.builder import TransactionBuilder


def test_builder_add_input_output() -> None:
    builder = TransactionBuilder(None)
    builder.add_input("a" * 64, 0, 100_000).add_output("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", 50_000)
    tx = builder.build()
    assert tx.fee_sats >= 0
    assert tx.vsize > 0


def test_builder_negative_input_amount() -> None:
    builder = TransactionBuilder(None)
    with pytest.raises(ValueError):
        builder.add_input("a" * 64, 0, -1)


def test_builder_negative_output_amount() -> None:
    builder = TransactionBuilder(None)
    with pytest.raises(ValueError):
        builder.add_output("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", -1)
