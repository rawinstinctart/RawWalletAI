# RawWalletAI – Technical Debt Register

This register tracks known technical debt, its impact, and whether it blocks the 1.0 release.

## Critical

| # | Item | Impact | Priority | Estimated effort | Blocking 1.0? |
|---|------|--------|----------|------------------|---------------|
| 1 | PSBT finalization missing | Transactions cannot be broadcast as raw Bitcoin transactions | P0 | High | Yes |
| 2 | No integration tests against regtest/testnet | No validation that finalized transactions are accepted by Bitcoin Core | P0 | Medium | Yes |
| 3 | No external security audit | Unaudited cryptographic and protocol code | P0 | Medium | Yes |

## High

| # | Item | Impact | Priority | Estimated effort | Blocking 1.0? |
|---|------|--------|----------|------------------|---------------|
| 4 | Electrum backend removed | One network backend option missing | P1 | Low | No |
| 5 | Blind Exception catches in pipeline/signer | Poor error observability | P1 | Low | No |
| 6 | RawTransaction undefined in pipeline | Type error, stub finalization | P1 | Low | No |
| 7 | No typed response models for external APIs | mypy errors, fragile parsing | P1 | Medium | No |

## Medium

| # | Item | Impact | Priority | Estimated effort | Blocking 1.0? |
|---|------|--------|----------|------------------|---------------|
| 8 | Missing explicit __all__ exports | mypy attr-defined errors | P2 | Low | No |
| 9 | BLE001 blind catches in broadcast/backends | Reduced error transparency | P2 | Low | No |
| 10 | No secret zeroization strategy | Keys may remain in memory | P2 | Medium | No |
| 11 | Mempool backend uses sync urlopen replacement incomplete | Network I/O in async context | P2 | Medium | No |

## Low

| # | Item | Impact | Priority | Estimated effort | Blocking 1.0? |
|---|------|--------|----------|------------------|---------------|
| 12 | Unused imports after ruff fixes | Code cleanliness | P3 | Low | No |
| 13 | Import sorting issues | Lint noise | P3 | Low | No |
| 14 | PEP 570 positional-only parameter warnings | Lint noise | P3 | Low | No |

## Resolution Strategy

- Critical items must be resolved before 1.0
- High items should be resolved in 0.8–0.9
- Medium items can be resolved in 1.x
- Low items can be addressed opportunistically
