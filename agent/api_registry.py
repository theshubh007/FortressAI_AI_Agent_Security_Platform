"""
FortressAI - Agent API Registry
Maps user intents to internal API endpoints
"""

import re
from typing import Optional, Dict, Any, Tuple


class APIRegistry:
    """
    Registry of internal APIs and intent mapping
    Maps natural language intents to internal:// API endpoints
    """
    
    # Internal API definitions
    INTERNAL_APIS = {
        # Account Operations
        "account_inquiry": "internal://agent/account_inquiry",
        "balance_check": "internal://agent/balance_check",
        "transaction_history": "internal://agent/transaction_history",
        "freeze_account": "internal://agent/freeze_account",
        "unfreeze_account": "internal://agent/unfreeze_account",
        
        # Payment Operations
        "initiate_transfer": "internal://agent/initiate_transfer",
        "batch_payment": "internal://agent/batch_payment",
        "bill_payment": "internal://agent/bill_payment",
        "payment_status": "internal://agent/payment_status",
        "cancel_payment": "internal://agent/cancel_payment",
        
        # Fraud & Security
        "fraud_alert": "internal://agent/fraud_alert",
        "kyc_verify": "internal://agent/kyc_verify",
        "aml_check": "internal://agent/aml_check",
        "transaction_analysis": "internal://agent/transaction_analysis",
        
        # Treasury & FX
        "fx_execution": "internal://agent/fx_execution",
        "cash_forecast": "internal://agent/cash_forecast",
        "liquidity_report": "internal://agent/liquidity_report",
        
        # Lending
        "credit_check": "internal://agent/credit_check",
        "loan_application": "internal://agent/loan_application",
        "approve_loan": "internal://agent/approve_loan",
        
        # Compliance & Risk
        "regulatory_report": "internal://agent/regulatory_report",
        "audit_trail": "internal://agent/audit_trail",
        "risk_assessment": "internal://agent/risk_assessment",
        "portfolio_analysis": "internal://agent/portfolio_analysis",
        "stress_test": "internal://agent/stress_test",
        
        # Overrides
        "override_limit": "internal://agent/override_limit",
    }
    
    # Intent patterns (regex) → API mapping
    INTENT_PATTERNS = [
        # Account queries
        (r"(?i)(show|check|view|what.?s|get).*(balance|account)", "account_inquiry"),
        (r"(?i)(transaction|statement|history)", "transaction_history"),
        
        # Transfers
        (r"(?i)(transfer|wire|send|pay).*(money|\$|amount)", "initiate_transfer"),
        (r"(?i)(bill|utility|payment)", "bill_payment"),
        
        # Fraud
        (r"(?i)(freeze|lock|block|suspend).*(account)", "freeze_account"),
        (r"(?i)(fraud|suspicious|alert)", "fraud_alert"),
        (r"(?i)(kyc|know.your.customer|verify.identity)", "kyc_verify"),
        
        # Loans
        (r"(?i)(loan|credit|borrow)", "loan_application"),
        (r"(?i)(approve|authorization).*(loan)", "approve_loan"),
        
        # Compliance
        (r"(?i)(compliance|regulatory|audit)", "regulatory_report"),
        (r"(?i)(aml|anti.money.laundering)", "aml_check"),
        
        # Risk
        (r"(?i)(risk|assessment|analysis)", "risk_assessment"),
        (r"(?i)(portfolio)", "portfolio_analysis"),
    ]
    
    def __init__(self):
        """Initialize API registry"""
        pass
    
    def resolve_intent(self, user_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve user intent to internal API
        
        Args:
            user_text: User's natural language input
            
        Returns:
            (api_endpoint, intent_name) or (None, None) if no match
        """
        for pattern, intent_name in self.INTENT_PATTERNS:
            if re.search(pattern, user_text):
                api_endpoint = self.INTERNAL_APIS.get(intent_name)
                return api_endpoint, intent_name
        
        return None, None
    
    def extract_amount(self, user_text: str) -> Optional[float]:
        """
        Extract dollar amount from text
        
        Args:
            user_text: User input
            
        Returns:
            Amount as float or None
        """
        # Pattern: $1,000 or $1000.50 or 1000
        patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',  # $1,000.50
            r'([0-9,]+(?:\.[0-9]{2})?)\s*(?:dollars|usd)',  # 1000 dollars
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_payee(self, user_text: str) -> Optional[str]:
        """
        Extract payee name from text
        
        Args:
            user_text: User input
            
        Returns:
            Payee name or None
        """
        # Pattern: "to [payee name]"
        patterns = [
            r'to\s+([A-Z][A-Za-z\s&\.,]+?)(?:\s|$|[^A-Za-z])',
            r'payee[:\s]+([A-Z][A-Za-z\s&\.,]+?)(?:\s|$|[^A-Za-z])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def get_api_info(self, api_endpoint: str) -> Dict[str, Any]:
        """
        Get information about an API endpoint
        
        Args:
            api_endpoint: API endpoint (e.g., "internal://agent/initiate_transfer")
            
        Returns:
            Dict with API metadata
        """
        # Extract API name from endpoint
        api_name = api_endpoint.replace("internal://agent/", "")
        
        # Define API metadata
        api_metadata = {
            "initiate_transfer": {
                "requires_amount": True,
                "requires_payee": True,
                "operation_type": "transfer"
            },
            "account_inquiry": {
                "requires_amount": False,
                "requires_payee": False,
                "operation_type": "read"
            },
            "freeze_account": {
                "requires_amount": False,
                "requires_payee": False,
                "operation_type": "admin"
            },
            "approve_loan": {
                "requires_amount": True,
                "requires_payee": False,
                "operation_type": "loan"
            }
        }
        
        return api_metadata.get(api_name, {
            "requires_amount": False,
            "requires_payee": False,
            "operation_type": "unknown"
        })


# Global registry instance
registry = APIRegistry()


# Convenience functions
def resolve_intent(user_text: str) -> Tuple[Optional[str], Optional[str]]:
    """Resolve user intent to API"""
    return registry.resolve_intent(user_text)


def extract_amount(user_text: str) -> Optional[float]:
    """Extract amount from text"""
    return registry.extract_amount(user_text)


def extract_payee(user_text: str) -> Optional[str]:
    """Extract payee from text"""
    return registry.extract_payee(user_text)


def get_api_info(api_endpoint: str) -> Dict[str, Any]:
    """Get API metadata"""
    return registry.get_api_info(api_endpoint)


if __name__ == "__main__":
    # Test API registry
    print("🔧 Testing API Registry...")
    
    test_cases = [
        "Show me my account balance",
        "Transfer $5000 to ACME LLC",
        "Check transaction history",
        "Freeze account #12345 due to fraud",
        "Approve loan for $50,000",
        "Generate compliance report",
    ]
    
    for test in test_cases:
        api, intent = resolve_intent(test)
        amount = extract_amount(test)
        payee = extract_payee(test)
        
        print(f"\n📝 Input: {test}")
        print(f"   API: {api}")
        print(f"   Intent: {intent}")
        if amount:
            print(f"   Amount: ${amount:,.2f}")
        if payee:
            print(f"   Payee: {payee}")
    
    print("\n✅ API Registry tests complete!")
