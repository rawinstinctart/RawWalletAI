# Architektur

## Übersicht

```
┌─────────────────────────────────────────┐
│  Hermes Agent                           │
│  ┌─────────────┐                        │
│  │  Wallet API │ ←── Unix Socket/HTTP   │
│  └──────┬──────┘                        │
│         │                               │
│  ┌──────▼──────┐                        │
│  │   Client    │                        │
│  └──────┬──────┘                        │
│         │                               │
│  ┌──────▼──────────────────────────┐    │
│  │         Wallet Core             │    │
│  │  ┌─────────┐  ┌─────────────┐  │    │
│  │  │  Keys   │  │  Storage    │  │    │
│  │  │ (BDK)   │  │ (Encrypted) │  │    │
│  │  └─────────┘  └─────────────┘  │    │
│  │  ┌─────────┐  ┌─────────────┐  │    │
│  │  │Tx Builder│ │Fee Estimate │  │    │
│  │  └─────────┘  └─────────────┘  │    │
│  └──────┬──────────────────────────┘    │
│         │                               │
│  ┌──────▼──────┐                        │
│  │  Bitcoin    │ ←── RPC/Electrum      │
│  │   Node      │                        │
│  └─────────────┘                        │
└─────────────────────────────────────────┘
```

## Kerngrundsätze

1. **Keine zentralen Abhängigkeiten:** Wallet funktioniert ohne Drittanbieter
2. **Self-Custody:** Private Keys verlassen niemals den lokalen Speicher
3. **API-first:** Core ist eine Bibliothek, keine App
4. **Security by Design:** Kritische Pfade nutzen auditierten Code (bdk)
5. **Modular:** Chains und Storage sind austauschbar

## Module

### Core
- `keys.py`: HD Wallet (BIP-39/32/44), Key Derivation
- `wallet.py`: Wallet-Instanz-Management
- `crypto.py`: Verschlüsselung, Argon2id

### Storage
- `encrypted.py`: Dateibasierte, verschlüsselte Ablage
- `hsm.py`: Hardware-Token-Support (zukünftig)

### Chains
- `base.py`: Abstrakte Chain-Adapter
- `bitcoin.py`: Bitcoin on-chain

### Transactions
- `builder.py`: Transaktionskonstruktion
- `signer.py`: Signierung
- `fee.py`: Gebührenschätzung

### API
- `server.py`: REST/JSON über Unix Socket
- `client.py`: Python-Client

### CLI
- `main.py`: Dünner Wrapper um die API
