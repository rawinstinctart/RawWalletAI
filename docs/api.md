# API-Referenz

## Endpunkte

### POST /wallet/create
Erstellt eine neue Wallet.

**Request:**
```json
{
  "name": "meine-wallet",
  "passphrase": "optional",
  "network": "bitcoin"
}
```

**Response:**
```json
{
  "wallet_id": "uuid",
  "address": "bc1q...",
  "mnemonic": "word1 word2 ... word12"
}
```

### POST /wallet/{wallet_id}/send
Sendet eine Transaktion.

**Request:**
```json
{
  "to": "bc1q...",
  "amount_sats": 50000,
  "fee_rate": 2.0
}
```

### GET /wallet/{wallet_id}/balance
Gibt den aktuellen Kontostand zurück.

### GET /wallet/{wallet_id}/transactions
Listet alle Transaktionen auf.

## Authentifizierung

- Unix Socket: Nur lokale Prozesse
- HTTP: Bearer Token oder mTLS (zukünftig)
