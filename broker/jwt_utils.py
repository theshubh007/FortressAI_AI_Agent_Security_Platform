"""
FortressAI - JWT Capability Tokens (Unified RBAC)
Issue and verify capability-based access tokens with allowed_apis[] model
"""

import jwt
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class CapabilityTokenManager:
    """
    Manage JWT capability tokens for agent authorization
    Uses unified allowed_apis[] model (no distinction between tools and APIs)
    """
    
    def __init__(self, secret: str):
        """
        Initialize token manager
        
        Args:
            secret: JWT signing secret (HS256)
        """
        self.secret = secret
        self.algorithm = "HS256"
        self.token_ttl = 300  # 5 minutes
    
    def issue_token(
        self,
        user_id: str,
        role_id: str,
        allowed_apis: List[str],
        limits: Dict[str, Any],
        request_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Issue a capability token with unified API permissions
        
        Args:
            user_id: User identifier
            role_id: User's role (csr, branch_manager, etc.)
            allowed_apis: List of allowed API endpoints (internal:// and https://)
            limits: Financial and rate limits
            request_context: Optional context (purpose, amount, etc.)
            
        Returns:
            JWT token string
        """
        now = int(time.time())
        
        payload = {
            "iss": "broker",
            "aud": "agent",
            "sub": user_id,
            "role_id": role_id,
            "allowed_apis": allowed_apis,
            "limits": limits,
            "iat": now,
            "exp": now + self.token_ttl
        }
        
        # Add request context if provided
        if request_context:
            payload["context"] = request_context
        
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token
    
    def issue_token_legacy(
        self,
        agent_id: str,
        allowed_tools: list[str],
        data_scope: list[str],
        budgets: dict,
        payment_policy: dict = None,
        payment_details: dict = None
    ) -> str:
        """
        Legacy method for backward compatibility
        Converts old tools[] model to new allowed_apis[] model
        
        DEPRECATED: Use issue_token() instead
        """
        # Convert tools to internal APIs
        allowed_apis = [f"internal://agent/{tool}" for tool in allowed_tools]
        
        # Convert budgets to limits
        limits = {
            "max_tokens": budgets.get("max_tokens", 1500),
            "max_tool_calls": budgets.get("max_tool_calls", 3),
            "max_transfer_amount": payment_policy.get("max_amount", 5000) if payment_policy else 5000
        }
        
        now = int(time.time())
        
        payload = {
            "iss": "broker",
            "aud": "agent",
            "sub": agent_id,
            "tools": allowed_tools,  # Keep for backward compat
            "scopes": data_scope,
            "budgets": budgets,
            "allowed_apis": allowed_apis,  # New field
            "limits": limits,  # New field
            "iat": now,
            "exp": now + self.token_ttl
        }
        
        if payment_policy:
            payload["payment_policy"] = payment_policy
        
        if payment_details:
            payload["payment_details"] = payment_details
        
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> dict | None:
        """
        Verify and decode a capability token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                audience="agent",
                issuer="broker"
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_token_info(self, token: str) -> dict:
        """
        Get token information without verification (for logging)
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload (unverified)
        """
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return payload
        except:
            return {}
