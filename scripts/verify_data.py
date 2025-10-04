"""Verify MongoDB data"""
from pymongo import MongoClient

MONGODB_URL = "mongodb+srv://kothiyashubham007_db_user:NU3gkfSvA5zchEEe@cluster0.kfahhtr.mongodb.net/"
client = MongoClient(MONGODB_URL)
db = client.banking_db

print("📊 Database Contents:")
print(f"  Roles: {db.roles.count_documents({})}")
print(f"  Users: {db.users.count_documents({})}")
print(f"  User-Roles: {db.user_roles.count_documents({})}")
print(f"  Customers: {db.customers.count_documents({})}")
print(f"  Accounts: {db.accounts.count_documents({})}")
print(f"  Transactions: {db.transactions.count_documents({})}")

print("\n👥 Sample Roles:")
for role in db.roles.find().sort("level", -1).limit(5):
    print(f"  - {role['role_name']} (Level {role['level']}) - {role['role_code']}")

print("\n👤 Sample Users:")
for user in db.users.find().limit(5):
    print(f"  - {user['full_name']} ({user['username']}) - {user['department']}")

print("\n💳 Sample Accounts:")
for account in db.accounts.find():
    print(f"  - {account['account_id']}: {account['nickname']} - ${account['balance']}")

client.close()
