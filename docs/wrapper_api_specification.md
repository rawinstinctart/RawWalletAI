# RawWalletAI – Wrapper API Specification

**Version:** 0.1.0-draft  
**Date:** 2026-08-01  
**Status:** Proposed  
**Phase:** B — Wrapper API Specification  
**Owner:** RawInstinctAI  
**Audience:** Python developers, Rust developers, security reviewers

---

## 1. Purpose

This document defines the **stable, production-ready Wrapper API** between Python and the future Rust Bitcoin Engine.

It is the **implementation contract** for Phase B and beyond.

### Goals

- Hide all Bitcoin implementation details from Python
- Expose only high-level wallet functionality
- Keep Rust fully replaceable internally
- Minimize Python↔Rust calls
- Remain stable across RawWalletAI 1.x releases

### Non-Goals

- Implement wallet logic in Rust
- Implement Bitcoin consensus logic in Python
- Add new dependencies
- Expose PSBT internals to Python unless explicitly required

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Hermes                                                       │
│ - Intelligence                                                │
│ - Automation                                                  │
│ - Decision making                                             │
└──────────────────────────────┬──────────────────────────────┘
                               │ API calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ RawWalletAI Python Layer                                     │
│ - Wallet orchestration                                       │
│ - Policy enforcement                                         │
│ - Authentication / Authorization                             │
│ - Audit logging                                              │
│ - Secure storage                                             │
│ - Provider abstraction                                       │
│ - Plugin system                                              │
└──────────────────────────────┬──────────────────────────────┘
                               │ Wrapper API v1 calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ PyO3 Wrapper Boundary                                        │
│ - Type conversion                                            │
│ - Error translation                                          │
│ - GIL release                                                │
│ - Memory ownership management                                │
└──────────────────────────────┬──────────────────────────────┘
                               │ Rust FFI
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Rust Bitcoin Engine                                          │
│ - BIP-32 / BIP-39                                           │
│ - PSBT build/sign/finalize                                   │
│ - Transaction construction                                   │
│ - Serialization                                              │
│ - Validation                                                 │
└─────────────────────────────────────────────────────────────┘
```

### Responsibility Summary

| Layer | Owns | Must Never Do |
|-------|------|---------------|
| Hermes | Decisions, user interaction | Handle raw keys, PSBT internals |
| Python | Orchestration, policies, auth, audit | Implement Bitcoin consensus |
| Wrapper | Translation, error mapping, GIL | Add business logic |
| Rust | Consensus, serialization, signing | Enforce business policies |

---

## 3. Public Wrapper API

All functions are exposed through a single Python module: `rawwalletai.rust_wrapper`.

### 3.1 Wallet Lifecycle

#### `create_wallet(name: str, passphrase: str, network: str = "mainnet") -> WalletData`

**Purpose:** Create a new wallet from a random seed.  
**Input:**
- `name`: Human-readable wallet name
- `passphrase`: Encryption passphrase for seed storage
- `network`: Bitcoin network (`"mainnet"`, `"testnet"`, `"signet"`)

**Output:** `WalletData` object containing `wallet_id`, `master_fingerprint`, `network`, `xpub`, `created_at`.

**Errors:**
- `WalletError` — Wallet creation failed
- `ValidationError` — Invalid network

**Security:** Seed is generated in Rust, encrypted in Rust, never exposed to Python. Passphrase is used for encryption only, never stored.

---

#### `import_wallet(seed_phrase: str, passphrase: str, network: str = "mainnet") -> WalletData`

**Purpose:** Import an existing wallet from a BIP-39 seed phrase.  
**Input:**
- `seed_phrase`: 12 or 24 word mnemonic
- `passphrase`: BIP-39 passphrase
- `network`: Bitcoin network

**Output:** `WalletData` object.

**Errors:**
- `WalletError` — Invalid seed phrase or derivation failed
- `ValidationError` — Invalid network

**Security:** Seed phrase is consumed by Rust, not stored in plaintext. Passphrase not stored.

---

#### `export_public_metadata(wallet_id: str) -> PublicWalletData`

**Purpose:** Export public-only wallet information.  
**Input:**
- `wallet_id`: Wallet identifier

**Output:** `PublicWalletData` containing `wallet_id`, `master_fingerprint`, `network`, `xpub`, `created_at`.

**Errors:**
- `WalletError` — Wallet not found
- `WalletLockedError` — Wallet is locked

**Security:** No private keys, no seed, no internal state exposed.

---

### 3.2 Key Operations

#### `derive_key(wallet_id: str, path: str) -> KeyData`

**Purpose:** Derive a key at a BIP-32 path.  
**Input:**
- `wallet_id`: Wallet identifier
- `path`: BIP-32 derivation path, e.g., `m/84'/0'/0'/0/0`

