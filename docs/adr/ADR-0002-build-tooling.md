# ADR-0002 — Build Tooling and Packaging Strategy

**Status:** Proposed  
**Date:** 2026-08-01  
**Decision Owner:** Pascal Haux / RawInstinctAI  
**Context:** Post-ADR-0007, preparing for rust-bitcoin integration

---

## Current State

- Pure Python project with setuptools
- No compiled extensions
- Dependencies installed via pip
- CI runs on Ubuntu only
- Version: 0.1.0

## Problem

Adding rust-bitcoin via PyO3 changes the project from pure-Python to a mixed Python/Rust project. This affects:

- Build environment setup
- Dependency installation
- CI/CD pipelines
- Release engineering
- Developer onboarding
- Cross-platform support

## Option A — maturin

### Advantages
- Purpose-built for PyO3 projects
- Handles version pinning automatically
- Builds wheels for all platforms
- Integrates with pip
- Supports optional Rust dependencies
- Active maintenance
- Industry standard for Rust+Python projects

### Disadvantages
- Additional build dependency
- Requires Rust toolchain on developer machines
- Wheels must be prebuilt for release
- Maturin-specific configuration

## Option B — setuptools-rust

### Advantages
- Integrates with existing setuptools workflow
- Minimal configuration changes
- Familiar to Python developers

### Disadvantages
- Less mature than maturin
- Fewer PyO3-specific features
- Wheel building more manual
- Smaller community

## Option C — scikit-build / scikit-build-core

### Advantages
- CMake-based, flexible
- Good for complex projects
- Supports multiple backends

### Disadvantages
- Overkill for single PyO3 extension
- CMake knowledge required
- More complex configuration
- Heavier dependency

## Recommendation

**Option A — maturin**

### Rationale
- Best PyO3 support
- Handles version management for rust-bitcoin
- Wheel building automation
- Active maintenance
- Industry standard for Rust+Python projects
- Aligns with rust-bitcoin ecosystem

## Required Setup

1. Add `maturin` to dev dependencies in `pyproject.toml`
2. Add `rust-bitcoin` to `Cargo.toml`
3. Create PyO3 wrapper module in `src/rawwalletai/rust/`
4. Configure maturin in `pyproject.toml`
5. Add Rust toolchain check to CI
6. Document Rust installation for developers

## Fallback Strategy

When Rust is unavailable:
- Graceful import error with clear message
- PSBT finalization methods raise `ImportError` with instructions
- Other wallet functionality remains operational
- Pure-Python mode for development

## Consequences

- Developer machines need Rust toolchain
- CI needs Rust setup step
- Release process includes wheel building
- Longer CI times
- Better type safety and performance for Bitcoin operations

## Decision

**Status:** Proposed  
**Next Step:** Validate maturin compatibility with current project structure
