#!/bin/bash
# Integration test script for FortressAI Banking System

echo "🧪 FortressAI Banking Integration Tests"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BANKING_API="http://localhost:8004"
AGENT_API="http://localhost:8003"
API_KEY="BANKING-API-KEY-123"

# Test counter
PASSED=0
FAILED=0

# Helper function
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local data=$4
    local headers=$5
    
    echo -n "Testing: $name... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -H "$headers" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" "$url" -H "$headers")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED (HTTP $http_code)${NC}"
        echo "  Response: $body"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "1️⃣  Testing Banking API"
echo "------------------------"

test_endpoint "Banking API Health" "$BANKING_API/health"
test_endpoint "Banking API Root" "$BANKING_API/"
test_endpoint "Get User Accounts" "$BANKING_API/accounts/user123" "GET" "" "X-API-Key: $API_KEY"
test_endpoint "Get Account Balance" "$BANKING_API/accounts/ACC001/balance" "GET" "" "X-API-Key: $API_KEY"
test_endpoint "Get Transactions" "$BANKING_API/accounts/ACC001/transactions?limit=3" "GET" "" "X-API-Key: $API_KEY"
test_endpoint "Get Account Summary" "$BANKING_API/accounts/ACC001/summary" "GET" "" "X-API-Key: $API_KEY"

echo ""
echo "2️⃣  Testing Fund Transfer"
echo "------------------------"

transfer_data='{"from_account":"ACC001","to_account":"ACC002","amount":50.00,"description":"Test transfer"}'
test_endpoint "Transfer Funds" "$BANKING_API/transfer" "POST" "$transfer_data" "X-API-Key: $API_KEY"

echo ""
echo "3️⃣  Testing LangGraph Agent"
echo "------------------------"

test_endpoint "Agent Health" "$AGENT_API/health"
test_endpoint "Agent Root" "$AGENT_API/"
test_endpoint "Agent Metrics" "$AGENT_API/metrics"

echo ""
echo "4️⃣  Testing Agent Queries"
echo "------------------------"

query1='{"query":"What is my account balance?","user_id":"user123"}'
test_endpoint "Balance Query" "$AGENT_API/query" "POST" "$query1"

query2='{"query":"Show me my recent transactions","user_id":"user123"}'
test_endpoint "Transaction Query" "$AGENT_API/query" "POST" "$query2"

query3='{"query":"List all my accounts","user_id":"user123"}'
test_endpoint "Account List Query" "$AGENT_API/query" "POST" "$query3"

echo ""
echo "5️⃣  Testing Error Handling"
echo "------------------------"

test_endpoint "Invalid Account" "$BANKING_API/accounts/ACC999/balance" "GET" "" "X-API-Key: $API_KEY" || true
test_endpoint "Invalid API Key" "$BANKING_API/accounts/user123" "GET" "" "X-API-Key: wrong-key" || true

echo ""
echo "========================================"
echo "📊 Test Results"
echo "========================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
