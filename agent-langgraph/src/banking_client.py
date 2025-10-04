"""
Banking API Client
HTTP client for calling the Banking API service
"""
import os
import httpx
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class BankingAPIClient:
    """Client for interacting with the Banking API."""
    
    def __init__(self):
        self.base_url = os.getenv("BANKING_API_URL", "http://localhost:8004")
        self.api_key = os.getenv("BANKING_API_KEY", "BANKING-API-KEY-123")
        self.headers = {"X-API-Key": self.api_key}
        self.timeout = 10.0
        
        logger.info(f"Banking API Client initialized: {self.base_url}")
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to Banking API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=self.timeout,
                    **kwargs
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    error_msg = f"API error {response.status_code}"
                    try:
                        error_detail = response.json().get("detail", error_msg)
                    except:
                        error_detail = error_msg
                    
                    logger.error(f"Banking API error: {error_detail}")
                    return {"error": error_detail}
                    
        except httpx.TimeoutException:
            logger.error(f"Banking API timeout: {url}")
            return {"error": "Banking API timeout"}
        except Exception as e:
            logger.error(f"Banking API exception: {str(e)}")
            return {"error": f"API error: {str(e)}"}
    
    async def get_user_accounts(self, user_id: str) -> List[Dict]:
        """Get all accounts for a user."""
        result = await self._make_request("GET", f"/accounts/{user_id}")
        return result
    
    async def get_account_balance(self, account_id: str) -> Dict:
        """Get account balance."""
        result = await self._make_request("GET", f"/accounts/{account_id}/balance")
        return result
    
    async def get_transactions(self, account_id: str, limit: int = 5) -> List[Dict]:
        """Get transaction history."""
        result = await self._make_request(
            "GET",
            f"/accounts/{account_id}/transactions",
            params={"limit": limit}
        )
        return result
    
    async def transfer_funds(
        self,
        from_account: str,
        to_account: str,
        amount: float,
        description: str = "Transfer"
    ) -> Dict:
        """Transfer funds between accounts."""
        result = await self._make_request(
            "POST",
            "/transfer",
            json={
                "from_account": from_account,
                "to_account": to_account,
                "amount": amount,
                "description": description
            }
        )
        return result
    
    async def get_account_summary(self, account_id: str) -> Dict:
        """Get account summary with analytics."""
        result = await self._make_request("GET", f"/accounts/{account_id}/summary")
        return result
    
    async def health_check(self) -> Dict:
        """Check Banking API health."""
        result = await self._make_request("GET", "/health")
        return result


# Singleton instance
banking_client = BankingAPIClient()
