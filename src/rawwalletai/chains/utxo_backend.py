"""UTXO backend interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class UTXO:
    txid: str
    vout: int
    amount_sats: int
    script_pubkey: str
    address: str
    confirmed: bool
    height: Optional[int] = None


class UTXOBackend(ABC):
    """Abstract backend for UTXO lookups."""

    @abstractmethod
    async def get_utxos(self, address: str) -> list[UTXO]:
        """Get all UTXOs for an address."""
        ...

    @abstractmethod
    async def broadcast_transaction(self, tx_hex: str) -> str:
        """Broadcast a transaction and return the txid."""
        ...

    @abstractmethod
    async def get_fee_estimate(self, target_blocks: int = 6) -> int:
        """Get fee estimate in sat/vB."""
        ...

    @abstractmethod
    async def get_transaction(self, txid: str) -> Optional[dict]:
        """Get transaction details."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if backend is reachable."""
        ...
