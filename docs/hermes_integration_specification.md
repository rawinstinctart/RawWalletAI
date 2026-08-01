# RawWalletAI – Hermes Integration Specification

**Version:** 0.1.0-draft  
**Date:** 2026-08-01  
**Status:** Proposed  
**Owner:** RawInstinctAI  
**Audience:** Hermes developers, RawWalletAI architects, security reviewers

---

## 1. Vision

Hermes is the **first AI agent** built on top of RawWalletAI.

- **Hermes** provides intelligence, automation, decision making, and user interaction.
- **RawWalletAI** provides secure wallet orchestration, Bitcoin execution, and storage.

This document defines the **functional boundary** between Hermes and RawWalletAI. Everything below that boundary is RawWalletAI responsibility. Everything above is Hermes responsibility.

### Core Principle

Hermes **never** handles raw private keys, seed phrases, PSBT internals, or Bitcoin consensus logic. Hermes issues high-level intents; RawWalletAI executes them safely.

---

## 2. Architecture

### Layered Responsibility Model

```
┌─────────────────────────────────────────┐
│ Hermes                                   │
│ - Intelligence                            │
│ - Automation                              │
│ - Decision making                         │
│ - User interaction                        │
└──────────────────┬──────────────────────┘
                   │ HTTP/gRPC/Embedded API
                   ▼
┌─────────────────────────────────────────┐
│ RawWalletAI API                           │
│ - Authentication                          │
│ - Authorization                           │
│ - Rate limiting                           │
│ - Input validation                        │
│ - Response formatting                     │
└──────────────────┬──────────────────────┘
                   │ Policy-enforced calls
                   ▼
┌─────────────────────────────────────────┐
│ Wallet Engine                             │
│ - Wallet lifecycle                        │
│ - Multi-agent permissions                 │
│ - Policy engine                           │
│ - Coin selection                          │
│ - Audit logging                           │
│ - Backup/export                           │
└──────────────────┬──────────────────────┘
                   │ Canonical intents
                   ▼
┌─────────────────────────────────────────┐
│ Bitcoin Engine                            │
│ - Key derivation                          │
│ - Address generation                      │
│ - PSBT build/sign/finalize                │
│ - Transaction serialization               │
│ - Validation                              │
└──────────────────┬──────────────────────┘
                   │ Signed transaction
                   ▼
┌─────────────────────────────────────────┐
│ Bitcoin Network                           │
│ - Broadcast                               │
│ - UTXO retrieval                          │
└─────────────────────────────────────────┘
```

### Responsibility Summary

| Layer | Owns | Must Never Do |
|-------|------|---------------|
| Hermes | Decisions, policies, user interaction | Handle raw keys, PSBT internals |
| RawWalletAI API | Auth, transport, validation | Make financial decisions |
| Wallet Engine | Orchestration, policies, audit | Implement Bitcoin consensus |
| Bitcoin Engine | Consensus, serialization, signing | Enforce business policies |
| Bitcoin Network | Broadcast, chain data | Trust Bitcoin Core blindly |

---

## 3. Primary Use Cases

### 3.1 Wallet Creation

**Trigger:** Hermes requests a new wallet.  
**Flow:**

1. Hermes → RawWalletAI API: `POST /wallets { name, passphrase_hint, policy }`
2. RawWalletAI validates request, checks permissions
3. Wallet Engine creates wallet metadata
4. Bitcoin Engine generates seed, derives master key
5. Wallet Engine encrypts seed with AES-256-GCM
6. Wallet Engine stores encrypted seed + metadata
7. RawWalletAI returns `wallet_id`, `fingerprint`, `created_at`

**Hermes never sees:**
- Mnemonic phrase
- Private keys
- Seed bytes
- Encryption key

**Hermes receives:**
- `wallet_id`
- `master_fingerprint`
- `network`
- `created_at`

---

### 3.2 Balance Query

**Trigger:** Hermes requests balances for a wallet.  
**Flow:**

1. Hermes → RawWalletAI API: `GET /wallets/{id}/balance`
2. RawWalletAI validates wallet access, checks permissions
3. Wallet Engine queries UTXO Backend
4. Bitcoin Engine validates scripts
5. Wallet Engine computes confirmed, unconfirmed, spendable balances
6. RawWalletAI returns balance object

**Response:**
```json
{
  "wallet_id": "...",
  "confirmed": 150000,
  "unconfirmed": 0,
  "spendable": 142500,
  "utxo_count": 3,
  "last_updated": "2026-08-01T12:00:00Z"
}
```

