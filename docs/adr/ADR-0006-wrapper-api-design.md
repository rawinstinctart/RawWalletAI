# ADR-0006 — Wrapper API Design

**Status:** Proposed  
**Date:** 2026-08-01  
**Decision Owner:** Pascal Haux / RawInstinctAI  
**Context:** Post-ADR-0007, defining the permanent Python↔Rust boundary for RawWalletAI

---

## Problem

RawWalletAI needs a stable, long-term interface between:

- **Python platform layer:** wallet orchestration, Hermes integration, policies, audit, API
- **Rust Bitcoin engine:** consensus logic, PSBT finalization, serialization, validation

This ADR defines that boundary. The implementation must follow this contract.

---

## Design Principles

### Rust Owns

- Bitcoin consensus logic
- PSBT parsing, finalization, extraction
- Transaction serialization and deserialization
- Witness/scriptSig construction
- Signature generation and verification
- Script handling
- Taproot (BIP-340/341/342)
- Miniscript compilation and analysis
- Bitcoin-specific validation rules
- Sighash computation (BIP-143, future Taproot sighash)

### Python Owns

- Wallet orchestration and state management
- Hermes integration
- Multi-agent workflows and rights management
- Policy engine (limits, approvals, constraints)
- Encryption and secure storage
- API layer (FastAPI)
- Authentication and authorization
- Audit logging
- User configuration and preferences
- Plugin system
- Provider abstraction (broadcast, UTXO, chain adapters)

### Golden Rule

**Never duplicate Bitcoin logic in Python.**  
All consensus-critical operations must flow through Rust.

---

## Rust Public API Surface

### Wallet Operations

```rust
// Create a new wallet from a seed
pub fn create_wallet(seed: &[u8; 64], network: Network) -> Result<WalletData, WalletError>

// Import an existing wallet
pub fn import_wallet(xprv: &[u8], network: Network) -> Result<WalletData, WalletError>

// Export public-only wallet data
pub fn export_public_data(wallet: &WalletHandle) -> Result<PublicWalletData, WalletError>
```

### Key Operations

```rust
// Derive a key at a BIP-32 path
pub fn derive_key(wallet: &WalletHandle, path: &str) -> Result<KeyData, KeyError>

// Derive an address for a script type
pub fn derive_address(wallet: &WalletHandle, path: &str, script_type: ScriptType) -> Result<AddressData, KeyError>

// Export extended public key
pub fn derive_xpub(wallet: &WalletHandle, path: &str) -> Result<XpubData, KeyError>
```

### Transaction Operations

```rust
// Build a PSBT from inputs/outputs
pub fn build_psbt(inputs: &[TxInput], outputs: &[TxOutput], fee_rate: u64) -> Result<PsbtData, PsbtError>

// Sign a PSBT
pub fn sign_psbt(wallet: &WalletHandle, psbt: &mut PsbtData) -> Result<SignatureResult, SignatureError>

// Finalize a signed PSBT into a raw transaction
pub fn finalize_psbt(psbt: &PsbtData) -> Result<RawTransactionData, FinalizeError>

// Serialize a transaction
pub fn serialize_transaction(tx: &TransactionData) -> Result<Vec<u8>, SerializeError>
```

### Validation Operations

```rust
// Validate a Bitcoin address
pub fn validate_address(address: &str, network: Network) -> Result<AddressInfo, ValidationError>

// Validate a transaction
pub fn validate_transaction(tx: &TransactionData) -> Result<ValidationResult, ValidationError>

// Verify a signature
pub fn verify_signature(message: &[u8], signature: &[u8], pubkey: &[u8]) -> Result<bool, VerificationError>
```

### Utility Operations

```rust
// Estimate fee for a transaction
pub fn estimate_fee(inputs: &[TxInput], outputs: &[TxOutput], fee_rate: u64) -> Result<FeeEstimate, FeeError>

// Calculate transaction weight
pub fn calculate_weight(tx: &TransactionData) -> Result<u64, WeightError>

// Compute transaction ID
pub fn transaction_id(tx: &TransactionData) -> Result<Vec<u8>, TxIdError>
```