**Output:** `KeyData` containing `path`, `address`, `script_type`, `public_key`, `fingerprint`.

**Errors:**
- `KeyError` — Derivation failed
- `WalletLockedError` — Wallet is locked
- `AuthorizationError` — Caller not allowed to derive keys

**Security:** Private key never returned. Only public key and address.

---

#### `derive_address(wallet_id: str, path: str, script_type: str = "p2wpkh") -> AddressData`

**Purpose:** Derive a Bitcoin address for a script type.  
**Input:**
- `wallet_id`: Wallet identifier
- `path`: BIP-32 derivation path
- `script_type`: `"p2wpkh"`, `"p2tr"`, `"p2sh-p2wpkh"`, `"p2pkh"`

**Output:** `AddressData` containing `address`, `script_type`, `path`, `script_pubkey`.

**Errors:**
- `KeyError` — Derivation failed
- `ValidationError` — Unsupported script type
- `WalletLockedError` — Wallet is locked

**Security:** Private key never exposed.

---

#### `derive_xpub(wallet_id: str, path: str) -> XpubData`

**Purpose:** Export an extended public key.  
**Input:**
- `wallet_id`: Wallet identifier
- `path`: BIP-32 path for xpub derivation

**Output:** `XpubData` containing `xpub`, `path`, `depth`, `fingerprint`.

**Errors:**
- `KeyError` — Derivation failed
- `WalletLockedError` — Wallet is locked

---

### 3.3 Transaction Operations

#### `build_transaction(wallet_id: str, recipients: list[dict], fee_rate: int | None = None) -> PsbtData`

**Purpose:** Build an unsigned PSBT from recipients and fee rate.  
**Input:**
- `wallet_id`: Wallet identifier
- `recipients`: List of `{address, amount_sats}`
- `fee_rate`: Satoshis per vbyte, or `None` for auto-estimate

**Output:** `PsbtData` containing `psbt_hex`, `inputs`, `outputs`, `fee_sats`, `vsize`, `weight`.

**Errors:**
- `PsbtError` — PSBT construction failed
- `InsufficientFundsError` — Not enough balance
- `ValidationError` — Invalid recipient or amount
- `WalletLockedError` — Wallet is locked
- `PolicyViolationError` — Policy would be violated

**Security:** No signing occurs. PSBT is unsigned.

---

#### `sign_psbt(wallet_id: str, psbt_hex: str) -> SignedPsbtData`

**Purpose:** Sign an unsigned or partially signed PSBT.  
**Input:**
- `wallet_id`: Wallet identifier
- `psbt_hex`: Base64 or hex encoded PSBT

**Output:** `SignedPsbtData` containing `psbt_hex`, `signed_inputs`, `total_inputs`, `complete`.

**Errors:**
- `SignatureError` — Signing failed
- `PsbtError` — Invalid PSBT
- `WalletLockedError` — Wallet is locked
- `AuthorizationError` — Caller not allowed to sign

**Security:** Private keys used only within Rust. PSBT may contain partially signed inputs from other signers.

---

#### `finalize_psbt(psbt_hex: str) -> TransactionData`

**Purpose:** Finalize a fully signed PSBT into a raw transaction.  
**Input:**
- `psbt_hex`: Base64 or hex encoded signed PSBT

**Output:** `TransactionData` containing `tx_hex`, `txid`, `inputs`, `outputs`, `fee_sats`, `vsize`, `weight`.

**Errors:**
- `FinalizeError` — PSBT could not be finalized
- `ValidationError` — Transaction invalid after finalization

**Security:** No private keys involved. Input signatures verified.

---

#### `broadcast_transaction(tx_hex: str) -> BroadcastResult`

**Purpose:** Broadcast a finalized transaction to the Bitcoin network.  
**Input:**
- `tx_hex`: Hex encoded raw transaction

**Output:** `BroadcastResult` containing `success`, `txid`, `error`.

