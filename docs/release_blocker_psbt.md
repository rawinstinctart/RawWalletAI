# RawWalletAI – Release Blocker Report

**Status:** NOT READY FOR 1.0 RELEASE  
**Datum:** 2026-08-01  
**Prüfer:** Hermes Agent  
**Betreff:** Fehlende PSBT-Finalisierung mit audited Library

---

## Executive Summary

RawWalletAI ist **nicht release-bereit für Version 1.0**.

Der Kernblocker ist die fehlende Implementierung einer vollständigen, standard-konformen PSBT-Finalisierung. Eine solche Implementierung erfordert entweder:

1. Eine audierte Bitcoin-Bibliothek mit vollständiger BIP-174-Unterstützung in Python, oder
2. Eine gewartete Wrapper-Bibliothek um eine native Implementierung.

Beide Optionen sind im aktuellen Stack **nicht vorhanden**.

---

## Technische Analyse

### Vorhandene Bibliotheken

| Bibliothek | Vorhanden | PSBT-Finalisierung | Bewertung |
|------------|-----------|---------------------|-----------|
| `python-bitcoinlib` | Ja | Nein | Keine Witness-Serialisierung |
| `cryptography` | Ja | Nein | Nur ECDSA, kein Bitcoin-Format |
| `secp256k1` | Ja | Nein | Nur Signaturprüfung |
| `bdk` | Nein | Ja | Nicht installiert |
| `bitcoinlib` | Nein | Teilweise | Würde SQLAlchemy + fastecdsa + pycryptodome einführen |

### Warum keine ad-hoc-Implementierung?

- Bitcoin-Transaktionsserialisierung mit Witness-Daten ist **nicht trivial**
- Fehler führen zu **unbcastbaren Transaktionen** oder **Geldverlust**
- BIP-143-Sighash-Berechnung ist fehleranfällig
- Keine proprietäre Kryptographie-Policy-Verletzung, aber: **keine Bitcoin-Protokoll-Serialisierung ohne audierte Library**

---

## Konsequenz

Bis eine der folgenden Bedingungen erfüllt ist, bleibt RawWalletAI **Pre-Alpha**:

1. Integration einer audierten PSBT-Finalisierungsbibliothek
2. Externe Prüfung einer selbst implementierten Lösung
3. Explizite Dokumentation als "nicht mainnet-tauglich"

---

## Empfehlung

**Sperre 1.0-Release bis PSBT-Finalisierung abgeschlossen ist.**

Mögliche Pfade:

- Kurzfristig: `bdk` als Python-Binding evaluieren
- Mittelfristig: `rust-bitcoin` via PyO3 Wrapper
- Langfristig: Eigener gewarteter Wrapper um `libsecp256k1`

---

## Nächste Schritte

1. Architektur-Entscheidung für PSBT-Bibliothek treffen
2. Abhängigkeitsanalyse durchführen
3. Implementierung + Tests + Regtest-Validierung
4. Externer Security-Audit
5. Release 1.0
