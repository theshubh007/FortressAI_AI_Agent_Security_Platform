# 🤖 LangGraph Banking Agent Documentation

## Overview

The **LangGraph Banking Agent** is an advanced AI agent built with **LangGraph** and **Anthropic Claude 3.5 Sonnet** for handling complex banking operations with multi-step reasoning.

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                   LangGraph Agent                        │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │   Agent      │─────▶│  Claude LLM  │                │
│  │   Node       │◀─────│  (3.5 Sonnet)│                │
│  └──────────────┘      └──────────────┘                │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                       │
│  │   Tool       │                                       │
│  │   Node       │                                       │
│  └──────────────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────────────────────────┐              │
│  │  Banking Tools                        │              │
│  │  • get_account_balance                │              │
│  │  • get_transaction_history            │              │
│  │  • transfer_funds                     │              │
│  │  • get_user_accounts                  │              │
│  └──────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

### State Management

```python
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]  # Conversation history
    user_id: str                      # User identifier
```

## Banking Tools

### 1. get_account_balance

Retrieves current balance for a specific account.

**Input:**
- `account_id` (str): Account identifier

**Output:**
```json
{
  "balance": 5420.50,
  "currency": "USD",
  "account_type": "checking"
}
```

### 2. get_transaction_history

Fetches recent transaction history.

**Input:**
- `account_id` (str): Account identifier
- `limit` (int): Number of transactions (default: 5)

**Output:**
```json
{
  "account_id": "ACC001",
  "transactions": [
    {
      "date": "2025-10-03",
      "description": "Grocery Store",
      "amount": -85.20
    }
  ]
}
```

### 3. transfer_funds

Transfers money between accounts with validation.

**Input:**
- `from_account` (str): Source account
- `to_account` (str): Destination account
- `amount` (float): Transfer amount

**Validation:**
- Amount must be positive
- Maximum transfer: $10,000

**Output:**
```json
{
  "success": true,
  "transaction_id": "TXN12345678",
  "from_account": "ACC001",
  "to_account": "ACC002",
  "amount": 500.00,
  "status": "completed"
}
```

### 4. get_user_accounts

Lists all accounts for a user.

**Input:**
- `user_id` (str): User identifier

**Output:**
```json
{
  "user_id": "user123",
  "accounts": [
    {
      "account_id": "ACC001",
      "type": "checking",
      "nickname": "Main Checking"
    }
  ]
}
```

## LangGraph Workflow

### Graph Structure

```
START
  │
  ▼
┌─────────┐
│  Agent  │ ◀──┐
│  Node   │    │
└─────────┘    │
  │            │
  ▼            │
Decision       │
  │            │
  ├─ Continue ─┤
  │            │
  ▼            │
┌─────────┐    │
│  Tool   │────┘
│  Node   │
└─────────┘
  │
  ▼ End
END
```

### Execution Flow

1. **User Query** → Agent receives query as HumanMessage
2. **Agent Node** → Claude analyzes query and decides on tool calls
3. **Decision** → Check if tool calls are needed
4. **Tool Node** → Execute banking tools if needed
5. **Loop** → Return to Agent with tool results
6. **End** → Final response when no more tools needed

## API Endpoints

### POST /query

Process a banking query.

**Request:**
```json
{
  "query": "What's my account balance?",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "response": "Your checking account (ACC001) has a balance of $5,420.50 USD.",
  "message_count": 4,
  "tool_calls_made": 2,
  "timestamp": "2025-10-04T12:00:00Z",
  "agent_type": "langgraph"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent": "LangGraph Banking Agent",
  "llm": "Anthropic Claude",
  "timestamp": "2025-10-04T12:00:00Z"
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | **Required** Anthropic API key |
| `LLM_MODEL` | `claude-3-5-sonnet-20241022` | Claude model version |
| `LLM_TEMPERATURE` | `0.1` | Response randomness (0-1) |
| `LLM_MAX_TOKENS` | `1000` | Maximum response length |
| `AGENT_PORT` | `8003` | API server port |

### Why Claude 3.5 Sonnet?

- **Superior reasoning** for complex banking queries
- **Excellent tool use** with reliable function calling
- **Safety features** aligned with banking security
- **200K context window** for long conversations
- **Fast response times** for better UX

## Example Queries

### Simple Balance Check
```
Query: "What's my checking account balance?"
Tools: get_user_accounts → get_account_balance
Response: "Your checking account has a balance of $5,420.50."
```

### Transaction Analysis
```
Query: "Show me my recent spending"
Tools: get_user_accounts → get_transaction_history
Response: "Here are your recent transactions: [list]"
```

### Fund Transfer
```
Query: "Transfer $500 from checking to savings"
Tools: get_user_accounts → transfer_funds
Response: "Successfully transferred $500. Transaction ID: TXN12345678"
```

### Complex Multi-Step
```
Query: "How much can I transfer to savings without going below $1000?"
Tools: get_account_balance → calculation → transfer_funds
Response: "You can transfer up to $4,420.50 while keeping $1,000 in checking."
```

## Security Features

### Input Validation
- Transfer amount limits ($10,000 max)
- Positive amount validation
- Account ID format checking

### LLM Configuration
- **Low temperature (0.1)** for consistent responses
- **Token limits** to prevent excessive usage
- **Tool binding** restricts available actions

### Integration with FortressAI
- Requests pass through **Gateway** security
- **Broker/Firewall** validates all prompts
- **Logging** for audit trails

## Testing

### Unit Tests

```bash
cd agent-langgraph
pytest tests/test_agent.py -v
```

### Integration Testing

```bash
# Start the agent
uvicorn src.app:app --port 8003

# Test query
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check my balance", "user_id": "user123"}'
```

### Load Testing

```bash
# Using Apache Bench
ab -n 100 -c 10 -p query.json -T application/json \
  http://localhost:8003/query
```

## Deployment

### Docker

```bash
# Build
docker build -t fortress-agent-langgraph ./agent-langgraph

# Run
docker run -p 8003:8003 \
  -e ANTHROPIC_API_KEY=your-key \
  fortress-agent-langgraph
```

### Docker Compose

```bash
# Start all services including LangGraph agent
docker-compose up -d agent-langgraph

# View logs
docker-compose logs -f agent-langgraph
```

## Monitoring

### Metrics to Track
- Query response time
- Tool call frequency
- Error rates
- Token usage
- User satisfaction

### Logging

```python
# Logs include:
- User queries
- Tool invocations
- LLM responses
- Error traces
```

## Future Enhancements

1. **Real Banking API Integration**
   - Replace mock data with actual banking APIs
   - Add authentication and authorization

2. **Advanced Features**
   - Bill payment scheduling
   - Investment advice
   - Fraud detection alerts
   - Budget analysis

3. **Multi-Language Support**
   - Spanish, French, German translations
   - Localized currency formatting

4. **Enhanced Security**
   - Multi-factor authentication
   - Transaction confirmation workflows
   - Anomaly detection

## Troubleshooting

### Common Issues

**Issue:** "ANTHROPIC_API_KEY not found"
**Solution:** Set the environment variable in `.env` file

**Issue:** "Tool call timeout"
**Solution:** Increase `LLM_MAX_TOKENS` or check API connectivity

**Issue:** "Transfer limit exceeded"
**Solution:** This is expected behavior for amounts > $10,000

## Support

For issues or questions:
- Check the [main README](../README.md)
- Review [Architecture docs](./ARCHITECTURE.md)
- Open an issue on GitHub
