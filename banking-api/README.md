# 🏦 Banking API Service

FastAPI-based banking operations backend for FortressAI.

## Features

- **Account Management** - Get user accounts and balances
- **Transaction History** - View transaction records
- **Fund Transfers** - Transfer money between accounts
- **Account Summary** - Get spending analytics
- **API Key Authentication** - Secure endpoints

## API Endpoints

### GET /accounts/{user_id}
Get all accounts for a user.

**Headers:**
- `X-API-Key: BANKING-API-KEY-123`

**Response:**
```json
[
  {
    "account_id": "ACC001",
    "user_id": "user123",
    "account_type": "checking",
    "nickname": "Main Checking",
    "balance": 5420.50,
    "currency": "USD",
    "status": "active"
  }
]
```

### GET /accounts/{account_id}/balance
Get account balance.

**Response:**
```json
{
  "account_id": "ACC001",
  "balance": 5420.50,
  "currency": "USD",
  "account_type": "checking",
  "status": "active"
}
```

### GET /accounts/{account_id}/transactions
Get transaction history.

**Query Parameters:**
- `limit` (optional): Number of transactions (default: 10)

**Response:**
```json
[
  {
    "transaction_id": "TXN001",
    "account_id": "ACC001",
    "date": "2025-10-03T12:00:00",
    "description": "Grocery Store",
    "amount": -85.20,
    "balance_after": 5420.50,
    "category": "groceries",
    "status": "completed"
  }
]
```

### POST /transfer
Transfer funds between accounts.

**Request:**
```json
{
  "from_account": "ACC001",
  "to_account": "ACC002",
  "amount": 500.00,
  "description": "Savings transfer"
}
```

**Response:**
```json
{
  "success": true,
  "transaction_id": "TXN12345678",
  "from_account": "ACC001",
  "to_account": "ACC002",
  "amount": 500.00,
  "timestamp": "2025-10-04T12:00:00",
  "status": "completed"
}
```

### GET /accounts/{account_id}/summary
Get account summary with analytics.

**Response:**
```json
{
  "account": {...},
  "recent_transactions": [...],
  "spending_by_category": {
    "groceries": 85.20,
    "utilities": 120.50
  },
  "total_spent_last_5": 350.00
}
```

## Quick Start

### Local Development

```bash
cd banking-api

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload
```

### Docker

```bash
# Build
docker build -t banking-api .

# Run
docker run -p 8004:8004 banking-api
```

### Testing

```bash
# Health check
curl http://localhost:8004/health

# Get accounts (with API key)
curl -H "X-API-Key: BANKING-API-KEY-123" \
  http://localhost:8004/accounts/user123

# Get balance
curl -H "X-API-Key: BANKING-API-KEY-123" \
  http://localhost:8004/accounts/ACC001/balance

# Transfer funds
curl -X POST http://localhost:8004/transfer \
  -H "X-API-Key: BANKING-API-KEY-123" \
  -H "Content-Type: application/json" \
  -d '{
    "from_account": "ACC001",
    "to_account": "ACC002",
    "amount": 100.00,
    "description": "Test transfer"
  }'
```

## Authentication

All endpoints (except `/` and `/health`) require an API key in the header:

```
X-API-Key: BANKING-API-KEY-123
```

## Mock Data

The API currently uses mock data for demonstration:

**Users:**
- `user123` - Has ACC001 (checking) and ACC002 (savings)
- `user456` - Has ACC003 (business checking)

**Accounts:**
- `ACC001` - Checking, $5,420.50
- `ACC002` - Savings, $12,350.75
- `ACC003` - Business, $8,750.00

## Validation Rules

- Transfer amount must be positive
- Maximum transfer: $10,000
- Sufficient balance required
- Can only transfer between same user's accounts

## Integration with LangGraph Agent

Update the LangGraph agent to call this API:

```python
import httpx

async def get_account_balance(account_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://banking-api:8004/accounts/{account_id}/balance",
            headers={"X-API-Key": "BANKING-API-KEY-123"}
        )
        return response.json()
```

## Future Enhancements

- [ ] PostgreSQL database integration
- [ ] JWT authentication
- [ ] Rate limiting
- [ ] Transaction webhooks
- [ ] Bill payment API
- [ ] Investment accounts
- [ ] Multi-currency support
- [ ] Fraud detection
