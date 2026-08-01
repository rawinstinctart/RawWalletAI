# RawWalletAI – Master Implementation Plan

**Datum:** 2026-08-01  
**Status:** Entwurf  
**Geltungsbereich:** Implementierungsplanung für RawWalletAI 0.2 bis 1.0  
**Constraint:** Keine Code-Änderungen, keine Dependency-Änderungen, keine Prototypen in diesem Dokument

---

## Ziel

Dieses Dokument ist der **einzige Implementierungs-Blueprint** für RawWalletAI 0.2 → 1.0.

Es definiert:
- Phasenplan
- Abhängigkeiten
- Risiken
- Teststrategie
- Migrationspfad
- Exit Criteria

---

## Phasenplan

### Phase A — Rust Foundation

**Objective:**  
Rust-Build-Infrastruktur aufsetzen, ohne Wallet-Logik zu ändern.

**Deliverables:**
- `Cargo.toml` mit `rust-bitcoin`, `pyo3`, `maturin`
- `src/rawwalletai/rust/` Verzeichnisstruktur
- Minimaler PyO3-Build, der ein leeres Modul kompiliert
- Entwicklerdokumentation für Rust-Toolchain
- CI-Schritt für Rust-Setup

**Dependencies:**
- ADR-0001 accepted
- ADR-0002 accepted
- ADR-0007 accepted

**Risks:**
- Rust-Toolchain-Kompatibilität auf Entwickler-Maschinen
- Build-Zeit-Explosion
- PyO3-Versionskonflikte

**Success Criteria:**
- `maturin build` erzeugt leeres Wheel
- CI baut erfolgreich auf Ubuntu, macOS, Windows
- Entwickler können `pip install -e .` ausführen

**Estimated Complexity:** Mittel  
**Estimated Effort:** 1–2 Wochen  
**Blocking Issues:** Keine  
**Exit Criteria:**
- Leere Rust-Extension kompiliert und installiert
- CI grün auf allen Zielplattformen

---

### Phase B — Wrapper API

**Objective:**  
Stabile Python↔Rust-Grenze implementieren.

**Deliverables:**
- PyO3-Wrapper-Modul mit ADR-0006-Funktionen
- Type-Conversions Python ↔ Rust
- Error-Handling-Bridge
- GIL-Freigabe während Rust-Calls
- Wrapper-Tests (FFI, Typen, Fehler)

**Dependencies:**
- Phase A abgeschlossen
- ADR-0006 accepted

**Risks:**
- PyO3-API-Änderungen
- Memory-Safety in Wrapper-Boundary
- Performance-Overhead bei schlechtem Batch-Design

**Success Criteria:**
- Alle ADR-0006-Funktionen exportiert
- Wrapper-Tests grün
- Keine Memory-Leaks (valgrind-Test)
- < 1ms Overhead pro FFI-Call

**Estimated Complexity:** Hoch  
**Estimated Effort:** 2–3 Wochen  
**Blocking Issues:** ADR-0006 muss final akzeptiert sein  
**Exit Criteria:**
- Vollständige Wrapper-API implementiert
- FFI-Tests + Property-Tests grün

---

### Phase C — Python Integration

**Objective:**  
Wallet-Core an Wrapper-API anbinden, ohne Logik zu ändern.

**Deliverables:**
- `WalletAbstractionLayer` in Python
- PSBT-Workflow über Wrapper
- Fallback bei fehlender Rust-Extension
- API-Aktualisierungen
- Deprecation-Warnungen für alte Pfade

**Dependencies:**
- Phase B abgeschlossen
- Python-Test-Suite angepasst

**Risks:**
- Rückgabewerte wrappen
- Async-Kompatibilität
- Fehlerbehandlung zwischen Schichten

**Success Criteria:**
- Bestehende Python-Wallet-Logik funktioniert unverändert
- Neue Pfade über Rust getestet
- Keine Regression in Unit-Tests

