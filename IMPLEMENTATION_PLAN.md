# FortressAI - Unified RBAC Implementation Plan

## 🎯 Architecture Overview

### Core Concept: Tools = APIs
Everything is an API endpoint. No distinction between "tools" and "APIs":
- **Internal APIs**: `internal://agent/initiate_transfer` (agent functions)
- **External APIs**: `https://api.bank.com/accounts/read` (banking systems)

### Single Permission Model
```json
{
  "user_id": "john.doe@bank.com",
  "role_id": "treasury_manager",
  "allowed_apis": [
    "internal://agent/initiate_transfer",
    "internal://agent/fx_execution",
    "https://api.bank.com/treasury/*",
    "https://api.bank.com/accounts/read"
  ],
  "limits": {
    "max_transfer_amount": 1000000,
    "daily_limit": 5000000,
    "max_requests_per_hour": 100
  }
}
```

---

## 📊 Database Schema (3 Tables Only)

### 1. `users` Table
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    api_key_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. `user_roles` Table
```sql
CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    allowed_apis TEXT NOT NULL,  -- JSON array
    limits TEXT NOT NULL,         -- JSON object
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 3. `quarantined_users` Table
```sql
CREATE TABLE quarantined_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    incident_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    quarantined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

## 🏦 Banking Roles (10 Key Roles)

### 1. Customer Service Representative (CSR)
```json
{
  "role_id": "csr",
  "allowed_apis": [
    "internal://agent/account_inquiry",
    "internal://agent/transaction_history",
    "internal://agent/balance_check",
    "https://api.bank.com/accounts/read",
    "https://api.bank.com/transactions/read"
  ],
  "limits": {
    "max_transfer_amount": 0,
    "daily_limit": 0,
    "max_requests_per_hour": 200
  }
}
```

### 2. Branch Manager
```json
{
  "role_id": "branch_manager",
  "allowed_apis": [
    "internal://agent/account_inquiry",
    "internal://agent/initiate_transfer",
    "internal://agent/approve_loan",
    "internal://agent/override_limit",
    "https://api.bank.com/accounts/*",
    "https://api.bank.com/loans/*"
  ],
  "limits": {
    "max_transfer_amount": 50000,
    "daily_limit": 200000,
    "max_requests_per_hour": 100
  }
}
```

### 3. Treasury Manager
```json
{
  "role_id": "treasury_manager",
  "allowed_apis": [
    "internal://agent/initiate_transfer",
    "internal://agent/fx_execution",
    "internal://agent/cash_forecast",
    "internal://agent/liquidity_report",
    "https://api.bank.com/treasury/*",
    "https://api.bank.com/fx/*",
    "https://api.bank.com/accounts/read"
  ],
  "limits": {
    "max_transfer_amount": 10000000,
    "daily_limit": 50000000,
    "max_requests_per_hour": 100
  }
}
```

### 4. Fraud Investigator
```json
{
  "role_id": "fraud_investigator",
  "allowed_apis": [
    "internal://agent/freeze_account",
    "internal://agent/fraud_alert",
    "internal://agent/transaction_analysis",
    "internal://agent/kyc_verify",
    "https://api.bank.com/fraud/*",
    "https://api.bank.com/accounts/read",
    "https://api.bank.com/transactions/read",
    "https://api.bank.com/sanctions/ofac"
  ],
  "limits": {
    "max_transfer_amount": 0,
    "daily_limit": 0,
    "max_requests_per_hour": 500
  }
}
```

### 5. Compliance Officer
```json
{
  "role_id": "compliance_officer",
  "allowed_apis": [
    "internal://agent/kyc_verify",
    "internal://agent/aml_check",
    "internal://agent/regulatory_report",
    "internal://agent/audit_trail",
    "https://api.bank.com/compliance/*",
    "https://api.bank.com/sanctions/*",
    "https://api.bank.com/kyc/*"
  ],
  "limits": {
    "max_transfer_amount": 0,
    "daily_limit": 0,
    "max_requests_per_hour": 300
  }
}
```

