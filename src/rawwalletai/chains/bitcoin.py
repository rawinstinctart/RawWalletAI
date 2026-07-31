"""Bitcoin chain adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BitcoinAddress:
    address: str
    script_type: str
    path: Optional[str] = None


class BitcoinChain:
    """Bitcoin chain adapter."""

    def __init__(self, network: str = "bitcoin") -> None:
        self.network = network

    def generate_address(self, public_key_bytes: bytes, script_type: str = "p2wpkh") -> BitcoinAddress:
        """Generate a Bitcoin address from public key bytes."""
        raise NotImplementedError("Address generation not yet implemented")

    def estimate_fee(self, target_blocks: int = 6) -> int:
        """Estimate fee rate in satoshis per byte."""
        raise NotImplementedError("Fee estimation not yet implemented")
