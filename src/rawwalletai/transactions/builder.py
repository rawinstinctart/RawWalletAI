"""Transaction handling."""

from __future__ import annotations

from dataclasses import dataclass

from rawwalletai.transactions.psbt import PSBT, PSBTInput, PSBTOutput

DUST_LIMIT = 500
MAX_FEE_RATE = 10_000
MAX_REASONABLE_FEE = 5_000_000


@dataclass
class TxInput:
    txid: str
    vout: int
    amount_sats: int
    script: str
    sequence: int = 0xFFFFFFFF


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
    rbf_enabled: bool = False


def _double_sha256(data: bytes) -> bytes:
    import hashlib
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def _validate_transaction_values(inputs: list[TxInput], outputs: list[TxOutput], fee_rate: int) -> None:
    if fee_rate < 1:
        raise ValueError("Fee rate must be at least 1 sat/vB")
    if fee_rate > MAX_FEE_RATE:
        raise ValueError(f"Fee rate {fee_rate} exceeds sanity limit {MAX_FEE_RATE}")

    for i, inp in enumerate(inputs):
        if inp.amount_sats < 0:
            raise ValueError(f"Input {i} amount must be non-negative")

    for i, out in enumerate(outputs):
        if out.amount_sats < 0:
            raise ValueError(f"Output {i} amount must be non-negative")
        if out.amount_sats < DUST_LIMIT:
            raise ValueError(f"Output {i} is dust: {out.amount_sats} sats < {DUST_LIMIT} sats")

    total_in = sum(inp.amount_sats for inp in inputs)
    total_out = sum(out.amount_sats for out in outputs)

    if total_in < total_out:
        raise ValueError("Total input value is less than total output value")

    estimated_vsize = max(1, len(inputs) * 41 + len(outputs) * 31 + 10)
    fee = total_in - total_out
    if fee < 0:
        raise ValueError("Transaction fee is negative")
    if fee > MAX_REASONABLE_FEE:
        raise ValueError(f"Transaction fee {fee} exceeds sanity limit {MAX_REASONABLE_FEE}")

    implied_fee_rate = fee / estimated_vsize
    if implied_fee_rate > MAX_FEE_RATE:
        raise ValueError(f"Implied fee rate {implied_fee_rate:.2f} exceeds sanity limit {MAX_FEE_RATE}")


class TransactionBuilder:
    """Builds Bitcoin transactions."""

    def __init__(self, chain, rbf_enabled: bool = False) -> None:
        self.chain = chain
        self.rbf_enabled = rbf_enabled
        self._inputs: list[TxInput] = []
        self._outputs: list[TxOutput] = []
        self._fee_rate: int = 10  # sat/vB

    def add_input(self, txid: str, vout: int, amount_sats: int, script: str = "", sequence: int | None = None) -> TransactionBuilder:
        if amount_sats < 0:
            raise ValueError("Input amount must be non-negative")
        seq = sequence if sequence is not None else (0xFFFFFFFD if self.rbf_enabled else 0xFFFFFFFF)
        self._inputs.append(TxInput(txid=txid, vout=vout, amount_sats=amount_sats, script=script, sequence=seq))
        return self

    def add_output(self, address: str, amount_sats: int) -> TransactionBuilder:
        if amount_sats < 0:
            raise ValueError("Output amount must be non-negative")
        if amount_sats < DUST_LIMIT:
            raise ValueError(f"Output amount is dust: {amount_sats} sats < {DUST_LIMIT} sats")
        self._outputs.append(TxOutput(address=address, amount_sats=amount_sats, script=""))
        return self

    def set_fee_rate(self, sat_per_vbyte: int) -> TransactionBuilder:
        if sat_per_vbyte < 1:
            raise ValueError("Fee rate must be at least 1 sat/vB")
        if sat_per_vbyte > MAX_FEE_RATE:
            raise ValueError(f"Fee rate {sat_per_vbyte} exceeds sanity limit {MAX_FEE_RATE}")
        self._fee_rate = sat_per_vbyte
        return self

    def build(self) -> RawTransaction:
        if not self._inputs:
            raise ValueError("Transaction has no inputs")
        if not self._outputs:
            raise ValueError("Transaction has no outputs")
        _validate_transaction_values(self._inputs, self._outputs, self._fee_rate)
        total_in = sum(inp.amount_sats for inp in self._inputs)
        total_out = sum(out.amount_sats for out in self._outputs)
        fee = max(0, total_in - total_out)
        vsize = max(1, len(self._inputs) * 41 + len(self._outputs) * 31 + 10)
        psbt_inputs = [
            PSBTInput(
                txid=bytes.fromhex(inp.txid),
                vout=inp.vout,
                amount_sats=inp.amount_sats,
                script_pubkey=b"",
            )
            for inp in self._inputs
        ]
        psbt_outputs = [
            PSBTOutput(
                address=out.address,
                amount_sats=out.amount_sats,
                script_pubkey=b"",
            )
            for out in self._outputs
        ]
        psbt = PSBT(inputs=psbt_inputs, outputs=psbt_outputs)
        serialized = psbt.serialize()
        txid = "".join(f"{b:02x}" for b in _double_sha256(serialized)[::-1])
        return RawTransaction(
            txid=txid,
            hex=serialized.hex(),
            inputs=list(self._inputs),
            outputs=list(self._outputs),
            fee_sats=fee,
            vsize=vsize,
            rbf_enabled=self.rbf_enabled,
        )