---

## Python API

Python exposes high-level, wallet-centric methods only.

### Wallet Lifecycle

```python
class Wallet:
    def create(name: str, passphrase: str) -> Wallet
    def load(wallet_id: str, passphrase: str) -> Wallet
    def export_public() -> dict
    def lock()
    def unlock(passphrase: str) -> bool
    def is_unlocked() -> bool
```

### Address Management

```python
class Wallet:
    def get_address(script_type: str = "p2wpkh") -> Address
    def get_account_xpub(account: int = 0) -> str
```

### Transaction Workflow

```python
class Wallet:
    def send(
        recipients: list[dict],
        fee_rate: int | None = None,
        policy: Policy | None = None,
    ) -> TransactionResult:
        """High-level send with policy enforcement.
        
        Internally performs:
        1. Coin selection
        2. PSBT building
        3. Signing
        4. Finalization
        5. Broadcast
        
        Caller never manages PSBT manually unless explicitly requested.
        """
    
    def build_psbt(
        recipients: list[dict],
        fee_rate: int | None = None,
    ) -> Psbt:
        """Build but do not sign/finalize."""

    def sign_psbt(psbt: Psbt) -> SignedPsbt:
        """Sign a PSBT."""

    def finalize_psbt(psbt: SignedPsbt) -> RawTransaction:
        """Finalize a signed PSBT."""

    def broadcast(tx: RawTransaction) -> BroadcastResult:
        """Broadcast a finalized transaction."""
```

### Validation Utilities

```python
class Wallet:
    @staticmethod
    def validate_address(address: str) -> AddressInfo
    @staticmethod
    def validate_transaction(tx_hex: str) -> ValidationResult
    @staticmethod
    def verify_signature(message: bytes, signature: bytes, pubkey: bytes) -> bool
```

### Fee Estimation

```python
class Wallet:
    @staticmethod
    def estimate_fee(inputs: list[dict], outputs: list[dict], fee_rate: int) -> FeeEstimate
```

---

## Data Model

### Wallet

| Field | Type | Purpose | Owner | Serialization |
|-------|------|---------|-------|---------------|
| `wallet_id` | `str` | Unique identifier | Python | UUID |
| `name` | `str` | Human-readable name | Python | UTF-8 |
| `network` | `str` | Bitcoin network | Both | String enum |
| `script_type` | `str` | Default script type | Python | String enum |
| `master_fingerprint` | `bytes` | BIP-32 fingerprint | Rust | 4 bytes |
| `xpub` | `str` | Extended public key | Rust | Base58 |
| `created_at` | `datetime` | Creation timestamp | Python | ISO 8601 |

### Address

| Field | Type | Purpose | Owner | Serialization |
|-------|------|---------|-------|---------------|
| `address` | `str` | Bech32/Base58 address | Rust | String |
| `script_type` | `str` | p2wpkh, p2tr, etc. | Rust | String enum |
| `path` | `str` | BIP-32 derivation path | Python | String |
| `script_pubkey` | `bytes` | Output script | Rust | Hex |

### Transaction

| Field | Type | Purpose | Owner | Serialization |
|-------|------|---------|-------|---------------|
| `txid` | `str` | Transaction ID | Rust | Hex |
| `tx_hex` | `str` | Raw transaction hex | Rust | Hex |
| `inputs` | `list[TxInput]` | Transaction inputs | Rust | JSON |
| `outputs` | `list[TxOutput]` | Transaction outputs | Rust | JSON |
| `fee_sats` | `int` | Fee in satoshis | Rust | Integer |
| `vsize` | `int` | Virtual size | Rust | Integer |
| `weight` | `int` | Weight units | Rust | Integer |

### PSBT

