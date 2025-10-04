"""
LangGraph Banking Agent with AWS Bedrock Claude
Handles banking operations with multi-step reasoning
"""
import os
from typing import TypedDict, Annotated, Sequence
from langchain_aws import ChatBedrock
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()


# Define agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    user_id: str


# Banking API client
from .banking_client import banking_client
import logging

logger = logging.getLogger(__name__)


# Banking tools that call the Banking API
@tool
async def get_user_accounts(user_id: str) -> dict:
    """
    Get all bank accounts for a user. 
    
    ALWAYS call this tool FIRST before any other banking operation to see what accounts the user has.
    
    Args:
        user_id: The user's ID (e.g., 'user123')
    
    Returns:
        Dictionary with user_id and list of accounts with account_id, type, nickname, and balance
    """
    logger.info(f"Tool called: get_user_accounts({user_id})")
    accounts = await banking_client.get_user_accounts(user_id)
    
    if isinstance(accounts, list):
        return {"user_id": user_id, "accounts": accounts}
    return accounts


@tool
async def get_account_balance(account_id: str) -> dict:
    """
    Get the current balance for a specific bank account.
    
    Use this when user asks about balance, how much money they have, or account status.
    
    Args:
        account_id: The account ID (e.g., 'ACC001')
    
    Returns:
        Dictionary with account_id, balance, currency, account_type, and status
    """
    logger.info(f"Tool called: get_account_balance({account_id})")
    result = await banking_client.get_account_balance(account_id)
    return result


@tool
async def get_transaction_history(account_id: str, limit: int = 5) -> dict:
    """
    Get recent transaction history for an account.
    
    Use this when user asks about transactions, spending, recent activity, or transaction history.
    
    Args:
        account_id: The account ID (e.g., 'ACC001')
        limit: Number of transactions to return (default: 5, max: 50)
    
    Returns:
        Dictionary with account_id and list of transactions with date, description, amount, category
    """
    logger.info(f"Tool called: get_transaction_history({account_id}, limit={limit})")
    transactions = await banking_client.get_transactions(account_id, limit)
    
    if isinstance(transactions, list):
        return {
            "account_id": account_id,
            "transactions": transactions
        }
    return transactions


@tool
async def transfer_funds(from_account: str, to_account: str, amount: float) -> dict:
    """
    Transfer money between two accounts.
    
    Use this when user wants to transfer, move, or send money between accounts.
    
    Args:
        from_account: Source account ID (e.g., 'ACC001')
        to_account: Destination account ID (e.g., 'ACC002')
        amount: Amount to transfer in USD (must be positive, max $10,000)
    
    Returns:
        Dictionary with success status, transaction_id, and transfer details
    """
    logger.info(f"Tool called: transfer_funds({from_account} -> {to_account}, ${amount})")
    result = await banking_client.transfer_funds(from_account, to_account, amount)
    return result


@tool
async def get_account_summary(account_id: str) -> dict:
    """
    Get detailed account summary with spending analytics and categorized expenses.
    
    Use this when user asks for account overview, spending analysis, or financial summary.
    
    Args:
        account_id: The account ID (e.g., 'ACC001')
    
    Returns:
        Dictionary with account details, recent transactions, spending by category, and totals
    """
    logger.info(f"Tool called: get_account_summary({account_id})")
    result = await banking_client.get_account_summary(account_id)
    return result



# Initialize LLM with tools
def create_agent():
    """Create the LangGraph banking agent with AWS Bedrock Claude."""
    
    # Initialize Bedrock Claude
    llm = ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        region_name="us-east-1",
        credentials_profile_name=None,  # Use environment variables
        model_kwargs={
            "temperature": 0.1,
            "max_tokens": 1000
        }
    )
    
    # Bind tools to LLM - put get_user_accounts first as it should be called first
    tools = [
        get_user_accounts,  # Always call this first
        get_account_balance,
        get_transaction_history,
        transfer_funds,
        get_account_summary
    ]
    # Bind tools without forcing - let the prompt guide usage
    llm_with_tools = llm.bind_tools(tools)
    
    # Define agent logic
    def should_continue(state: AgentState):
        """Determine if we should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are no tool calls, we're done
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        return "continue"
    
    def call_model(state: AgentState):
        """Call the LLM with current state."""
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    return workflow.compile()


# Create singleton agent instance
agent_graph = create_agent()


async def process_banking_query(user_id: str, query: str) -> dict:
    """Process a banking query through the agent."""
    
    try:
        # Create a clear prompt for Gemini
        system_message = f"""You are a banking assistant. User ID: {user_id}

User asks: {query}

You have these tools available:
- get_user_accounts(user_id) - Get all accounts for user
- get_account_balance(account_id) - Get balance for specific account
- get_transaction_history(account_id, limit) - Get recent transactions
- transfer_funds(from_account, to_account, amount) - Transfer money
- get_account_summary(account_id) - Get account summary with analytics

To answer, first call get_user_accounts("{user_id}") to see available accounts, then use other tools as needed."""

        initial_state = {
            "messages": [HumanMessage(content=system_message)],
            "user_id": user_id
        }
        
        # Run the agent with config to ensure fresh execution
        result = await agent_graph.ainvoke(
            initial_state,
            config={"recursion_limit": 10}
        )
        
        # Extract final response
        messages = result["messages"]
        final_message = messages[-1]
        
        # Get the actual content
        response_text = ""
        if hasattr(final_message, "content"):
            if isinstance(final_message.content, str):
                response_text = final_message.content
            elif isinstance(final_message.content, list):
                # Handle list of content blocks
                response_text = " ".join(
                    block.get("text", "") if isinstance(block, dict) else str(block)
                    for block in final_message.content
                )
            else:
                response_text = str(final_message.content)
        else:
            response_text = str(final_message)
        
        return {
            "response": response_text,
            "message_count": len(messages),
            "tool_calls_made": sum(1 for m in messages if isinstance(m, ToolMessage))
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise
