"""RBF tests."""

from pathlib import Path

import pytest

from rawwalletai.transactions.builder import TransactionBuilder


def test_rbf_builder_sets_sequence() -> None:
    builder = TransactionBuilder(None, rbf_enabled=True)
    builder.add_input("a" * 64, 0, 100_000)
    assert builder._inputs[0].sequence == 0xFFFFFFFD


def test_non_rbf_builder_sets_sequence() -> None:
    builder = TransactionBuilder(None, rbf_enabled=False)
    builder.add_input("a" * 64, 0, 100_000)
    assert builder._inputs[0].sequence == 0xFFFFFFFF