| Field | Type | Purpose | Owner | Serialization |
|-------|------|---------|-------|---------------|
| `psbt_hex` | `str` | PSBT serialization | Rust | Base64/Hex |
| `inputs` | `list[PSBTInput]` | PSBT input metadata | Rust | JSON |
| `outputs` | `list[PSBTOutput]` | PSBT output metadata | Rust | JSON |
| `signed` | `bool` | All signatures present | Rust | Boolean |

### UTXO

| Field | Type | Purpose | Owner | Serialization |
|-------|------|---------|-------|---------------|
| `txid` | `str` | Source transaction ID | Rust | Hex |
| `vout` | `int` | Output index | Rust | Integer |
| `amount_sats` | `int` | Amount in satoshis | Rust | Integer |
| `script_pubkey` | `bytes` | Output script | Rust | Hex |
| `address` | `str` | Bitcoin address | Rust | String |
| `confirmed` | `bool` | Confirmation status | Python | Boolean |
| `height` | `int | None` | Block height | Python | Integer |

### Balance

| Field | Type | Purpose | Owner | Serialization |
|-------|------|---------|-------|---------------|
| `confirmed` | `int` | Confirmed balance | Rust | Satoshis |
| `unconfirmed` | `int` | Unconfirmed balance | Rust | Satoshis |
| `total` | `int` | Total balance | Rust | Satoshis |
| `utxo_count` | `int` | Number of UTXOs | Rust | Integer |

### FeeEstimate

| Field | Type | Purpose | Owner | Serialization |
|-------|------|---------|-------|---------------|
| `fee_rate` | `int` | Satoshis per vbyte | Rust | Integer |
| `total_fee` | `int` | Estimated fee | Rust | Satoshis |
| `vsize` | `int` | Estimated vsize | Rust | Integer |

### SignatureResult

| Field | Type | Purpose | Owner | Serialization |
|-------|------|---------|-------|---------------|
| `success` | `bool` | Signing succeeded | Rust | Boolean |
| `input_index` | `int` | Signed input index | Rust | Integer |
| `signature` | `bytes | None` | DER signature | Rust | Hex |
| `error` | `str | None` | Error message | Rust | String |

### BroadcastResult

| Field | Type | Purpose | Owner | Serialization |
|-------|------|---------|-------|---------------|
| `success` | `bool` | Broadcast succeeded | Python | Boolean |
| `txid` | `str | None` | Transaction ID | Python | Hex |
| `error` | `str | None` | Error message | Python | String |

### Error

All Rust errors are translated to Python exceptions. No Rust types leak.

| Rust Error | Python Exception | Meaning |
|------------|------------------|---------|
| `WalletError` | `WalletError` | Wallet operation failed |
| `KeyError` | `KeyError` | Key derivation failed |
| `PsbtError` | `PSBTError` | PSBT parsing/manipulation failed |
| `SignatureError` | `SigningError` | Signing failed |
| `FinalizeError` | `FinalizationError` | Finalization failed |
| `ValidationError` | `ValidationError` | Validation failed |
| `SerializeError` | `SerializationError` | Serialization failed |

---

## Error Handling

### Rust Side

- All operations return `Result<T, ErrorType>`
- Errors are typed and enumerated
- No panics in public API
- No unwrap() in public API
- Sensitive errors do not leak key material

### Python Side

- All Rust errors are caught and re-raised as Python exceptions
- No Rust stack traces exposed to Python callers
- Error messages are user-friendly
- Sensitive operations log minimal information

### Error Propagation

```rust
// Rust
pub fn finalize_psbt(psbt: &PsbtData) -> Result<RawTransactionData, FinalizeError>

// Python wrapper
def finalize_psbt(psbt_hex: str) -> str:
    try:
        result = _rust.finalize_psbt(psbt_hex)
        return result.hex
    except FinalizeError as e:
        raise FinalizationError(f"PSBT finalization failed: {e}")
```

---

## Memory Ownership

### Rust Owns

- Wallet handles (opaque pointers)
- Key material in memory
- PSBT structures during processing
- Transaction structures during serialization

### Python Owns

- Wallet state metadata
- Policy configuration
- Audit log entries
- API request/response objects

