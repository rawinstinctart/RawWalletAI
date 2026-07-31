"""PSBT handling for RawWalletAI."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional


def _double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


@dataclass
class PSBTInput:
    txid: bytes
    vout: int
    amount_sats: int
    script_pubkey: bytes
    signature: Optional[bytes] = None
    public_key: Optional[bytes] = None
    sighash: int = 1  # SIGHASH_ALL


@dataclass
class PSBTOutput:
    address: str
    amount_sats: int
    script_pubkey: bytes

    def __post_init__(self) -> None:
        if self.amount_sats < 0:
            raise ValueError("Output amount must be non-negative")


class PSBT:
    """Minimal PSBT container for Bitcoin (BIP-174)."""

    GLOBAL_MAGIC = b"psbt\xff"
    INPUT_KEY_SIG = b"\x01"
    OUTPUT_KEY_SCRIPT = b"\x02"

    def __init__(self, inputs: list[PSBTInput], outputs: list[PSBTOutput], version: int = 0) -> None:
        if not inputs:
            raise ValueError("PSBT must have at least one input")
        if not outputs:
            raise ValueError("PSBT must have at least one output")
        self.inputs = inputs
        self.outputs = outputs
        self.version = version
        self._signed = False

    def serialize(self) -> bytes:
        """Serialize PSBT to bytes."""
        out = bytearray()
        out += self.GLOBAL_MAGIC
        out += self._encode_varint(self.version)
        out += self._encode_varint(len(self.inputs))
        for i, inp in enumerate(self.inputs):
            out += self._encode_input(inp, i)
        out += self._encode_varint(len(self.outputs))
        for out_obj in self.outputs:
            out += self._encode_output(out_obj)
        return bytes(out)

    def _encode_input(self, inp: PSBTInput, index: int) -> bytes:
        data = bytearray()
        data += self._encode_varint(index)
        data += self._encode_key_value(self.INPUT_KEY_SIG, inp.signature or b"")
        if inp.public_key:
            data += self._encode_key_value(b"\x03", inp.public_key)
        return bytes(data)

    def _encode_output(self, out_obj: PSBTOutput) -> bytes:
        data = bytearray()
        data += self._encode_key_value(self.OUTPUT_KEY_SCRIPT, out_obj.script_pubkey)
        return bytes(data)

    def _encode_key_value(self, key: bytes, value: bytes) -> bytes:
        data = bytearray()
        data += self._encode_varint(len(key))
        data += key
        data += self._encode_varint(len(value))
        data += value
        return bytes(data)

    @staticmethod
    def _encode_varint(n: int) -> bytes:
        if n < 0xFD:
            return bytes([n])
        elif n < 0xFFFF:
            return b"\xfd" + n.to_bytes(2, "little")
        elif n < 0xFFFFFFFF:
            return b"\xfe" + n.to_bytes(4, "little")
        else:
            return b"\xff" + n.to_bytes(8, "little")
