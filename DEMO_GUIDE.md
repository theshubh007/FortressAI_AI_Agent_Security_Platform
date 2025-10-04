# FortressAI - Demo Guide for Judges

## 🎯 5-Minute Demo Script

### Opening (30 seconds)
**"FortressAI is a banking security platform with unified RBAC, DLP policies, and financial guardrails."**

---

## 📊 Part 1: RBAC Dashboard (2 minutes)

### Step 1: Show Overview
**Navigate to**: RBAC Dashboard tab

**Say**: 
> "We've implemented a unified RBAC system with 10 banking roles, each with different permissions and financial limits."

**Point out**:
- 10 role cards displayed
- 15 active users
- 25+ internal APIs
- Zero-trust architecture

### Step 2: Demonstrate Role Hierarchy

**Click**: Customer Service Rep (Blue card)

**Say**:
> "Customer Service Reps have read-only access. They can check balances but cannot transfer money."

**Show**:
- Transfer Limit: $0
- APIs: account_inquiry, transaction_history, balance_check

**Test**: Click "Small Transfer ($1,000)" scenario

**Result**: ❌ DENIED - "API not permitted"

**Say**:
> "As expected, CSRs cannot initiate transfers. This is enforced at the API level."

---

### Step 3: Show Financial Limits

**Click**: Branch Manager (Indigo card)

**Say**:
> "Branch Managers can approve transfers up to $50,000."

**Test 1**: Click "Small Transfer ($1,000)"
- **Result**: ✅ ALLOWED
- **Say**: "Within their $50K limit, so allowed."

**Test 2**: Click "Large Transfer ($100,000)"
- **Result**: ❌ DENIED - "Amount exceeds limit ($50,000)"
- **Say**: "Exceeds their limit, automatically blocked."

---

### Step 4: Show High-Value Access

**Click**: Treasury Manager (Purple card)

**Say**:
> "Treasury Managers handle corporate treasury with a $10 million limit."

**Test**: Click "Large Transfer ($100,000)"
- **Result**: ✅ ALLOWED
- **Say**: "Well within their $10M limit for corporate operations."

---

### Step 5: Show Specialized Roles

**Click**: Fraud Investigator (Red card)

**Say**:
> "Fraud Investigators can freeze accounts but cannot transfer money."

**Test 1**: Click "Freeze Account"
- **Result**: ✅ ALLOWED
- **Say**: "They have security operations access."

**Test 2**: Click "Small Transfer ($1,000)"
- **Result**: ❌ DENIED - "API not permitted"
- **Say**: "But they cannot move money - separation of duties."

---

### Step 6: Show Executive Access

**Click**: CFO (Amber card)

**Say**:
> "The CFO has wildcard access to all APIs with a $100 million limit."

**Show**:
- APIs: `internal://agent/*` and `https://api.bank.com/*`
- Transfer Limit: $100,000,000

**Test**: Click any scenario
- **Result**: ✅ ALLOWED
- **Say**: "Full access for executive oversight."

---

## 🔐 Part 2: Key Features (1 minute)

### Unified API Model

**Say**:
> "We use a unified API model - no distinction between 'tools' and 'APIs'. Everything is an API endpoint with an `internal://` or `https://` prefix."

**Show on screen**:
```
internal://agent/initiate_transfer
internal://agent/freeze_account
https://api.bank.com/accounts/read
```

**Say**:
> "This simplifies permission management - one array of allowed APIs per role."

---

### Financial Guardrails

**Say**:
> "Each role has financial limits enforced automatically:"

**Point to different roles**:
- Customer: $5,000
- Branch Manager: $50,000
- Payment Processor: $100,000
- Treasury Manager: $10,000,000
- CFO: $100,000,000

**Say**:
> "These limits are checked in real-time. No manual approval needed for amounts within limits."

---

### Zero-Trust Architecture

**Say**:
> "We implement zero-trust at three layers:"

1. **Broker (Ingress)**: Validates user, checks RBAC, issues JWT token
2. **Agent (Sandbox)**: Validates JWT, enforces capabilities
3. **Gateway (Egress)**: Re-validates permissions, checks for threats

**Say**:
> "Every request is validated at every layer. No implicit trust."

---

## 🛡️ Part 3: DLP & Security (1 minute)

### DLP Policies

**Say**:
> "We have comprehensive DLP policies already implemented:"

**List**:
- ✅ PAN (card number) detection in chat
- ✅ CVV detection
- ✅ SSN pattern detection
- ✅ API key/secret scanning
- ✅ Base64 blob detection (data exfiltration)
- ✅ Automatic quarantine on sensitive data

**Say**:
> "If a customer tries to share their card number in chat, it's blocked immediately."

---

### Organization-Based Permissions

**Say**:
> "We've implemented organization-based permissions with:"

**Show RBAC Dashboard**:
- 10 distinct roles
- Role-based API access
- Financial limits per role
- User assignments per role

**Say**:
> "Each role has exactly the permissions they need - principle of least privilege."

