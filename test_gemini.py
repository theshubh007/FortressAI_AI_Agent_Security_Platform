"""Test Gemini API and tool calling"""
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyCeV8sBiikarKPWU4krCEzZ2-3biM93xFA"

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"The weather in {city} is sunny and 72°F"

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1
)

# Bind tool
llm_with_tools = llm.bind_tools([get_weather])

# Test
message = HumanMessage(content="What's the weather in Paris?")
response = llm_with_tools.invoke([message])

print(f"Response type: {type(response)}")
print(f"Has tool_calls: {hasattr(response, 'tool_calls')}")
if hasattr(response, 'tool_calls'):
    print(f"Tool calls: {response.tool_calls}")
print(f"Content: {response.content}")
