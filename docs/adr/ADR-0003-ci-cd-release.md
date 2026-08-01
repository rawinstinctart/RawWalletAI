# ADR-0003 — CI/CD and Release Engineering

**Status:** Proposed  
**Date:** 2026-08-01  
**Decision Owner:** Pascal Haux / RawInstinctAI  
**Context:** Post-ADR-0001/0002, preparing for rust-bitcoin integration

---

## Context

After accepting rust-bitcoin via PyO3 wrapper and maturin as build tool, we need to update CI/CD and release engineering to handle:

1. Rust toolchain installation
2. Cross-platform wheel building
3. Multi-architecture testing
4. Release artifact management
5. Dependency updates for rust-bitcoin

## Current State

- GitHub Actions CI on Ubuntu only
- Python version matrix: 3.11, 3.12, 3.13
- Release workflow builds wheels via `python -m build`
- No Rust toolchain in CI

## Problem

Current CI/CD assumes pure Python. Adding Rust requires:

- Rust toolchain setup
- Caching for faster builds
- Multi-architecture testing
- Wheel building for multiple platforms
- Release process changes

## Option A — GitHub Actions only

### Advantages
- Already using GitHub Actions
- No new infrastructure
- GitHub-native artifact storage

### Disadvantages
- Limited cross-platform support
- macOS/Windows runners are slower/expensive
- No self-hosted runner option

## Option B — GitHub Actions + self-hosted runners

### Advantages
- Full control over build environment
- Can add ARM64, Windows, macOS
- Faster builds with dedicated hardware
- Consistent environment

### Disadvantages
- Infrastructure overhead
- Maintenance burden
- Cost for multiple runners

## Option C — GitHub Actions + cross-Rust targets

### Advantages
- Use `cross` for cross-compilation
- No self-hosted runners needed
- Single CI configuration

### Disadvantages
- Slower builds
- More complex configuration
- Limited testing on actual hardware

## Recommendation

**Option A — GitHub Actions with multi-runner matrix**

### Rationale
- Start with GitHub-hosted runners
- Add Ubuntu, macOS, Windows matrix
- Use `dtolnay/rust-action` for Rust setup
- Use `maturin-action` for wheel building
- Add self-hosted ARM64 runner if needed later

## CI/CD Changes

1. Add Rust setup step to all test jobs
2. Add `maturin build` step for release
3. Build wheels for:
   - `manylinux2014` x86_64
   - `macosx` x86_64 + arm64
   - `win_amd64`
4. Upload wheels as release artifacts
5. Run tests on all platforms

## Release Engineering Changes

1. Version rust-bitcoin in `Cargo.lock`
2. Build wheels during release workflow
3. Publish to PyPI with Rust wheels
4. Keep pure-Python fallback for development

## Consequences

- Longer CI times (~5-10 min increase)
- More complex release process
- Better cross-platform coverage
- Professional wheel distribution

## Decision

**Status:** Proposed  
**Next Step:** Prototype CI configuration with Rust setup
