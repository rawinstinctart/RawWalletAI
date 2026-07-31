# Sicherheitsrichtlinien

## Grundsätze

1. **Private Keys nie im Klartext:** Seeds werden nur verschlüsselt gespeichert
2. **Argon2id für Key Derivation:**resistenter gegen GPU/ASIC-Angriffe als PBKDF2
3. **BDK für kritische Pfade:** Nutzung auditierten Codes für Key-Generation und Signing
4. **Keine Netzwerk-Anfragen ohne explizite Konfiguration:** Standard ist offline
5. **Minimaler Angriffsvektor:** Keine unnötigen Abhängigkeiten, keine GUI-Schwachstellen

## Speicher

- Seed Phrases: Argon2id-verschlüsselt, hardware-gebunden
- Private Keys: Nur im Speicher, nie auf Disk außer verschlüsselt
- Session Keys: Kurzlebig, flüchtig

## Audit

- Externe Prüfung vor Production
- Alle kritischen Pfade dokumentiert
- Keine proprietären Kryptographie-Verfahren