**Errors:**
- `NetworkError` — Broadcast backend unavailable
- `ValidationError` — Transaction rejected by network

**Security:** Transaction must be finalized before broadcast. No raw transaction modification allowed.

---

### 3.4 Validation

#### `validate_address(address: str, network: str = "mainnet") -> AddressInfo`

**Purpose:** Validate a Bitcoin address.  
**Input:**
- `address`: Bitcoin address string
- `network`: Network context

**Output:** `AddressInfo` containing `valid`, `address`, `script_type`, `network`.

**Errors:**
- `ValidationError` — Invalid address format

---

#### `validate_transaction(tx_hex: str) -> ValidationResult`

**Purpose:** Validate a raw transaction.  
**Input:**
- `tx_hex`: Hex encoded raw transaction

**Output:** `ValidationResult` containing `valid`, `errors`, `warnings`.

**Errors:** None — always returns result object with validation status.

---

#### `verify_signature(message: bytes, signature: bytes, pubkey: bytes) -> bool`

**Purpose:** Verify a Bitcoin signature.  
**Input:**
- `message`: Message bytes
- `signature`: DER signature
- `pubkey`: Public key bytes

**Output:** `bool` — signature validity.

**Errors:**
- `VerificationError` — Verification failed due to invalid input

---

### 3.5 Utility

#### `estimate_fee(inputs: list[dict], outputs: list[dict], fee_rate: int) -> FeeEstimate`

**Purpose:** Estimate transaction fee.  
**Input:**
- `inputs`: List of `{txid, vout, script_pubkey, witness}`
- `outputs`: List of `{address, amount_sats}`
- `fee_rate`: Satoshis per vbyte

**Output:** `FeeEstimate` containing `fee_sats`, `vsize`, `weight`.

**Errors:**
- `ValidationError` — Invalid input/output data
- `FeeError` — Fee estimation failed

---

#### `transaction_weight(tx_hex: str) -> int`

**Purpose:** Calculate transaction weight.  
**Input:**
- `tx_hex`: Hex encoded raw transaction

**Output:** Weight units (integer).

**Errors:**
- `ValidationError` — Invalid transaction

---

#### `transaction_id(tx_hex: str) -> str`

**Purpose:** Compute transaction ID.  
**Input:**
- `tx_hex`: Hex encoded raw transaction

**Output:** Transaction ID hex string.

**Errors:**
- `ValidationError` — Invalid transaction

---

## 4. Python Responsibilities

These responsibilities **always** remain in Python:

### 4.1 Wallet Orchestration

- Wallet lifecycle management (create, lock, unlock, delete)
- Wallet state tracking (unlocked, locked, encrypted)
- Address index tracking
- Transaction metadata enrichment

### 4.2 Hermes Integration

- Agent authentication
- Agent authorization
- Agent session management
- API request routing from Hermes

### 4.3 Policy Engine

- Policy definition storage
- Policy evaluation logic
- Policy enforcement before Rust calls
- Policy violation handling

### 4.4 Secure Storage

- Wallet metadata storage (encrypted)
- Policy storage
- Configuration storage
- Audit log storage

### 4.5 Audit Logging

- Log format definition
- Log storage and rotation
- Log correlation ID generation
- Sensitive data redaction

### 4.6 Provider Abstraction

- Broadcast backend selection (mempool.space, Bitcoin Core RPC, future)
- UTXO backend selection
- Chain adapter abstraction
- Fallback logic

### 4.7 API Layer

- FastAPI endpoint definitions
- Request/response validation
- Rate limiting
- API versioning
- OpenAPI documentation

### 4.8 Plugin System

- Plugin discovery
- Plugin loading
- Plugin API boundaries
- Plugin permission isolation

---

## 5. Rust Responsibilities

These responsibilities **always** belong to Rust:

### 5.1 Bitcoin Consensus

- BIP-32 hierarchical deterministic key derivation
- BIP-39 mnemonic generation and seed derivation
- BIP-174 PSBT parsing, manipulation, finalization
- BIP-143 legacy witness sighash computation
- BIP-340 Schnorr signatures
- BIP-341 Taproot outputs
- BIP-342 Taproot sighash
- Transaction serialization and deserialization
- Script parsing and evaluation
- Witness construction
- Fee rate validation
- Transaction weight calculation

### 5.2 Key Management

- Secure key generation
- Key derivation within Rust memory
- Key zeroization after use
- Extended key handling