---

### 3.3 Address Generation

**Trigger:** Hermes requests a new receive address.  
**Flow:**

1. Hermes → RawWalletAI API: `POST /wallets/{id}/addresses { script_type }`
2. RawWalletAI validates permissions
3. Bitcoin Engine derives key at next index
4. Bitcoin Engine generates address
5. Wallet Engine marks address as used in metadata
6. RawWalletAI returns address + derivation path

**Hermes never sees:**
- Private key for address
- Extended private key

**Hermes receives:**
- `address`
- `script_type`
- `path`
- `script_pubkey`

---

### 3.4 Payment Flow

**Trigger:** Hermes requests a payment.  
**Flow:**

```
Hermes: "Send 50000 sats to bc1qxyz..."
    ↓
RawWalletAI API
    ↓
Wallet Engine
    ↓
[Policy Check] ← Is Hermes allowed to spend? Within limits?
    ↓
[UTXO Selection]
    ↓
[Fee Estimation]
    ↓
Bitcoin Engine: build PSBT
    ↓
Bitcoin Engine: sign PSBT
    ↓
Bitcoin Engine: finalize PSBT
    ↓
Wallet Engine: broadcast via Backend
    ↓
RawWalletAI API: return result
```

**Hermes receives:**
```json
{
  "success": true,
  "txid": "...",
  "fee_sats": 250,
  "vsize": 200,
  "status": "broadcasted"
}
```

**Hermes never sees:**
- PSBT internals
- Private keys used
- Signing process
- Internal error stack traces

---

### 3.5 Transaction History

**Trigger:** Hermes requests recent transactions.  
**Flow:**

1. Hermes → RawWalletAI API: `GET /wallets/{id}/transactions?limit=50`
2. RawWalletAI validates permissions
3. Wallet Engine queries transaction history from Backend
4. Wallet Engine enriches with metadata (labels, agent, policy)
5. RawWalletAI returns transaction list

**Response includes:**
- `txid`
- `amount_sats`
- `fee_sats`
- `confirmations`
- `timestamp`
- `status`
- `agent_id`
- `policy_id`

---

### 3.6 Wallet Backup

**Trigger:** Hermes requests wallet backup.  
**Flow:**

1. Hermes → RawWalletAI API: `POST /wallets/{id}/backup`
2. RawWalletAI validates:
   - Wallet access permission
   - Backup authorization (separate from spend)
   - Export policy constraints
3. Wallet Engine retrieves encrypted seed
4. Wallet Engine applies export policy:
   - Requires multi-agent approval for backup
   - Logs backup event
   - May encrypt backup with additional key
5. RawWalletAI returns encrypted backup

**Hermes receives:**
- Encrypted backup blob
- Backup metadata

**Hermes never receives:**
- Unencrypted seed
- Mnemonic phrase
- Private keys

---

## 4. Policy Engine

Policies are enforced **before** any Bitcoin Engine call.

### Example Policies

#### Daily Spending Limit

```json
{
  "policy_id": "daily-limit-001",
  "type": "spending_limit",
  "scope": "daily",
  "amount_sats": 100000,
  "reset_time": "00:00 UTC"
}
```

#### Maximum Transaction Amount

```json
{
  "policy_id": "max-tx-001",
  "type": "max_transaction",
  "amount_sats": 50000
}
```

#### Allowed Destinations

```json
{
  "policy_id": "allowed-dest-001",
  "type": "address_whitelist",
  "addresses": ["bc1q...", "bc1q..."]
}
```

#### Blocked Destinations

```json
{
  "policy_id": "blocked-dest-001",
  "type": "address_blacklist",
  "addresses": ["bc1q..."]
}
```

#### Time Restrictions

```json
{
  "policy_id": "time-restrict-001",
  "type": "time_window",
  "allowed_hours": ["09:00-18:00 UTC"],
  "allowed_days": ["Mon-Fri"]
}
```

#### Multi-Agent Approval

```json
{
  "policy_id": "multi-approval-001",
  "type": "multi_agent_approval",
  "required_agents": ["security-agent", "finance-agent"],
  "threshold": 2
}
```

#### Emergency Lock

```json
{
  "policy_id": "emergency-lock-001",
  "type": "emergency_lock",
  "triggered_by": ["admin"],
  "requires_unlock": ["recovery-agent"]
}
```

### Policy Evaluation Order