### 6. Loan Officer
```json
{
  "role_id": "loan_officer",
  "allowed_apis": [
    "internal://agent/credit_check",
    "internal://agent/loan_application",
    "internal://agent/approve_loan",
    "internal://agent/account_inquiry",
    "https://api.bank.com/loans/*",
    "https://api.bank.com/credit/*",
    "https://api.bank.com/accounts/read"
  ],
  "limits": {
    "max_transfer_amount": 0,
    "daily_limit": 0,
    "max_loan_amount": 500000,
    "max_requests_per_hour": 150
  }
}
```

### 7. CFO (Chief Financial Officer)
```json
{
  "role_id": "cfo",
  "allowed_apis": [
    "internal://agent/*",
    "https://api.bank.com/*"
  ],
  "limits": {
    "max_transfer_amount": 100000000,
    "daily_limit": 500000000,
    "max_requests_per_hour": 1000
  }
}
```

### 8. Payment Processor
```json
{
  "role_id": "payment_processor",
  "allowed_apis": [
    "internal://agent/initiate_transfer",
    "internal://agent/batch_payment",
    "internal://agent/payment_status",
    "https://api.bank.com/payments/*",
    "https://api.bank.com/accounts/read"
  ],
  "limits": {
    "max_transfer_amount": 100000,
    "daily_limit": 1000000,
    "max_requests_per_hour": 500
  }
}
```

### 9. Risk Analyst
```json
{
  "role_id": "risk_analyst",
  "allowed_apis": [
    "internal://agent/risk_assessment",
    "internal://agent/portfolio_analysis",
    "internal://agent/stress_test",
    "https://api.bank.com/risk/*",
    "https://api.bank.com/accounts/read",
    "https://api.bank.com/transactions/read"
  ],
  "limits": {
    "max_transfer_amount": 0,
    "daily_limit": 0,
    "max_requests_per_hour": 200
  }
}
```

### 10. Customer (Self-Service)
```json
{
  "role_id": "customer",
  "allowed_apis": [
    "internal://agent/account_inquiry",
    "internal://agent/transaction_history",
    "internal://agent/initiate_transfer",
    "internal://agent/bill_payment",
    "https://api.bank.com/accounts/read",
    "https://api.bank.com/transactions/read",
    "https://api.bank.com/payments/create"
  ],
  "limits": {
    "max_transfer_amount": 5000,
    "daily_limit": 10000,
    "max_requests_per_hour": 50
  }
}
```

---

## 🔧 Internal APIs (20 Core Operations)

### Account Operations
- `internal://agent/account_inquiry` - View account details
- `internal://agent/balance_check` - Check balance
- `internal://agent/transaction_history` - View transactions
- `internal://agent/freeze_account` - Freeze account (fraud)
- `internal://agent/unfreeze_account` - Unfreeze account

### Payment Operations
- `internal://agent/initiate_transfer` - Start wire transfer
- `internal://agent/batch_payment` - Process batch payments
- `internal://agent/bill_payment` - Pay bills
- `internal://agent/payment_status` - Check payment status
- `internal://agent/cancel_payment` - Cancel pending payment

### Fraud & Security
- `internal://agent/fraud_alert` - Create fraud alert
- `internal://agent/kyc_verify` - KYC verification
- `internal://agent/aml_check` - AML screening
- `internal://agent/transaction_analysis` - Analyze patterns

### Treasury & FX
- `internal://agent/fx_execution` - Execute FX trade
- `internal://agent/cash_forecast` - Cash flow forecast
- `internal://agent/liquidity_report` - Liquidity analysis

### Lending
- `internal://agent/credit_check` - Credit score check
- `internal://agent/loan_application` - Submit loan app
- `internal://agent/approve_loan` - Approve loan