### 5.3 Validation

- Address validation
- Transaction structural validation
- Signature verification
- PSBT completeness checks
- Script validity checks

### 5.4 Serialization

- Bitcoin binary formats
- PSBT serialization
- Transaction serialization
- Deterministic encoding

---

## 6. Data Contracts

All objects crossing the Python↔Rust boundary are **immutable data transfer objects (DTOs)**.

### 6.1 WalletData

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `wallet_id` | `str` (UUID) | Python | String |
| `name` | `str` | Python | String |
| `network` | `str` | Python | Enum string |
| `master_fingerprint` | `str` (hex) | Rust | 4-byte hex |
| `xpub` | `str` | Rust | Base58 |
| `created_at` | `str` (ISO 8601) | Python | String |
| `encrypted_seed` | `bytes` | Rust | Hex (base64 in transit) |

---

### 6.2 PublicWalletData

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `wallet_id` | `str` | Python | String |
| `network` | `str` | Python | Enum string |
| `master_fingerprint` | `str` | Rust | 4-byte hex |
| `xpub` | `str` | Rust | Base58 |
| `created_at` | `str` | Python | ISO 8601 |

---

### 6.3 KeyData

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `path` | `str` | Python | String |
| `address` | `str` | Rust | Bech32/Base58 |
| `script_type` | `str` | Rust | Enum string |
| `public_key` | `str` (hex) | Rust | Hex |
| `fingerprint` | `str` (hex) | Rust | 4-byte hex |

---

### 6.4 AddressData

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `address` | `str` | Rust | Bech32/Base58 |
| `script_type` | `str` | Rust | Enum string |
| `path` | `str` | Python | String |
| `script_pubkey` | `str` (hex) | Rust | Hex |

---

### 6.5 XpubData

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `xpub` | `str` | Rust | Base58 |
| `path` | `str` | Python | String |
| `depth` | `int` | Rust | Integer |
| `fingerprint` | `str` | Rust | 4-byte hex |

---

### 6.6 PsbtData

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `psbt_hex` | `str` | Rust | Base64 |
| `inputs` | `list[dict]` | Rust | JSON array |
| `outputs` | `list[dict]` | Rust | JSON array |
| `fee_sats` | `int` | Rust | Integer |
| `vsize` | `int` | Rust | Integer |
| `weight` | `int` | Rust | Integer |

---

### 6.7 SignedPsbtData

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `psbt_hex` | `str` | Rust | Base64 |
| `signed_inputs` | `int` | Rust | Integer |
| `total_inputs` | `int` | Rust | Integer |
| `complete` | `bool` | Rust | Boolean |

---

### 6.8 TransactionData

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `tx_hex` | `str` | Rust | Hex |
| `txid` | `str` | Rust | Hex |
| `inputs` | `list[dict]` | Rust | JSON array |
| `outputs` | `list[dict]` | Rust | JSON array |
| `fee_sats` | `int` | Rust | Integer |
| `vsize` | `int` | Rust | Integer |
| `weight` | `int` | Rust | Integer |

---

### 6.9 BroadcastResult

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `success` | `bool` | Python | Boolean |
| `txid` | `str | None` | Python | Hex |
| `error` | `str | None` | Python | String |
| `timestamp` | `str | None` | Python | ISO 8601 |

---

### 6.10 FeeEstimate

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `fee_sats` | `int` | Rust | Integer |
| `vsize` | `int` | Rust | Integer |
| `weight` | `int` | Rust | Integer |
| `fee_rate` | `int` | Rust | Integer |

---

### 6.11 AddressInfo

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `valid` | `bool` | Rust | Boolean |
| `address` | `str | None` | Rust | String |
| `script_type` | `str | None` | Rust | Enum string |
| `network` | `str` | Rust | Enum string |

---

### 6.12 ValidationResult

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `valid` | `bool` | Rust | Boolean |
| `errors` | `list[str]` | Rust | String array |
| `warnings` | `list[str]` | Rust | String array |

---

### 6.13 SignatureResult

| Field | Type | Owner | Serialization |
|-------|------|-------|---------------|
| `success` | `bool` | Rust | Boolean |
| `input_index` | `int` | Rust | Integer |
| `signature` | `bytes | None` | Rust | Hex |
| `error` | `str | None` | Rust | String |

---

### 6.14 ErrorResponse

