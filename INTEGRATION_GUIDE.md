# 🔗 FortressAI Integration Guide

Complete guide for running and testing the integrated system.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FortressAI System                        │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   Gateway    │─────▶│    Broker    │                    │
│  │  (Port 9000) │◀─────│  (Port 8001) │                    │
│  └──────────────┘      └──────────────┘                    │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │  LangGraph   │─────▶│  Banking API │                    │
│  │    Agent     │◀─────│  (Port 8004) │                    │
│  │  (Port 8003) │      └──────────────┘                    │
│  └──────────────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │   Frontend   │                                           │
│  │  (Port 3000) │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Docker & Docker Compose** installed
2. **Anthropic API Key** (for Claude)
3. **Python 3.11+** (for local development)
4. **Node.js 18+** (for frontend)

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
nano .env
```

Required variables:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
BANKING_API_KEY=BANKING-API-KEY-123
LLM_MODEL=claude-3-5-sonnet-20241022
```

### 2. Start All Services

```bash
# Start everything with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Verify Services

```bash
# Banking API
curl http://localhost:8004/health

# LangGraph Agent
curl http://localhost:8003/health

# Broker/Firewall
curl http://localhost:8001/health

# Gateway
curl http://localhost:9000/health
```

## Testing the Integration

### Option 1: Automated Test Script

```bash
# Install dependencies
pip install httpx

# Run integration tests
python test_integration.py
```

### Option 2: Manual Testing

#### Test Banking API Directly

```bash
# Get user accounts
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
    "amount": 100.00
  }'
```

#### Test LangGraph Agent

```bash
# Check balance
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is my account balance?",
    "user_id": "user123"
  }'

# View transactions
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me my recent transactions",
    "user_id": "user123"
  }'

# Transfer money
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Transfer $50 from checking to savings",
    "user_id": "user123"
  }'
```

## Service Details

### Banking API (Port 8004)

**Purpose:** Provides banking operations (accounts, transactions, transfers)

**Endpoints:**
- `GET /accounts/{user_id}` - Get user accounts
- `GET /accounts/{account_id}/balance` - Get balance
- `GET /accounts/{account_id}/transactions` - Get transactions
- `POST /transfer` - Transfer funds
- `GET /accounts/{account_id}/summary` - Get summary

**Authentication:** API Key in `X-API-Key` header

**Documentation:** http://localhost:8004/docs

### LangGraph Agent (Port 8003)

**Purpose:** AI agent using Claude to handle banking queries

**Endpoints:**
- `POST /query` - Process natural language banking query
- `GET /health` - Health check

**Tools:**
- `get_user_accounts` - List accounts
- `get_account_balance` - Check balance
- `get_transaction_history` - View transactions
- `transfer_funds` - Transfer money
- `get_account_summary` - Get analytics

**Documentation:** http://localhost:8003/docs

### Broker/Firewall (Port 8001)

**Purpose:** Security layer with prompt injection detection

**Features:**
- Regex-based filtering
- LLM-based semantic analysis (PromptShield)
- Request/response logging

### Gateway (Port 9000)

**Purpose:** API gateway and routing

**Features:**
- Request routing
- Authentication
- Rate limiting

## Data Flow Example

### Query: "What's my checking account balance?"

```
1. User → Agent (POST /query)
   {
     "query": "What's my checking account balance?",
     "user_id": "user123"
   }

2. Agent → Claude LLM
   Analyzes query, decides to use tools

3. Agent → Banking API (GET /accounts/user123)
   Headers: X-API-Key: BANKING-API-KEY-123
   Response: [{"account_id": "ACC001", "type": "checking", ...}]

4. Agent → Banking API (GET /accounts/ACC001/balance)
   Response: {"balance": 5420.50, "currency": "USD"}

5. Agent → Claude LLM
   Formats response

6. Agent → User
   {
     "response": "Your checking account has a balance of $5,420.50 USD",
     "message_count": 4,
     "tool_calls_made": 2
   }
```

## Local Development

### Run Banking API Locally

```bash
cd banking-api
pip install -r requirements.txt
uvicorn src.main:app --port 8004 --reload
```

### Run LangGraph Agent Locally

```bash
cd agent-langgraph
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY=sk-ant-your-key
export BANKING_API_URL=http://localhost:8004
export BANKING_API_KEY=BANKING-API-KEY-123

# Run
uvicorn src.app:app --port 8003 --reload
```

## Troubleshooting

### Issue: Agent can't connect to Banking API

**Solution:**
```bash
# Check if Banking API is running
curl http://localhost:8004/health

# Check Docker network
docker network inspect fortressai_mesh

# Check agent logs
docker-compose logs agent-langgraph
```

### Issue: API Key authentication fails

**Solution:**
```bash
# Verify API key in .env
cat .env | grep BANKING_API_KEY

# Test with correct key
curl -H "X-API-Key: BANKING-API-KEY-123" \
  http://localhost:8004/accounts/user123
```

### Issue: Claude API errors

**Solution:**
```bash
# Verify Anthropic API key
cat .env | grep ANTHROPIC_API_KEY

# Check agent logs for API errors
docker-compose logs agent-langgraph | grep -i error
```

### Issue: Timeout errors

**Solution:**
```bash
# Increase timeout in agent-langgraph/src/banking_client.py
# Change: self.timeout = 10.0
# To: self.timeout = 30.0

# Rebuild
docker-compose up -d --build agent-langgraph
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f banking-api
docker-compose logs -f agent-langgraph

# Last 100 lines
docker-compose logs --tail=100 agent-langgraph
```

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Production Considerations

### Security

- [ ] Replace mock data with real database
- [ ] Implement JWT authentication
- [ ] Add rate limiting
- [ ] Enable HTTPS/TLS
- [ ] Implement audit logging
- [ ] Add request signing
- [ ] Use secrets management (Vault, AWS Secrets Manager)

### Performance

- [ ] Add Redis caching
- [ ] Implement connection pooling
- [ ] Add load balancing
- [ ] Enable horizontal scaling
- [ ] Optimize database queries
- [ ] Add CDN for frontend

### Monitoring

- [ ] Add Prometheus metrics
- [ ] Setup Grafana dashboards
- [ ] Implement error tracking (Sentry)
- [ ] Add APM (Application Performance Monitoring)
- [ ] Setup alerting (PagerDuty, Slack)

## Next Steps

1. ✅ **Test the integration** - Run `python test_integration.py`
2. ✅ **Verify all services** - Check health endpoints
3. 🔄 **Connect frontend** - Update frontend to call agent
4. 🔄 **Add authentication** - Implement user auth
5. 🔄 **Replace mock data** - Connect to real database
6. 🔄 **Deploy to production** - Setup CI/CD pipeline

## Support

- **Documentation:** See `docs/` folder
- **API Docs:** 
  - Banking API: http://localhost:8004/docs
  - Agent: http://localhost:8003/docs
- **Issues:** Open GitHub issue
- **Questions:** Check README.md

## Summary

✅ **Integration Complete!**

The system is fully integrated:
- Banking API provides data operations
- LangGraph Agent uses Claude for intelligence
- Agent calls Banking API via HTTP
- All services communicate via Docker network
- API key authentication in place
- Error handling implemented

**Just run:** `docker-compose up -d` and test with `python test_integration.py`
