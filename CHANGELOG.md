# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI workflows for test, security scanning, and release
- Fee validation with dust limits and sanity checks
- PSBT finalization verification tests

### Changed
- BIP-32 derivation corrected to HMAC-SHA512 with "Bitcoin seed" key
- KeyPair now derives actual compressed public key via ECKey
- Encrypted storage uses random 16-byte salt per encryption

### Fixed
- Mnemonic leak in wallet creation API
- MockUTXOBackend inheritance
- BitcoinAddress optional path parameter

### Security
- HKDF salt added to encrypted storage
- Electrum backend marked experimental due missing dependency

## [0.1.0] - 2026-08-01

### Added
- Initial project structure
- BIP-39 mnemonic generation
- BIP-32 master key derivation
- AES-256-GCM encrypted storage
- Bitcoin address generation (p2wpkh)
- ECDSA signing via `cryptography`
- PSBT creation and signing
- Transaction builder with fee estimation
- UTXO engine with multiple backends
- Broadcast layer abstraction
- RBF support via sequence numbers
- FastAPI server

### Security
- Security audit completed: 6 findings fixed, 5 accepted with rationale

[Unreleased]: https://github.com/rawinstinctart/RawWalletAI/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/rawinstinctart/RawWalletAI/releases/tag/v0.1.0
