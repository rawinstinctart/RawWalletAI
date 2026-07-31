"""UTXO engine for RawWalletAI."""

from __future__ import annotations

from dataclasses import dataclass

from rawwalletai.chains.utxo_backends import UTXO, UTXOBackend


@dataclass
class CoinSelectionResult:
    utxos: list[UTXO]
    total_amount: int
    fee: int
    change_amount: int
    change_address: str | None = None
    error: str | None = None


class UTXOEngine:
    """UTXO selection and management engine."""

    def __init__(self, backend: UTXOBackend) -> None:
        self.backend = backend
        self._used_txids: set[str] = set()

    async def select_coins(
        self,
        address: str,
        amount_sats: int,
        fee_rate: int = 10,
        change_address: str | None = None,
    ) -> CoinSelectionResult:
        if amount_sats <= 0:
            return CoinSelectionResult(utxos=[], total_amount=0, fee=0, change_amount=0, error="Amount must be positive")

        utxos = await self.backend.get_utxos(address)
        confirmed = [u for u in utxos if u.confirmed]
        unconfirmed = [u for u in utxos if not u.confirmed]
        available = [u for u in confirmed + unconfirmed if u.txid not in self._used_txids]

        if not available:
            return CoinSelectionResult(utxos=[], total_amount=0, fee=0, change_amount=0, error="No UTXOs available")

        estimated_vbytes = self._estimate_vsize(1, 1)
        fee = estimated_vbytes * fee_rate
        target_with_fee = amount_sats + fee

        selected, total = self._pick_utxos(available, target_with_fee)
        if not selected:
            return CoinSelectionResult(utxos=[], total_amount=0, fee=0, change_amount=0, error="Insufficient funds")

        estimated_vbytes = self._estimate_vsize(len(selected), 1)
        fee = estimated_vbytes * fee_rate
        if total < amount_sats + fee:
            return CoinSelectionResult(utxos=[], total_amount=0, fee=0, change_amount=0, error="Insufficient funds after fee")

        change_amount = total - amount_sats - fee
        return CoinSelectionResult(
            utxos=selected,
            total_amount=total,
            fee=fee,
            change_amount=change_amount,
            change_address=change_address,
        )

    def _pick_utxos(self, utxos: list[UTXO], target: int) -> tuple[list[UTXO], int]:
        smallest_first = sorted(utxos, key=lambda u: u.amount_sats)
        selected: list[UTXO] = []
        total = 0
        for utxo in smallest_first:
            selected.append(utxo)
            total += utxo.amount_sats
            if total >= target:
                return selected, total
        return [], 0

    def _estimate_vsize(self, input_count: int, output_count: int) -> int:
        return max(1, input_count * 41 + output_count * 31 + 10)

    def mark_used(self, txid: str) -> None:
        self._used_txids.add(txid)

    def unmark_used(self, txid: str) -> None:
        self._used_txids.discard(txid)

    async def check_double_spend(self, txid: str) -> bool:
        if txid in self._used_txids:
            return True
        tx = await self.backend.get_transaction(txid)
        if tx and tx.get("confirmed"):
            return False
        return txid in self._used_txids

    async def get_balance(self, address: str) -> dict:
        return await self.backend.get_balance(address)
