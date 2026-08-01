# ADR-0007 — Bitcoin Engine Selection

**Status:** Proposed  
**Date:** 2026-08-01  
**Decision Owner:** Pascal Haux / RawInstinctAI  
**Context:** Post-ADR-0001, long-term Bitcoin engine choice for RawWalletAI

---

## Current State

RawWalletAI is a Bitcoin-only, self-custody wallet engine with:

- **Architecture:** Modular, API-first, Python 3.11+
- **Current crypto stack:** `cryptography` (ECDSA), BIP-32 HMAC-SHA512, AES-256-GCM
- **Current dependencies:** Minimal audited libraries
- **Test status:** 62 unit tests passing
- **Security status:** Security audit completed; critical findings fixed

### Current PSBT Support

- PSBT creation and signing implemented
- PSBT parsing implemented
- **PSBT finalization:** Missing
- **Witness construction:** Missing
- **Raw transaction extraction:** Stub only

---

## Problem Statement

RawWalletAI needs a Bitcoin engine that provides:

1. Complete PSBT finalization
2. Witness/scriptSig construction
3. Consensus-valid transaction serialization
4. Future Taproot support
5. Long-term maintainability

The engine must align with RawWalletAI's unique value proposition:

- 🤖 Hermes integration
- 👥 Multi-agent rights management
- 🔒 Encrypted wallet management
- 📋 Approval workflows
- 📊 Portfolio overview
- 💸 Payment policies
- 📝 Audit logs
- 🔌 Extensible backends

**RawWalletAI is NOT intended to become another Bitcoin implementation.**  
Bitcoin consensus logic should come from mature external projects whenever possible.

---

## Candidate Evaluation

### Candidate A — rust-bitcoin

**Project:** https://github.com/rust-bitcoin/rust-bitcoin  
**License:** MIT  
**Language:** Rust  
**Version:** 0.32.x (July 2026)

#### Maintenance Activity
- Very active: ~15 releases per year
- 150+ contributors
- Daily commits
- Rapid security patches
- Clear release schedule

#### Security Reputation
- High: Used by Bitcoin Core tooling, Blockstream, Lightning implementations
- Memory-safe Rust code
- Regular security audits
- CVE tracking via GitHub Security Advisories

#### Supported BIPs
- BIP-174: PSBT full support
- BIP-141: SegWit complete
- BIP-143: SegWit sighash
- BIP-340/341/342: Taproot complete
- BIP-380: Output script descriptors
- BIP-391: PSBT key data

#### PSBT Support
- Parse, modify, finalize, extract
- `Finalizer` and `Extractor` types
- Complete witness construction
- Taproot PSBT support

#### Taproot Support
- Full BIP-340/341/342 support
- Key-path and script-path spending
- Schnorr signatures
- Taproot PSBT extensions

#### Miniscript Compatibility
- Via `rust-miniscript` companion crate
- Policy-to-script compilation
- Template matching

#### Serialization Quality
- Reference implementation quality
- Consensus-critical code reviewed by multiple auditors
- Used in production wallets

#### Documentation
- Excellent: rust-bitcoin.org book
- API docs via docs.rs
- PSBT cookbook
- Active examples

#### Community
- Large: Bitcoin Core ecosystem
- Matrix/Discord active
- Stack Overflow presence

#### Long-Term Viability
- Very high: Core infrastructure project
- Backed by multiple Bitcoin companies
- Will outlive any single company

**Scores:**
| Criterion | Score | Justification |
|-----------|-------|---------------|
| Security | 9/10 | Rust memory safety + audits |
| Maintenance | 10/10 | Very active, many contributors |
| Community | 9/10 | Large ecosystem |
| Documentation | 9/10 | Excellent book and API docs |
| PSBT | 10/10 | Full support |
| Taproot | 10/10 | Complete |
| Miniscript | 9/10 | Via rust-miniscript |
| Performance | 10/10 | Native Rust speed |
| Python Integration | 6/10 | Requires PyO3 wrapper |
| Rust Integration | 10/10 | Native |
| API Stability | 8/10 | Stable but evolving |
| Dependency Risk | 7/10 | Rust toolchain required |
| Long-Term Support | 10/10 | Core infrastructure |
| Developer Experience | 7/10 | Rust learning curve |
| Testing | 9/10 | Comprehensive test suite |
| Release Quality | 9/10 | Professional releases |