### Data Transfer

- All data crossing the boundary is serialized
- No raw pointers cross the boundary
- No borrowed references held across calls
- Sensitive data is zeroized in Rust after use

### Copy vs Borrow

| Operation | Strategy |
|-----------|----------|
| PSBT hex → Rust | Copy into Rust string |
| Raw tx hex → Python | Copy into Python bytes |
| Key derivation | Rust returns new key material |
| Address derivation | Rust returns new address object |
| Signing | Rust uses key material, returns signature |

### Sensitive Memory

- Private keys zeroized after use in Rust
- Mnemonics never exposed via API
- Seed material never logged
- Memory cleared on wallet lock

---

## Thread Safety

### Rust Side

- All Rust types implement `Send`
- No `Sync` required (Python GIL protects)
- Rust extensions release GIL during computation
- No mutable static state

### Python Side

- Python GIL protects Rust calls
- Wallet objects are not thread-safe by default
- Concurrent access requires explicit locking in Python

### Async Compatibility

- All Rust calls are synchronous but fast
- Python wrapper releases GIL during Rust calls
- Compatible with `asyncio` via `await asyncio.to_thread(...)`
- No blocking event loop

### Future Multiprocessing

- Wallet handles cannot be shared across processes
- Process restart required for wallet access
- Unix domain sockets for inter-process communication (future)

---

## Performance Rules

### Minimize Cross-Language Calls

- Batch operations where possible
- Single Rust call for coin selection + PSBT building
- Avoid per-input/per-output Python↔Rust transitions

### Minimize Memory Copies

- PSBT passed as hex string (single copy)
- Raw transaction returned as hex string (single copy)
- No intermediate Python objects for large data

### Minimize Serialization Overhead

- Hex encoding for PSBT and transactions
- JSON for structured metadata only
- Binary formats reserved for future optimization

### Python↔Rust Transitions

- Target: < 1ms per transition
- PSBT finalization: single transition
- Transaction building: single transition
- Address derivation: single transition

---

## Versioning

### Wrapper API Version

```
RawWalletAI Wrapper API v1
```

- Rust engine version is independent
- Wrapper API changes require major version bump
- Python API version tied to RawWalletAI version

### Compatibility Guarantee

- Wrapper API v1 remains stable throughout RawWalletAI 1.x
- Breaking changes require Wrapper API v2
- New functions can be added without breaking changes
- Deprecated functions remain for at least 2 minor versions

### Version Negotiation

```python
# Python can query wrapper version
rust_wrapper_version() -> str  # e.g., "1.2.0"
rust_engine_version() -> str   # e.g., "0.32.0"
```

---

## Backward Compatibility

### What Can Change

- Internal Rust implementation
- Rust crate versions
- Performance optimizations
- Error message wording
- Deprecated function internals

### What Must Never Change

- Public Rust function signatures
- Python wrapper function signatures
- Data model field names and types
- Error type names and hierarchy
- Serialization formats for public API

### Deprecation Policy

1. Mark function as deprecated in documentation
2. Add replacement function
3. Keep deprecated function for 2 minor versions
4. Remove in next major version

---

## Security Rules

### Key Material

- Private keys never leave Rust unless explicitly requested by secure export API
- Mnemonics never exposed via wrapper API
- Seed material never logged
- Keys zeroized after use

### Wrapper Boundary

- No secrets cross boundary accidentally
- Python receives only minimum required information
- Sensitive operations audited
- All public API calls logged (without secrets)

### Audit Logging

- Rust emits structured log events
- Python aggregates and stores logs
- No key material in logs
- Log correlation IDs maintained

### Authentication

- Wallet unlock required before key operations
- Lock state enforced in Rust
- Failed unlock attempts logged

### Authorization

- Policy enforcement in Python, not Rust
- Rust assumes caller is authorized
- Python validates policies before calling Rust

---

## Testing Strategy

### Rust Unit Tests

- Test each Rust function independently
- Use official Bitcoin test vectors
- Property-based testing for serialization
- Fuzzing for edge cases

