"""
Tests for LangGraph Banking Agent
"""
import pytest
from src.agent import (
    get_account_balance,
    get_transaction_history,
    transfer_funds,
    get_user_accounts
)


def test_get_account_balance():
    """Test account balance retrieval."""
    result = get_account_balance.invoke({"account_id": "ACC001"})
    assert result["balance"] == 5420.50
    assert result["currency"] == "USD"


def test_get_transaction_history():
    """Test transaction history retrieval."""
    result = get_transaction_history.invoke({"account_id": "ACC001", "limit": 3})
    assert result["account_id"] == "ACC001"
    assert len(result["transactions"]) == 3


def test_transfer_funds_success():
    """Test successful fund transfer."""
    result = transfer_funds.invoke({
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": 100.0
    })
    assert result["success"] is True
    assert result["amount"] == 100.0


def test_transfer_funds_limit_exceeded():
    """Test transfer limit validation."""
    result = transfer_funds.invoke({
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": 15000.0
    })
    assert result["success"] is False
    assert "limit exceeded" in result["error"]


def test_transfer_funds_negative_amount():
    """Test negative amount validation."""
    result = transfer_funds.invoke({
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": -50.0
    })
    assert result["success"] is False
    assert "positive" in result["error"]


def test_get_user_accounts():
    """Test user accounts retrieval."""
    result = get_user_accounts.invoke({"user_id": "user123"})
    assert result["user_id"] == "user123"
    assert len(result["accounts"]) == 2
