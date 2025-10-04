# FortressAI - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Docker Desktop running
- Node.js installed
- Terminal/Command Prompt

---

## Step 1: Start Backend (2 minutes)

```bash
# From project root
docker-compose up --build
```

**Wait for**:
```
✅ Broker ready on port 8001
✅ Agent ready on port 7000
✅ Gateway ready on port 9000
```

---

## Step 2: Start Frontend (1 minute)

**Open new terminal:**

```bash
cd fortress-ai-frontend
npm install
npm run dev
```

**Wait for**:
```
✅ Local: http://localhost:5173
```

---

## Step 3: Open Browser (30 seconds)

**Navigate to**: http://localhost:5173

**You should see**:
- Light theme UI
- FortressAI header
- 4 navigation tabs

---

## Step 4: Explore RBAC Dashboard (1 minute)

**Click**: "RBAC Dashboard" tab

**You'll see**:
- 10 banking role cards
- Stats: 10 roles, 15 users, 25+ APIs
- Color-coded roles

**Try this**:
1. Click "Customer Service Rep" (blue card)
2. Scroll down to "Test Scenarios"
3. Click "Small Transfer ($1,000)"
4. See result: ❌ DENIED - "API not permitted"

**Try this**:
1. Click "Branch Manager" (indigo card)
2. Click "Small Transfer ($1,000)"
3. See result: ✅ ALLOWED
4. Click "Large Transfer ($100,000)"
5. See result: ❌ DENIED - "Amount exceeds limit ($50,000)"

---

## Step 5: Test Backend Directly (30 seconds)

**Optional - verify backend is working:**

```bash
# Test RBAC engine
python broker/rbac_engine.py

# Run full demo
python tests/test_rbac_demo.py
```

**Expected output**:
```
✅ 22/24 scenarios passing (91.7%)
```

---

## 🎯 Quick Demo Script

### For Judges (2 minutes):

1. **Show RBAC Dashboard**
   - "We have 10 banking roles with different permissions"

2. **Click CSR**
   - "Customer Service Reps are read-only"
   - Test transfer → DENIED

3. **Click Branch Manager**
   - "Branch Managers can transfer up to $50K"
   - Test $30K → ALLOWED
   - Test $100K → DENIED (exceeds limit)

4. **Click Treasury Manager**
   - "Treasury handles large corporate transfers up to $10M"
   - Test $100K → ALLOWED

5. **Click CFO**
   - "CFO has full access with wildcard permissions"
   - Show `internal://agent/*`

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Check if ports are in use
netstat -ano | findstr :8001
netstat -ano | findstr :9000

# Kill processes if needed
taskkill /PID <process_id> /F

# Restart Docker Desktop
```

### Frontend won't start?
```bash
# Clear node_modules
cd fortress-ai-frontend
rmdir /s /q node_modules
npm install
npm run dev
```

### Database not initialized?
```bash
# Initialize manually
python broker/database.py
```

### Tests failing?
```bash
# Check Python path
python --version  # Should be 3.11+

# Install dependencies
pip install -r broker/requirements.txt
```

---

## 📊 What to Show Judges

### 1. RBAC Dashboard (Most Impressive)
- 10 roles displayed
- Interactive testing
- Real-time ALLOW/DENY
- Financial limits enforced

### 2. Test Suite (Backup)
```bash
python tests/test_rbac_demo.py
```
- Shows 24 scenarios
- 91.7% passing
- Clear output

### 3. Database (Technical Proof)
```bash
python broker/database.py
```
- Shows 15 users
- Shows role assignments
- Proves implementation

---

## 🎯 Key Points to Mention

1. **Unified API Model**
   - No distinction between tools and APIs
   - Everything is `internal://` or `https://`

2. **Financial Guardrails**
   - Automatic limit enforcement
   - No manual approval needed
   - Different limits per role

3. **Zero-Trust Architecture**
   - 3-layer validation
   - Every request checked
   - No implicit trust

4. **Minimal Database**
   - 3 tables only
   - JSONB for flexibility
   - <20ms validation

---

## 📁 Important Files

### Backend:
- `broker/database.py` - Database manager
- `broker/rbac_engine.py` - Permission engine
- `broker/seed_data.sql` - Sample data
- `tests/test_rbac_demo.py` - Test suite

### Frontend:
- `fortress-ai-frontend/src/App.jsx` - Main app
- `fortress-ai-frontend/src/components/RBACDashboard.jsx` - RBAC UI

### Documentation:
- `DEMO_GUIDE.md` - 5-minute demo script
- `COMPLETE_IMPLEMENTATION_SUMMARY.md` - Full summary

---

## ✅ Pre-Demo Checklist

**5 Minutes Before Demo:**

- [ ] Backend running (docker-compose up)
- [ ] Frontend running (npm run dev)
- [ ] Browser open to http://localhost:5173
- [ ] RBAC Dashboard tab selected
- [ ] Test one scenario to verify it works
- [ ] Have backup terminal ready for test suite
- [ ] Review DEMO_GUIDE.md

---

## 🎉 You're Ready!

**Everything is set up and working.**

**Demo Flow:**
1. Show RBAC Dashboard (2 min)
2. Test different roles (1 min)
3. Explain architecture (1 min)
4. Q&A (1 min)

**Total**: 5 minutes

**Confidence**: High 🎯

---

## 📞 Emergency Contacts

**If something breaks:**

1. **Restart everything**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **Use test suite as backup**
   ```bash
   python tests/test_rbac_demo.py
   ```

3. **Show the code**
   - Open `broker/rbac_engine.py`
   - Explain the logic
   - Judges will understand

---

**Status**: Ready to Demo ✅  
**Time to Start**: Now 🚀  
**Good Luck**: You've got this! 💪