1. Emergency lock check
2. Time restriction check
3. Agent permission check
4. Transaction limit check
5. Daily spending check
6. Destination whitelist/blacklist check
7. Multi-agent approval check

Any failure at any step returns `PolicyViolationError`.

---

## 5. Permission Model

Agents are assigned **roles**. Roles define **permissions**. Permissions are enforced at the API layer.

### Roles

| Role | Permissions |
|------|-------------|
| **Viewer** | Read balance, read addresses, read history |
| **Operator** | Create addresses, view transactions |
| **Trader** | Send transactions within limits |
| **Administrator** | Manage policies, agents, wallets |
| **Recovery** | Export encrypted backup, unlock wallets |

### Permission Matrix

| Action | Viewer | Operator | Trader | Administrator | Recovery |
|--------|--------|----------|--------|---------------|----------|
| View balance | ✅ | ✅ | ✅ | ✅ | ✅ |
| Generate address | ❌ | ✅ | ✅ | ✅ | ❌ |
| Send transaction | ❌ | ❌ | ✅ | ✅ | ❌ |
| View history | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manage policies | ❌ | ❌ | ❌ | ✅ | ❌ |
| Manage agents | ❌ | ❌ | ❌ | ✅ | ❌ |
| Backup wallet | ❌ | ❌ | ❌ | ❌ | ✅ |
| Unlock wallet | ❌ | ❌ | ❌ | ❌ | ✅ |

### Agent Identity

- Each Hermes agent has an `agent_id`
- Agents authenticate via API token
- Tokens are scoped to wallet + role
- Token revocation is immediate

---

## 6. Multi-Agent Workflows

### Example: Payment Approval Workflow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Hermes   │────▶│ Finance  │────▶│ Security │
│ Agent    │     │ Agent    │     │ Agent    │
└──────────┘     └──────────┘     └──────────┘
       │               │                │
       │  1. Request   │                │
       │──────────────▶│                │
       │               │ 2. Review      │
       │               │────────────────▶│
       │               │                │ 3. Approve
       │               │◀───────────────│
       │ 4. Approved   │                │
       │◀──────────────│                │
       │               │                │
       ▼               ▼                ▼
  RawWalletAI executes transaction
```

### Example: Emergency Lock Workflow

```
Administrator triggers emergency lock
    ↓
RawWalletAI freezes wallet immediately
    ↓
Recovery Agent notified
    ↓
Recovery Agent + Administrator unlock
    ↓