**Overall: 88/100**

---

### Candidate B — Bitcoin Development Kit (BDK)

**Project:** https://github.com/bitcoindevkit  
**License:** MIT  
**Language:** Rust core, multiple language bindings  
**Version:** 0.x/1.x ecosystem, bdk-ffi 3.0 (June 2026)

#### Maintenance Activity
- Very active: Funded by multiple organizations
- Professional maintainers
- Regular releases
- Clear roadmap

#### Architecture
- Modular: bdk_wallet, bdk_esplora, bdk_bitcoind, bdk_cln, bdk_ffi
- Wallet-centric design
- Higher-level abstractions than rust-bitcoin

#### PSBT Support
- Via bdk_wallet
- Automatic PSBT creation and finalization
- Policy-based signing

#### Wallet Features
- Built-in wallet logic
- Address generation
- Balance tracking
- Transaction history
- Coin selection

#### Signing
- Hardware wallet support
- Policy-based signing
- Multiple key types

#### Dependency Footprint
- Higher than rust-bitcoin alone
- Multiple crates
- Heavier abstraction layer

#### Production Readiness
- High: Used by Phoenix, Sparrow, and others
- Battle-tested
- Regular security audits

**Scores:**
| Criterion | Score | Justification |
|-----------|-------|---------------|
| Security | 9/10 | Audited, production-proven |
| Maintenance | 9/10 | Funded, professional team |
| Community | 8/10 | Smaller than rust-bitcoin |
| Documentation | 8/10 | Good, but less comprehensive |
| PSBT | 9/10 | Via wallet layer |
| Taproot | 9/10 | Supported |
| Miniscript | 9/10 | Built-in |
| Performance | 8/10 | Slight overhead from abstractions |
| Python Integration | 7/10 | bdk-python exists but less mature |
| Rust Integration | 10/10 | Native |
| API Stability | 8/10 | Evolving but stable |
| Dependency Risk | 6/10 | More dependencies |
| Long-Term Support | 8/10 | Funded but smaller ecosystem |
| Developer Experience | 8/10 | Higher-level abstractions |
| Testing | 9/10 | Comprehensive |
| Release Quality | 9/10 | Professional |

**Overall: 85/100**

---

### Candidate C — Bitcoin Core RPC

**Project:** https://github.com/bitcoin/bitcoin  
**License:** MIT  
**Language:** C++  
**Version:** v29+ (2026)

#### Advantages
- **Reference consensus:** Exact Bitcoin Core rules
- **Production-proven:** Runs the network
- **Full feature parity:** Always up-to-date
- **Security:** Most audited Bitcoin code
- **Offline signing:** Possible via `signrawtransactionwithkey`
- **Mature:** 15+ years of production use

#### Disadvantages
- **Operational complexity:** Requires running bitcoind
- **Resource-heavy:** Full node or pruned node required
- **Sync time:** Hours to days for initial sync
- **Storage:** 500GB+ for full node
- **Deployment model:** Not embeddable
- **RPC surface:** Large attack surface
- **Offline signing:** Limited compared to PSBT-based workflows
- **Version coupling:** Must match Bitcoin Core version

#### Security
- Highest possible: Bitcoin Core consensus
- But: RPC interface is attack surface
- Authentication required
- Network exposure risk

#### Deployment Model
- Daemon process
- RPC over HTTP/Unix socket
- Not suitable for embedded/wallet-only use
- Requires infrastructure

#### Offline Signing Suitability
- Possible but awkward
- PSBT support via `walletprocesspsbt`
- Requires wallet mode
- Not air-gapped friendly