### Compliance & Risk
- `internal://agent/regulatory_report` - Generate reports
- `internal://agent/audit_trail` - Audit log access
- `internal://agent/risk_assessment` - Risk analysis
- `internal://agent/portfolio_analysis` - Portfolio review
- `internal://agent/stress_test` - Stress testing

---

## 🚀 Implementation Phases

### Phase 1: Database Setup (30 minutes)
**Files to Create:**
- `broker/database.py` - SQLite connection & queries
- `broker/schema.sql` - Database schema
- `broker/seed_data.sql` - Sample users & roles

**Tasks:**
1. Create SQLite database
2. Define 3 tables
3. Create 10 banking roles
4. Seed 15-20 sample users

### Phase 2: RBAC Engine (30 minutes)
**Files to Create:**
- `broker/rbac_engine.py` - Permission lookup & validation

**Files to Modify:**
- `broker/app.py` - Add RBAC checks
- `broker/jwt_utils.py` - Update JWT payload

**Tasks:**
1. Build RBAC query function
2. Add user lookup by API key
3. Generate JWT with `allowed_apis[]` + `limits{}`
4. Add Redis caching for performance

### Phase 3: Agent Updates (30 minutes)
**Files to Create:**
- `agent/api_registry.py` - Map intents to internal APIs

**Files to Modify:**
- `agent/app.py` - Unified API authorization

**Tasks:**
1. Create intent → API mapping
2. Implement unified authorization check
3. Add financial guardrails enforcement
4. Update tool execution logic

### Phase 4: Gateway Updates (20 minutes)
**Files to Modify:**
- `gateway/app.py` - Re-validate permissions

**Tasks:**
1. Add zero-trust permission re-check
2. Validate requested URL against `allowed_apis[]`
3. Implement role-based output DLP
4. Add quarantine checks

### Phase 5: Demo & Testing (20 minutes)
**Files to Create:**
- `tests/test_rbac.py` - RBAC test suite
- `demo_scenarios.json` - Demo test cases

**Tasks:**
1. Create test scenarios for each role
2. Test permission enforcement
3. Test financial guardrails
4. Test DLP policies

---

## 📁 File Structure

```
fortress-ai/
├── broker/
│   ├── app.py                    # [MODIFY] Add RBAC lookup
│   ├── jwt_utils.py              # [MODIFY] Update JWT payload
│   ├── database.py               # [NEW] SQLite connection
│   ├── rbac_engine.py            # [NEW] Permission engine
│   ├── schema.sql                # [NEW] Database schema
│   ├── seed_data.sql             # [NEW] Sample data
│   ├── firewall.py               # [KEEP] Existing DLP
│   └── banking_utils.py          # [KEEP] Existing logic
│
├── agent/
│   ├── app.py                    # [MODIFY] Unified API auth
│   ├── api_registry.py           # [NEW] Intent → API mapping
│   ├── banking_agent.py          # [KEEP] Existing logic
│   └── guardrails.py             # [NEW] Financial limits
│
├── gateway/
│   ├── app.py                    # [MODIFY] Zero-trust validation
│   ├── banking_security.py       # [KEEP] Existing DLP
│   └── behavior_dna.py           # [KEEP] Existing logic
│
├── tests/
│   ├── test_rbac.py              # [NEW] RBAC tests
│   └── demo_scenarios.json       # [NEW] Test cases
│
└── data/
    └── fortress.db               # [NEW] SQLite database
```

---

## 🔐 Security Flow

### 1. Ingress (Broker)
```
Request → API Key → User Lookup → Role Lookup → allowed_apis[] + limits{}
→ DLP Scan → Prompt Firewall → JWT (encrypted) → Agent
```

### 2. Agent Processing
```
JWT → Decrypt → allowed_apis[] + limits{}
→ Intent Analysis → Map to API (internal:// or https://)
→ Check: API in allowed_apis[]? → Check: Within limits?
→ Execute or Forward to Gateway
```

