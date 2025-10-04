"""
Populate MongoDB with test data for banking system with 17 roles
"""
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import random

# MongoDB connection
MONGODB_URL = "mongodb+srv://kothiyashubham007_db_user:NU3gkfSvA5zchEEe@cluster0.kfahhtr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "banking_db"

# 17 Banking Roles
ROLES_DATA = [
    {
        "role_id": "ROLE001",
        "role_name": "Super Admin",
        "role_code": "SUPER_ADMIN",
        "description": "Full system access and administration",
        "level": 10,
        "category": "administration",
        "permissions": ["*"],  # All permissions
        "status": "active"
    },
    {
        "role_id": "ROLE002",
        "role_name": "Bank Manager",
        "role_code": "BANK_MANAGER",
        "description": "Overall bank management and strategy",
        "level": 9,
        "category": "management",
        "permissions": [
            "accounts.view_all", "accounts.approve_all", "users.manage_all",
            "reports.view_all", "policies.manage", "branches.manage"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE003",
        "role_name": "Branch Manager",
        "role_code": "BRANCH_MANAGER",
        "description": "Manages branch operations and staff",
        "level": 8,
        "category": "management",
        "permissions": [
            "accounts.view_branch", "accounts.approve_large", "users.manage_branch",
            "reports.view_branch", "transactions.approve_large"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE004",
        "role_name": "Assistant Manager",
        "role_code": "ASSISTANT_MANAGER",
        "description": "Assists branch manager with operations",
        "level": 7,
        "category": "management",
        "permissions": [
            "accounts.view_branch", "accounts.approve_medium",
            "transactions.approve_medium", "reports.view_branch"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE005",
        "role_name": "Loan Officer",
        "role_code": "LOAN_OFFICER",
        "description": "Processes and approves loan applications",
        "level": 6,
        "category": "operations",
        "permissions": [
            "loans.view", "loans.create", "loans.approve_small",
            "customers.view", "credit.check"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE006",
        "role_name": "Teller",
        "role_code": "TELLER",
        "description": "Handles customer transactions at counter",
        "level": 3,
        "category": "operations",
        "permissions": [
            "transactions.create", "transactions.view_own",
            "accounts.view_basic", "cash.handle"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE007",
        "role_name": "Customer Service Representative",
        "role_code": "CUSTOMER_SERVICE_REP",
        "description": "Provides customer support and assistance",
        "level": 3,
        "category": "customer_service",
        "permissions": [
            "customers.view", "accounts.view_basic",
            "transactions.view_basic", "support.create_ticket"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE008",
        "role_name": "Account Manager",
        "role_code": "ACCOUNT_MANAGER",
        "description": "Manages customer relationships and accounts",
        "level": 5,
        "category": "customer_service",
        "permissions": [
            "customers.view_assigned", "accounts.view_assigned",
            "accounts.update", "products.recommend"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE009",
        "role_name": "Compliance Officer",
        "role_code": "COMPLIANCE_OFFICER",
        "description": "Ensures regulatory compliance",
        "level": 7,
        "category": "compliance",
        "permissions": [
            "compliance.view_all", "audit.view_all", "reports.compliance",
            "kyc.review", "aml.investigate"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE010",
        "role_name": "Auditor",
        "role_code": "AUDITOR",
        "description": "Conducts internal audits",
        "level": 7,
        "category": "compliance",
        "permissions": [
            "audit.view_all", "audit.create_report", "logs.view_all",
            "accounts.audit", "transactions.audit"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE011",
        "role_name": "Risk Analyst",
        "role_code": "RISK_ANALYST",
        "description": "Analyzes and manages risk",
        "level": 6,
        "category": "risk",
        "permissions": [
            "risk.view_all", "risk.assess", "reports.risk",
            "customers.risk_profile", "transactions.flag_suspicious"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE012",
        "role_name": "Fraud Investigator",
        "role_code": "FRAUD_INVESTIGATOR",
        "description": "Investigates fraud and suspicious activity",
        "level": 6,
        "category": "security",
        "permissions": [
            "fraud.investigate", "transactions.view_all", "accounts.freeze",
            "customers.flag", "reports.fraud"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE013",
        "role_name": "IT Administrator",
        "role_code": "IT_ADMIN",
        "description": "Manages technical systems",
        "level": 8,
        "category": "technology",
        "permissions": [
            "system.manage", "users.manage_technical", "logs.view_system",
            "backup.manage", "security.configure"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE014",
        "role_name": "Operations Manager",
        "role_code": "OPERATIONS_MANAGER",
        "description": "Oversees daily operations",
        "level": 7,
        "category": "operations",
        "permissions": [
            "operations.view_all", "operations.manage", "staff.schedule",
            "reports.operations", "processes.optimize"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE015",
        "role_name": "Treasury Manager",
        "role_code": "TREASURY_MANAGER",
        "description": "Manages treasury and liquidity",
        "level": 8,
        "category": "finance",
        "permissions": [
            "treasury.manage", "liquidity.monitor", "investments.manage",
            "reports.treasury", "cash.manage_large"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE016",
        "role_name": "Credit Analyst",
        "role_code": "CREDIT_ANALYST",
        "description": "Evaluates creditworthiness",
        "level": 5,
        "category": "risk",
        "permissions": [
            "credit.analyze", "credit.score", "loans.review",
            "customers.credit_history", "reports.credit"
        ],
        "status": "active"
    },
    {
        "role_id": "ROLE017",
        "role_name": "Back Office Clerk",
        "role_code": "BACK_OFFICE_CLERK",
        "description": "Handles administrative tasks",
        "level": 2,
        "category": "operations",
        "permissions": [
            "documents.process", "data.entry", "records.maintain",
            "reports.generate_basic"
        ],
        "status": "active"
    }
]

# Sample users for each role
USERS_DATA = [
    {"user_id": "USR001", "username": "admin", "full_name": "System Administrator", "role_code": "SUPER_ADMIN", "department": "IT"},
    {"user_id": "USR002", "username": "bank.manager", "full_name": "Robert Johnson", "role_code": "BANK_MANAGER", "department": "Management"},
    {"user_id": "USR003", "username": "branch.mgr1", "full_name": "Sarah Williams", "role_code": "BRANCH_MANAGER", "department": "Branch Operations"},
    {"user_id": "USR004", "username": "asst.mgr1", "full_name": "Michael Brown", "role_code": "ASSISTANT_MANAGER", "department": "Branch Operations"},
    {"user_id": "USR005", "username": "loan.officer1", "full_name": "Jennifer Davis", "role_code": "LOAN_OFFICER", "department": "Lending"},
    {"user_id": "USR006", "username": "teller1", "full_name": "David Miller", "role_code": "TELLER", "department": "Customer Service"},
    {"user_id": "USR007", "username": "csr1", "full_name": "Emily Wilson", "role_code": "CUSTOMER_SERVICE_REP", "department": "Customer Service"},
    {"user_id": "USR008", "username": "acct.mgr1", "full_name": "James Moore", "role_code": "ACCOUNT_MANAGER", "department": "Relationship Management"},
    {"user_id": "USR009", "username": "compliance1", "full_name": "Patricia Taylor", "role_code": "COMPLIANCE_OFFICER", "department": "Compliance"},
    {"user_id": "USR010", "username": "auditor1", "full_name": "Christopher Anderson", "role_code": "AUDITOR", "department": "Internal Audit"},
    {"user_id": "USR011", "username": "risk.analyst1", "full_name": "Linda Thomas", "role_code": "RISK_ANALYST", "department": "Risk Management"},
    {"user_id": "USR012", "username": "fraud.inv1", "full_name": "Daniel Jackson", "role_code": "FRAUD_INVESTIGATOR", "department": "Security"},
    {"user_id": "USR013", "username": "it.admin1", "full_name": "Barbara White", "role_code": "IT_ADMIN", "department": "IT"},
    {"user_id": "USR014", "username": "ops.mgr1", "full_name": "Richard Harris", "role_code": "OPERATIONS_MANAGER", "department": "Operations"},
    {"user_id": "USR015", "username": "treasury1", "full_name": "Susan Martin", "role_code": "TREASURY_MANAGER", "department": "Treasury"},
    {"user_id": "USR016", "username": "credit.analyst1", "full_name": "Joseph Thompson", "role_code": "CREDIT_ANALYST", "department": "Credit"},
    {"user_id": "USR017", "username": "clerk1", "full_name": "Karen Garcia", "role_code": "BACK_OFFICE_CLERK", "department": "Back Office"},
]

# Sample customers
CUSTOMERS_DATA = [
    {
        "customer_id": "CUST001",
        "customer_type": "individual",
        "personal_info": {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": datetime(1985, 5, 15),
            "gender": "male",
            "nationality": "US"
        },
        "contact_info": {
            "email": "john.doe@email.com",
            "phone": "+1-555-0123",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            }
        },
        "customer_segment": "premium",
        "status": "active"
    },
    {
        "customer_id": "CUST002",
        "customer_type": "individual",
        "personal_info": {
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": datetime(1990, 8, 22),
            "gender": "female",
            "nationality": "US"
        },
        "contact_info": {
            "email": "jane.smith@email.com",
            "phone": "+1-555-0124",
            "address": {
                "street": "456 Oak Ave",
                "city": "Los Angeles",
                "state": "CA",
                "zip": "90001",
                "country": "USA"
            }
        },
        "customer_segment": "basic",
        "status": "active"
    }
]

# Sample accounts
ACCOUNTS_DATA = [
    {
        "account_id": "ACC001",
        "account_number": "1234567890",
        "customer_id": "CUST001",
        "account_type": "checking",
        "nickname": "Main Checking",
        "balance": 5420.50,
        "currency": "USD",
        "status": "active",
        "opened_date": datetime(2023, 1, 15)
    },
    {
        "account_id": "ACC002",
        "account_number": "1234567891",
        "customer_id": "CUST001",
        "account_type": "savings",
        "nickname": "Emergency Fund",
        "balance": 12350.75,
        "currency": "USD",
        "status": "active",
        "opened_date": datetime(2023, 1, 15)
    },
    {
        "account_id": "ACC003",
        "account_number": "1234567892",
        "customer_id": "CUST002",
        "account_type": "checking",
        "nickname": "Personal Checking",
        "balance": 2150.00,
        "currency": "USD",
        "status": "active",
        "opened_date": datetime(2024, 3, 10)
    }
]

# Sample transactions
def generate_transactions():
    transactions = []
    categories = ["groceries", "utilities", "dining", "shopping", "gas", "entertainment"]
    
    for i in range(20):
        days_ago = random.randint(1, 30)
        amount = round(random.uniform(-200, -10), 2)
        
        transactions.append({
            "transaction_id": f"TXN{str(i+1).zfill(3)}",
            "account_id": "ACC001",
            "transaction_type": "debit",
            "category": random.choice(categories),
            "amount": amount,
            "description": f"Purchase at {random.choice(['Store', 'Restaurant', 'Gas Station'])}",
            "status": "completed",
            "timestamp": datetime.now() - timedelta(days=days_ago),
            "channel": random.choice(["pos", "online", "atm"])
        })
    
    return transactions


def populate_database():
    """Populate MongoDB with test data."""
    
    print("🔗 Connecting to MongoDB Atlas...")
    client = MongoClient(MONGODB_URL, server_api=ServerApi('1'))
    db = client[DATABASE_NAME]
    
    try:
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas\n")
        
        # 1. Insert Roles
        print("📝 Inserting 17 banking roles...")
        roles_collection = db.roles
        roles_collection.delete_many({})  # Clear existing
        result = roles_collection.insert_many(ROLES_DATA)
        print(f"   ✅ Inserted {len(result.inserted_ids)} roles\n")
        
        # 2. Insert Users
        print("👥 Inserting users...")
        users_collection = db.users
        users_collection.delete_many({})
        
        users_to_insert = []
        for user in USERS_DATA:
            users_to_insert.append({
                **user,
                "email": f"{user['username']}@bank.com",
                "password_hash": "$2b$12$dummy_hash",  # In production, use real bcrypt
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "mfa_enabled": False
            })
        
        result = users_collection.insert_many(users_to_insert)
        print(f"   ✅ Inserted {len(result.inserted_ids)} users\n")
        
        # 3. Insert User-Role mappings
        print("🔗 Creating user-role mappings...")
        user_roles_collection = db.user_roles
        user_roles_collection.delete_many({})
        
        user_roles = []
        for user in USERS_DATA:
            # Find role_id for this user's role_code
            role = next((r for r in ROLES_DATA if r['role_code'] == user['role_code']), None)
            if role:
                user_roles.append({
                    "user_id": user['user_id'],
                    "role_id": role['role_id'],
                    "assigned_at": datetime.now(),
                    "status": "active"
                })
        
        result = user_roles_collection.insert_many(user_roles)
        print(f"   ✅ Created {len(result.inserted_ids)} user-role mappings\n")
        
        # 4. Insert Customers
        print("👤 Inserting customers...")
        customers_collection = db.customers
        customers_collection.delete_many({})
        
        customers_to_insert = []
        for customer in CUSTOMERS_DATA:
            customers_to_insert.append({
                **customer,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
        
        result = customers_collection.insert_many(customers_to_insert)
        print(f"   ✅ Inserted {len(result.inserted_ids)} customers\n")
        
        # 5. Insert Accounts
        print("💳 Inserting accounts...")
        accounts_collection = db.accounts
        accounts_collection.delete_many({})
        
        accounts_to_insert = []
        for account in ACCOUNTS_DATA:
            accounts_to_insert.append({
                **account,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
        
        result = accounts_collection.insert_many(accounts_to_insert)
        print(f"   ✅ Inserted {len(result.inserted_ids)} accounts\n")
        
        # 6. Insert Transactions
        print("💸 Inserting transactions...")
        transactions_collection = db.transactions
        transactions_collection.delete_many({})
        
        transactions = generate_transactions()
        result = transactions_collection.insert_many(transactions)
        print(f"   ✅ Inserted {len(result.inserted_ids)} transactions\n")
        
        # 7. Create Indexes
        print("🔍 Creating indexes...")
        
        # Users indexes
        users_collection.create_index("user_id", unique=True)
        users_collection.create_index("username", unique=True)
        print("   ✅ Users indexes created")
        
        # Roles indexes
        roles_collection.create_index("role_id", unique=True)
        roles_collection.create_index("role_code", unique=True)
        print("   ✅ Roles indexes created")
        
        # Accounts indexes
        accounts_collection.create_index("account_id", unique=True)
        accounts_collection.create_index("customer_id")
        print("   ✅ Accounts indexes created")
        
        # Transactions indexes
        transactions_collection.create_index("transaction_id", unique=True)
        transactions_collection.create_index([("account_id", 1), ("timestamp", -1)])
        print("   ✅ Transactions indexes created\n")
        
        # Summary
        print("=" * 60)
        print("✅ DATABASE POPULATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   • Roles: {len(ROLES_DATA)}")
        print(f"   • Users: {len(USERS_DATA)}")
        print(f"   • Customers: {len(CUSTOMERS_DATA)}")
        print(f"   • Accounts: {len(ACCOUNTS_DATA)}")
        print(f"   • Transactions: {len(transactions)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()
        print("\n🔌 Connection closed")


if __name__ == "__main__":
    populate_database()
