"""
Tests for Banking API
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

API_KEY = "BANKING-API-KEY-123"
HEADERS = {"X-API-Key": API_KEY}


def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


def test_get_user_accounts():
    """Test getting user accounts."""
    response = client.get("/accounts/user123", headers=HEADERS)
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) == 2
    assert accounts[0]["user_id"] == "user123"


def test_get_user_accounts_unauthorized():
    """Test unauthorized access."""
    response = client.get("/accounts/user123")
    assert response.status_code == 401


def test_get_account_balance():
    """Test getting account balance."""
    response = client.get("/accounts/ACC001/balance", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == "ACC001"
    assert data["balance"] == 5420.50


def test_get_account_balance_not_found():
    """Test getting balance for non-existent account."""
    response = client.get("/accounts/ACC999/balance", headers=HEADERS)
    assert response.status_code == 404


def test_get_transactions():
    """Test getting transaction history."""
    response = client.get("/accounts/ACC001/transactions?limit=3", headers=HEADERS)
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) <= 3


def test_transfer_funds_success():
    """Test successful fund transfer."""
    transfer_data = {
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": 100.00,
        "description": "Test transfer"
    }
    response = client.post("/transfer", json=transfer_data, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["amount"] == 100.00


def test_transfer_funds_insufficient():
    """Test transfer with insufficient funds."""
    transfer_data = {
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": 999999.00
    }
    response = client.post("/transfer", json=transfer_data, headers=HEADERS)
    assert response.status_code == 400
    assert "Insufficient" in response.json()["detail"]


def test_transfer_funds_limit_exceeded():
    """Test transfer exceeding limit."""
    transfer_data = {
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": 15000.00
    }
    response = client.post("/transfer", json=transfer_data, headers=HEADERS)
    assert response.status_code == 400
    assert "limit exceeded" in response.json()["detail"]


def test_get_account_summary():
    """Test getting account summary."""
    response = client.get("/accounts/ACC001/summary", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "account" in data
    assert "recent_transactions" in data
    assert "spending_by_category" in data