Wallet restored
```

---

## 7. Audit Logging

Every critical action is logged with full context.

### Logged Events

| Event | Data Logged |
|-------|-------------|
| Wallet creation | agent_id, wallet_id, timestamp, policy |
| Address generation | agent_id, wallet_id, address, path |
| Signing request | agent_id, wallet_id, txid, inputs, outputs |
| Broadcast | agent_id, wallet_id, txid, fee, vsize |
| Backup | agent_id, wallet_id, backup_size, policy |
| Policy violation | agent_id, wallet_id, policy_id, attempted_action |
| Authentication | agent_id, method, result |
| Permission change | agent_id, target_agent, old_role, new_role |

### Log Format

```json
{
  "event": "transaction_signed",
  "timestamp": "2026-08-01T12:00:00Z",
  "agent_id": "hermes-main",
  "wallet_id": "wallet-001",
  "txid": "...",
  "policy_id": "daily-limit-001",
  "result": "success",
  "metadata": {}
}
```

### Log Storage

- Local encrypted log file
- Optional remote syslog
- Logs never contain private keys, seeds, or sensitive paths
- Correlation ID maintained across all layers

---

## 8. Error Model

Errors flow from Bitcoin Engine → Wallet Engine → API → Hermes.

### Rule

**No Rust implementation details may leak into Hermes.**

### Error Categories

| Category | Hermes Sees | Example |
|----------|-------------|---------|
| Policy violation | `PolicyViolationError` | Daily limit exceeded |
| Authentication | `AuthenticationError` | Invalid token |
| Authorization | `AuthorizationError` | Viewer cannot send |
| Validation | `ValidationError` | Invalid address |
| Insufficient funds | `InsufficientFundsError` | Balance too low |
| Network | `NetworkError` | Backend unavailable |
| Wallet locked | `WalletLockedError` | Wallet is locked |
| Internal | `InternalError` | Generic failure |

### What Hermes Never Sees

- Private keys
- Seed phrases
- Mnemonics
- Rust stack traces
- Cargo/PyO3 errors
- Internal file paths
- Database errors
- FFI errors

### Error Response Format

```json
{
  "error": {
    "code": "policy_violation",
    "message": "Daily spending limit exceeded",
    "policy_id": "daily-limit-001",
    "retryable": false,
    "correlation_id": "..."
  }
}
```

---

## 9. Future Extensions

### Lightning

- Interface: `POST /wallets/{id}/lightning/invoice`
- Backend: `rust-lightning` or `LDK`
- Hermes unaware of channel management

### Hardware Wallets

- Interface: `POST /wallets/{id}/hw/sign`
- Backend: HID transport + HWI
- Hermes unaware of device communication

### Multisig

- Interface: `POST /wallets/{id}/multisig/prepare`
- Backend: rust-miniscript + coordinated signing
- Hermes sees single signing request

### Nostr Wallet Connect

- Interface: `POST /nwc/connect`
- Backend: Nostr protocol handler
- Hermes can interact with NWC-enabled services

### Additional Blockchains

- Interface: same `/wallets/{id}` surface
- Backend: pluggable chain adapter
- Hermes sees unified wallet model

### External Signing Devices

- Interface: `POST /wallets/{id}/sign/external`
- Backend: PSBT export + device polling
- Hermes never sees key material

### Plugin System

- Python plugins: standard entry points
- Rust plugins: dynamic library loading
- Hermes sees plugin capabilities via discovery API

---

## 10. Security Boundaries

### Hermes Must Never

- Access raw private keys
- See seed phrases or mnemonics
- Handle PSBT internals
- Bypass policy engine
- Directly call Bitcoin Engine
- Access internal Rust state
- See stack traces or internal paths

### RawWalletAI Must Never

- Make financial decisions without explicit Hermes intent
- Expose more data than requested
- Log sensitive material
- Allow unsigned transactions
- Bypass policy engine
- Trust Hermes without authentication

### Shared Responsibility

- Authentication: Hermes provides credentials, RawWalletAI validates
- Authorization: Hermes defines roles, RawWalletAI enforces
- Audit: Hermes defines log format, RawWalletAI implements
- Policies: Hermes defines policies, RawWalletAI enforces

---

## 11. Supported Hermes Workflows

| Workflow | Hermes Action | RawWalletAI Responsibility |
|----------|---------------|---------------------------|
| Create wallet | Request | Generate, encrypt, store |
| Fund recovery | Request backup | Export encrypted seed |
| Daily operations | Request addresses, balances | Derive, query |
| Payments | Request send | Validate, select, sign, broadcast |
| Compliance | Request report | Aggregate, filter, return |
| Emergency | Trigger lock | Freeze immediately |
| Multi-sig | Request coordination | Manage signing rounds |
| Hardware | Request sign | Communicate with device |

---

## 12. API Responsibilities

### RawWalletAI API Owns

- Authentication and token management
- Request validation
- Rate limiting
- Error translation
- Response formatting
- API versioning
- OpenAPI documentation

### Hermes Owns

- User interaction
- Decision making
- Policy definition
- Agent coordination
- Retry logic
- Fallback behavior
- User communication

---

## 13. Wallet Responsibilities

### Wallet Engine Owns

- Wallet lifecycle
- Agent management
- Permission enforcement
- Policy evaluation
- Coin selection
- UTXO tracking
- Audit logging
- Backup/export control

### Bitcoin Engine Owns

- Key derivation
- Address generation
- PSBT manipulation
- Transaction signing
- Transaction serialization
- Script validation
- Sighash computation

---

## 14. Remaining Open Questions

1. **Authentication mechanism:** API tokens vs mTLS vs signed requests?
2. **Embedded vs network API:** Should Hermes embed RawWalletAI or call it over HTTP?
3. **Policy storage:** Where are policies stored — in Wallet Engine or external config?
4. **Multi-user:** Should RawWalletAI support multiple end-users or only agent identities?
5. **Backup format:** Should backup be a standard format or RawWalletAI-specific?
6. **Recovery flow:** How does multi-agent recovery work in practice?
7. **Offline mode:** Can Hermes queue requests when RawWalletAI is offline?
8. **Telemetry:** What telemetry is acceptable without compromising privacy?

---

## 15. Decision

**Status:** Proposed  
**Next Step:** Review and accept specification before Phase B implementation

This document defines the **contract between Hermes and RawWalletAI**. Implementation must adhere to this specification.
