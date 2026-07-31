"""Fee and dust validation tests."""


import pytest

from rawwalletai.transactions.builder import (
    MAX_FEE_RATE,
    TransactionBuilder,
)


def test_dust_output_rejected() -> None:
    builder = TransactionBuilder(None)
    builder.add_input("a" * 64, 0, 100_000)
    with pytest.raises(ValueError, match="dust"):
        builder.add_output("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", 100)


def test_negative_output_rejected() -> None:
    builder = TransactionBuilder(None)
    builder.add_input("a" * 64, 0, 100_000)
    with pytest.raises(ValueError, match="Output amount must be non-negative"):
        builder.add_output("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", -1)


def test_max_fee_rate_sanity() -> None:
    builder = TransactionBuilder(None)
    builder.add_input("a" * 64, 0, 100_000)
    builder.add_output("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", 50_000)
    with pytest.raises(ValueError, match="exceeds sanity limit"):
        builder.set_fee_rate(MAX_FEE_RATE + 1)
    builder.set_fee_rate(MAX_FEE_RATE)
    tx = builder.build()
    assert tx.fee_sats >= 0


def test_fee_consistency() -> None:
    builder = TransactionBuilder(None)
    builder.add_input("a" * 64, 0, 100_000)
    builder.add_output("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", 50_000)
    tx = builder.build()
    assert tx.fee_sats > 0
    assert tx.inputs[0].amount_sats >= tx.outputs[0].amount_sats


def test_reasonable_fee_limit() -> None:
    builder = TransactionBuilder(None)
    for _ in range(1000):
        builder.add_input("a" * 64, 0, 1_000_000)
    builder.add_output("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", 50_000)
    with pytest.raises(ValueError, match="exceeds sanity limit"):
        builder.build()
