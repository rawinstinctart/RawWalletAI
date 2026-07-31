"""Broadcast backends for RawWalletAI."""

from __future__ import annotations

import asyncio
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen


class BroadcastBackend(ABC):
    """Abstract backend for transaction broadcasting."""

    @abstractmethod
    async def broadcast_transaction(self, tx_hex: str) -> str:
        """Broadcast a transaction and return the txid."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if backend is reachable."""
        ...


class MockBroadcastBackend(BroadcastBackend):
    """In-memory mock backend for testing."""

    def __init__(self) -> None:
        self._broadcast_log: list[str] = []
        self._next_txid = 0

    async def broadcast_transaction(self, tx_hex: str) -> str:
        await asyncio.sleep(0)
        self._next_txid += 1
        txid = hashlib.sha256(f"{tx_hex}{self._next_txid}".encode()).hexdigest()[:64]
        self._broadcast_log.append(tx_hex)
        return txid

    async def health_check(self) -> bool:
        await asyncio.sleep(0)
        return True


class MempoolBroadcastBackend(BroadcastBackend):
    """Mempool.space broadcast backend."""

    def __init__(self, base_url: str = "https://mempool.space/api") -> None:
        self.base_url = base_url.rstrip("/")

    async def _post(self, path: str, body: str) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        req = Request(url, data=body.encode(), headers={"Content-Type": "text/plain"})
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    async def broadcast_transaction(self, tx_hex: str) -> str:
        data = await self._post("tx", tx_hex)
        return data.get("txid", "")

    async def health_check(self) -> bool:
        try:
            await self._post("statistics/2h", "")
            return True
        except Exception:
            return False


class ElectrumBroadcastBackend(BroadcastBackend):
    """Electrum server broadcast backend."""

    def __init__(self, host: str = "127.0.0.1", port: int = 50001, ssl: bool = False) -> None:
        self.host = host
        self.port = port
        self.ssl = ssl

    async def broadcast_transaction(self, tx_hex: str) -> str:
        raise NotImplementedError("Electrum broadcast not yet implemented")

    async def health_check(self) -> bool:
        return False


class BitcoinCoreBroadcastBackend(BroadcastBackend):
    """Bitcoin Core RPC broadcast backend."""

    def __init__(self, rpc_url: str = "http://127.0.0.1:8332", rpc_user: str = "", rpc_password: str = "") -> None:
        self.rpc_url = rpc_url
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password

    def _rpc_call(self, method: str, params: list | dict = None) -> dict:
        payload = json.dumps({"jsonrpc": "1.0", "id": "rawwalletai", "method": method, "params": params or []}).encode()
        req = Request(self.rpc_url, data=payload, headers={"Content-Type": "application/json"})
        import base64
        auth = base64.b64encode(f"{self.rpc_user}:{self.rpc_password}".encode()).decode()
        req.add_header("Authorization", f"Basic {auth}")
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    async def broadcast_transaction(self, tx_hex: str) -> str:
        result = self._rpc_call("sendrawtransaction", [tx_hex])
        return result.get("result", "")

    async def health_check(self) -> bool:
        try:
            result = self._rpc_call("getblockchaininfo")
            return "result" in result
        except Exception:
            return False
