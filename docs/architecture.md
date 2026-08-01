# RawWalletAI Architecture Documentation

## Overview
RawWalletAI is a Bitcoin-only, self-custody wallet engine with PSBT-based transaction signing and modular network backends.

## Modules
- `core`: Key generation and wallet management
- `storage`: Encrypted persistence with AES-256-GCM
- `chains`: Bitcoin chain adapters and network backends
- `transactions`: PSBT handling, transaction builder, signing
- `config`: Pydantic-based configuration
- `api`: FastAPI server

## Security Model
- Private keys never leave the core signing module
- All secrets encrypted at rest with unique salt per encryption
- BIP-32 compliant master key derivation via HMAC-SHA512
- ECDSA signing via audited `cryptography` library
- Schnorr/BIP-340 planned for future with audited wrapper

## Transaction Flow
1. Build transaction with inputs/outputs
2. Validate values, dust, fees
3. Create PSBT
4. Sign PSBT with private key
5. Finalize transaction
6. Broadcast via backend

## Testing
- Unit tests for each module
- Integration tests for PSBT signing
- BIP-32 derivation tests

## Known Blockers
- PSBT finalization requires audited external library/wrapper
- Electrum backend removed pending `electrumx` package
- Secret zeroization is limited in CPython; use process isolation for production
