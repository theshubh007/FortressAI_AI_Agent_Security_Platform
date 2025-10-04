# 🤖 FortressAI Banking Agent (LangGraph + Claude)

Advanced banking AI agent built with **LangGraph** and **Anthropic Claude 3.5 Sonnet**.

## 🎯 Features

- **Multi-step reasoning** with LangGraph state management
- **Tool calling** for banking operations (balance, transactions, transfers)
- **Anthropic Claude 3.5 Sonnet** for intelligent responses
- **Safety-first** design with low temperature and validation
- **RESTful API** with FastAPI

## 🏗️ Architecture

```
User Query → LangGraph Agent → Claude LLM → Tool Selection → Banking Tools → Response
```

### Banking Tools

1. **get_account_balance** - Check account balances
2. **get_transaction_history** - View recent transactions
3. **transfer_funds** - Transfer money between accounts
4. **get_user_accounts** - List all user accounts

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd agent-langgraph
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 3. Run the Agent

```bash
uvicorn src.app:app --host 0.0.0.0 --port 8003 --reload
```

### 4. Test the Agent

```bash
# Health check
curl http://localhost:8003/health

# Query example
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is my account balance?", "user_id": "user123"}'
```

## 🐳 Docker Deployment

```bash
# Build
docker build -t fortress-agent-langgraph .

# Run
docker run -p 8003:8003 --env-file .env fortress-agent-langgraph
```

## 📊 Example Queries

- "What's my checking account balance?"
- "Show me my last 5 transactions"
- "Transfer $500 from ACC001 to ACC002"
- "List all my accounts"
- "How much did I spend on groceries this week?"

## 🔧 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | Your Anthropic API key (required) |
| `LLM_MODEL` | `claude-3-5-sonnet-20241022` | Claude model version |
| `LLM_TEMPERATURE` | `0.1` | Response randomness (0-1) |
| `LLM_MAX_TOKENS` | `1000` | Max response length |
| `AGENT_PORT` | `8003` | API server port |

## 🔒 Security Features

- Low temperature (0.1) for consistent, accurate responses
- Transfer limits ($10,000 max)
- Input validation on all tools
- Mock data for safe testing

## 📚 API Documentation

Interactive API docs available at: `http://localhost:8003/docs`

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test with curl
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Transfer $100 from checking to savings", "user_id": "user123"}'
```

## 🔗 Integration with FortressAI

This agent integrates with the FortressAI security stack:

1. Requests pass through **Gateway** (port 8000)
2. **Broker/Firewall** validates prompts (port 8001)
3. **Agent** processes queries (port 8003)
4. Responses logged and monitored

## 📝 Notes

- Currently uses **mock banking data** for demonstration
- Replace mock tools with real banking API calls for production
- Claude 3.5 Sonnet provides excellent reasoning for complex queries
- LangGraph enables multi-step workflows and tool orchestration
