import os
from dotenv import load_dotenv

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools

# Load environment variables
load_dotenv()

# Initialize tools
duckduckgo_tool = DuckDuckGo()
yfinance_tool = YFinanceTools(
    stock_price=True,
    analyst_recommendations=True,
    stock_fundamentals=True
)

# Create a Groq-based agent with both tools
groq_agent = Agent(
    name="GroqFinancialSearchAgent",
    description="Agent using Groq to search web and analyze financial data.",
    instructions=[
        "Always include the source of your data.",
        "Use tables for financial information."
    ],
    model=Groq(id="llama-3.1-8b-instant"),  # or "mixtral-8x7b-32768"
    tools=[duckduckgo_tool, yfinance_tool],
    show_tool_calls=True,
    markdown=True,
)

# Ask the agent a question
groq_agent.print_response(
    "What are the latest news on Apple Inc.? Also give me its current stock price, fundamentals, and analyst recommendations."
)
