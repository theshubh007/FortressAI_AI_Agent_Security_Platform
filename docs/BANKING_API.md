# 🏦 Banking API Documentation

## Overview

The **Banking API** is a FastAPI-based microservice that provides secure banking operations for the FortressAI system. It handles account management, transactions, and fund transfers with API key authentication.

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Banking API Service                    │
│                                                  │
│  ┌──────────────┐      ┌──────────────┐        │
│  │   FastAPI    │─────▶│  Mock Data   │        │
│  │   Endpoints  │◀─────│   Store      │        │
│  └──────────────┘      └──────────────┘        │
│         │                                        │
│         ▼                                        │
│  ┌──────────────┐                               │
│  │  API Key     │                               │
│  │  Auth        │                               │
│  └──────────────┘                               │
└─────────────────────────────────────────────────┘
         │
         ▼
  LangGraph Agent
```

## API Endpoints

### Authentication

All endpoints (except `/` and `/health`) require API key authentication:

**Header:**
```
X-API-Key: BANKING-API-KEY-123
```

### Endpoints

#### GET /
Root endpoint with API information.

**Response:**
```json
{
  "service": "FortressAI Banking API",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": {...}
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Banking API",
  "timestamp": "2025-10-04T12:00:00Z"
}
```

#### GET /accounts/{user_id}
Get all accounts for a user.

**Parameters:**
- `user_id` (path): User identifier

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
    "status": "active",
    "created_at": "2023-01-15T00:00:00"
  }
]
```

#### GET /accounts/{account_id}/balance
Get account balance.

**Parameters:**
- `account_id` (path): Account identifier

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

#### GET /accounts/{account_id}/transactions
Get transaction history.

**Parameters:**
- `account_id` (path): Account identifier
- `limit` (query, optional): Number of transactions (default: 10)

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

#### POST /transfer
Transfer funds between accounts.

**Request Body:**
```json
{
  "from_account": "ACC001",
  "to_account": "ACC002",
  "amount": 500.00,
  "description": "Savings transfer"
}
```

**Validation:**
- Amount must be positive
- Maximum transfer: $10,000
- Sufficient balance required
- Same user accounts only

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

**Error Response:**
```json
{
  "detail": "Insufficient funds"
}
```

#### GET /accounts/{account_id}/summary
Get account summary with analytics.

**Parameters:**
- `account_id` (path): Account identifier

**Response:**
```json
{
  "account": {
    "account_id": "ACC001",
    "balance": 5420.50,
    ...
  },
  "recent_transactions": [...],
  "spending_by_category": {
    "groceries": 85.20,
    "utilities": 120.50,
    "dining": 45.30
  },
  "total_spent_last_5": 350.00
}
```

## Data Models

### Account
```python
{
  "account_id": str,
  "user_id": str,
  "account_type": str,  # checking, savings, credit
  "nickname": str,
  "balance": float,
  "currency": str,
  "status": str,        # active, frozen, closed
  "created_at": datetime
}
```

### Transaction
```python
{
  "transaction_id": str,
  "account_id": str,
  "date": datetime,
  "description": str,
  "amount": float,      # negative for debits
  "balance_after": float,
  "category": str,      # optional
  "status": str
}
```

## Mock Data

### Users
- **user123**: Personal banking customer
  - ACC001: Checking ($5,420.50)
  - ACC002: Savings ($12,350.75)
  
- **user456**: Business customer
  - ACC003: Business Checking ($8,750.00)

### Transaction Categories
- `groceries` - Grocery purchases
- `utilities` - Utility bills
- `dining` - Restaurants
- `income` - Salary, deposits
- `transfer` - Account transfers
- `cash` - ATM withdrawals
- `interest` - Interest payments

## Security

### API Key Authentication
Simple header-based authentication for demo purposes.

**Production Recommendations:**
- JWT tokens with expiration
- OAuth 2.0 integration
- Rate limiting per API key
- IP whitelisting
- Request signing

### Validation
- Input sanitization
- Amount validation (positive, within limits)
- Account ownership verification
- Balance checks before transfers

### Audit Logging
All operations are logged with:
- Timestamp
- User ID
- Operation type
- Request details
- Response status

## Integration with LangGraph Agent

The LangGraph agent calls the Banking API through HTTP:

```python
# agent-langgraph/src/agent.py

@tool
async def get_account_balance(account_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BANKING_API_URL}/accounts/{account_id}/balance",
            headers={"X-API-Key": BANKING_API_KEY}
        )
        return response.json()
```

### Environment Variables
```bash
BANKING_API_URL=http://banking-api:8004
BANKING_API_KEY=BANKING-API-KEY-123
```

## Testing

### Unit Tests
```bash
cd banking-api
pytest tests/test_api.py -v
```

### Manual Testing
```bash
# Health check
curl http://localhost:8004/health

# Get accounts
curl -H "X-API-Key: BANKING-API-KEY-123" \
  http://localhost:8004/accounts/user123

# Transfer funds
curl -X POST http://localhost:8004/transfer \
  -H "X-API-Key: BANKING-API-KEY-123" \
  -H "Content-Type: application/json" \
  -d '{
    "from_account": "ACC001",
    "to_account": "ACC002",
    "amount": 100.00
  }'
```

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 10 \
  -H "X-API-Key: BANKING-API-KEY-123" \
  http://localhost:8004/accounts/user123
```

## Deployment

### Docker
```bash
# Build
docker build -t banking-api ./banking-api

# Run
docker run -p 8004:8004 \
  -e BANKING_API_KEY=your-key \
  banking-api
```

### Docker Compose
```bash
# Start banking API
docker-compose up -d banking-api

# View logs
docker-compose logs -f banking-api

# Check health
curl http://localhost:8004/health
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad request (validation error)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found (account/user doesn't exist)
- `500` - Internal server error

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

## Performance

### Response Times (Target)
- GET requests: < 50ms
- POST requests: < 100ms
- Complex queries: < 200ms

### Optimization
- In-memory mock data (fast)
- Async endpoints
- Connection pooling (for real DB)
- Caching (for production)

## Future Enhancements

### Database Integration
Replace mock data with PostgreSQL:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:pass@localhost/banking"
engine = create_engine(DATABASE_URL)
```

### Advanced Features
- [ ] Bill payment scheduling
- [ ] Recurring transfers
- [ ] Account statements (PDF)
- [ ] Transaction search/filtering
- [ ] Multi-currency support
- [ ] Investment accounts
- [ ] Credit card management
- [ ] Loan applications

### Security Enhancements
- [ ] JWT authentication
- [ ] 2FA for transfers
- [ ] Transaction limits per user
- [ ] Fraud detection
- [ ] Encryption at rest
- [ ] PCI DSS compliance

### Monitoring
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (APM)
- [ ] Audit log retention

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc

## Support

For issues or questions:
- Check the [main README](../README.md)
- Review [LangGraph Agent docs](./LANGGRAPH_AGENT.md)
- Open an issue on GitHub
