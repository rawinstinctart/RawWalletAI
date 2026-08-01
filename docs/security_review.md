# RawWalletAI – Security Review

## Threat Model

### Assets
- Seed phrases / master private keys
- Derived private keys
- Encrypted wallet storage files
- Broadcast transaction hex
- RPC credentials

### Threat Actors
- Local attacker with file-system access
- Network attacker during broadcast
- Supply-chain attacker via dependencies
- Malicious RPC endpoint

### Trust Boundaries
- Local disk ↔ Wallet core
- Wallet core ↔ Network backends
- Network backends ↔ External APIs

## Secrets

- Mnemonics are encrypted at rest with AES-256-GCM + random salt
- Mnemonics are never returned via API after creation
- Private keys exist only in memory during signing
- No secrets are logged

## Key Handling

- BIP-32 master derivation via HMAC-SHA512 with "Bitcoin seed"
- Private key material is not written to disk unencrypted
- ECKey from `cryptography` used for actual compressed public key derivation
- No custom key derivation; audited libraries only

## Storage

- AES-256-GCM with 16-byte random salt per encryption
- Salt prepended to ciphertext
- Decryption failures are explicit
- No plaintext key material on disk

## Broadcast

- Mempool backends use HTTPS only
- Bitcoin Core RPC uses Basic Auth over HTTP in current stub
- Planned: TLS verification for all backends
- No transaction metadata leakage

## Dependencies

- `cryptography>=42.0` — audited, maintained
- `pydantic>=2.0` — audited, maintained
- `mnemonic>=0.20` — audited
- `python-bitcoinlib>=0.12` — maintained, limited PSBT support
- No custom cryptography

## Remaining Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| PSBT finalization missing | Critical | Certain | Block 1.0 release |
| Memory zeroization limited in CPython | Medium | Certain | Process isolation for production |
| Electrum backend removed | Low | Certain | Re-evaluate after dependency decision |
| Blind exception catches | Medium | Likely | Replace with typed exceptions |
| RPC over HTTP | High | Certain | Enforce HTTPS/TLS |
| No external audit | Critical | Certain | Required before mainnet |

## Future Audit Recommendations

1. External cryptographic review of BIP-32 implementation
2. External review of PSBT finalization wrapper
3. Dependency audit before each release
4. Fuzzing of transaction serialization after finalizer implementation
5. Penetration test of API surface

## Security Contact

Report vulnerabilities to rawinstinctai@mail.de.
