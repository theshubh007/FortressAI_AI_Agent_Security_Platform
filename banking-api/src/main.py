"""
Banking API Service
FastAPI-based banking operations backend
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FortressAI Banking API",
    description="Secure banking operations API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class Account(BaseModel):
    account_id: str
    user_id: str
    account_type: str  # checking, savings, credit
    nickname: str
    balance: float
    currency: str = "USD"
    status: str = "active"
    created_at: datetime


class Transaction(BaseModel):
    transaction_id: str
    account_id: str
    date: datetime
    description: str
    amount: float
    balance_after: float
    category: Optional[str] = None
    status: str = "completed"


class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float = Field(gt=0, description="Amount must be positive")
    description: Optional[str] = "Transfer"


class TransferResponse(BaseModel):
    success: bool
    transaction_id: str
    from_account: str
    to_account: str
    amount: float
    timestamp: datetime
    status: str


# Mock Database
MOCK_ACCOUNTS = {
    "ACC001": Account(
        account_id="ACC001",
        user_id="user123",
        account_type="checking",
        nickname="Main Checking",
        balance=5420.50,
        currency="USD",
        status="active",
        created_at=datetime(2023, 1, 15)
    ),
    "ACC002": Account(
        account_id="ACC002",
        user_id="user123",
        account_type="savings",
        nickname="Emergency Fund",
        balance=12350.75,
        currency="USD",
        status="active",
        created_at=datetime(2023, 1, 15)
    ),
    "ACC003": Account(
        account_id="ACC003",
        user_id="user456",
        account_type="checking",
        nickname="Business Account",
        balance=8750.00,
        currency="USD",
        status="active",
        created_at=datetime(2023, 3, 20)
    ),
}

MOCK_TRANSACTIONS = {
    "ACC001": [
        Transaction(
            transaction_id="TXN001",
            account_id="ACC001",
            date=datetime.now() - timedelta(days=1),
            description="Grocery Store",
            amount=-85.20,
            balance_after=5420.50,
            category="groceries"
        ),
        Transaction(
            transaction_id="TXN002",
            account_id="ACC001",
            date=datetime.now() - timedelta(days=2),
            description="Salary Deposit",
            amount=3500.00,
            balance_after=5505.70,
            category="income"
        ),
        Transaction(
            transaction_id="TXN003",
            account_id="ACC001",
            date=datetime.now() - timedelta(days=3),
            description="Electric Bill",
            amount=-120.50,
            balance_after=2005.70,
            category="utilities"
        ),
        Transaction(
            transaction_id="TXN004",
            account_id="ACC001",
            date=datetime.now() - timedelta(days=4),
            description="Restaurant",
            amount=-45.30,
            balance_after=2126.20,
            category="dining"
        ),
        Transaction(
            transaction_id="TXN005",
            account_id="ACC001",
            date=datetime.now() - timedelta(days=5),
            description="ATM Withdrawal",
            amount=-100.00,
            balance_after=2171.50,
            category="cash"
        ),
    ],
    "ACC002": [
        Transaction(
            transaction_id="TXN006",
            account_id="ACC002",
            date=datetime.now() - timedelta(days=10),
            description="Interest Payment",
            amount=25.75,
            balance_after=12350.75,
            category="interest"
        ),
    ]
}


# Authentication (simple API key for demo)
async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from header."""
    if not x_api_key or x_api_key != "BANKING-API-KEY-123":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# Endpoints
@app.get("/")
async def root():
    """API information."""
    return {
        "service": "FortressAI Banking API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "accounts": "/accounts/{user_id}",
            "balance": "/accounts/{account_id}/balance",
            "transactions": "/accounts/{account_id}/transactions",
            "transfer": "/transfer (POST)",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Banking API",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/accounts/{user_id}", response_model=List[Account])
async def get_user_accounts(user_id: str, api_key: str = Depends(verify_api_key)):
    """Get all accounts for a user."""
    logger.info(f"Fetching accounts for user: {user_id}")
    
    accounts = [acc for acc in MOCK_ACCOUNTS.values() if acc.user_id == user_id]
    
    if not accounts:
        raise HTTPException(status_code=404, detail="No accounts found for user")
    
    return accounts