**Estimated Complexity:** Mittel  
**Estimated Effort:** 2 Wochen  
**Blocking Issues:** Keine  
**Exit Criteria:**
- Alle 62 Unit-Tests plus neuer Wrapper-Tests grün
- Integrationstests gegen Mock-Rust erfolgreich

---

### Phase D — PSBT Finalization

**Objective:**  
Erste echte Bitcoin-Transaktionen erzeugen.

**Deliverables:**
- `finalize_psbt()` über rust-bitcoin
- Witness-Konstruktion
- Raw-Transaction-Extraktion
- PSBT-Validierung
- BIP-174-Testvektoren
- Regtest-Integrationstest gegen Bitcoin Core

**Dependencies:**
- Phase C abgeschlossen
- Bitcoin Core Regtest-Umgebung verfügbar

**Risks:**
- PSBT-Format-Inkompatibilitäten
- Witness-Gewichtsberechnung
- Regtest-Umgebung instabil

**Success Criteria:**
- Finalisierte PSBTs werden von Bitcoin Core akzeptiert
- Alle BIP-174-Testvektoren bestehen
- Signatur-Validierung erfolgreich

**Estimated Complexity:** Hoch  
**Estimated Effort:** 3 Wochen  
**Blocking Issues:** Regtest-Infrastruktur muss stehen  
**Exit Criteria:**
- 10 verschiedene PSBT-Szenarien auf Regtest erfolgreich
- Keine Custom-Serialisierung

---

### Phase E — Hermes Integration

**Objective:**  
RawWalletAI als autonomen Agenten-Wallet verfügbar machen.

**Deliverables:**
- Hermes-Skill für RawWalletAI
- Multi-Agent-Rechteverwaltung
- Freigabe-Workflows
- Zahlungsrichtlinien
- Audit-Log-Integration
- Telegram-Benachrichtigungen

**Dependencies:**
- Phase D abgeschlossen
- Hermes-Agent-SDK stabil

**Risks:**
- Rechteverwaltung komplex
- Workflow-Engpässe durch falsche Policies
- Audit-Log-Datenschutz

**Success Criteria:**
- Hermes kann Transaktionen autonom ausführen
- Multi-Agent-Freigabe funktioniert
- Policies werden durchgesetzt

**Estimated Complexity:** Sehr hoch  
**Estimated Effort:** 4–6 Wochen  
**Blocking Issues:** Hermes-API-Stabilität  
**Exit Criteria:**
- End-to-End-Agenten-Workflow auf Testnet erfolgreich

---

### Phase F — Public API

**Objective:**  
Produktionsreifes API exposing.

**Deliverables:**
- API-Authentifizierung
- Rate-Limiting
- Request-Validierung
- OpenAPI-Spezifikation
- API-Versionierung
- Monitoring-Hooks

**Dependencies:**
- Phase E abgeschlossen

**Risks:**
- Authentication-Bypass
- Rate-Limiting-Lücken
- API-Inkonsistenzen

**Success Criteria:**
- API penetration-tested
- Keine unauthentifizierten Endpunkte
- OpenAPI vollständig

**Estimated Complexity:** Mittel  
**Estimated Effort:** 2–3 Wochen  
**Blocking Issues:** Keine  
**Exit Criteria:**
- API Security Review bestanden
- Integrationstests für alle Endpunkte grün

---

### Phase G — Testnet Validation

**Objective:**  
Wallet gegen Bitcoin-Testnet validieren.

**Deliverables:**
- 100+ Testnet-Transaktionen
- Bugfixes aus Testnet-Exposition
- Performance-Benchmarks
- Edge-Case-Dokumentation

**Dependencies:**
- Phase F abgeschlossen

**Risks:**
- Testnet-Besonderheiten
- Timing-Probleme
- unforeseen Edge-Cases

**Success Criteria:**
- 100 Transaktionen ohne kritische Fehler
- Kein Geldverlust
- Performance im Rahmen

**Estimated Complexity:** Mittel  
**Estimated Effort:** 2–3 Wochen  
**Blocking Issues:** Testnet-Zugang stabil  
**Exit Criteria:**
- Testnet-Report mit Metriken

