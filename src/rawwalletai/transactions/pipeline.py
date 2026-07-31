"""End-to-end transaction pipeline for RawWalletAI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from rawwalletai.chains.utxo_backends import UTXO, UTXOBackend
from rawwalletai.chains.utxo_engine import UTXOEngine, CoinSelectionResult
from rawwalletai.chains.broadcast import BroadcastBackend, MockBroadcastBackend
from rawwalletai.transactions.builder import TransactionBuilder
from rawwalletai.transactions.psbt import PSBT, PSBTInput, PSBTOutput
from rawwalletai.transactions.signer_psbt import PSBTSigner
from rawwalletai.core.keys import KeyManager


@dataclass
class TransactionRequest:
    from_address: str
    to_address: str
    amount_sats: int
    fee_rate: int = 10
    change_address: Optional[str] = None
    private_key_bytes: Optional[bytes] = None


@dataclass
class TransactionResult:
    success: bool
    txid: Optional[str] = None
    tx_hex: Optional[str] = None
    fee_sats: int = 0
    change_sats: int = 0
    inputs_used: int = 0
    outputs_created: int = 0
    error: Optional[str] = None


class TransactionPipeline:
    """Complete transaction pipeline from request to broadcast."""

    def __init__(
        self,
        utxo_backend: UTXOBackend,
        broadcast_backend: BroadcastBackend,
        key_manager: KeyManager,
    ) -> None:
        self.utxo_engine = UTXOEngine(utxo_backend)
        self.broadcast_backend = broadcast_backend
        self.key_manager = key_manager
        self.signer = PSBTSigner()

    async def execute(self, request: TransactionRequest) -> TransactionResult:
        """Execute complete transaction pipeline."""
        # Step 1: Coin selection
        selection = await self.utxo_engine.select_coins(
            request.from_address,
            request.amount_sats,
            request.fee_rate,
            request.change_address,
        )

        if selection.error:
            return TransactionResult(success=False, error=selection.error)

        # Step 2: Build transaction
        builder = TransactionBuilder(None)
        for utxo in selection.utxos:
            builder.add_input(utxo.txid, utxo.vout, utxo.amount_sats, utxo.script_pubkey)

        builder.add_output(request.to_address, request.amount_sats)

        # Add change output if needed
        if selection.change_amount > 0:
            if selection.change_address:
                builder.add_output(selection.change_address, selection.change_amount)

        tx = builder.build()

        # Step 3: Create PSBT
        psbt_inputs = [
            PSBTInput(
                txid=bytes.fromhex(utxo.txid),
                vout=utxo.vout,
                amount_sats=utxo.amount_sats,
                script_pubkey=utxo.script_pubkey.encode() if utxo.script_pubkey else b"",
            )
            for utxo in selection.utxos
        ]

        psbt_outputs = [PSBTOutput(address=request.to_address, amount_sats=request.amount_sats, script_pubkey=b"")]

        if selection.change_amount > 0 and selection.change_address:
            psbt_outputs.append(
                PSBTOutput(address=selection.change_address, amount_sats=selection.change_amount, script_pubkey=b"")
            )

        psbt = PSBT(inputs=psbt_inputs, outputs=psbt_outputs)

        # Step 4: Sign PSBT
        if request.private_key_bytes:
            try:
                psbt = self.signer.sign_psbt(psbt, request.private_key_bytes)
            except Exception as e:
                return TransactionResult(success=False, error=f"Signing failed: {e}")

        # Step 5: Finalize and broadcast
        try:
            final_tx = self._finalize_transaction(psbt, tx)
            txid = await self.broadcast_backend.broadcast_transaction(final_tx.hex())
            return TransactionResult(
                success=True,
                txid=txid,
                tx_hex=final_tx.hex(),
                fee_sats=selection.fee,
                change_sats=selection.change_amount,
                inputs_used=len(selection.utxos),
                outputs_created=len(psbt.outputs),
            )
        except Exception as e:
            return TransactionResult(success=False, error=f"Finalization/broadcast failed: {e}")

    def _finalize_transaction(self, psbt: PSBT, raw_tx) -> "RawTransaction":
        """Finalize transaction from signed PSBT."""
        # For now, use the raw transaction hex as final
        return raw_tx