@app.get("/accounts/{account_id}/balance")
async def get_account_balance(account_id: str, api_key: str = Depends(verify_api_key)):
    """Get account balance."""
    logger.info(f"Fetching balance for account: {account_id}")
    
    if account_id not in MOCK_ACCOUNTS:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = MOCK_ACCOUNTS[account_id]
    
    return {
        "account_id": account.account_id,
        "balance": account.balance,
        "currency": account.currency,
        "account_type": account.account_type,
        "status": account.status
    }


@app.get("/accounts/{account_id}/transactions", response_model=List[Transaction])
async def get_transactions(
    account_id: str,
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
):
    """Get transaction history for an account."""
    logger.info(f"Fetching transactions for account: {account_id}, limit: {limit}")
    
    if account_id not in MOCK_ACCOUNTS:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transactions = MOCK_TRANSACTIONS.get(account_id, [])
    
    return transactions[:limit]


@app.post("/transfer", response_model=TransferResponse)
async def transfer_funds(
    transfer: TransferRequest,
    api_key: str = Depends(verify_api_key)
):
    """Transfer funds between accounts."""
    logger.info(f"Transfer request: {transfer.from_account} -> {transfer.to_account}, amount: {transfer.amount}")
    
    # Validate accounts exist
    if transfer.from_account not in MOCK_ACCOUNTS:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    if transfer.to_account not in MOCK_ACCOUNTS:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    from_account = MOCK_ACCOUNTS[transfer.from_account]
    to_account = MOCK_ACCOUNTS[transfer.to_account]
    
    # Validate sufficient balance
    if from_account.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Validate transfer limit
    if transfer.amount > 10000:
        raise HTTPException(status_code=400, detail="Transfer limit exceeded (max $10,000)")
    
    # Validate same user (for demo)
    if from_account.user_id != to_account.user_id:
        raise HTTPException(status_code=403, detail="Cannot transfer between different users")
    
    # Execute transfer (update mock data)
    from_account.balance -= transfer.amount
    to_account.balance += transfer.amount
    
    transaction_id = f"TXN{uuid.uuid4().hex[:8].upper()}"
    
    # Record transactions
    debit_txn = Transaction(
        transaction_id=transaction_id,
        account_id=transfer.from_account,
        date=datetime.now(),
        description=f"Transfer to {transfer.to_account}: {transfer.description}",
        amount=-transfer.amount,
        balance_after=from_account.balance,
        category="transfer"
    )
    
    credit_txn = Transaction(
        transaction_id=transaction_id,
        account_id=transfer.to_account,
        date=datetime.now(),
        description=f"Transfer from {transfer.from_account}: {transfer.description}",
        amount=transfer.amount,
        balance_after=to_account.balance,
        category="transfer"
    )
    
    # Add to transaction history
    if transfer.from_account not in MOCK_TRANSACTIONS:
        MOCK_TRANSACTIONS[transfer.from_account] = []
    if transfer.to_account not in MOCK_TRANSACTIONS:
        MOCK_TRANSACTIONS[transfer.to_account] = []
    
    MOCK_TRANSACTIONS[transfer.from_account].insert(0, debit_txn)
    MOCK_TRANSACTIONS[transfer.to_account].insert(0, credit_txn)
    
    logger.info(f"Transfer completed: {transaction_id}")
    
    return TransferResponse(
        success=True,
        transaction_id=transaction_id,
        from_account=transfer.from_account,
        to_account=transfer.to_account,
        amount=transfer.amount,
        timestamp=datetime.now(),
        status="completed"
    )


@app.get("/accounts/{account_id}/summary")
async def get_account_summary(account_id: str, api_key: str = Depends(verify_api_key)):
    """Get account summary with recent activity."""
    if account_id not in MOCK_ACCOUNTS:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = MOCK_ACCOUNTS[account_id]
    transactions = MOCK_TRANSACTIONS.get(account_id, [])[:5]
    
    # Calculate spending by category
    spending_by_category = {}
    for txn in transactions:
        if txn.amount < 0 and txn.category:
            category = txn.category
            spending_by_category[category] = spending_by_category.get(category, 0) + abs(txn.amount)
    
    return {
        "account": account,
        "recent_transactions": transactions,
        "spending_by_category": spending_by_category,
        "total_spent_last_5": sum(abs(t.amount) for t in transactions if t.amount < 0)
    }
