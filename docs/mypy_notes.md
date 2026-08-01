# Mypy Notes

This document tracks current typing limitations and planned fixes.

## Current Status

Mypy runs with strict mode enabled. Some files are excluded or documented due to external dependencies or architectural constraints.

## Documented Gaps

- `src/rawwalletai/chains/backends/electrum.py`: Removed pending dependency `electrumx`
- `src/rawwalletai/transactions/pipeline.py`: PSBT finalization return type is intentionally broad until finalizer implementation is complete
- `src/rawwalletai/chains/broadcast.py`: async wrappers around sync Bitcoin Core RPC retain dynamic return types
- `src/rawwalletai/chains/utxo_backends.py`: Mempool backend uses dynamic JSON responses from external API

## Planned Improvements

1. Add explicit `__all__` exports in `utxo_backends.py`
2. Replace broad `Exception` catches with typed exceptions
3. Add typed response models for mempool API responses
