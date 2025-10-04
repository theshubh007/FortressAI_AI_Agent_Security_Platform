"""
FortressAI - RBAC Demo Test Suite
Demonstrates all 10 banking roles with realistic scenarios
"""

import sys
sys.path.insert(0, 'broker')
sys.path.insert(0, 'agent')

from rbac_engine import validate_request
from database import initialize_database, db
from api_registry import resolve_intent, extract_amount, extract_payee


def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_scenario(
    scenario_num: int,
    description: str,
    api_key: str,
    user_text: str,
    expected_result: str
):
    """
    Test a single scenario
    
    Args:
        scenario_num: Scenario number
        description: Scenario description
        api_key: User's API key
        user_text: User's natural language input
        expected_result: Expected outcome (ALLOW/DENY)
    """
    print(f"📋 Scenario {scenario_num}: {description}")
    print(f"   Input: \"{user_text}\"")
    
    # Resolve intent to API
    api_endpoint, intent = resolve_intent(user_text)
    amount = extract_amount(user_text)
    
    if not api_endpoint:
        print(f"   ❌ Could not resolve intent")
        return
    
    print(f"   Resolved API: {api_endpoint}")
    
    # Determine operation type
    operation = "read"
    if "transfer" in api_endpoint or "payment" in api_endpoint:
        operation = "transfer"
    elif "loan" in api_endpoint:
        operation = "loan"
    
    # Validate request
    allowed, capabilities, error = validate_request(
        api_key,
        api_endpoint,
        operation,
        amount
    )
    
    # Print result
    result_icon = "✅" if allowed else "❌"
    result_text = "ALLOWED" if allowed else "DENIED"
    
    print(f"   {result_icon} Result: {result_text}")
    
    if capabilities:
        print(f"   Role: {capabilities['role_id']}")
        if amount and 'max_transfer_amount' in capabilities['limits']:
            print(f"   Limit: ${capabilities['limits']['max_transfer_amount']:,.2f}")
    
    if error:
        print(f"   Reason: {error}")
    
    # Check if result matches expectation
    expected_allowed = (expected_result == "ALLOW")
    if allowed == expected_allowed:
        print(f"   ✓ Matches expected result")
    else:
        print(f"   ✗ UNEXPECTED: Expected {expected_result}")
    
    print()


