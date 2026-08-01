# RawWalletAI – Rust Foundation Documentation

**Phase:** A — Rust Foundation  
**Status:** Complete  
**Date:** 2026-08-01

---

## Architecture Overview

RawWalletAI is evolving from a pure Python project to a hybrid Python + Rust architecture.

- **Python layer:** Wallet orchestration, Hermes integration, policies, API, audit
- **Rust layer:** Bitcoin consensus, PSBT finalization, transaction serialization, validation

The Rust layer is accessed via a stable PyO3 wrapper. The wrapper is the only permanent boundary between Python and Rust.

### Current Phase A Scope

- Empty Rust crate that builds successfully
- CI workflow for Rust formatting, linting, building, testing
- Documentation of future integration strategy
- No wallet logic in Rust
- No Bitcoin functionality in Rust
- No changes to Python runtime dependencies

---

## Directory Structure

```
/home/ubuntu/projects/RawWalletAI/
├── src/                        # Python package
│   └── rawwalletai/
│       ├── api/
│       ├── chains/
│       ├── config/
│       ├── core/
│       ├── storage/
│       └── transactions/
├── rust-core/                  # Rust crate (Phase A foundation)
│   ├── Cargo.toml
│   └── src/
│       └── lib.rs
├── tests/
│   └── unit/
├── docs/
│   ├── adr/
│   ├── rust_foundation.md
│   └── ...
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── rust.yml
│       ├── security.yml
│       └── release.yml
├── pyproject.toml
├── README.md
├── LICENSE
└── ...
```

### Rationale

- `rust-core/` at repository root: clear separation, standard Rust layout
- `src/` unchanged: Python code remains untouched
- `.github/workflows/rust.yml`: independent Rust CI job
- No symlinks, no monorepo nesting, no complex build orchestration

---

## Build Instructions

### Prerequisites

- Rust 1.74+ (stable)
- Cargo
- Python 3.11+

### Build Rust Crate

```bash
cd rust-core
cargo build
cargo test
```

### Build Python Package

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/unit/ -q
```

### Full Verification

```bash
# Python tests
python -m pytest tests/unit/ -q

# Rust tests
cd rust-core && cargo test
```

---

## Developer Setup

### Rust Toolchain

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile minimal

# Verify
rustc --version
cargo --version
```

### Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### IDE Support

- **VS Code:** rust-analyzer extension
- **PyCharm:** Rust plugin available
- **Vim/Neovim:** rust.vim / nvim-lspconfig

---

## Python Integration Strategy

### Current State (Phase A)

- Rust crate builds independently
- No PyO3 bindings yet
- No Python imports from Rust
- Python package unchanged

### Future Integration (Phase B+)

- **PyO3** will expose Rust functions to Python
- **maturin** will build wheels and handle packaging
- Python will call Rust via wrapper module
- Wallet core remains in Python until Phase C+

### Local Development Workflow

1. Edit Rust code in `rust-core/`
2. Run `cargo build` and `cargo test`
3. Python tests run independently
4. No need to rebuild Python package during Rust development

### Wheel Generation (Future)

```bash
# Phase B+
maturin build
pip install target/wheels/rawwalletai_rust-*.whl
```

---

## Build System

### Rust Build

- **Tool:** Cargo
- **Edition:** 2021
- **Profile:** dev for development, release for production
- **Target:** x86_64-unknown-linux-gnu (Phase A)

### Python Build

- **Tool:** setuptools + wheel
- **Backend:** setuptools.build_meta
- **Package dir:** `src/`
- **Unchanged in Phase A**

### Packaging Process

- Python package: `python -m build`
- Rust crate: `cargo build --release`
- Future: `maturin build` for combined wheel

### Release Workflow

- Python: GitHub Actions `release.yml` builds wheels via `python -m build`
- Rust: Future `maturin build` in release workflow
- Artifacts uploaded to GitHub Releases and PyPI

