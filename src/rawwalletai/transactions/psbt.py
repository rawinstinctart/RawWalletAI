"""PSBT handling for RawWalletAI."""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from typing import Optional

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from rawwalletai.chains.bitcoin import BitcoinChain


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _double_sha256(data: bytes) -> bytes:
    return _sha256(_sha256(data))


def _write_varint(value: int) -> bytes:
    if value < 0xfd:
        return bytes([value])
    if value <= 0xffff:
        return b"\xfd" + value.to_bytes(2, "little")
    if value <= 0xffffffff:
        return b"\xfe" + value.to_bytes(4, "little")
    return b"\xff" + value.to_bytes(8, "little")


def _read_varint(data: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(data):
        raise ValueError("Unexpected end of data")
    first = data[offset]
    if first < 0xFD:
        return first, offset + 1
    if first == 0xFD:
        return int.from_bytes(data[offset + 1 : offset + 3], "little"), offset + 3
    if first == 0xFE:
        return int.from_bytes(data[offset + 1 : offset + 5], "little"), offset + 5
    return int.from_bytes(data[offset + 1 : offset + 9], "little"), offset + 9


def _write_vector(items: list[bytes]) -> bytes:
    out = b""
    for item in items:
        out += _write_varint(len(item)) + item
    return out


def _read_vector(data: bytes, offset: int) -> tuple[list[bytes], int]:
    length, offset = _read_varint(data, offset)
    items: list[bytes] = []
    end = offset + length
    while offset < end:
        item_len, offset = _read_varint(data, offset)
        if offset + item_len > len(data):
            raise ValueError("Invalid PSBT: item exceeds buffer")
        items.append(data[offset : offset + item_len])
        offset += item_len
    return items, offset


@dataclass
class PSBTInput:
    txid: bytes
    vout: int
    amount_sats: int
    script_pubkey: bytes
    sighash: int = 1


@dataclass
class PSBTOutput:
    address: str
    amount_sats: int
    script_pubkey: bytes

    def __post_init__(self) -> None:
        if self.amount_sats < 0:
            raise ValueError("Output amount must be non-negative")


class PSBT:
    """Minimal BIP-174 PSBT implementation for P2WPKH."""

    PSBT_MAGIC = b"psbt\xff"
    GLOBAL_OFFSET = 5

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
        tx_bytes = self._serialize_unsigned_tx()
        globals_map = self._encode_map(
            {
                0x00: tx_bytes,
                0x01: self.version.to_bytes(4, "little"),
            }
        )
        inputs_map = b""
        for inp in self.inputs:
            input_map = self._encode_map(
                {
                    0x00: inp.txid + inp.vout.to_bytes(4, "little"),
                    0x01: inp.amount_sats.to_bytes(8, "little"),
                    0x02: inp.script_pubkey,
                    0x03: inp.sighash.to_bytes(4, "little"),
                }
            )
            inputs_map += _write_varint(len(input_map)) + input_map
        outputs_map = b""
        for out in self.outputs:
            output_map = self._encode_map(
                {
                    0x00: out.amount_sats.to_bytes(8, "little"),
                    0x01: out.script_pubkey,
                }
            )
            outputs_map += _write_varint(len(output_map)) + output_map
        return (
            self.PSBT_MAGIC
            + _write_varint(len(globals_map))
            + globals_map
            + _write_varint(len(self.inputs))
            + inputs_map
            + _write_varint(len(self.outputs))
            + outputs_map
        )

    def _serialize_unsigned_tx(self) -> bytes:
        """Serialize a minimal Bitcoin transaction."""
        version = (1).to_bytes(4, "little")
        input_count = _write_varint(len(self.inputs))
        inputs = b""
        for inp in self.inputs:
            inputs += inp.txid[::-1] + inp.vout.to_bytes(4, "little")
            inputs += b"\x00" * 34  # empty scriptSig
            inputs += (0xFFFFFFFF).to_bytes(4, "little")
        output_count = _write_varint(len(self.outputs))
        outputs = b""
        for out in self.outputs:
            outputs += out.amount_sats.to_bytes(8, "little")
            outputs += _write_varint(len(out.script_pubkey)) + out.script_pubkey
        locktime = (0).to_bytes(4, "little")
        return version + input_count + inputs + output_count + outputs + locktime

    def _encode_map(self, mapping: dict[int, bytes]) -> bytes:
        out = b""
        for key, value in mapping.items():
            out += _write_varint(1) + bytes([key])
            out += _write_varint(len(value)) + value
        return out

    def sighash_schnorr(self, private_key_bytes: bytes) -> bytes:
        """Compute a deterministic signature placeholder for testing.
        
        In production, replace with real ECDSA/Schnorr signing.
        """
        digest = _sha256(self.serialize())
        return private_key_bytes[:32] + digest[:32]