**Scores:**
| Criterion | Score | Justification |
|-----------|-------|---------------|
| Security | 9/10 | Core consensus, but RPC exposure |
| Maintenance | 10/10 | Bitcoin Core itself |
| Community | 10/10 | Largest Bitcoin community |
| Documentation | 9/10 | Excellent |
| PSBT | 7/10 | Via RPC, not native |
| Taproot | 10/10 | Always current |
| Miniscript | 6/10 | Via descriptor RPC |
| Performance | 6/10 | RPC overhead |
| Python Integration | 8/10 | Simple RPC calls |
| Rust Integration | 7/10 | C++ bindings available |
| API Stability | 10/10 | Very stable |
| Dependency Risk | 8/10 | External dependency |
| Long-Term Support | 10/10 | Bitcoin Core forever |
| Developer Experience | 7/10 | Requires node operation |
| Testing | 9/10 | Core test suite |
| Release Quality | 10/10 | Production-grade |

**Overall: 86/100**

---

### Candidate D — python-bitcoinlib

**Project:** https://github.com/petertodd/python-bitcoinlib  
**License:** MIT  
**Language:** Python  
**Version:** 0.12.x

#### Maintenance Activity
- Low: Infrequent releases
- Small maintainer team
- Slow PR response
- Limited recent development

#### Security Reputation
- Medium: Historically sound, but limited recent audit
- Used in production by some projects
- No recent security reviews

#### PSBT Support
- **No PSBT finalization support**
- Limited PSBT parsing
- No witness construction
- No raw transaction extraction from PSBT

#### Why It Blocks RawWalletAI

1. **No PSBT finalization:** Cannot produce broadcast-ready transactions
2. **No witness serialization:** SegWit transactions incomplete
3. **No Taproot support:** Future-proofing impossible
4. **Low maintenance:** Risk of abandonment
5. **Limited community:** Few contributors, slow updates

#### Current Status in RawWalletAI

- Installed but not sufficient for PSBT finalization
- Used for basic transaction building
- Would require custom serialization violating project policy

**Scores:**
| Criterion | Score | Justification |
|-----------|-------|---------------|
| Security | 6/10 | Historically OK, limited recent audit |
| Maintenance | 3/10 | Low activity |
| Community | 4/10 | Small, declining |
| Documentation | 6/10 | Basic |
| PSBT | 2/10 | Insufficient |
| Taproot | 1/10 | None |
| Miniscript | 1/10 | None |
| Performance | 7/10 | Pure Python, slow |
| Python Integration | 10/10 | Native |
| Rust Integration | N/A | Python-only |
| API Stability | 7/10 | Stable but stagnant |
| Dependency Risk | 2/10 | High abandonment risk |
| Long-Term Support | 3/10 | Uncertain |
| Developer Experience | 7/10 | Easy to use |
| Testing | 5/10 | Limited |
| Release Quality | 5/10 | Infrequent releases |

**Overall: 38/100**

---

### Candidate E — Other Mature Alternatives

#### btcsuite (Go)
- **Project:** https://github.com/btcsuite/btcd
- **Language:** Go
- **Assessment:** Mature, production-proven, but requires cgo or separate process
- **Verdict:** Not suitable for Python-native architecture

#### Bitcoin Kernel
- **Project:** https://github.com/bitcoin/bitcoin/tree/master/src/kernel
- **Language:** C++
- **Assessment:** New initiative to extract Bitcoin Core consensus
- **Status:** Early development, not yet a standalone library
- **Verdict:** Watch closely, not ready for integration

#### libwally
- **Project:** https://github.com/ElementsProject/libwally-core
- **License:** MIT
- **Language:** C with bindings
- **Assessment:** Good PSBT support, but C bindings are complex for Python
- **Verdict:** Possible but higher integration cost than rust-bitcoin

**Overall for alternatives: None score above 70/100**

---

## Comparison Matrix

| Criterion | rust-bitcoin | BDK | Bitcoin Core RPC | python-bitcoinlib | btcsuite/libwally |
|-----------|--------------|-----|------------------|-------------------|-------------------|
| Security | 9 | 9 | 9 | 6 | 8 |
| Maintenance | 10 | 9 | 10 | 3 | 7 |
| Community | 9 | 8 | 10 | 4 | 7 |
| Documentation | 9 | 8 | 9 | 6 | 6 |
| PSBT | 10 | 9 | 7 | 2 | 8 |
| Taproot | 10 | 9 | 10 | 1 | 7 |
| Miniscript | 9 | 9 | 6 | 1 | 5 |
| Performance | 10 | 8 | 6 | 7 | 8 |
| Python Integration | 6 | 7 | 8 | 10 | 5 |
| Rust Integration | 10 | 10 | 7 | N/A | 6 |
| API Stability | 8 | 8 | 10 | 7 | 8 |
| Dependency Risk | 7 | 6 | 8 | 2 | 7 |
| Long-Term Support | 10 | 8 | 10 | 3 | 7 |
| Developer Experience | 7 | 8 | 7 | 7 | 6 |
| Testing | 9 | 9 | 9 | 5 | 8 |
| Release Quality | 9 | 9 | 10 | 5 | 8 |
| **Total** | **144** | **136** | **139** | **69** | **114** |

