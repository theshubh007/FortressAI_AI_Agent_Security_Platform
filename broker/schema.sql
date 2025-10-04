-- FortressAI - Unified RBAC Database Schema
-- 3 tables only: users, user_roles, quarantined_users

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    api_key_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. User roles table (contains allowed_apis and limits)
CREATE TABLE IF NOT EXISTS user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    allowed_apis TEXT NOT NULL,  -- JSON array of API endpoints
    limits TEXT NOT NULL,         -- JSON object with financial limits
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 3. Quarantined users table
CREATE TABLE IF NOT EXISTS quarantined_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    incident_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    quarantined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_quarantined_users_user_id ON quarantined_users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_api_key_hash ON users(api_key_hash);