### Wrapper Tests

- Test FFI boundary
- Test type conversions
- Test error propagation
- Test memory safety

### Python Integration Tests

- Test Python wrapper calls Rust correctly
- Test error translation
- Test data model serialization

### Cross-Platform Tests

- Linux x86_64
- Linux ARM64
- macOS x86_64/arm64
- Windows x86_64

### Official Test Vectors

- BIP-174 PSBT test vectors
- BIP-143 sighash test vectors
- BIP-340/341/342 Taproot test vectors
- Bitcoin Core transaction validation tests

### Property Tests

- Serialization round-trip consistency
- Address derivation determinism
- Transaction ID consistency
- Signature verification correctness

---

## Future Extensibility

### Extension Points

| Feature | Rust Support | Python Support | Status |
|---------|--------------|----------------|--------|
| Lightning | rust-lightning | Future plugin | Planned |
| Multisig | rust-miniscript | Policy engine | Future |
| Hardware Wallets | HWI Rust bindings | HID/transport layer | Future |
| Descriptors | rust-miniscript | Policy UI | Future |
| Miniscript | rust-miniscript | Policy compiler | Future |
| Additional chains | Optional Rust crates | Chain abstraction | Optional |

### Plugin System

- Rust plugins: compiled as dynamic libraries
- Python plugins: standard entry points
- Plugin API versioned independently
- Core API remains stable

---

## Wrapper Responsibilities

- Translate Python types to Rust types
- Manage Rust object lifetimes
- Handle FFI errors
- Provide Pythonic API
- Release GIL during Rust calls
- Zeroize sensitive Python objects after use

## Rust Responsibilities

- Implement Bitcoin consensus logic
- Manage wallet state in memory
- Zeroize key material after use
- Provide typed error results
- Never panic in public API
- Maintain thread safety

## Python Responsibilities

- Orchestrate wallet operations
- Enforce policies and limits
- Manage audit logs
- Provide API surface
- Handle authentication/authorization
- Coordinate broadcast backends

---

## API Stability Guarantees

1. **Wrapper API v1** stable for RawWalletAI 1.x
2. **Breaking changes** require Wrapper API v2
3. **New functions** can be added without breaking changes
4. **Deprecated functions** remain for 2 minor versions
5. **Data model** field names and types never change without major version

## Security Guarantees

1. Private keys never leave Rust unencrypted
2. Mnemonics never exposed via API
3. All secrets zeroized after use
4. No sensitive data in logs
5. Policy enforcement in Python prevents unauthorized operations

## Performance Considerations

1. Minimize Python↔Rust transitions
2. Batch operations where possible
3. Release GIL during Rust computation
4. Use hex strings for large data transfer
5. Target < 1ms per FFI call

## Future Migration Strategy

1. **Phase 1:** Implement wrapper with current Python API surface
2. **Phase 2:** Migrate PSBT finalization to Rust
3. **Phase 3:** Migrate transaction building to Rust
4. **Phase 4:** Migrate key derivation to Rust
5. **Phase 5:** Full Rust engine with Python orchestration

At each phase:
- Python API remains stable
- Internal implementation shifts to Rust
- Tests validate behavioral equivalence

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PyO3 breaking changes | Medium | High | Pin rust-bitcoin version |
| Memory safety bugs in wrapper | Low | High | Comprehensive testing, fuzzing |
| Performance regression | Low | Medium | Benchmark critical paths |
| API design flaws | Medium | High | Review before implementation |
| Cross-platform issues | Low | Medium | Multi-runner CI |

## Open Questions

1. Should wallet handles be opaque Python objects or simple integers?
2. How to handle wallet locking across async boundaries?
3. Should PSBT be passed as hex or binary in wrapper?
4. How to version the wrapper API independently?
5. Should we support wallet export/import via wrapper?

---

## Decision

**Status:** Proposed  
**Next Step:** Review and accept API design before implementation begins

This ADR defines the contract. Implementation must follow this design.
