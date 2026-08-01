"""Bitcoin Core RPC backend for RawWalletAI."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen

from rawwalletai.chains.utxo_backend import UTXO


class BitcoinCoreBackend:
    """Bitcoin Core RPC backend."""

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
        with urlopen(req, timeout=30) as resp:  # nosec B310
            return json.loads(resp.read().decode())

    async def get_utxos(self, address: str) -> list[UTXO]:
        raise NotImplementedError("Bitcoin Core UTXO scanning requires importaddress + listunspent")

    async def broadcast_transaction(self, tx_hex: str) -> str:
        result = self._rpc_call("sendrawtransaction", [tx_hex])
        return result.get("result", "")

    async def get_fee_estimate(self, target_blocks: int = 6) -> int:
        result = self._rpc_call("estimatesmartfee", [target_blocks])
        return int(result.get("result", {}).get("feerate", 0.0001) * 100_000_000)

    async def get_transaction(self, txid: str) -> dict | None:
        result = self._rpc_call("getrawtransaction", [txid, True])
        return result.get("result")

    async def health_check(self) -> bool:
        try:
            result = self._rpc_call("getblockchaininfo")
            return "result" in result
        except Exception:
            return False