| Field | Type | Description |
|-------|------|-------------|
| `code` | `str` | Machine-readable error code |
| `category` | `str` | Error category |
| `message` | `str` | Human-readable message |
| `retryable` | `bool` | Whether the operation can be retried |
| `correlation_id` | `str` | Log correlation ID |

---

## 7. Error Contracts

All errors follow a structured format.

### 7.1 Error Categories

| Category | Code Prefix | Description |
|----------|-------------|-------------|
| Policy | `POLICY_` | Policy engine violations |
| Authentication | `AUTH_` | Authentication failures |
| Authorization | `AUTHZ_` | Permission denied |
| Validation | `VALIDATION_` | Input/output validation failures |
| InsufficientFunds | `FUNDS_` | Balance too low |
| Network | `NETWORK_` | Backend/network unavailable |
| WalletLocked | `LOCKED_` | Wallet is locked |
| Internal | `INTERNAL_` | Unexpected failures |

### 7.2 Error Format

```json
{
  "code": "POLICY_DAILY_LIMIT_EXCEEDED",
  "category": "policy",
  "message": "Daily spending limit of 100000 sats exceeded",
  "retryable": false,
  "correlation_id": "abc-123"
}
```

### 7.3 Error Propagation Rules

- Rust returns typed `Result<T, ErrorType>`
- Wrapper translates to Python exceptions
- No Rust stack traces in Python
- No internal paths in error messages
- All errors include correlation ID

---

## 8. Security Boundary

### 8.1 What Crosses the Boundary

Allowed data types:
- Wallet metadata (IDs, names, timestamps)
- Public keys and addresses
- PSBT hex/base64
- Raw transaction hex
- Balance amounts
- Fee estimates
- Validation results
- Error codes and messages

### 8.2 What Must Never Cross

Prohibited data types:
- Private keys in plaintext
- Seed phrases or mnemonics
- Encryption keys
- Internal Rust memory addresses
- Rust stack traces
- File system paths
- Database connection strings
- API keys or tokens

### 8.3 Export Controls

Secure export workflows:
- `export_public_metadata()` — always allowed
- `backup_wallet()` — returns encrypted blob, requires Recovery role
- `export_seed()` — **not part of Wrapper API v1**, reserved for future secure export workflow

### 8.4 Memory Rules

- All data crossing boundary is copied, not borrowed
- No raw pointers cross boundary
- Sensitive data in Rust is zeroized after use
- Python garbage collection handles Python-side memory
- Wrapper releases GIL during Rust calls

---

## 9. Versioning

### 9.1 Wrapper API Version

- Current version: **Wrapper API v1**
- Rust engine version: independent
- Python API version: tied to RawWalletAI version

### 9.2 Compatibility Guarantees

| Can Change | Cannot Change Without Major Version |
|------------|-------------------------------------|
| Internal Rust implementation | Public Rust function signatures |
| Rust crate versions | Python wrapper function signatures |
| Error message wording | Data model field names and types |
| Performance optimizations | Error type names and hierarchy |
| Deprecated function internals | Serialization formats for public API |

### 9.3 Deprecation Policy

1. Mark function as deprecated in documentation
2. Add replacement function
3. Keep deprecated function for 2 minor versions
4. Remove in next major version

### 9.4 Version Negotiation

```python
# Python can query versions
rust_wrapper_version() -> str   # e.g., "1.0.0"
rust_engine_version() -> str    # e.g., "0.32.0"
```

---

## 10. Testing Requirements

### 10.1 Rust Unit Tests

- Test each Rust function independently
- Use official Bitcoin test vectors (BIP-174, BIP-143, BIP-340/341/342)
- Property-based testing for serialization round-trips
- Fuzzing for edge cases

### 10.2 Wrapper FFI Tests

- Test type conversions Python ↔ Rust
- Test error propagation
- Test memory safety
- Test GIL release/reacquire
- Test concurrent access patterns

### 10.3 Python Integration Tests

- Test Python wrapper calls Rust correctly
- Test error translation
- Test data model serialization
- Test fallback when Rust unavailable

### 10.4 Cross-Platform Tests

- Linux x86_64
- Linux ARM64
- macOS x86_64/arm64
- Windows x86_64

### 10.5 Bitcoin Test Vectors

- BIP-174 PSBT test vectors
- BIP-143 sighash test vectors
- BIP-340/341/342 Taproot test vectors
- Bitcoin Core transaction validation tests