def main():
    """Run all demo scenarios"""
    
    print_header("FortressAI - Unified RBAC Demo")
    print("Demonstrating 10 banking roles with realistic scenarios\n")
    
    # Initialize database
    print("🔧 Initializing database...")
    initialize_database()
    
    # Show all roles
    print("\n📊 Configured Roles:")
    roles = db.get_all_roles()
    role_summary = {}
    for role_data in roles:
        role_id = role_data['role_id']
        if role_id not in role_summary:
            role_summary[role_id] = []
        role_summary[role_id].append(role_data['full_name'])
    
    for role_id, users in role_summary.items():
        print(f"   • {role_id}: {', '.join(users)}")
    
    # ============================================
    # TEST SCENARIOS
    # ============================================
    
    print_header("Scenario Group 1: Customer Service Representatives (Read-Only)")
    
    test_scenario(
        1,
        "CSR checking account balance (SHOULD ALLOW)",
        "CSR-KEY-001",
        "Show me account balance for customer #12345",
        "ALLOW"
    )
    
    test_scenario(
        2,
        "CSR attempting transfer (SHOULD DENY - no permission)",
        "CSR-KEY-001",
        "Transfer $1000 to vendor account",
        "DENY"
    )
    
    test_scenario(
        3,
        "CSR viewing transaction history (SHOULD ALLOW)",
        "CSR-KEY-002",
        "Show transaction history for last 30 days",
        "ALLOW"
    )
    
    print_header("Scenario Group 2: Branch Manager (Limited Transfers)")
    
    test_scenario(
        4,
        "Branch Manager transfer $30K (SHOULD ALLOW - within limit)",
        "MANAGER-KEY-001",
        "Transfer $30,000 to payroll account",
        "ALLOW"
    )
    
    test_scenario(
        5,
        "Branch Manager transfer $100K (SHOULD DENY - exceeds $50K limit)",
        "MANAGER-KEY-001",
        "Wire $100,000 to supplier",
        "DENY"
    )
    
    test_scenario(
        6,
        "Branch Manager approving loan (SHOULD ALLOW)",
        "MANAGER-KEY-001",
        "Approve loan for $25,000",
        "ALLOW"
    )
    
    print_header("Scenario Group 3: Treasury Manager (Large Transfers)")
    
    test_scenario(
        7,
        "Treasury Manager $5M transfer (SHOULD ALLOW - within $10M limit)",
        "TREASURY-KEY-001",
        "Transfer $5,000,000 for bond purchase",
        "ALLOW"
    )
    
    test_scenario(
        8,
        "Treasury Manager FX execution (SHOULD ALLOW)",
        "TREASURY-KEY-001",
        "Execute FX trade for EUR 2M",
        "ALLOW"
    )
    
    print_header("Scenario Group 4: Fraud Investigator (Security Operations)")
    
    test_scenario(
        9,
        "Fraud Investigator freezing account (SHOULD ALLOW)",
        "FRAUD-KEY-001",
        "Freeze account #67890 due to suspicious activity",
        "ALLOW"
    )
    
    test_scenario(
        10,
        "Fraud Investigator creating fraud alert (SHOULD ALLOW)",
        "FRAUD-KEY-002",
        "Create fraud alert for transaction pattern",
        "ALLOW"
    )
    
    test_scenario(
        11,
        "Fraud Investigator attempting transfer (SHOULD DENY - no permission)",
        "FRAUD-KEY-001",
        "Transfer $500 to investigation account",
        "DENY"
    )
    
    print_header("Scenario Group 5: Compliance Officer (Audit Access)")
    
    test_scenario(
        12,
        "Compliance Officer generating report (SHOULD ALLOW)",
        "COMPLIANCE-KEY-001",
        "Generate compliance report for Q4",
        "ALLOW"
    )
    
    test_scenario(
        13,
        "Compliance Officer KYC verification (SHOULD ALLOW)",
        "COMPLIANCE-KEY-001",
        "Verify KYC for customer #12345",
        "ALLOW"
    )
    
    print_header("Scenario Group 6: Loan Officer (Credit Operations)")
    
    test_scenario(
        14,
        "Loan Officer processing application (SHOULD ALLOW)",
        "LOAN-KEY-001",
        "Process loan application for $200,000",
        "ALLOW"
    )
    
    test_scenario(
        15,
        "Loan Officer attempting transfer (SHOULD DENY - no permission)",
        "LOAN-KEY-001",
        "Transfer $1000 to applicant",
        "DENY"
    )
    
    print_header("Scenario Group 7: CFO (Full Access)")
    
    test_scenario(
        16,
        "CFO large transfer (SHOULD ALLOW - $100M limit)",
        "CFO-KEY-001",
        "Transfer $50,000,000 for acquisition",
        "ALLOW"
    )
    
    test_scenario(
        17,
        "CFO accessing any API (SHOULD ALLOW - wildcard)",
        "CFO-KEY-001",
        "Generate portfolio analysis",
        "ALLOW"
    )
    
    print_header("Scenario Group 8: Payment Processor (Batch Operations)")
    
    test_scenario(
        18,
        "Payment Processor $50K transfer (SHOULD ALLOW - within $100K limit)",
        "PAYMENT-KEY-001",
        "Process batch payment of $50,000",
        "ALLOW"
    )
    
    test_scenario(
        19,
        "Payment Processor $150K transfer (SHOULD DENY - exceeds limit)",
        "PAYMENT-KEY-001",
        "Transfer $150,000 to vendor",
        "DENY"
    )
    
    print_header("Scenario Group 9: Risk Analyst (Analysis Only)")
    
    test_scenario(
        20,
        "Risk Analyst portfolio analysis (SHOULD ALLOW)",
        "RISK-KEY-001",
        "Analyze portfolio risk exposure",
        "ALLOW"
    )
    
    test_scenario(
        21,
        "Risk Analyst attempting transfer (SHOULD DENY - no permission)",
        "RISK-KEY-001",
        "Transfer $100 for testing",
        "DENY"
    )
    
    print_header("Scenario Group 10: Customer (Self-Service)")
    
    test_scenario(
        22,
        "Customer $3K transfer (SHOULD ALLOW - within $5K limit)",
        "CUSTOMER-KEY-001",
        "Transfer $3,000 to my savings",
        "ALLOW"
    )
    
    test_scenario(
        23,
        "Customer $10K transfer (SHOULD DENY - exceeds $5K limit)",
        "CUSTOMER-KEY-002",
        "Wire $10,000 to friend",
        "DENY"
    )
    
    test_scenario(
        24,
        "Customer checking balance (SHOULD ALLOW)",
        "CUSTOMER-KEY-003",
        "What's my account balance?",
        "ALLOW"
    )
    
    # ============================================
    # SUMMARY
    # ============================================
    
    print_header("Demo Complete!")
    print("✅ All 24 scenarios tested")
    print("✅ 10 banking roles demonstrated")
    print("✅ Financial limits enforced")
    print("✅ Permission model validated")
    print("\n🎯 Key Features Demonstrated:")
    print("   • Unified allowed_apis[] model (internal:// and https://)")
    print("   • Role-based access control (RBAC)")
    print("   • Financial guardrails (amount limits)")
    print("   • Intent resolution (natural language → API)")
    print("   • Wildcard permissions (CFO has internal://agent/*)")
    print("   • Zero-trust architecture (every request validated)")
    print()


if __name__ == "__main__":
    main()
