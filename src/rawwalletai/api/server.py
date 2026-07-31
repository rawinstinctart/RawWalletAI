"""FastAPI server for RawWalletAI."""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rawwalletai.config.settings import WalletSettings
from rawwalletai.core.keys import KeyManager
from rawwalletai.core.wallet import WalletManager
from rawwalletai.storage.encrypted import EncryptedStorage
from rawwalletai.chains.bitcoin import BitcoinChain


app = FastAPI(title="RawWalletAI", version="0.1.0")

settings = WalletSettings()
key_manager = KeyManager(settings)
chain = BitcoinChain(settings.network)
storage = EncryptedStorage(settings=settings, key=b"\x00" * 32)
wallet_manager = WalletManager(key_manager, storage, chain)


class CreateWalletRequest(BaseModel):
    name: str
    passphrase: Optional[str] = ""
    network: Optional[str] = "bitcoin"


class SendRequest(BaseModel):
    wallet_id: str
    to: str
    amount_sats: int
    fee_rate: Optional[int] = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/wallet/create")
def create_wallet(req: CreateWalletRequest) -> dict:
    try:
        wallet = wallet_manager.create_wallet(req.name, req.passphrase)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "wallet_id": wallet.wallet_id,
        "address": wallet.address.address,
        "mnemonic": wallet.key_manager._mnemonic,
    }


@app.get("/wallet/{wallet_id}/balance")
def get_balance(wallet_id: str) -> dict:
    wallet = wallet_manager.load_wallet(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"balance_sats": 0, "address": wallet.address.address}


@app.get("/wallet/{wallet_id}/transactions")
def get_transactions(wallet_id: str) -> dict:
    wallet = wallet_manager.load_wallet(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"transactions": []}


@app.post("/wallet/send")
def send_transaction(req: SendRequest) -> dict:
    wallet = wallet_manager.load_wallet(req.wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"txid": "", "status": "not_implemented"}
