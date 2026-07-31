"""Bitcoin chain tests."""

from pathlib import Path

import pytest

from rawwalletai.chains.bitcoin import BitcoinChain


def test_p2wpkh_mainnet() -> None:
    chain = BitcoinChain("bitcoin")
    addr = chain.generate_address(b"\x02" * 33, "p2wpkh")
    assert addr.address.startswith("bc1q")
    assert addr.script_type == "p2wpkh"


def test_p2pkh_mainnet() -> None:
    chain = BitcoinChain("bitcoin")
    addr = chain.generate_address(b"\x02" * 33, "p2pkh")
    assert addr.script_type == "p2pkh"
    assert len(addr.address) > 20


def test_p2sh_mainnet() -> None:
    chain = BitcoinChain("bitcoin")
    addr = chain.generate_address(b"\x02" * 33, "p2sh")
    assert addr.script_type == "p2sh"
    assert len(addr.address) > 20


def test_testnet_p2wpkh() -> None:
    chain = BitcoinChain("testnet")
    addr = chain.generate_address(b"\x02" * 33, "p2wpkh")
    assert addr.address.startswith("tb1q")
    assert addr.script_type == "p2wpkh"


def test_unsupported_script_type() -> None:
    chain = BitcoinChain("bitcoin")
    with pytest.raises(ValueError):
        chain.generate_address(b"\x02" * 33, "unknown")