---

### Phase H — Mainnet Readiness

**Objective:**  
Vorbereitung auf Mainnet-Deployment.

**Deliverables:**
- Externer Security-Audit
- Penetrationstest
- Dokumentation finalisiert
- Release Candidate
- Backup/Recovery-Plan
- Incident-Response-Playbook

**Dependencies:**
- Phase G abgeschlossen

**Risks:**
- Audit findet kritische Fehler
- Penetrationstest schlägt fehl
- Performance-Probleme unter Last

**Success Criteria:**
- Externes Audit bestanden
- Keine kritischen/high findings
- RC 2 Wochen stabil

**Estimated Complexity:** Hoch  
**Estimated Effort:** 3–4 Wochen  
**Blocking Issues:** Externer Auditor verfügbar  
**Exit Criteria:**
- Audit-Bericht veröffentlicht
- RC auf Produktionsinfrastruktur getestet

---

### Phase I — Version 1.0

**Objective:**  
Erste stabile Version.

**Deliverables:**
- Produktionsreifer Wallet-Core
- Vollständige Dokumentation
- Stabile API
- Security-Audit-Bericht
- Release-Notes
- Known-Limitations-Dokument

**Dependencies:**
- Phase H abgeschlossen

**Risks:**
- Last-Minute-Regressionen
- Dokumentationslücken
- Support-Infrastruktur nicht bereit

**Success Criteria:**
- Alle kritischen/high-technical-debt-Items gelöst
- Externes Audit bestanden
- Community-Feedback eingearbeitet

**Estimated Complexity:** Mittel  
**Estimated Effort:** 1–2 Wochen  
**Blocking Issues:** Keine  
**Exit Criteria:**
- `v1.0.0` Tag erstellt
- PyPI-Release veröffentlicht
- GitHub Release Notes vollständig

---

## Abhängigkeitsgraph

```
Phase A ──→ Phase B ──→ Phase C ──→ Phase D
                                       │
                                       ↓
Phase E ◄── Phase F ◄── Phase G ◄── Phase H
   │
   ↓
Phase I
```

### Detaillierte Abhängigkeiten

| Phase | Benötigt | Blockiert |
|-------|----------|-----------|
| A | ADR-0001, ADR-0002, ADR-0007 | B, C, D |
| B | A, ADR-0006 | C |
| C | B | D |
| D | C, Regtest | E, G |
| E | D, Hermes-SDK | F |
| F | E | G |
| G | F | H |
| H | G | I |
| I | H | — |

**Keine zirkulären Abhängigkeiten.**

---

## Risikobewertung pro Phase

### Phase A — Rust Foundation
- **Technisch:** Mittel (Toolchain-Kompatibilität)
- **Security:** Niedrig (keine Logik-Änderung)
- **Build:** Hoch (Build-Zeiten, Caches)
- **Cross-Platform:** Mittel
- **Maintenance:** Niedrig

### Phase B — Wrapper API
- **Technisch:** Hoch (FFI-Boundary)
- **Security:** Hoch (Memory-Safety)
- **Build:** Mittel
- **Cross-Platform:** Mittel
- **Maintenance:** Mittel

### Phase C — Python Integration
- **Technisch:** Mittel
- **Security:** Mittel
- **Build:** Niedrig
- **Cross-Platform:** Niedrig
- **Maintenance:** Niedrig

### Phase D — PSBT Finalization
- **Technisch:** Hoch (Konsens-Logik)
- **Security:** Sehr hoch (Geldverlust-Risiko)
- **Build:** Niedrig
- **Cross-Platform:** Niedrig
- **Maintenance:** Mittel

### Phase E — Hermes Integration
- **Technisch:** Sehr hoch (Multi-Agent)
- **Security:** Hoch (Rechteverwaltung)
- **Build:** Niedrig
- **Cross-Platform:** Niedrig
- **Maintenance:** Hoch

