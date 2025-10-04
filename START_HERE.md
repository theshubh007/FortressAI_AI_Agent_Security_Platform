# 🚀 START HERE - FortressAI Quick Setup

## What You're Building

A complete AI banking system with security:
- **Banking API** - Handles accounts, transactions, transfers
- **LangGraph Agent** - AI assistant powered by Claude
- **Security Stack** - Firewall, gateway, monitoring

## Prerequisites

✅ Docker & Docker Compose installed  
✅ Anthropic API key (get from: https://console.anthropic.com/)  
✅ 10 minutes of your time

## Setup (3 Steps)

### Step 1: Get Your API Key

1. Go to https://console.anthropic.com/
2. Sign up / Log in
3. Create an API key
4. Copy it (starts with `sk-ant-`)

### Step 2: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit and add your key
nano .env
```

Add this line:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Step 3: Start Everything

```bash
# Start all services
docker-compose up -d

# Wait 30 seconds for services to start
sleep 30

# Check status
docker-compose ps
```

## Test It Works

### Test 1: Banking API

```bash
curl -H "X-API-Key: BANKING-API-KEY-123" \
  http://localhost:8004/accounts/user123
```

Expected: List of 2 accounts

### Test 2: AI Agent

```bash
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is my account balance?",
    "user_id": "user123"
  }'
```

Expected: AI response with balance

### Test 3: Full Integration

```bash
python test_integration.py
```

Expected: All tests pass ✅

## What You Can Do Now

Try these queries with the agent:

```bash
# Check balance
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is my checking account balance?", "user_id": "user123"}'

# View transactions
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me my recent transactions", "user_id": "user123"}'

# Transfer money
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Transfer $100 from checking to savings", "user_id": "user123"}'

# Get summary
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Give me a summary of my accounts", "user_id": "user123"}'
```

## View the UI

Open in browser:
- **Banking API Docs**: http://localhost:8004/docs
- **Agent API Docs**: http://localhost:8003/docs
- **Frontend** (if running): http://localhost:3000

## Troubleshooting

### Services won't start?

```bash
# Check logs
docker-compose logs

# Restart
docker-compose down
docker-compose up -d
```

### API key error?

```bash
# Verify key is set
cat .env | grep ANTHROPIC_API_KEY

# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

### Connection refused?

```bash
# Wait for services to fully start
sleep 30

# Check if running
docker-compose ps

# All should show "Up"
```

## Next Steps

1. ✅ **Read the docs**
   - [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Complete integration guide
   - [docs/LANGGRAPH_AGENT.md](docs/LANGGRAPH_AGENT.md) - Agent documentation
   - [docs/BANKING_API.md](docs/BANKING_API.md) - API documentation

2. ✅ **Explore the code**
   - `banking-api/src/main.py` - Banking API endpoints
   - `agent-langgraph/src/agent.py` - LangGraph agent logic
   - `agent-langgraph/src/banking_client.py` - API client

3. ✅ **Customize**
   - Add new banking operations
   - Modify agent prompts
   - Connect real database
   - Add authentication

## Architecture Overview

```
┌─────────────────────────────────────────┐
│  User Query: "Check my balance"         │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  LangGraph Agent (Claude 3.5 Sonnet)    │
│  - Analyzes query                        │
│  - Selects tools                         │
│  - Formats response                      │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Banking API                             │
│  - GET /accounts/{user_id}               │
│  - GET /accounts/{id}/balance            │
│  - POST /transfer                        │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Mock Database                           │
│  - Accounts: ACC001, ACC002              │
│  - Transactions                          │
│  - Balances                              │
└─────────────────────────────────────────┘
```

## Support

- **Issues?** Check [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Questions?** Read the docs in `docs/` folder
- **Bugs?** Open a GitHub issue

## Summary

You now have:
- ✅ Banking API running on port 8004
- ✅ LangGraph Agent running on port 8003
- ✅ Claude AI integrated
- ✅ Full integration working
- ✅ Test suite passing

**Start building!** 🚀
