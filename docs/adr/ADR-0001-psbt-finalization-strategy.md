# ADR-0001 — PSBT Finalization Strategy

**Status:** Proposed  
**Date:** 2026-08-01  
**Decision Owner:** Pascal Haux / RawInstinctAI  
**Context:** RawWalletAI architecture freeze, PSBT finalization release blocker

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

### Current Blockers

- `python-bitcoinlib` does not expose PSBT finalization APIs in this environment
- No audited Bitcoin serialization library with witness support is installed
- Custom serialization is explicitly forbidden by project policy

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
- Familiar API surface

**Disadvantages:**
- **No PSBT finalization support** in current version
- Low maintenance activity
- No witness serialization
- Would require custom implementation violating project policy

**Maintenance:** Low  
**Security:** Medium  
**Future Compatibility:** Poor (no Taproot support planned)

**Verdict:** Rejected — does not solve the problem

---

### Option B — bitcoinlib

**Advantages:**
- Active maintenance
- SegWit support
- Python-native API

**Disadvantages:**
- **Partial PSBT support only** — no guaranteed finalization
- **Heavy dependency footprint:** SQLAlchemy, fastecdsa, pycryptodome
- Increased attack surface
- Overkill for wallet engine that prefers minimal dependencies
- License: MIT (compatible)

**Dependency Footprint:** Very High  
**Attack Surface:** High  
**Maintenance:** Active  
**Security:** Medium

**Verdict:** Rejected — violates minimal-dependency principle and does not guarantee full PSBT finalization

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

**Security:** High (Rust memory safety + audited code)  
**Performance:** High  
**Maintainability:** Medium (requires wrapper maintenance)  
**Future Taproot Support:** Full

**Verdict:** **Recommended** — best long-term solution, but requires architectural decision and implementation effort

---

### Option D — Other mature alternatives

**Evaluated:**
- `btcpy` — fragmentary, no full PSBT support
- `btcsuite/btcec` — Go-based, would require cgo or separate process
- Custom wrapper around `libsecp256k1` — violates "no custom cryptography" policy

**Verdict:** None suitable as primary solution

---

## Decision

**Current Recommendation:** Adopt rust-bitcoin via a maintained PyO3 wrapper.

**Rationale:**
- Only option with complete PSBT finalization support
- Aligns with long-term maintainability goals
- Supports future Taproot requirements
- MIT license compatible

**Required Validation:**
1. Verify PyO3 wrapper stability and API completeness
2. Assess Rust toolchain requirements for target deployment environments
3. Evaluate build complexity and CI/CD integration
4. Conduct security review of wrapper boundary

**Remaining Unknowns:**
- Maturity of existing PyO3 bindings for rust-bitcoin
- Build reliability across Linux distributions
- Long-term wrapper maintenance model

**Decision Status:** Proposed  
**Next Step:** Formal architectural decision and implementation planning

---

## Consequences

If approved:
- Rust toolchain becomes a build dependency
- Additional CI complexity for cross-platform builds
- Long-term maintainability burden for wrapper
- Path to 1.0 release enabled

If rejected:
- RawWalletAI remains non-functional for Bitcoin transactions
- No clear path to 1.0 release
- Alternative: explicit "not production-ready" documentation indefinitely