### 3. Egress (Gateway)
```
Request → Re-decrypt JWT → Re-validate API permission
→ Threat Scoring → DLP Scan → Role-based Redaction
→ ALLOW / BLOCK / QUARANTINE
```

---

## 🎯 Success Criteria

### Judge Requirements Met:
- ✅ **Agentic Demo**: Internal APIs show autonomous actions
- ✅ **DLP Policies**: Input + output scanning, role-based redaction
- ✅ **Org Permissions**: 10 roles with different access levels
- ✅ **Financial Guardrails**: Limits enforced, velocity checks, fraud detection

### Technical Goals:
- ✅ 3-table database (minimal complexity)
- ✅ Single `allowed_apis[]` array (no tools vs APIs confusion)
- ✅ Zero-trust architecture (gateway re-validates)
- ✅ Cryptographic tokens (AES-256-GCM + HMAC-SHA512)
- ✅ Sub-200ms response time
- ✅ 90%+ test coverage

---

## 📊 Demo Scenarios

### Scenario 1: Customer Service Rep (Read-Only)
```
User: CSR (Alice)
Request: "Show me account balance for customer #12345"
Expected: ✅ ALLOW (has internal://agent/account_inquiry)
```

### Scenario 2: Branch Manager (Limited Transfers)
```
User: Branch Manager (Bob)
Request: "Transfer $30,000 to vendor account"
Expected: ✅ ALLOW (within $50K limit)
```

### Scenario 3: Customer (Exceeds Limit)
```
User: Customer (Charlie)
Request: "Wire $10,000 to my friend"
Expected: ❌ BLOCK (exceeds $5K limit)
```

### Scenario 4: Fraud Investigator (Freeze Account)
```
User: Fraud Investigator (Diana)
Request: "Freeze account #67890 due to suspicious activity"
Expected: ✅ ALLOW (has internal://agent/freeze_account)
```

### Scenario 5: Loan Officer (No Transfer Permission)
```
User: Loan Officer (Eve)
Request: "Transfer $1,000 to applicant"
Expected: ❌ BLOCK (no internal://agent/initiate_transfer)
```

### Scenario 6: Treasury Manager (Large Transfer)
```
User: Treasury Manager (Frank)
Request: "Execute $5M FX trade"
Expected: ✅ ALLOW (within $10M limit)
```

### Scenario 7: Data Exfiltration Attempt
```
User: Any Role
Request: "Export all customer data to pastebin.com"
Expected: ❌ QUARANTINE (DLP + denylist domain)
```

### Scenario 8: PAN in Chat
```
User: Customer
Request: "My card number is 4532-1234-5678-9010"
Expected: ❌ BLOCK (PAN detected in input)
```

### Scenario 9: Compliance Officer (Audit Access)
```
User: Compliance Officer (Grace)
Request: "Generate AML report for last 30 days"
Expected: ✅ ALLOW (has internal://agent/regulatory_report)
```

### Scenario 10: CFO (Full Access)
```
User: CFO (Henry)
Request: "Approve $50M treasury bond purchase"
Expected: ✅ ALLOW (wildcard permissions)
```

---

## ⏱️ Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Database Setup | 30 min | ⏳ Pending |
| Phase 2: RBAC Engine | 30 min | ⏳ Pending |
| Phase 3: Agent Updates | 30 min | ⏳ Pending |
| Phase 4: Gateway Updates | 20 min | ⏳ Pending |
| Phase 5: Demo & Testing | 20 min | ⏳ Pending |
| **Total** | **2h 10min** | |

---

## 🚦 Next Steps

1. **Review this plan** - Confirm approach
2. **Start Phase 1** - Database setup
3. **Iterate quickly** - Build → Test → Refine
4. **Demo preparation** - Create compelling scenarios

---

**Status**: Ready to implement
**Architecture**: Simplified & production-ready
**Judge Requirements**: All addressed