### Phase F — Public API
- **Technisch:** Mittel
- **Security:** Hoch (Attack Surface)
- **Build:** Niedrig
- **Cross-Platform:** Niedrig
- **Maintenance:** Mittel

### Phase G — Testnet Validation
- **Technisch:** Mittel
- **Security:** Mittel
- **Build:** Niedrig
- **Cross-Platform:** Niedrig
- **Maintenance:** Niedrig

### Phase H — Mainnet Readiness
- **Technisch:** Mittel
- **Security:** Sehr hoch (externer Audit)
- **Build:** Niedrig
- **Cross-Platform:** Niedrig
- **Maintenance:** Niedrig

### Phase I — Version 1.0
- **Technisch:** Niedrig
- **Security:** Mittel
- **Build:** Niedrig
- **Cross-Platform:** Niedrig
- **Maintenance:** Mittel

---

## Teststrategie pro Meilenstein

### Phase A
- Build-Tests auf allen Plattformen
- Maturin-Integrations-Tests
- Rust-Unit-Tests für Minimal-Modul

### Phase B
- Wrapper-FFI-Tests
- Property-Tests für Serialisierung
- Memory-Safety-Tests (valgrind)
- Benchmark-Overhead-Messung

### Phase C
- Alle bestehenden Unit-Tests
- Neue Integrationstests mit Mock-Rust
- Regressionstests

### Phase D
- PSBT-Finalisierungs-Tests
- BIP-174-Testvektoren
- Regtest-Integrationstests
- Bitcoin Core Validierung
- Witness-Gewichts-Tests

### Phase E
- End-to-End-Agenten-Tests
- Rechteverwaltungs-Tests
- Workflow-Tests
- Policy-Enforcement-Tests

### Phase F
- API-Security-Tests
- Penetrationstests
- Rate-Limiting-Tests
- OpenAPI-Validierung

### Phase G
- 100+ Testnet-Transaktionen
- Performance-Benchmarks
- Edge-Case-Tests
- Langzeit-Stabilität

### Phase H
- Externer Security-Audit
- Penetrationstest
- Fuzzing
- Incident-Response-Tests

### Phase I
- Vollständiger Regressionstest
- Dokumentationsreview
- Release-Candidate-Tests
- Community-Beta

---

## Migrationsstrategie

### Von Python-only zu Hybrid Python + Rust

**Schritt 1 — Foundation (Phase A)**
- Rust-Toolchain integrieren
- Leere Extension bauen
- Keine Funktionsänderung

**Schritt 2 — Wrapper (Phase B)**
- Python↔Rust-Grenze definieren
- FFI-Boundary implementieren
- Noch keine Wallet-Logik in Rust

**Schritt 3 — Integration (Phase C)**
- Wallet-Logik bleibt in Python
- Erste Aufrufe über Wrapper
- Fallback bei fehlender Rust-Extension

**Schritt 4 — Konsens-Migration (Phase D)**
- PSBT-Finalisierung nach Rust
- Bitcoin-Logik verlässt Python
- Python orchestriert nur noch

**Schritt 5 — Production Features (Phase E–G)**
- Hermes-Integration
- Testnet-Validierung
- Agenten-Features

**Schritt 6 — Release (Phase H–I)**
- Audit
- Mainnet
- 1.0

### Rückwärtskompatibilität

- Python-API bleibt stabil
- Wallet-Dateien lesbar bleiben
- Fallback auf Python-only bei fehlender Rust-Extension
- Deprecation-Warnungen 2 Versionen vor Entfernung

---

## Empfohlene Implementierungsreihenfolge

1. **Phase A** — Rust Foundation
2. **Phase B** — Wrapper API
3. **Phase C** — Python Integration
4. **Phase D** — PSBT Finalization
5. **Phase G** — Testnet Validation (parallel zu E/F möglich)
6. **Phase E** — Hermes Integration
7. **Phase F** — Public API
8. **Phase H** — Mainnet Readiness
9. **Phase I** — Version 1.0

### Alternative Reihenfolge

