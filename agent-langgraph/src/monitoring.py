"""
Monitoring and metrics for the LangGraph agent
"""
import time
import logging
from typing import Dict, Any
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class AgentMetrics:
    """Track agent performance metrics."""
    
    def __init__(self):
        self.query_count = 0
        self.tool_calls = defaultdict(int)
        self.response_times = []
        self.errors = []
        self.start_time = datetime.utcnow()
    
    def record_query(self, duration: float, tool_count: int):
        """Record a query execution."""
        self.query_count += 1
        self.response_times.append(duration)
        logger.info(f"Query #{self.query_count} completed in {duration:.2f}s with {tool_count} tool calls")
    
    def record_tool_call(self, tool_name: str):
        """Record a tool invocation."""
        self.tool_calls[tool_name] += 1
    
    def record_error(self, error: str):
        """Record an error."""
        self.errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": error
        })
        logger.error(f"Error recorded: {error}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0
        )
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "total_queries": self.query_count,
            "average_response_time": round(avg_response_time, 2),
            "tool_calls": dict(self.tool_calls),
            "total_tool_calls": sum(self.tool_calls.values()),
            "error_count": len(self.errors),
            "recent_errors": self.errors[-5:] if self.errors else []
        }
    
    def reset(self):
        """Reset all metrics."""
        self.query_count = 0
        self.tool_calls.clear()
        self.response_times.clear()
        self.errors.clear()
        self.start_time = datetime.utcnow()
        logger.info("Metrics reset")


# Singleton instance
metrics = AgentMetrics()
