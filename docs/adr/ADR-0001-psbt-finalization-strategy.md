# ADR-0001 — PSBT Finalization Strategy

**Status:** Accepted  
**Date:** 2026-08-01  
**Decision Owner:** Pascal Haux / RawInstinctAI  
**Context:** Architecture Freeze, PSBT finalization release blocker

---

## Current State

RawWalletAI is a Bitcoin-only, self-custody wallet engine with the following characteristics:

- **Architecture:** Modular, API-first, Python 3.11+
- **Crypto stack:** `cryptography` (ECDSA), BIP-32 HMAC-SHA512, AES-256-GCM
- **Dependencies:** Minimal audited libraries only
- **Test status:** 62 unit tests passing
- **Security status:** Security audit completed; 6 findings fixed, 5 accepted with rationale

### Current PSBT Support

- PSBT creation and signing implemented
- PSBT parsing implemented
- **PSBT finalization:** Missing
- **Witness construction:** Missing
- **Raw transaction extraction:** Stub only

---

## Problem Statement

RawWalletAI cannot become version 1.0 today because it cannot produce valid, broadcast-ready Bitcoin transactions from signed PSBTs.

### Missing Capabilities

1. **PSBT Finalization:** Extract finalized inputs/outputs from signed PSBT
2. **Witness Construction:** Build scriptWitness from partial signatures
3. **Transaction Serialization:** Produce consensus-valid raw transaction hex
4. **Validation:** Verify finalization matches signed PSBT and passes Bitcoin Core validation

### Impact

- Transactions cannot be broadcast to Bitcoin network
- Wallet is non-functional for actual Bitcoin operations
- Release 1.0 is impossible without this capability

---

## Evaluated Options

### Option A — python-bitcoinlib

**Advantages:**
- Already installed in current environment
- Minimal dependency footprint

**Disadvantages:**
- **No PSBT finalization support**
- Low maintenance activity
- No witness serialization
- Would require custom implementation violating project policy

**Maintenance:** Low  
**Security:** Medium  
**Future Compatibility:** Poor

**Verdict:** Rejected

---

### Option B — bitcoinlib

**Advantages:**
- Active maintenance
- SegWit support

**Disadvantages:**
- **Partial PSBT support only**
- **Heavy dependency footprint:** SQLAlchemy, fastecdsa, pycryptodome
- Increased attack surface
- Overkill for minimal wallet engine

**Dependency Footprint:** Very High  
**Maintenance:** Active  
**Security:** Medium

**Verdict:** Rejected

---

### Option C — rust-bitcoin via PyO3 or maintained wrapper

**Advantages:**
- **Reference implementation** for Bitcoin protocol serialization
- Full PSBT support (parse, finalize, extract)
- Complete SegWit and Taproot support
- High performance
- Rust memory safety
- Very active maintenance
- MIT license

**Disadvantages:**
- Requires Rust toolchain
- PyO3 bindings require build infrastructure
- Higher integration complexity
- Wrapper maintenance burden

**Security:** High  
**Performance:** High  
**Maintainability:** Medium  
**Future Taproot Support:** Full

**Verdict:** **Accepted** — chosen as strategic solution

---

### Option D — Other mature alternatives

**Evaluated:**
- `btcpy` — fragmentary, no full PSBT support
- `btcsuite/btcec` — Go-based, would require cgo or separate process
- Custom wrapper around `libsecp256k1` — violates "no custom cryptography" policy

**Verdict:** None suitable as primary solution

---

## Decision

**Recommendation:** Adopt rust-bitcoin via a maintained PyO3 wrapper.

**Rationale:**
- Only option with complete PSBT finalization support
- Aligns with long-term maintainability goals
- Supports future Taproot requirements
- MIT license compatible
- Matches RawWalletAI's unique value proposition: not just another Bitcoin signer, but an autonomous agent platform

### Why This Matters for RawWalletAI's Unique Position

RawWalletAI is not competing with existing wallets on basic Bitcoin features. Its unique value is:

- 🤖 Hermes integration for autonomous agents
- 👥 Multi-agent rights management
- 🔒 Encrypted wallet management
- 📋 Approval workflows
- 📊 Portfolio overview
- 💸 Payment policies and limits
- 📝 Audit logs
- 🔌 Extensible backends

To support these features, RawWalletAI needs:
1. **Reliable transaction finalization** — rust-bitcoin provides this
2. **Future Taproot support** — rust-bitcoin provides this
3. **High performance** — important for agent-driven automation
4. **Security** — Rust memory safety reduces attack surface
5. **Maintainability** — active project, clear upgrade path

---

## Consequences

- Rust toolchain becomes a build dependency
- Additional CI complexity for cross-platform builds
- Long-term maintainability burden for wrapper
- Path to 1.0 release enabled
- Foundation for unique agent-centric features established

---

## Next Steps

1. Create ADR-0002: Build tooling and packaging strategy
2. Create ADR-0003: CI/CD and release engineering
3. Create ADR-0004: Cross-platform support strategy
4. Create ADR-0005: Long-term maintenance model
5. Create ADR-0006: Wrapper API design
6. Implement minimal PyO3 wrapper for PSBT finalization
7. Integration tests against regtest
8. External security audit
