-- FortressAI - Seed Data for Demo
-- 10 Banking Roles with 15 Sample Users

-- Clear existing data
DELETE FROM quarantined_users;
DELETE FROM user_roles;
DELETE FROM users;

-- ============================================
-- SAMPLE USERS (15 users across 10 roles)
-- ============================================

-- API Key Hashes (for demo, using simple hashes)
-- Real implementation should use bcrypt/argon2

INSERT INTO users (user_id, email, full_name, api_key_hash) VALUES
-- Customer Service Representatives
('alice.csr', 'alice@bank.com', 'Alice Johnson', 'CSR-KEY-001'),
('bob.csr', 'bob@bank.com', 'Bob Smith', 'CSR-KEY-002'),

-- Branch Manager
('charlie.manager', 'charlie@bank.com', 'Charlie Brown', 'MANAGER-KEY-001'),

-- Treasury Manager
('diana.treasury', 'diana@bank.com', 'Diana Prince', 'TREASURY-KEY-001'),

-- Fraud Investigator
('eve.fraud', 'eve@bank.com', 'Eve Martinez', 'FRAUD-KEY-001'),
('frank.fraud', 'frank@bank.com', 'Frank Castle', 'FRAUD-KEY-002'),

-- Compliance Officer
('grace.compliance', 'grace@bank.com', 'Grace Hopper', 'COMPLIANCE-KEY-001'),

-- Loan Officer
('henry.loans', 'henry@bank.com', 'Henry Ford', 'LOAN-KEY-001'),

-- CFO
('iris.cfo', 'iris@bank.com', 'Iris West', 'CFO-KEY-001'),

-- Payment Processor
('jack.payments', 'jack@bank.com', 'Jack Ryan', 'PAYMENT-KEY-001'),

-- Risk Analyst
('kate.risk', 'kate@bank.com', 'Kate Bishop', 'RISK-KEY-001'),

-- Customers (self-service)
('customer.john', 'john.doe@email.com', 'John Doe', 'CUSTOMER-KEY-001'),
('customer.jane', 'jane.smith@email.com', 'Jane Smith', 'CUSTOMER-KEY-002'),
('customer.mike', 'mike.wilson@email.com', 'Mike Wilson', 'CUSTOMER-KEY-003'),

-- Demo/Test user
('demo.user', 'demo@bank.com', 'Demo User', 'DEMO-KEY');

-- ============================================
-- USER ROLES & PERMISSIONS
-- ============================================

-- 1. Customer Service Representatives (Read-Only)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('alice.csr', 'csr', 
 '["internal://agent/account_inquiry", "internal://agent/transaction_history", "internal://agent/balance_check", "https://api.bank.com/accounts/read", "https://api.bank.com/transactions/read"]',
 '{"max_transfer_amount": 0, "daily_limit": 0, "max_requests_per_hour": 200}'),
 
('bob.csr', 'csr',
 '["internal://agent/account_inquiry", "internal://agent/transaction_history", "internal://agent/balance_check", "https://api.bank.com/accounts/read", "https://api.bank.com/transactions/read"]',
 '{"max_transfer_amount": 0, "daily_limit": 0, "max_requests_per_hour": 200}');

-- 2. Branch Manager (Limited Transfers)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('charlie.manager', 'branch_manager',
 '["internal://agent/account_inquiry", "internal://agent/initiate_transfer", "internal://agent/approve_loan", "internal://agent/override_limit", "internal://agent/transaction_history", "https://api.bank.com/accounts/*", "https://api.bank.com/loans/*", "https://api.bank.com/transactions/read"]',
 '{"max_transfer_amount": 50000, "daily_limit": 200000, "max_requests_per_hour": 100}');

-- 3. Treasury Manager (Large Transfers)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('diana.treasury', 'treasury_manager',
 '["internal://agent/initiate_transfer", "internal://agent/fx_execution", "internal://agent/cash_forecast", "internal://agent/liquidity_report", "internal://agent/account_inquiry", "https://api.bank.com/treasury/*", "https://api.bank.com/fx/*", "https://api.bank.com/accounts/read"]',
 '{"max_transfer_amount": 10000000, "daily_limit": 50000000, "max_requests_per_hour": 100}');

-- 4. Fraud Investigators (Freeze Accounts)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('eve.fraud', 'fraud_investigator',
 '["internal://agent/freeze_account", "internal://agent/fraud_alert", "internal://agent/transaction_analysis", "internal://agent/kyc_verify", "internal://agent/account_inquiry", "https://api.bank.com/fraud/*", "https://api.bank.com/accounts/read", "https://api.bank.com/transactions/read", "https://api.bank.com/sanctions/ofac"]',
 '{"max_transfer_amount": 0, "daily_limit": 0, "max_requests_per_hour": 500}'),
 
