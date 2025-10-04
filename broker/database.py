"""
FortressAI - Database Manager
SQLite-based RBAC storage with connection pooling
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "fortress.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
SEED_PATH = Path(__file__).parent / "seed_data.sql"


class DatabaseManager:
    """Manages SQLite database connections and queries"""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager"""
        self.db_path = db_path or str(DB_PATH)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist"""
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create tables from schema
        with self.get_connection() as conn:
            with open(SCHEMA_PATH, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize_seed_data(self):
        """Load seed data (for demo/testing)"""
        with self.get_connection() as conn:
            with open(SEED_PATH, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
        print("✅ Database seeded with demo data")
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Get user by API key hash
        
        Args:
            api_key: API key from X-API-Key header
            
        Returns:
            User dict or None if not found
        """
        # For demo, we're using simple string matching
        # In production, use proper hashing (bcrypt/argon2)
        api_key_hash = api_key
        
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE api_key_hash = ?",
                (api_key_hash,)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_user_permissions(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's role and permissions
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with role_id, allowed_apis, limits or None
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT role_id, allowed_apis, limits, expires_at
                FROM user_roles
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    "role_id": row["role_id"],
                    "allowed_apis": json.loads(row["allowed_apis"]),
                    "limits": json.loads(row["limits"]),
                    "expires_at": row["expires_at"]
                }
            return None
    
    def is_user_quarantined(self, user_id: str) -> bool:
        """
        Check if user is quarantined
        
        Args:
            user_id: User identifier
            
        Returns:
            True if quarantined, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM quarantined_users WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row["count"] > 0
    
    def quarantine_user(self, user_id: str, role_id: str, incident_id: str, reason: str):
        """
        Quarantine a user
        
        Args:
            user_id: User identifier
            role_id: User's role
            incident_id: Incident identifier
            reason: Reason for quarantine
        """
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO quarantined_users (user_id, role_id, incident_id, reason)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, role_id, incident_id, reason)
            )
            conn.commit()
        print(f"⚠️  User {user_id} quarantined: {reason}")
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (for admin/debugging)"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_roles(self) -> List[Dict[str, Any]]:
        """Get all user roles (for admin/debugging)"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT u.user_id, u.email, u.full_name, ur.role_id, ur.allowed_apis, ur.limits
                FROM users u
                JOIN user_roles ur ON u.user_id = ur.user_id
                ORDER BY ur.role_id, u.user_id
                """
            )
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                result.append({
                    "user_id": row["user_id"],
                    "email": row["email"],
                    "full_name": row["full_name"],
                    "role_id": row["role_id"],
                    "allowed_apis": json.loads(row["allowed_apis"]),
                    "limits": json.loads(row["limits"])
                })
            return result


# Global database instance
db = DatabaseManager()


# Convenience functions
def get_user_by_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Get user by API key"""
    return db.get_user_by_api_key(api_key)


def get_user_permissions(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user permissions"""
    return db.get_user_permissions(user_id)


def is_user_quarantined(user_id: str) -> bool:
    """Check if user is quarantined"""
    return db.is_user_quarantined(user_id)


def quarantine_user(user_id: str, role_id: str, incident_id: str, reason: str):
    """Quarantine a user"""
    db.quarantine_user(user_id, role_id, incident_id, reason)


def initialize_database():
    """Initialize database with seed data"""
    db.initialize_seed_data()


if __name__ == "__main__":
    # Test database setup
    print("🔧 Initializing FortressAI database...")
    initialize_database()
    
    print("\n📊 Sample users:")
    users = db.get_all_users()
    for user in users[:5]:  # Show first 5
        print(f"  - {user['full_name']} ({user['email']}) - API Key: {user['api_key_hash']}")
    
    print(f"\n✅ Database ready at: {DB_PATH}")
