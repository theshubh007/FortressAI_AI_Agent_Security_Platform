"""
FastAPI application for LangGraph Banking Agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from datetime import datetime
import time
from .agent import process_banking_query
from .monitoring import metrics
from .banking_client import banking_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FortressAI Banking Agent (LangGraph)",
    description="AI-powered banking assistant with Claude and LangGraph",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    user_id: str = "user123"


class QueryResponse(BaseModel):
    response: str
    message_count: int
    tool_calls_made: int
    timestamp: str
    agent_type: str = "langgraph"


@app.get("/health")
async def health_check():
    """Health check endpoint with Banking API status."""
    # Check Banking API connectivity
    banking_api_status = "unknown"
    try:
        api_health = await banking_client.health_check()
        banking_api_status = api_health.get("status", "unknown")
    except Exception as e:
        banking_api_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "agent": "LangGraph Banking Agent",
        "llm": "Anthropic Claude",
        "banking_api": banking_api_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Process a banking query through the LangGraph agent.
    
    Example queries:
    - "What's my account balance?"
    - "Show me recent transactions"
    - "Transfer $500 from checking to savings"
    """
    start_time = time.time()
    
    try:
        logger.info(f"📥 Query from {request.user_id}: {request.query}")
        
        result = await process_banking_query(request.user_id, request.query)
        
        duration = time.time() - start_time
        metrics.record_query(duration, result["tool_calls_made"])
        
        logger.info(f"✓ Query completed in {duration:.2f}s")
        
        return QueryResponse(
            response=result["response"],
            message_count=result["message_count"],
            tool_calls_made=result["tool_calls_made"],
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        duration = time.time() - start_time
        metrics.record_error(str(e))
        logger.error(f"✗ Error after {duration:.2f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "FortressAI Banking Agent",
        "framework": "LangGraph",
        "llm": "Anthropic Claude 3.5 Sonnet",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/query (POST)",
            "docs": "/docs"
        }
    }



@app.get("/metrics")
async def get_metrics():
    """Get agent performance metrics."""
    return metrics.get_stats()


@app.post("/metrics/reset")
async def reset_metrics():
    """Reset all metrics."""
    metrics.reset()
    return {"status": "metrics reset", "timestamp": datetime.utcnow().isoformat()}
