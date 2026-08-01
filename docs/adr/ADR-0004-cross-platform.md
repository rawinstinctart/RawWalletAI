# ADR-0004 — Cross-Platform Support Strategy

**Status:** Proposed  
**Date:** 2026-08-01  
**Decision Owner:** Pascal Haux / RawInstinctAI  
**Context:** rust-bitcoin integration, platform coverage requirements

---

## Context

RawWalletAI targets Linux servers as primary deployment environment, but must also support:

- Developer machines: Linux, macOS, Windows
- CI environments: GitHub-hosted runners
- Future: Android/Termux, embedded systems
- Production: ARM64 servers

## Current State

- Linux-only development
- Python 3.11+ on x86_64
- No compiled extensions
- No ARM64 support

## Problem

rust-bitcoin + PyO3 introduces native code. We need a cross-platform strategy that:

1. Works on all major desktop platforms
2. Supports ARM64 architecture
3. Maintains reasonable build times
4. Doesn't break existing Linux workflows

## Option A — Universal2 + manylinux wheels

### Advantages
- Distribute prebuilt wheels via PyPI
- Users don't need Rust toolchain
- Fast installation
- Standard Python distribution model

### Disadvantages
- Need CI for each platform/arch
- Wheel storage and management
- Larger release artifacts

## Option B — Source builds only

### Advantages
- Single build artifact
- Users always get latest code
- No wheel management

### Disadvantages
- Users need Rust toolchain
- Slow installation
- High barrier to entry
- Not suitable for production

## Option C — Conditional dependencies

### Advantages
- Pure Python fallback when Rust unavailable
- Graceful degradation
- Best developer experience

### Disadvantages
- Two code paths to maintain
- Testing complexity
- Feature parity challenges

## Recommendation

**Option A — Universal2 + manylinux wheels, with Option C fallback**

### Rationale
- Production deployments use prebuilt wheels
- Developers can use source builds or wheels
- Fallback ensures project remains installable without Rust
- Standard Python packaging model

## Platform Targets

### Tier 1 — Required
- Linux x86_64 (manylinux2014)
- Linux ARM64 (manylinux2014)
- macOS x86_64 (macosx)
- macOS arm64 (macosx_11_0)
- Windows x86_64 (win_amd64)

### Tier 2 — Nice to have
- Linux armv7l (Raspberry Pi)
- Windows arm64
- Android/Termux (future)

## Build Strategy

1. Use `maturin` for wheel building
2. GitHub Actions matrix for Tier 1 platforms
3. Self-hosted ARM64 runner if needed
4. Publish to PyPI on release

## Consequences

- CI complexity increases
- Release process longer
- Better platform coverage
- Professional distribution model

## Decision

**Status:** Proposed  
**Next Step:** Validate cross-compilation feasibility
