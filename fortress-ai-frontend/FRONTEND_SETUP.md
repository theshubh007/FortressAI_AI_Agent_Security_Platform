# 🎨 Frontend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd fortress-ai-frontend
npm install
```

### 2. Configure Environment

The `.env` file is already configured with default values:

```bash
VITE_AGENT_URL=http://localhost:8003
VITE_BANKING_API_URL=http://localhost:8004
VITE_BANKING_API_KEY=BANKING-API-KEY-123
VITE_GATEWAY_URL=http://localhost:9000
```

### 3. Start Development Server

```bash
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### 4. Build for Production

```bash
npm run build
npm run preview
```

---

## Features Implemented

### ✅ Banking Chat Interface
- Real-time chat with Claude-powered agent
- Message history with timestamps
- Loading states and error handling
- Auto-scroll to latest message

### ✅ Account Sidebar
- Display all user accounts
- Real-time balance updates
- Account type indicators
- Click to select account

### ✅ Quick Actions
- Pre-defined banking queries
- One-click access to common tasks
- Visual action buttons

### ✅ Message Bubbles
- Different styles for user/agent
- Timestamp display
- Smooth animations

---

## Project Structure

```
fortress-ai-frontend/
├── src/
│   ├── components/
│   │   ├── Banking/
│   │   │   ├── BankingChat.jsx       # Main chat interface
│   │   │   ├── AccountSidebar.jsx    # Account list
│   │   │   ├── QuickActions.jsx      # Quick action buttons
│   │   │   └── MessageBubble.jsx     # Chat message display
│   │   ├── CustomerChat.jsx          # Updated wrapper
│   │   └── ...other components
│   ├── services/
│   │   ├── bankingAgent.js           # Agent API client
│   │   └── bankingAPI.js             # Banking API client
│   ├── App.jsx
│   └── main.jsx
├── .env                               # Environment config
└── package.json
```

---

## Usage

### Navigate to Banking Assistant

1. Open http://localhost:5173
2. Click "Banking Assistant" in the navigation
3. Start chatting!

### Try These Queries

- "What is my account balance?"
- "Show me my recent transactions"
- "Transfer $100 from checking to savings"
- "Give me a summary of my accounts"

### Use Quick Actions

Click any quick action button for instant queries:
- 💰 Check Balance
- 📊 Recent Transactions
- 💸 Transfer Money
- 📈 Account Summary

---

## API Integration

### Banking Agent (Port 8003)

```javascript
// Send query to agent
POST http://localhost:8003/query
{
  "query": "What is my balance?",
  "user_id": "user123"
}
```

### Banking API (Port 8004)

```javascript
// Get accounts
GET http://localhost:8004/accounts/user123
Headers: X-API-Key: BANKING-API-KEY-123

// Get balance
GET http://localhost:8004/accounts/ACC001/balance
Headers: X-API-Key: BANKING-API-KEY-123
```

---

## Troubleshooting

### Frontend won't start

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Can't connect to agent

1. Check agent is running: `curl http://localhost:8003/health`
2. Check CORS is enabled in agent
3. Verify `.env` has correct URLs

### Accounts not loading

1. Check Banking API: `curl -H "X-API-Key: BANKING-API-KEY-123" http://localhost:8004/health`
2. Verify API key in `.env`
3. Check browser console for errors

---

## Development Tips

### Hot Reload

Vite provides instant hot reload. Just save your files and see changes immediately.

### Component Development

Each component is self-contained and can be tested independently:

```javascript
// Test AccountSidebar
import AccountSidebar from './components/Banking/AccountSidebar'

<AccountSidebar userId="user123" />
```

### Styling

Uses Tailwind CSS. Modify styles directly in JSX:

```javascript
className="bg-blue-600 text-white rounded-lg px-4 py-2"
```

---

## Next Steps

1. ✅ Test the banking chat interface
2. ✅ Try all quick actions
3. ✅ Verify account sidebar loads
4. 🔄 Add more features (Phase 2)
5. 🔄 Implement dashboard view
6. 🔄 Add transaction display

---

## Support

- Check browser console for errors
- Verify all services are running
- Review API responses in Network tab
- Check `.env` configuration
