"""
FortressAI - RBAC Engine
Unified permission checking for internal and external APIs
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from database import get_user_by_api_key, get_user_permissions, is_user_quarantined


class RBACEngine:
    """
    Role-Based Access Control Engine
    Validates API access using unified allowed_apis[] model
    """
    
    def __init__(self):
        """Initialize RBAC engine"""
        pass
    
    def authenticate_user(self, api_key: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate user by API key
        
        Args:
            api_key: API key from X-API-Key header
            
        Returns:
            (success, user_data, error_message)
        """
        if not api_key:
            return False, None, "Missing API key"
        
        user = get_user_by_api_key(api_key)
        if not user:
            return False, None, "Invalid API key"
        
        # Check if user is quarantined
        if is_user_quarantined(user['user_id']):
            return False, None, f"User {user['user_id']} is quarantined"
        
        return True, user, None
    
    def get_user_capabilities(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's capabilities (allowed_apis + limits)
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with role_id, allowed_apis, limits or None
        """
        return get_user_permissions(user_id)
    
    def check_api_permission(
        self, 
        allowed_apis: List[str], 
        requested_api: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if requested API is in allowed list
        Supports wildcards (e.g., "internal://agent/*")
        
        Args:
            allowed_apis: List of allowed API patterns
            requested_api: API being requested
            
        Returns:
            (is_allowed, reason)
        """
        # Check for exact match
        if requested_api in allowed_apis:
            return True, None
        
        # Check for wildcard matches
        for pattern in allowed_apis:
            if self._matches_pattern(pattern, requested_api):
                return True, None
        
        return False, f"API not permitted: {requested_api}"
    
    def _matches_pattern(self, pattern: str, api: str) -> bool:
        """
        Check if API matches pattern (supports wildcards)
        
        Examples:
            "internal://agent/*" matches "internal://agent/initiate_transfer"
            "https://api.bank.com/accounts/*" matches "https://api.bank.com/accounts/read"
        """
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        regex_pattern = f"^{regex_pattern}$"
        
        return bool(re.match(regex_pattern, api))
    
    def check_financial_limits(
        self,
        limits: Dict[str, Any],
        operation: str,
        amount: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if operation is within financial limits
        
        Args:
            limits: User's financial limits
            operation: Operation type (transfer, loan, etc.)
            amount: Transaction amount (if applicable)
            
        Returns:
            (is_allowed, reason)
        """
        if operation == "transfer" and amount is not None:
            max_transfer = limits.get("max_transfer_amount", 0)
            if amount > max_transfer:
                return False, f"Amount ${amount:,.2f} exceeds limit ${max_transfer:,.2f}"
        
        if operation == "loan" and amount is not None:
            max_loan = limits.get("max_loan_amount", 0)
            if amount > max_loan:
                return False, f"Loan amount ${amount:,.2f} exceeds limit ${max_loan:,.2f}"
        
        return True, None
    
    def validate_request(
        self,
        api_key: str,
        requested_api: str,
        operation: str = "read",
        amount: Optional[float] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Complete request validation
        
        Args:
            api_key: User's API key
            requested_api: API endpoint being requested
            operation: Operation type (read, transfer, loan, etc.)
            amount: Transaction amount (if applicable)
            
        Returns:
            (is_allowed, capabilities, error_message)
        """
        # 1. Authenticate user
        success, user, error = self.authenticate_user(api_key)
        if not success:
            return False, None, error
        
        # 2. Get user capabilities
        capabilities = self.get_user_capabilities(user['user_id'])
        if not capabilities:
            return False, None, f"No permissions found for user {user['user_id']}"
        
        # 3. Check API permission
        allowed, reason = self.check_api_permission(
            capabilities['allowed_apis'],
            requested_api
        )
        if not allowed:
            return False, capabilities, reason
        
        # 4. Check financial limits (if applicable)
        if amount is not None:
            allowed, reason = self.check_financial_limits(
                capabilities['limits'],
                operation,
                amount
            )
            if not allowed:
                return False, capabilities, reason
        
        # All checks passed
        return True, capabilities, None


# Global RBAC engine instance
rbac = RBACEngine()


# Convenience functions
def authenticate_user(api_key: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Authenticate user by API key"""
    return rbac.authenticate_user(api_key)


def get_user_capabilities(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user capabilities"""
    return rbac.get_user_capabilities(user_id)


def check_api_permission(allowed_apis: List[str], requested_api: str) -> Tuple[bool, Optional[str]]:
    """Check API permission"""
    return rbac.check_api_permission(allowed_apis, requested_api)


def validate_request(
    api_key: str,
    requested_api: str,
    operation: str = "read",
    amount: Optional[float] = None
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Validate complete request"""
    return rbac.validate_request(api_key, requested_api, operation, amount)


if __name__ == "__main__":
    # Test RBAC engine
    from database import initialize_database
    
    print("🔧 Testing RBAC Engine...")
    initialize_database()
    
    # Test 1: CSR trying to read account
    print("\n📋 Test 1: CSR reading account")
    allowed, caps, error = validate_request(
        "CSR-KEY-001",
        "internal://agent/account_inquiry"
    )
    print(f"  Result: {'✅ ALLOWED' if allowed else '❌ DENIED'}")
    if error:
        print(f"  Reason: {error}")
    
    # Test 2: CSR trying to transfer (should fail)
    print("\n📋 Test 2: CSR attempting transfer")
    allowed, caps, error = validate_request(
        "CSR-KEY-001",
        "internal://agent/initiate_transfer",
        "transfer",
        1000
    )
    print(f"  Result: {'✅ ALLOWED' if allowed else '❌ DENIED'}")
    if error:
        print(f"  Reason: {error}")
    
    # Test 3: Branch Manager transfer within limit
    print("\n📋 Test 3: Branch Manager transfer $30K")
    allowed, caps, error = validate_request(
        "MANAGER-KEY-001",
        "internal://agent/initiate_transfer",
        "transfer",
        30000
    )
    print(f"  Result: {'✅ ALLOWED' if allowed else '❌ DENIED'}")
    if error:
        print(f"  Reason: {error}")
    
    # Test 4: Branch Manager exceeding limit
    print("\n📋 Test 4: Branch Manager transfer $100K (exceeds limit)")
    allowed, caps, error = validate_request(
        "MANAGER-KEY-001",
        "internal://agent/initiate_transfer",
        "transfer",
        100000
    )
    print(f"  Result: {'✅ ALLOWED' if allowed else '❌ DENIED'}")
    if error:
        print(f"  Reason: {error}")
    
    # Test 5: CFO wildcard access
    print("\n📋 Test 5: CFO accessing any internal API")
    allowed, caps, error = validate_request(
        "CFO-KEY-001",
        "internal://agent/some_random_api"
    )
    print(f"  Result: {'✅ ALLOWED' if allowed else '❌ DENIED'}")
    if error:
        print(f"  Reason: {error}")
    
    print("\n✅ RBAC Engine tests complete!")