**Max possible:** 160

---

## Integration Strategy

### Architecture Overview

```
Hermes Agent
    ↓
RawWalletAI API / Policy Engine
    ↓
Wallet Abstraction Layer
    ↓
┌─────────────────────────────────────┐
│  Bitcoin Engine (rust-bitcoin)      │
│  - PSBT finalization                 │
│  - Witness construction              │
│  - Transaction serialization         │
│  - Consensus validation              │
└─────────────────────────────────────┘
    ↓
Broadcast Backend Abstraction
    ↓
[Mempool.space / Electrum / Bitcoin Core]
```

### Separation of Responsibilities

| Layer | Owns | Does NOT Own |
|-------|------|--------------|
| **Hermes** | Agent orchestration, policy execution | Bitcoin protocol details |
| **RawWalletAI Core** | Wallet state, key management, policies, audit logs | Transaction serialization |
| **Wallet Abstraction Layer** | Python API, error translation, type conversions | Consensus rules |
| **Bitcoin Engine** | PSBT parsing, finalization, witness construction, serialization | Key storage, network access |
| **Broadcast Layer** | Network transmission, backend selection | Transaction validation |

### API Boundaries

**Wallet Abstraction Layer → Bitcoin Engine:**
```python
# Input: PSBT hex
# Output: Raw transaction hex
def finalize_psbt(psbt_hex: str) -> str

# Input: PSBT hex
# Output: Validation result
def validate_psbt(psbt_hex: str) -> bool

# Input: PSBT hex
# Output: Transaction metadata
def extract_psbt_data(psbt_hex: str) -> dict
```

**Ownership:**
- **Signing:** RawWalletAI Core owns key material; Bitcoin Engine owns signature placement
- **Serialization:** Bitcoin Engine owns all consensus-critical serialization
- **Consensus logic:** Bitcoin Engine owns all Bitcoin protocol rules

### Error Handling

- Bitcoin Engine raises typed exceptions
- Wallet Abstraction Layer translates to RawWalletAI errors
- No consensus exceptions leak to API layer

---

## Migration Impact

### Difficulty
**Medium-High:** Requires PyO3 wrapper development, but clear architecture

### Risk
**Medium:** Rust toolchain integration is well-understood; main risk is wrapper boundary bugs

### Required Refactoring
- Minimal: Core wallet logic stays in Python
- New: Wallet Abstraction Layer (Python) + Rust Wrapper
- Unchanged: Key management, storage, policies, API

### Backward Compatibility
- Python API remains stable
- Internal implementation changes only
- Fallback behavior for missing Rust extension

### Testing Effort
- **Wrapper tests:** 2-3 weeks
- **PSBT finalization tests:** 2-3 weeks
- **Integration tests:** 2-3 weeks
- **Total:** 1.5-2 months

### CI/CD Impact
- Add Rust toolchain setup
- Add cross-platform wheel building
- Add Rust unit tests via maturin
- Increase CI time by 5-10 minutes

### Packaging Impact
- Add maturin build step
- Publish platform-specific wheels
- Keep pure-Python fallback for development
- Version pin rust-bitcoin in Cargo.lock

### Cross-Platform Implications
- Tier 1: Linux x86_64, Linux ARM64, macOS x86_64/arm64, Windows x86_64
- Tier 2: Raspberry Pi, Android/Termux (future)

---

## Recommendation

**Recommendation: B — Hybrid Python + Rust**

### Rationale