### 10.6 Property Tests

- Serialization round-trip consistency
- Address derivation determinism
- Transaction ID consistency
- Signature verification correctness
- Fee estimation accuracy

---

## 11. Performance Targets

| Metric | Target |
|--------|--------|
| Python↔Rust transition overhead | < 1ms per call |
| PSBT build + sign + finalize | < 100ms total |
| Address derivation | < 10ms |
| Fee estimation | < 50ms |
| Memory copies per operation | Minimum required only |
| PSBT transfer size | Single hex/base64 string |
| Transaction transfer size | Single hex string |

### Performance Rules

1. Batch operations where possible
2. Minimize cross-language calls
3. Use hex/base64 for large data, not per-field JSON
4. Release GIL during Rust computation
5. Avoid per-input/per-output Python↔Rust transitions

---

## 12. Security Requirements

### 12.1 Authentication

- Wallet operations require wallet unlock
- Lock state enforced in Rust
- Failed unlock attempts logged
- Lockout after N failed attempts

### 12.2 Authorization

- Policy enforcement in Python before Rust calls
- Rust assumes caller is authorized
- Python validates permissions
- Token-based authentication

### 12.3 Audit Logging

- All public API calls logged (without secrets)
- Structured log events from Rust
- Python aggregates and stores logs
- Correlation IDs maintained

### 12.4 Sensitive Data

- Private keys zeroized after use in Rust
- Mnemonics never exposed via API
- Seeds never logged
- Passwords never stored
- Backup encrypted at rest

---

## 13. Implementation Contract

### 13.1 Python→Rust Interface

Python calls are **synchronous** but release the GIL.

All functions return **immutable DTOs**.

All errors are translated to **Python exceptions**.

### 13.2 Rust→Python Interface

Rust functions receive **serialized parameters**.

Rust functions return **serialized results**.

Rust functions never panic in public API.

### 13.3 Ownership Rules

| Data | Owner in transit | Lifetime |
|------|------------------|----------|
| Wallet ID | Python | Persistent |
| PSBT hex | Rust (during processing) | Call-scoped |
| Transaction hex | Rust (during processing) | Call-scoped |
| Address | Rust | Persistent in Python cache |
| Balance | Rust | Fresh per query |

---

## 14. Risks Before Implementation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PyO3 API changes break wrapper | Medium | High | Pin PyO3 version, CI matrix |
| Memory safety in FFI boundary | Low | High | Valgrind tests, fuzzing |
| Performance overhead unacceptable | Low | Medium | Benchmark critical paths early |
| Data model design flaws | Medium | High | Review before coding |
| Error handling inconsistencies | Medium | Medium | Strict error contract enforcement |
| Cross-platform build failures | Low | Medium | Multi-runner CI |
| GIL contention under load | Low | Medium | Async benchmarks |
| Rust panic in public API | Low | High | No unwrap/panic in public API |

---

## 15. Decision

**Status:** Proposed  
**Next Step:** Accept this specification before implementing Phase B

This document is the **binding contract** for the Python↔Rust integration. Implementation must adhere to this specification without deviation.

---

## 16. Summary

### Wrapper API Summary

The Wrapper API v1 exposes 14 public functions across 5 categories: wallet lifecycle, key operations, transactions, validation, and utility. All functions are synchronous, return immutable DTOs, and translate Rust errors to Python exceptions.

### Security Model

- Private keys never leave Rust
- Seeds never exposed
- All data crossing boundary is serialized
- No Rust internals leak to Python
- Audit logging without secrets

### Responsibility Split

- **Python:** orchestration, policies, auth, audit, storage, API
- **Rust:** consensus, serialization, signing, validation
- **Wrapper:** translation, error mapping, GIL management

### Data Model Summary

14 DTO types defined with explicit field types, ownership, and serialization formats. All objects are immutable data carriers.

### Error Model Summary

8 error categories with structured JSON format. Error codes, categories, messages, retryable flags, and correlation IDs. No implementation details exposed.

### API Stability Guarantees

- Wrapper API v1 stable for RawWalletAI 1.x
- Breaking changes require Wrapper API v2
- New functions can be added without breaking changes
- Deprecated functions remain for 2 minor versions

### Risks Before Implementation

7 risks identified with mitigations. Highest risk: PyO3 API stability and memory safety at FFI boundary.
