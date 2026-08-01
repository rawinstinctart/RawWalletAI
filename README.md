# RawWalletAI

> **Autonome Krypto-Wallet-Engine für automatisierte Systeme und KI-Agenten.**

## Ziele
- Keine Registrierung, kein KYC, keine zentralen Anbieter
- Vollständige Self-Custody
- Modulare Architektur, API-first
- Sicherheit durch auditierten Code und standardisierte Kryptografie

## Status
- Phase 1: Grundgerüst stabil
- Bitcoin on-chain als erste Chain
- ECDSA + PSBT-basierte Transaktionen
- UTXO-Engine mit austauschbaren Backends

## Schnellstart
```bash
git clone https://github.com/rawinstinctart/RawWalletAI.git
cd RawWalletAI
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/unit/ -q
```

## Sicherheit
- Private Keys werden nie im Klartext übertragen oder gespeichert
- Seed Phrases: AES-256-GCM verschlüsselt mit zufälligem Salt pro Verschlüsselung
- BIP-32 kompatible Master-Key-Ableitung (HMAC-SHA512)
- ECDSA Signierung über `cryptography` Library
- Keine proprietäre Kryptographie

## Tests
```bash
# Unit-Tests
python -m pytest tests/unit/ -q

# Mit Coverage
python -m pytest --cov=src/rawwalletai --cov-report=term --cov-report=html tests/unit/
```

## Lizenz
MIT