('frank.fraud', 'fraud_investigator',
 '["internal://agent/freeze_account", "internal://agent/fraud_alert", "internal://agent/transaction_analysis", "internal://agent/kyc_verify", "internal://agent/account_inquiry", "https://api.bank.com/fraud/*", "https://api.bank.com/accounts/read", "https://api.bank.com/transactions/read", "https://api.bank.com/sanctions/ofac"]',
 '{"max_transfer_amount": 0, "daily_limit": 0, "max_requests_per_hour": 500}');

-- 5. Compliance Officer (Audit Access)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('grace.compliance', 'compliance_officer',
 '["internal://agent/kyc_verify", "internal://agent/aml_check", "internal://agent/regulatory_report", "internal://agent/audit_trail", "internal://agent/account_inquiry", "https://api.bank.com/compliance/*", "https://api.bank.com/sanctions/*", "https://api.bank.com/kyc/*"]',
 '{"max_transfer_amount": 0, "daily_limit": 0, "max_requests_per_hour": 300}');

-- 6. Loan Officer (Credit Checks)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('henry.loans', 'loan_officer',
 '["internal://agent/credit_check", "internal://agent/loan_application", "internal://agent/approve_loan", "internal://agent/account_inquiry", "https://api.bank.com/loans/*", "https://api.bank.com/credit/*", "https://api.bank.com/accounts/read"]',
 '{"max_transfer_amount": 0, "daily_limit": 0, "max_loan_amount": 500000, "max_requests_per_hour": 150}');

-- 7. CFO (Full Access)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('iris.cfo', 'cfo',
 '["internal://agent/*", "https://api.bank.com/*"]',
 '{"max_transfer_amount": 100000000, "daily_limit": 500000000, "max_requests_per_hour": 1000}');

-- 8. Payment Processor (Batch Payments)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('jack.payments', 'payment_processor',
 '["internal://agent/initiate_transfer", "internal://agent/batch_payment", "internal://agent/payment_status", "internal://agent/account_inquiry", "https://api.bank.com/payments/*", "https://api.bank.com/accounts/read"]',
 '{"max_transfer_amount": 100000, "daily_limit": 1000000, "max_requests_per_hour": 500}');

-- 9. Risk Analyst (Portfolio Analysis)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('kate.risk', 'risk_analyst',
 '["internal://agent/risk_assessment", "internal://agent/portfolio_analysis", "internal://agent/stress_test", "internal://agent/account_inquiry", "https://api.bank.com/risk/*", "https://api.bank.com/accounts/read", "https://api.bank.com/transactions/read"]',
 '{"max_transfer_amount": 0, "daily_limit": 0, "max_requests_per_hour": 200}');

-- 10. Customers (Self-Service)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('customer.john', 'customer',
 '["internal://agent/account_inquiry", "internal://agent/transaction_history", "internal://agent/initiate_transfer", "internal://agent/bill_payment", "https://api.bank.com/accounts/read", "https://api.bank.com/transactions/read", "https://api.bank.com/payments/create"]',
 '{"max_transfer_amount": 5000, "daily_limit": 10000, "max_requests_per_hour": 50}'),
 
('customer.jane', 'customer',
 '["internal://agent/account_inquiry", "internal://agent/transaction_history", "internal://agent/initiate_transfer", "internal://agent/bill_payment", "https://api.bank.com/accounts/read", "https://api.bank.com/transactions/read", "https://api.bank.com/payments/create"]',
 '{"max_transfer_amount": 5000, "daily_limit": 10000, "max_requests_per_hour": 50}'),
 
('customer.mike', 'customer',
 '["internal://agent/account_inquiry", "internal://agent/transaction_history", "internal://agent/initiate_transfer", "internal://agent/bill_payment", "https://api.bank.com/accounts/read", "https://api.bank.com/transactions/read", "https://api.bank.com/payments/create"]',
 '{"max_transfer_amount": 5000, "daily_limit": 10000, "max_requests_per_hour": 50}');

-- Demo user (for testing - has CSR permissions)
INSERT INTO user_roles (user_id, role_id, allowed_apis, limits) VALUES
('demo.user', 'csr',
 '["internal://agent/account_inquiry", "internal://agent/transaction_history", "internal://agent/balance_check", "https://api.bank.com/accounts/read", "https://api.bank.com/transactions/read"]',
 '{"max_transfer_amount": 0, "daily_limit": 0, "max_requests_per_hour": 200}');