---

## CI/CD Preparation

### Current CI Jobs

- `.github/workflows/ci.yml` — Python tests on 3.11, 3.12, 3.13
- `.github/workflows/rust.yml` — Rust formatting, linting, build, test
- `.github/workflows/security.yml` — pip-audit, secret scanning
- `.github/workflows/release.yml` — Python package build

### Rust Job Details

```yaml
- name: Check formatting
  run: cd rust-core && cargo fmt -- --check

- name: Lint
  run: cd rust-core && cargo clippy -- -D warnings

- name: Build
  run: cd rust-core && cargo build

- name: Test
  run: cd rust-core && cargo test
```

### Independence

- Python tests pass without Rust
- Rust tests pass without Python
- CI runs both independently
- No cross-dependency in CI

---

## Coding Standards

### Rust Edition

- **Edition:** 2021
- **MSRV:** 1.74 (aligned with rust-bitcoin)

### Formatting

- **Tool:** `cargo fmt`
- **Style:** rustfmt defaults
- **Enforcement:** CI fails on formatting mismatch

### Linting

- **Tool:** `cargo clippy`
- **Configuration:** `-D warnings` in CI
- **Local development:** `cargo clippy --all-targets`

### Documentation

- All public items must have doc comments
- Use `///` for functions and structs
- Use `//!` for module-level docs
- Examples in doc comments where helpful

### Error Handling

- No `unwrap()` in public API
- No `panic!()` in public API
- Use `Result<T, E>` for all fallible operations
- Typed errors, no string errors
- Sensitive errors do not leak key material

### Naming

- **Functions:** snake_case
- **Types:** PascalCase
- **Constants:** SCREAMING_SNAKE_CASE
- **Modules:** snake_case

---

## Troubleshooting

### Rust Toolchain Not Found

```bash
source "$HOME/.cargo/env"
rustc --version
```

### Cargo Build Fails

```bash
cd rust-core
cargo clean
cargo build
cargo update
```

### Clippy Warnings

```bash
cd rust-core
cargo clippy --fix --allow-dirty
```

### PyO3 Version Mismatch (Future)

```bash
cd rust-core
cargo update -p pyo3
```

---

## Future Migration Path

### Phase A (Current)

- Empty Rust crate
- CI for Rust
- Documentation complete

### Phase B

- Add PyO3 bindings
- Expose minimal API surface
- Wrapper tests
- No wallet logic

### Phase C

- Python wrapper module
- Fallback behavior
- Integration with existing Python code

### Phase D

- PSBT finalization in Rust
- Witness construction
- Transaction serialization

### Phase E+

- Hermes integration
- Testnet validation
- Mainnet readiness

---

## Verification Checklist

- [x] Python project still works unchanged
- [x] Rust crate builds successfully
- [x] No wallet functionality exists in Rust
- [x] No new runtime dependency introduced into Python wallet
- [x] CI includes Rust formatting, linting, build, test
- [x] Python tests continue to pass independently
- [x] Documentation complete

---

## Remaining Work Before Phase B

1. Accept ADR-0002 (Build Tooling) formally
2. Choose maturin as build tool
3. Add `maturin` to dev dependencies in `pyproject.toml`
4. Add PyO3 and rust-bitcoin to `rust-core/Cargo.toml`
5. Create wrapper module structure
6. Define wrapper API surface (ADR-0006 accepted)

---

## Risks Identified

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Rust toolchain unavailable on target platforms | Medium | High | Document setup, CI validation |
| PyO3 version incompatibility | Medium | Medium | Pin versions, CI matrix |
| Build time increase | Medium | Low | Caching, incremental builds |
| Developer onboarding friction | Medium | Low | Good docs, setup scripts |
| Cross-platform wheel issues | Low | Medium | Multi-runner CI |

---

## Decision

**Status:** Complete  
**Next Phase:** Phase B — Wrapper API (pending ADR acceptance)
