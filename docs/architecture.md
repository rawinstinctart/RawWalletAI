# RawWalletAI Architecture Documentation

## Overview
RawWalletAI is a Bitcoin-only, self-custody wallet engine with PSBT-based transaction signing.

## Modules
- `core`: Key generation and wallet management
- `storage`: Encrypted persistence with AES-256-GCM
- `chains`: Bitcoin chain adapters (mainnet, testnet)
- `transactions`: PSBT handling, transaction builder, signing
- `config`: Pydantic-based configuration
- `api`: FastAPI server
- `cli`: Command-line interface

## Security Model
- Private keys never leave the core signing module
- All secrets encrypted at rest
- No external dependencies for key material
- Memory cleared after signing operations

## Signing Architecture

### ECDSA (Production-Ready)
- Uses `cryptography` library (audited, maintained)
- SECP256K1 curve
- SIGHASH_ALL for transaction signing
- BIP-174 PSBT serialization

### BIP-340/Schnorr (Planned)
**Status:** Design prepared, implementation pending

**Rationale for delay:**
- No stable Python binding with complete BIP-340 API exposed
- `secp256k1` Python binding supports signing but not verification through stable Python API
- Need audited implementation before production use

**Planned implementation path:**
1. Use `libsecp256k1` directly via stable C wrapper
2. OR integrate Rust-based `rust-secp256k1` via `PyO3`
3. OR use Go-based `btcsuite/btcec` via `cgo`

**Recommended library for BIP-340:**
- Primary: `rust-secp256k1` with `PyO3` bindings
- Fallback: `btcec` from `btcsuite/btcec` (Go, mature)
- Alternative: Wait for stable `secp256k1-zkp` Python bindings

**BIP-340-ready components:**
- `PSBT` class already supports Taproot inputs/outputs via extensible key-value format
- `TransactionBuilder` can serialize Taproot transactions
- `WalletSettings` can specify script types (`p2wpkh`, `p2sh`, `p2tr`)

**Components requiring modification for BIP-340:**
- `signer_psbt.py`: Add Taproot sighash computation
- `chains/bitcoin.py`: Add `p2tr` address generation
- `core/keys.py`: Add x-only public key support

## Transaction Flow
1. Build transaction with inputs/outputs
2. Create PSBT
3. Sign PSBT with private key
4. Serialize and broadcast

## Testing
- Unit tests for each module
- Integration tests for PSBT signing
- Test vectors for ECDSA signatures
