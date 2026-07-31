"""Transaction tests."""

from pathlib import Path

import pytest

from rawwalletai.transactions.builder import TransactionBuilder


def test_builder_add_input_output() -> None:
    builder = TransactionBuilder(None)
    builder.add_input("abcd" * 8, 0, 50000).add_output("bc1qxxx", 25000)
    assert len(builder._inputs) == 1
    assert len(builder._outputs) == 1


def test_builder_fee_rate() -> None:
    builder = TransactionBuilder(None)
    builder.set_fee_rate(15)
    assert builder._fee_rate == 15
