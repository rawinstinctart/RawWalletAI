"""UTXO backends."""

from __future__ import annotations

import asyncio
import hashlib
import json
from urllib.request import Request, urlopen

from rawwalletai.chains.utxo_backend import UTXO, UTXOBackend


class MockUTXOBackend(UTXOBackend):
    """In-memory mock backend for testing."""

    def __init__(self) -> None:
        self._utxos: dict[str, list[UTXO]] = {}
        self._broadcast_log: list[str] = []

    def add_utxo(self, utxo: UTXO) -> None:
        key = utxo.address
        self._utxos.setdefault(key, []).append(utxo)

    async def get_utxos(self, address: str) -> list[UTXO]:
        await asyncio.sleep(0)
        return list(self._utxos.get(address, []))

    async def broadcast_transaction(self, tx_hex: str) -> str:
        await asyncio.sleep(0)
        txid = hashlib.sha256(tx_hex.encode()).hexdigest()[:64]
        self._broadcast_log.append(tx_hex)
        return txid

    async def get_fee_estimate(self, target_blocks: int = 6) -> int:
        await asyncio.sleep(0)
        return 10

    async def get_transaction(self, txid: str) -> dict | None:
        await asyncio.sleep(0)
        return None

    async def get_balance(self, address: str) -> dict:
        await asyncio.sleep(0)
        utxos = self._utxos.get(address, [])
        confirmed = sum(u.amount_sats for u in utxos if u.confirmed)
        unconfirmed = sum(u.amount_sats for u in utxos if not u.confirmed)
        return {
            "confirmed": confirmed,
            "unconfirmed": unconfirmed,
            "total": confirmed + unconfirmed,
            "utxo_count": len(utxos),
        }

    async def health_check(self) -> bool:
        await asyncio.sleep(0)
        return True


class MempoolUTXOBackend:
    """Mempool.space API backend."""

    def __init__(self, base_url: str = "https://mempool.space/api") -> None:
        self.base_url = base_url.rstrip("/")

    async def _get(self, path: str) -> dict | list:
        url = f"{self.base_url}/{path.lstrip('/')}"
        req = Request(url, headers={"User-Agent": "RawWalletAI/0.1"})
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    async def get_utxos(self, address: str) -> list[UTXO]:
        data = await self._get(f"address/{address}/utxo")
        return [
            UTXO(
                txid=u["txid"],
                vout=u["vout"],
                amount_sats=u["value"],
                script_pubkey="",
                address=address,
                confirmed=u["status"].get("confirmed", False),
                height=u["status"].get("block_height"),
            )
            for u in data
        ]

    async def broadcast_transaction(self, tx_hex: str) -> str:
        data = await self._post("tx", tx_hex)
        return data.get("txid", "")

    async def _post(self, path: str, body: str) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        req = Request(url, data=body.encode(), headers={"Content-Type": "text/plain"})
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    async def get_fee_estimate(self, target_blocks: int = 6) -> int:
        data = await self._get("v1/fees/recommended")
        key = {1: "fastestFee", 3: "halfHourFee", 6: "hourFee"}.get(target_blocks, "hourFee")
        return int(data.get(key, 10))

    async def get_transaction(self, txid: str) -> dict | None:
        return await self._get(f"tx/{txid}")

    async def health_check(self) -> bool:
        try:
            await self._get("statistics/2h")
            return True
        except Exception:
            return False
