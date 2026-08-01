# RawWalletAI – Project Roadmap

## Phase 0 — Architecture Freeze

**Status:** Complete  
**Objectives:** Stabilize wallet core, freeze feature additions, document blockers  
**Deliverables:**
- Security audit completed
- Fee validation hardened
- CI/CD workflows created
- Release blocker documented
- ADR-0001 created

**Exit Criteria:**
- Core crypto stack unchanged
- All tests passing
- Documentation complete

**Dependencies:** None  
**Risks:** Low

---

## Phase 1 — PSBT Finalization

**Status:** Planned  
**Objectives:** Integrate audited PSBT finalization library, produce broadcast-ready transactions  
**Deliverables:**
- Library selection and integration
- PSBT finalization implementation
- Witness/scriptSig construction
- Raw transaction extraction
- End-to-end tests

**Exit Criteria:**
- Finalized transactions pass Bitcoin Core regtest validation
- All PSBT test vectors pass
- No custom serialization code

**Dependencies:**
- ADR-0001 decision
- External audit of finalizer

**Risks:** High (library integration complexity)

---

## Phase 2 — Public API Hardening

**Status:** Planned  
**Objectives:** Harden API surface, add authentication, rate limiting, monitoring  
**Deliverables:**
- API authentication
- Rate limiting
- Request validation
- Monitoring hooks
- OpenAPI spec

**Exit Criteria:**
- API penetration tested
- No unauthenticated endpoints

**Dependencies:** Phase 1  
**Risks:** Medium

---

## Phase 3 — Hermes Integration

**Status:** Planned  
**Objectives:** Native integration with Hermes Agent for autonomous transaction workflows  
**Deliverables:**
- Hermes skill for RawWalletAI
- Autonomous transaction execution
- Notification integration

**Exit Criteria:**
- End-to-end autonomous workflow tested
- No manual intervention required

**Dependencies:** Phase 2  
**Risks:** Medium

---

## Phase 4 — Testnet Validation

**Status:** Planned  
**Objectives:** Validate wallet against Bitcoin testnet, fix edge cases  
**Deliverables:**
- Integration tests on testnet
- Bug fixes from testnet exposure
- Performance benchmarks

**Exit Criteria:**
- 100 testnet transactions successful
- No critical bugs found

**Dependencies:** Phase 1  
**Risks:** Medium

---

## Phase 5 — Mainnet Readiness

**Status:** Planned  
**Objectives:** Prepare for mainnet deployment  
**Deliverables:**
- External security audit
- Penetration test
- Documentation finalization
- Release candidate

**Exit Criteria:**
- External audit passed
- No critical/high findings
- RC tested in production-like environment

**Dependencies:** Phase 4  
**Risks:** High

---

## Phase 6 — Version 1.0

**Status:** Planned  
**Objectives:** First stable release  
**Deliverables:**
- Production-ready wallet core
- Complete documentation
- Stable API
- Security audit report

**Exit Criteria:**
- All critical/high technical debt resolved
- External audit passed
- Community feedback incorporated

**Dependencies:** Phase 5  
**Risks:** Low
