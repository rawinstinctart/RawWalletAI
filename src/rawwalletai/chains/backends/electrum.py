"""Electrum backend for RawWalletAI."""

from __future__ import annotations

from rawwalletai.chains.utxo_backend import UTXO


class ElectrumBackend:
    """Electrum server backend.

    NOTE: This is an experimental stub.
    It depends on the `electrumx` package, which is not currently installed.
    Implement only when a real Electrum client dependency is added.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 50001, ssl: bool = False) -> None:
        self.host = host
        self.port = port
        self.ssl = ssl
        self._client = None

    async def _get_client(self):
        if self._client is None:
            try:
                import electrumx
                self._client = electrumx.connect(self.host, self.port, self.ssl)
            except Exception:
                self._client = None
        return self._client

    async def get_utxos(self, address: str) -> list[UTXO]:
        client = await self._get_client()
        if client is None:
            raise RuntimeError("Electrum client not available")
        result = await client.blockchain_address_get_balance(address)
        return []

    async def broadcast_transaction(self, tx_hex: str) -> str:
        raise NotImplementedError("Electrum broadcast not implemented")

    async def get_fee_estimate(self, target_blocks: int = 6) -> int:
        raise NotImplementedError("Electrum fee estimation not implemented")

    async def get_transaction(self, txid: str) -> dict | None:
        raise NotImplementedError("Electrum transaction lookup not implemented")

    async def health_check(self) -> bool:
        try:
            client = await self._get_client()
            return client is not None
        except Exception:
            return False
