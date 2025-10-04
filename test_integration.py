"""
Integration Test Script
Tests the complete flow: User → Agent → Banking API
"""
import asyncio
import httpx
import json
from datetime import datetime


# Configuration
AGENT_URL = "http://localhost:8003"
BANKING_API_URL = "http://localhost:8004"
BANKING_API_KEY = "BANKING-API-KEY-123"


async def test_banking_api():
    """Test Banking API directly."""
    print("\n" + "="*60)
    print("🏦 Testing Banking API")
    print("="*60)
    
    headers = {"X-API-Key": BANKING_API_KEY}
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("\n1. Health Check...")
        response = await client.get(f"{BANKING_API_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test 2: Get user accounts
        print("\n2. Get User Accounts...")
        response = await client.get(
            f"{BANKING_API_URL}/accounts/user123",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        accounts = response.json()
        print(f"   Found {len(accounts)} accounts")
        for acc in accounts:
            print(f"   - {acc['nickname']}: ${acc['balance']}")
        
        # Test 3: Get balance
        print("\n3. Get Account Balance...")
        response = await client.get(
            f"{BANKING_API_URL}/accounts/ACC001/balance",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        balance = response.json()
        print(f"   Balance: ${balance['balance']} {balance['currency']}")
        
        # Test 4: Get transactions
        print("\n4. Get Transactions...")
        response = await client.get(
            f"{BANKING_API_URL}/accounts/ACC001/transactions?limit=3",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        transactions = response.json()
        print(f"   Found {len(transactions)} transactions")
        for txn in transactions[:3]:
            print(f"   - {txn['description']}: ${txn['amount']}")
        
        # Test 5: Transfer funds
        print("\n5. Transfer Funds...")
        response = await client.post(
            f"{BANKING_API_URL}/transfer",
            headers=headers,
            json={
                "from_account": "ACC001",
                "to_account": "ACC002",
                "amount": 50.00,
                "description": "Test transfer"
            }
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        if result.get("success"):
            print(f"   ✅ Transfer successful: {result['transaction_id']}")
        else:
            print(f"   ❌ Transfer failed: {result.get('error')}")


async def test_agent():
    """Test LangGraph Agent."""
    print("\n" + "="*60)
    print("🤖 Testing LangGraph Agent")
    print("="*60)
    
    test_queries = [
        "What is my account balance?",
        "Show me my recent transactions",
        "Transfer $25 from checking to savings",
        "What are all my accounts?",
        "Give me a summary of my checking account"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Health check
        print("\n1. Agent Health Check...")
        try:
            response = await client.get(f"{AGENT_URL}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # Test queries
        for i, query in enumerate(test_queries, 2):
            print(f"\n{i}. Query: '{query}'")
            try:
                response = await client.post(
                    f"{AGENT_URL}/query",
                    json={"query": query, "user_id": "user123"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Response: {result['response'][:200]}...")
                    print(f"   📊 Messages: {result['message_count']}, Tools: {result['tool_calls_made']}")
                else:
                    print(f"   ❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")


async def test_full_integration():
    """Test complete integration flow."""
    print("\n" + "="*60)
    print("🔗 Full Integration Test")
    print("="*60)
    
    print("\nScenario: User checks balance, views transactions, and transfers money")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Check initial balance
        print("\n📍 Step 1: Check initial balance")
        response = await client.post(
            f"{AGENT_URL}/query",
            json={
                "query": "What's my checking account balance?",
                "user_id": "user123"
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   Agent: {result['response']}")
        
        # Step 2: View recent transactions
        print("\n📍 Step 2: View recent transactions")
        response = await client.post(
            f"{AGENT_URL}/query",
            json={
                "query": "Show me my last 3 transactions",
                "user_id": "user123"
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   Agent: {result['response'][:300]}...")
        
        # Step 3: Transfer money
        print("\n📍 Step 3: Transfer $100 to savings")
        response = await client.post(
            f"{AGENT_URL}/query",
            json={
                "query": "Transfer $100 from my checking to savings account",
                "user_id": "user123"
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   Agent: {result['response']}")
        
        # Step 4: Verify new balance
        print("\n📍 Step 4: Verify new balance")
        response = await client.post(
            f"{AGENT_URL}/query",
            json={
                "query": "What's my checking balance now?",
                "user_id": "user123"
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   Agent: {result['response']}")


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 FortressAI Integration Test Suite")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test Banking API
        await test_banking_api()
        
        # Test Agent
        await test_agent()
        
        # Test Full Integration
        await test_full_integration()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
