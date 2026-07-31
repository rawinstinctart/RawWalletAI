"""API tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rawwalletai.api.server import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_wallet() -> None:
    response = client.post(
        "/wallet/create",
        json={"name": "test-wallet", "passphrase": "", "network": "bitcoin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "wallet_id" in data
    assert "address" in data
    assert "mnemonic" in data


def test_get_balance_not_found() -> None:
    response = client.get("/wallet/nonexistent/balance")
    assert response.status_code == 404


def test_get_transactions_not_found() -> None:
    response = client.get("/wallet/nonexistent/transactions")
    assert response.status_code == 404