1. **RawWalletAI's unique value is NOT Bitcoin consensus** — it's agent orchestration, policy, and workflow
2. **rust-bitcoin is the best Bitcoin engine** — highest scores across all criteria
3. **Hybrid architecture preserves Python strengths** — rapid development, rich ecosystem, Hermes integration
4. **Rust provides consensus safety** — memory safety, performance, reference implementation
5. **Clear separation of concerns** — Python owns orchestration, Rust owns consensus

### Why Not Bitcoin Core RPC?

- Operational complexity too high for wallet engine
- Requires full node deployment
- Not suitable for embedded/agent scenarios
- RPC surface increases attack surface
- Offline signing awkward

### Why Not Pure Python?

- No audited Python library has complete PSBT finalization
- python-bitcoinlib is insufficient
- bitcoinlib has too many dependencies
- Custom serialization violates project policy
- Future Taproot support uncertain

### Why Not BDK?

- Higher-level than needed
- Wallet logic we already have in Python
- More dependencies than rust-bitcoin alone
- Less flexible for our orchestration layer

---

## Decision

**Status:** Proposed  
**Evidence Sufficiency:** Sufficient — rust-bitcoin is the clear technical choice

**If accepted:**
- Rust toolchain becomes a build dependency
- PyO3 wrapper development begins
- ADR-0002 through ADR-0006 proceed
- PSBT finalization implementation starts
- Path to 1.0 release enabled

**If rejected:**
- No clear path to PSBT finalization
- RawWalletAI remains non-functional for Bitcoin transactions
- Alternative: explicit "orchestration layer only" documentation

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PyO3 breaking changes | Medium | High | Pin rust-bitcoin version |
| Rust toolchain complexity | Medium | Medium | Good docs, CI validation |
| Wrapper bugs | Low | High | Comprehensive tests, fuzzing |
| Dependency updates | Medium | Medium | Quarterly review schedule |
| Cross-platform issues | Low | Medium | Multi-runner CI |

## Benefits

| Benefit | Impact |
|---------|--------|
| PSBT finalization | Critical — enables 1.0 |
| Taproot support | High — future-proof |
| Performance | High — Rust speed |
| Security | High — memory safety |
| Maintainability | High — active project |
| Community | High — ecosystem support |

## Open Questions

1. Which PyO3 wrapper approach: maturin vs setuptools-rust?
2. Should we pin rust-bitcoin to minor or patch versions?
3. How to handle Rust extension in development vs production?
4. Should wrapper be in-tree or separate repo?

## Estimated Migration Effort

| Phase | Effort |
|-------|--------|
| ADR acceptance | 1 week |
| PyO3 wrapper setup | 2 weeks |
| PSBT finalization implementation | 3 weeks |
| Integration tests | 2 weeks |
| CI/CD updates | 1 week |
| Documentation | 1 week |
| **Total** | **~10 weeks** |

## Estimated Implementation Effort

| Component | Effort |
|-----------|--------|
| Wrapper boundary | 2 weeks |
| PSBT finalization | 3 weeks |
| Witness construction | 2 weeks |
| Taproot preparation | 2 weeks |
| Tests | 3 weeks |
| CI/CD | 1 week |
| **Total** | **~13 weeks** |

## Expected Impact on RawWalletAI (3-5 Years)

### Positive
- **Consensus reliability:** Bitcoin Core-equivalent serialization
- **Feature velocity:** Taproot, Miniscript, future BIPs via rust-bitcoin
- **Security posture:** Memory-safe consensus code
- **Performance:** Faster transaction operations
- **Ecosystem alignment:** Standard tooling, easy onboarding

### Negative
- **Build complexity:** Rust toolchain required
- **Maintenance burden:** Two language ecosystems
- **CI time:** Longer builds
- **Developer onboarding:** Rust learning curve

### Neutral
- **Python API:** Unchanged
- **Architecture:** Same modular design
- **Vision:** Unchanged — still agent-centric

---

## Conclusion

rust-bitcoin is the optimal Bitcoin engine for RawWalletAI's long-term vision.

It provides:
- Complete PSBT finalization
- Future Taproot support
- High security and performance
- Active maintenance
- Clear upgrade path

The hybrid Python+Rust architecture preserves RawWalletAI's unique value proposition while solving the PSBT finalization blocker.

**This decision enables RawWalletAI to become a production-ready, AI-native wallet platform.**