---

## 🎯 Part 4: Technical Implementation (30 seconds)

### Database

**Say**:
> "We use a minimal 3-table database:"

1. **users** - User accounts
2. **user_roles** - Permissions (JSONB for `allowed_apis[]` and `limits{}`)
3. **quarantined_users** - Security incidents

**Say**:
> "No complex joins, no 8-10 table schema. Simple and fast."

---

### Performance

**Say**:
> "Performance metrics:"

- User lookup: <5ms
- Permission check: <10ms
- Complete validation: <20ms
- Intent resolution: <5ms

**Say**:
> "Sub-20ms overhead for complete RBAC validation."

---

## 🎬 Closing (30 seconds)

### Summary

**Say**:
> "To summarize, FortressAI provides:"

1. ✅ **Agentic Demo**: 25+ internal APIs with intent resolution
2. ✅ **DLP Policies**: Comprehensive data loss prevention
3. ✅ **Org Permissions**: 10 banking roles with RBAC
4. ✅ **Financial Guardrails**: Automatic limit enforcement

**Say**:
> "All implemented with a unified API model, zero-trust architecture, and minimal database design."

---

## 🎯 Q&A Preparation

### Expected Questions:

**Q: How do you handle role changes?**
**A**: "We update the `user_roles` table. JWT tokens expire in 5 minutes, so new permissions take effect immediately on next request."

**Q: What about multi-factor authentication?**
**A**: "We have OTP verification implemented for high-value transactions. You can see it in the Customer Chat demo."

**Q: How do you prevent privilege escalation?**
**A**: "Three layers: Broker validates at ingress, Agent enforces in sandbox, Gateway re-validates at egress. Zero-trust means no layer trusts the previous one."

**Q: What about audit logs?**
**A**: "Every request is logged to JSONL files with user_id, role_id, API called, decision, and reason. Full audit trail."

**Q: Can you show a real attack scenario?**
**A**: "Yes, switch to Customer Chat tab and I'll demonstrate PAN detection and data exfiltration blocking."

---

## 🎨 Visual Highlights

### What Judges Will See:

1. **Professional UI**: Light theme, clean design, elegant
2. **10 Role Cards**: Color-coded, clear hierarchy
3. **Interactive Testing**: Click and see results immediately
4. **Real-time Validation**: ALLOW/DENY with reasons
5. **Financial Limits**: Clearly displayed per role
6. **API Permissions**: Complete list per role

---

## 📊 Key Metrics to Mention

- **10 Banking Roles**: Complete role hierarchy
- **15 Sample Users**: Ready to test
- **25+ Internal APIs**: Comprehensive coverage
- **3 Database Tables**: Minimal complexity
- **<20ms Validation**: High performance
- **91.7% Test Success**: 22/24 scenarios passing
- **Zero-Trust**: 3-layer validation

---

## 🎯 Demo Tips

### Do:
- ✅ Start with RBAC Dashboard (most impressive)
- ✅ Show role hierarchy (CSR → Manager → Treasury → CFO)
- ✅ Demonstrate financial limits (small vs large transfers)
- ✅ Test multiple scenarios per role
- ✅ Explain the "why" behind each decision

### Don't:
- ❌ Rush through the demo
- ❌ Skip the financial limits demonstration
- ❌ Forget to mention zero-trust architecture
- ❌ Ignore the unified API model explanation

---

## 🚀 Backup Demos

### If RBAC Dashboard Fails:

**Option 1**: Show the test suite
```bash
python tests/test_rbac_demo.py
```
- Shows all 24 scenarios
- Terminal output is clear
- Demonstrates same concepts

**Option 2**: Show the database
```bash
python broker/database.py
```
- Shows 15 users
- Shows role assignments
- Proves implementation

**Option 3**: Show the code
- Open `broker/rbac_engine.py`
- Show permission validation logic
- Explain wildcard matching

---

## 🎯 Success Criteria

### Judge Feedback Addressed:

1. ✅ **Agentic Demo**: Internal APIs show autonomous operations
2. ✅ **DLP Policies**: Comprehensive and role-based
3. ✅ **Org Permissions**: 10 roles with clear hierarchy
4. ✅ **Financial Guardrails**: Automatic enforcement

### Technical Excellence:

1. ✅ **Unified API Model**: Simpler than tools vs APIs
2. ✅ **Minimal Database**: 3 tables vs 8-10
3. ✅ **Zero-Trust**: 3-layer validation
4. ✅ **High Performance**: <20ms overhead

### Visual Impact:

1. ✅ **Professional UI**: Light theme, elegant design
2. ✅ **Interactive Demo**: Click and see results
3. ✅ **Clear Hierarchy**: Color-coded roles
4. ✅ **Real-time Feedback**: Immediate ALLOW/DENY

---

**Demo Duration**: 5 minutes  
**Preparation Time**: 2 minutes  
**Confidence Level**: High 🎯  
**Ready to Present**: Yes ✅
