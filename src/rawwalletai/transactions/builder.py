"""Transaction handling."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class TxInput:
    txid: str
    vout: int
    amount_sats: int
    script: str
    sequence: int = 0xffffffff


@dataclass
class TxOutput:
    address: str
    amount_sats: int
    script: str


@dataclass
class RawTransaction:
    txid: str
    hex: str
    inputs: list[TxInput]
    outputs: list[TxOutput]
    fee_sats: int
    vsize: int


class TransactionBuilder:
    """Builds and signs Bitcoin transactions."""

    def __init__(self, chain) -> None:
        self.chain = chain
        self._inputs: list[TxInput] = []
        self._outputs: list[TxOutput] = []
        self._fee_rate: int = 10  # sat/vB

    def add_input(self, txid: str, vout: int, amount_sats: int, script: str = "") -> "TransactionBuilder":
        """Add an input to the transaction."""
        self._inputs.append(TxInput(txid=txid, vout=vout, amount_sats=amount_sats, script=script))
        return self

    def add_output(self, address: str, amount_sats: int) -> "TransactionBuilder":
        """Add an output to the transaction."""
        self._outputs.append(TxOutput(address=address, amount_sats=amount_sats, script=""))
        return self

    def set_fee_rate(self, sat_per_vbyte: int) -> "TransactionBuilder":
        """Set the fee rate in satoshis per byte."""
        self._fee_rate = sat_per_vbyte
        return self

    def build(self) -> RawTransaction:
        """Build the transaction."""
        from bitcoinlib.transactions import Transaction
        from bitcoinlib.keys import Key
        t = Transaction()
        for i, inp in enumerate(self._inputs):
            txin = t.add_input(inp.txid, inp.vout)
        total_out = sum(o.amount_sats for o in self._outputs)
        fee = max(0, len(t.raw()) * self._fee_rate)
        for out in self._outputs:
            t.add_output(out.address, out.amount_sats)
        t.fee = fee
        t.update_txs()
        return RawTransaction(
            txid=t.txid,
            hex=t.raw_hex(),
            inputs=list(self._inputs),
            outputs=list(self._outputs),
            fee_sats=fee,
            vsize=t.vsize,
        )

    def sign(self, private_key_bytes: bytes) -> str:
        """Sign the transaction."""
        raise NotImplementedError("Transaction signing not yet implemented")