Falls Hermes-Integration kritisch ist:
- Phase E kann parallel zu F/G laufen
- Voraussetzung: D abgeschlossen

---

## Höchst-Risiko-Phase

**Phase D — PSBT Finalization**

### Gründe
- Konsens-kritische Logik
- Geldverlust-Risiko bei Fehlern
- PSBT-Format-Inkompatibilitäten
- Witness-Gewichtsberechnung fehleranfällig
- Regtest-Umgebung muss stabil sein
- Externe Validierung durch Bitcoin Core erforderlich

### Mitigation
- Offizielle BIP-174-Testvektoren
- Regtest vor Testnet
- Externes Audit vor Mainnet
- Fuzzing
- Langsame, schrittweise Integration

---

## Pfad zu Version 1.0

### Geschätzter Zeitplan

| Phase | Dauer | Kumuliert |
|-------|-------|-----------|
| A | 1–2 Wochen | 2 Wochen |
| B | 2–3 Wochen | 5 Wochen |
| C | 2 Wochen | 7 Wochen |
| D | 3 Wochen | 10 Wochen |
| E | 4–6 Wochen | 16 Wochen |
| F | 2–3 Wochen | 19 Wochen |
| G | 2–3 Wochen | 22 Wochen |
| H | 3–4 Wochen | 26 Wochen |
| I | 1–2 Wochen | 28 Wochen |

**Geschätzte Dauer: ~6–7 Monate** bei Vollzeit-Entwicklung.

### Meilensteine

- **Woche 2:** Rust Foundation abgeschlossen
- **Woche 5:** Wrapper API stabil
- **Woche 7:** Python Integration abgeschlossen
- **Woche 10:** PSBT Finalization auf Regtest
- **Woche 16:** Hermes Integration
- **Woche 19:** Public API produktionsreif
- **Woche 22:** Testnet Validation abgeschlossen
- **Woche 26:** Mainnet Readiness
- **Woche 28:** Version 1.0

---

## Verbleibende architektonische Unbekannte

1. **PyO3-Wrapper-Stabilität:** Wie stabil ist die PyO3-API über rust-bitcoin-Releases hinweg?
2. **Rust-Toolchain-Verfügbarkeit:** Ist Rust auf allen Zielplattformen (Android/Termux, ARM64) verfügbar?
3. **Build-Zeiten:** Wie lange dauern Cross-Platform-Wheels in der Praxis?
4. **Memory-Profiling:** Wie verhält sich Rust-Speicher unter langfristiger Wallet-Nutzung?
5. **Bitcoin Kernel:** Sollten wir zukünftig `libbitcoinkernel` statt rust-bitcoin evaluieren?
6. **Taproot-Strategie:** Wann und wie integrieren wir Taproot vollständig?
7. **Multi-Chain:** Soll die Architektur später Bitcoin Lightning oder andere Chains unterstützen?

---

## Entscheidungsbedarf

Für den Start der Implementierung müssen folgende ADRs formal akzeptiert werden:

| ADR | Thema | Status |
|-----|-------|--------|
| ADR-0001 | PSBT Finalization Strategy | Accepted |
| ADR-0002 | Build Tooling and Packaging | Proposed |
| ADR-0003 | CI/CD and Release Engineering | Proposed |
| ADR-0004 | Cross-Platform Support | Proposed |
| ADR-0005 | Long-Term Maintenance Model | Proposed |
| ADR-0006 | Wrapper API Design | Proposed |
| ADR-0007 | Bitcoin Engine Selection | Proposed |

**Empfehlung:**  
ADR-0002 bis ADR-0007 vor Implementierungsbeginn akzeptieren.

---

## Fazit

Dieser Plan ist der **verbindliche Implementierungsfahrplan** für RawWalletAI 0.2 bis 1.0.

Er basiert auf:
- Akzeptierten Architektur-Entscheidungen
- Objektiver Kandidatenbewertung
- Realistischer Aufwandsschätzung
- Klarer Risikobewertung

**Nächster Schritt:**  
Formelle Annahme dieses Plans und Start mit Phase A.
