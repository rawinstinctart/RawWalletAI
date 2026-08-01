# RawWalletAI – Technische Bewertung: PSBT-Finalisierungsbibliotheken

**Zweck:** Entscheidungsgrundlage für die Integration einer audited PSBT-Finalisierungsbibliothek.  
**Datum:** 2026-08-01  
**Status:** Bewertung, keine Implementierung

---

## Auswahlkriterien

1. Vollständige BIP-174-Unterstützung (PSBT Parse, Finalize, Extract)
2. BIP-141/BIP-143 SegWit-Unterstützung
3. BIP-340/Taproot-Kompatibilität (zukünftig)
4. Gewartete Codebasis
5. Sicherheitshistorie
6. Lizenzkompatibilität (MIT/BSD/Apache bevorzugt)
7. Abhängigkeitsfootprint

---

## Kandidaten

### 1. rust-bitcoin (via PyO3)

| Kriterium | Bewertung |
|-----------|-----------|
| PSBT-Finalisierung | Vollständig |
| SegWit | Ja |
| Taproot | Ja |
| Wartung | Sehr aktiv |
| Sicherheit | Hoch (Rust memory safety) |
| Lizenz | MIT |
| Footprint | Rust-Toolchain + PyO3 |
| Python-Reife | Mittel (PyO3 Bindings) |

**Empfehlung:** **Primärkandidat**  
**Begründung:** Rust-bitcoin ist die Referenzimplementierung für Bitcoin-Protokollserialisierung. Die Rust-Toolchain ist für Linux-Server verfügbar. PyO3-Bindings sind möglich, erfordern aber Build-Infrastruktur.

---

### 2. bdk (Bitcoin Dev Kit)

| Kriterium | Bewertung |
|-----------|-----------|
| PSBT-Finalisierung | Ja |
| SegWit | Ja |
| Taproot | Ja |
| Wartung | Sehr aktiv |
| Sicherheit | Hoch (audited Rust-Core) |
| Lizenz | MIT |
| Footprint | Rust + Python-Binding |
| Python-Reife | Niedrig (hauptsächlich Swift/Kotlin/C++) |

**Empfehlung:** **Sekundärkandidat**  
**Begründung:** BDK ist production-ready, aber Python-Bindings sind nicht First-Class. Integration würde erheblichen Wrapper-Aufwand erfordern.

---

### 3. python-bitcoinlib

| Kriterium | Bewertung |
|-----------|-----------|
| PSBT-Finalisierung | **Nein** |
| SegWit | Teilweise |
| Taproot | Nein |
| Wartung | Niedrig |
| Sicherheit | Mittel |
| Lizenz | MIT |
| Footprint | Gering |

**Empfehlung:** **Nicht geeignet**  
**Begründung:** Keine vollständige PSBT-Finalisierung. Würde ad-hoc-Serialisierung erfordern.

---

### 4. bitcoinlib

| Kriterium | Bewertung |
|-----------|-----------|
| PSBT-Finalisierung | Teilweise |
| SegWit | Ja |
| Taproot | Nein |
| Wartung | Aktiv |
| Sicherheit | Mittel |
| Lizenz | MIT |
| Footprint | **Hoch** (SQLAlchemy, fastecdsa, pycryptodome) |

**Empfehlung:** **Nicht geeignet für RawWalletAI**  
**Begründung:** Zu viele Abhängigkeiten für eine Wallet-Engine mit Minimalismus-Ansatz. SQLAlchemy als Core-Dependency ist überdimensioniert.

---

### 5. btcpy / andere Python-Only Libraries

| Kriterium | Bewertung |
|-----------|-----------|
| PSBT-Finalisierung | Fragmentiert |
| Wartung | Unklar |
| Sicherheit | Unbekannt |

**Empfehlung:** **Nicht bewertbar**  
**Begründung:** Keine etablierten Python-Only-Bibliotheken mit vollständiger PSBT-Unterstützung gefunden.

---

## Vergleichsmatrix

| Bibliothek | PSBT | SegWit | Taproot | Wartung | Footprint | Empfehlung |
|------------|------|--------|---------|---------|-----------|------------|
| rust-bitcoin | ✅ | ✅ | ✅ | Sehr hoch | Mittel | ✅ **Primär** |
| bdk | ✅ | ✅ | ✅ | Sehr hoch | Hoch | ⚠️ Sekundär |
| python-bitcoinlib | ❌ | ⚠️ | ❌ | Niedrig | Gering | ❌ |
| bitcoinlib | ⚠️ | ✅ | ❌ | Mittel | Sehr hoch | ❌ |
| btcpython-like | ❓ | ❓ | ❓ | Unbekannt | Gering | ❓ |

---

## Empfehlung

### Kurzfristig (Q3 2026)

1. **rust-bitcoin via PyO3** als strategische Lösung wählen
2. Minimalen Wrapper entwickeln: PSBT-Finalisierung + Extract
3. Rust-Toolchain in CI/CD integrieren
4. Regtest-Validierung gegen Bitcoin Core

### Mittelfristig (Q4 2026)

1. Eigenen gewarteten Python-Wrapper pflegen
2. Taproot-Support vorbereiten
3. Security-Audit durchführen

### Langfristig (2027)

1. Vollständige PSBT-Integration in RawWalletAI-Core
2. Release 1.0 nach bestandenem Audit

---

## Risiken

| Risiko | Wahrscheinlichkeit | Auswirkung | Mitigation |
|--------|-------------------|------------|------------|
| PyO3-Breaking Changes | Mittel | Hoch | Pin rust-bitcoin Version |
| Rust-Toolchain-Komplexität | Mittel | Mittel | CI vorcommit prüfen |
| Security-Bugs in Wrapper | Niedrig | Sehr hoch | Externes Audit |
| Lizenzkonflikte | Niedrig | Mittel | MIT-Lizenz kompatibel |

---

## Entscheidungsbedarf

**Diese Bewertung erfordert einen expliziten Architektur-Entscheid:**

1. Soll rust-bitcoin via PyO3 integriert werden?
2. Soll ein externer Security-Auditor beauftragt werden?
3. Soll der Release-Zeitplan angepasst werden?

Ohne diese Entscheidung bleibt RawWalletAI **nicht 1.0-release-fähig**.
