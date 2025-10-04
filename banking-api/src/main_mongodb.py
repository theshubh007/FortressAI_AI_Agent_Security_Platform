"""
Banking API Service with MongoDB Integration
FastAPI-based banking operations backend
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import logging
from contextlib import asynccontextmanager
from .database import (
    connect_to_mongo, 
    close_mongo_connection,
    get_accounts_collection,
    get_transactions_collection,
    get_customers_collection
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="FortressAI Banking API",
    description="Secure banking operations API with MongoDB Atlas",
    version="1.0.0",
    lifespan=lifespan
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
    account_number: Optional[str] = None
    customer_id: str
    account_type: str
    nickname: str
    balance: float
    currency: str = "USD"
    status: str = "active"
    opened_date: Optional[datetime] = None


class Transaction(BaseModel):
    transaction_id: str
    account_id: str
    timestamp: datetime
    description: str
    amount: float
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


# Helper function
def mongo_to_dict(doc):
    """Convert MongoDB document to dictionary, removing _id."""
    if doc:
        doc.pop('_id', None)
    return doc


# Authentication
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
        "database": "MongoDB Atlas",
        "endpoints": {
            "accounts": "/accounts/{customer_id}",
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
        "database": "MongoDB Atlas",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/accounts/{customer_id}")
async def get_user_accounts(customer_id: str, api_key: str = Depends(verify_api_key)):
    """Get all accounts for a customer."""
    logger.info(f"Fetching accounts for customer: {customer_id}")
    
    try:
        collection = get_accounts_collection()
        cursor = collection.find({"customer_id": customer_id})
        accounts = [mongo_to_dict(doc) for doc in cursor]
        
        if not accounts:
            raise HTTPException(status_code=404, detail="No accounts found for customer")
        
        return accounts
        
    except Exception as e:
        logger.error(f"Error fetching accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts/{account_id}/balance")
async def get_account_balance(account_id: str, api_key: str = Depends(verify_api_key)):
    """Get account balance."""
    logger.info(f"Fetching balance for account: {account_id}")
    
    try:
        collection = get_accounts_collection()
        account = collection.find_one({"account_id": account_id})
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return {
            "account_id": account["account_id"],
            "balance": account["balance"],
            "currency": account.get("currency", "USD"),
            "account_type": account["account_type"],
            "status": account["status"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts/{account_id}/transactions")
async def get_transactions(
    account_id: str,
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
):
    """Get transaction history for an account."""
    logger.info(f"Fetching transactions for account: {account_id}, limit: {limit}")
    
    try:
        # First verify account exists
        accounts_collection = get_accounts_collection()
        account = accounts_collection.find_one({"account_id": account_id})
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Get transactions
        transactions_collection = get_transactions_collection()
        cursor = transactions_collection.find(
            {"account_id": account_id}
        ).sort("timestamp", -1).limit(limit)
        
        transactions = [mongo_to_dict(doc) for doc in cursor]
        
        return transactions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transfer")
async def transfer_funds(
    transfer: TransferRequest,
    api_key: str = Depends(verify_api_key)
):
    """Transfer funds between accounts."""
    logger.info(f"Transfer request: {transfer.from_account} -> {transfer.to_account}, amount: {transfer.amount}")
    
    try:
        accounts_collection = get_accounts_collection()
        
        # Get both accounts
        from_account = accounts_collection.find_one({"account_id": transfer.from_account})
        to_account = accounts_collection.find_one({"account_id": transfer.to_account})
        
        if not from_account:
            raise HTTPException(status_code=404, detail="Source account not found")
        
        if not to_account:
            raise HTTPException(status_code=404, detail="Destination account not found")
        
        # Validate sufficient balance
        if from_account["balance"] < transfer.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Validate transfer limit
        if transfer.amount > 10000:
            raise HTTPException(status_code=400, detail="Transfer limit exceeded (max $10,000)")
        
        # Validate same customer (for demo)
        if from_account["customer_id"] != to_account["customer_id"]:
            raise HTTPException(status_code=403, detail="Cannot transfer between different customers")
        
        # Execute transfer - update balances
        new_from_balance = from_account["balance"] - transfer.amount
        new_to_balance = to_account["balance"] + transfer.amount
        
        accounts_collection.update_one(
            {"account_id": transfer.from_account},
            {"$set": {"balance": new_from_balance, "updated_at": datetime.now()}}
        )
        
        accounts_collection.update_one(
            {"account_id": transfer.to_account},
            {"$set": {"balance": new_to_balance, "updated_at": datetime.now()}}
        )
        
        # Create transaction records
        transaction_id = f"TXN{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now()
        
        transactions_collection = get_transactions_collection()
        
        # Debit transaction
        transactions_collection.insert_one({
            "transaction_id": transaction_id,
            "account_id": transfer.from_account,
            "transaction_type": "debit",
            "category": "transfer",
            "amount": -transfer.amount,
            "balance_before": from_account["balance"],
            "balance_after": new_from_balance,
            "description": f"Transfer to {transfer.to_account}: {transfer.description}",
            "status": "completed",
            "timestamp": timestamp,
            "channel": "api"
        })
        
        # Credit transaction
        transactions_collection.insert_one({
            "transaction_id": transaction_id,
            "account_id": transfer.to_account,
            "transaction_type": "credit",
            "category": "transfer",
            "amount": transfer.amount,
            "balance_before": to_account["balance"],
            "balance_after": new_to_balance,
            "description": f"Transfer from {transfer.from_account}: {transfer.description}",
            "status": "completed",
            "timestamp": timestamp,
            "channel": "api"
        })
        
        logger.info(f"Transfer completed: {transaction_id}")
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "from_account": transfer.from_account,
            "to_account": transfer.to_account,
            "amount": transfer.amount,
            "timestamp": timestamp,
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transfer error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts/{account_id}/summary")
async def get_account_summary(account_id: str, api_key: str = Depends(verify_api_key)):
    """Get account summary with recent activity."""
    logger.info(f"Fetching summary for account: {account_id}")
    
    try:
        accounts_collection = get_accounts_collection()
        account = accounts_collection.find_one({"account_id": account_id})
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Get recent transactions
        transactions_collection = get_transactions_collection()
        cursor = transactions_collection.find(
            {"account_id": account_id}
        ).sort("timestamp", -1).limit(5)
        
        transactions = [mongo_to_dict(doc) for doc in cursor]
        
        # Calculate spending by category
        spending_by_category = {}
        for txn in transactions:
            if txn.get("amount", 0) < 0 and txn.get("category"):
                category = txn["category"]
                spending_by_category[category] = spending_by_category.get(category, 0) + abs(txn["amount"])
        
        return {
            "account": mongo_to_dict(account),
            "recent_transactions": transactions,
            "spending_by_category": spending_by_category,
            "total_spent_last_5": sum(abs(t.get("amount", 0)) for t in transactions if t.get("amount", 0) < 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
