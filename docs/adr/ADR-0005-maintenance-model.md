# ADR-0005 — Long-Term Maintenance Model

**Status:** Proposed  
**Date:** 2026-08-01  
**Decision Owner:** Pascal Haux / RawInstinctAI  
**Context:** rust-bitcoin integration, long-term sustainability

---

## Context

RawWalletAI is moving from pure Python to a mixed Python/Rust architecture. This introduces:

1. Two language ecosystems to maintain
2. PyO3 wrapper as a first-class component
3. Rust dependency updates
4. Cross-platform compatibility concerns
5. Different release cycles for Python and Rust components

## Current State

- Single-language project (Python)
- Single dependency tree
- Simple release process
- Low maintenance burden

## Problem

Mixed-language projects have higher maintenance burden. We need a model that:

1. Keeps wrapper maintainable
2. Manages rust-bitcoin updates
3. Handles breaking changes in either ecosystem
4. Maintains security posture
5. Doesn't overwhelm small team

## Option A — Pin rust-bitcoin, update manually

### Advantages
- Predictable behavior
- No surprise breaking changes
- Simple CI configuration

### Disadvantages
- Manual update process
- Risk of falling behind
- Security patches may be delayed

## Option B — Dependabot for Rust

### Advantages
- Automated PRs for rust-bitcoin updates
- Security patches auto-proposed
- Reduces manual work

### Disadvantages
- PR noise
- Need to validate each update
- Possible breakage from upstream changes

## Option C — Fork rust-bitcoin

### Advantages
- Full control over changes
- Can apply patches directly
- Independent release cycle

### Disadvantages
- Maintenance burden of fork
- Divergence risk
- Security audit complexity

## Recommendation

**Option A — Pin rust-bitcoin, scheduled updates**

### Rationale
- Rust-bitcoin is stable, major API changes are rare
- Pinning ensures reproducible builds
- Scheduled quarterly reviews balance security and stability
- Simpler than maintaining a fork
- Less noise than Dependabot

## Maintenance Schedule

### Weekly
- Monitor rust-bitcoin security advisories
- Review Python dependency updates
- Triage issues

### Monthly
- Run full test suite
- Update documentation
- Review technical debt

### Quarterly
- Evaluate rust-bitcoin minor updates
- Review ADR compliance
- Plan next quarter's work

### Annually
- Evaluate major rust-bitcoin upgrades
- External security audit
- Major version planning

## Wrapper Maintenance

1. Keep wrapper thin: expose only needed PSBT functions
2. No business logic in Rust
3. Comprehensive tests for wrapper boundary
4. Document all unsafe code blocks
5. Fuzz testing for serialization edge cases

## Security Model

1. Subscribe to rust-bitcoin security announcements
2. Monitor CVE databases
3. Quarterly dependency review
4. Annual external audit
5. Incident response plan for critical Rust CVEs

## Consequences

- Predictable maintenance burden
- Clear update process
- Security-conscious approach
- Sustainable for small team

## Decision

**Status:** Proposed  
**Next Step:** Define wrapper API surface in ADR-0006
