# src/agent.py
import os
import json
import logging
import asyncio
from typing import List, Optional
from pydantic_ai import Agent, RunContext
from src.schema import PCPart, FullBuild
from src.validator import BuildValidator

logger = logging.getLogger(__name__)

# Initialize the Pydantic AI Agent using the Coordinator Pattern
architect_agent = Agent(
    "openai:gpt-4-turbo",
    system_prompt=(
        "You are The Master Architect, an elite PC hardware engineer. "
        "Your objective is to conduct a recursive interview with the user to discover their budget, "
        "intent (e.g., gaming, workstation), and form-factor preferences. "
        "Once constraints are clear, use your tools to fetch live component prices. "
        "You must assemble a complete, 100% compatible PC build. "
        "Do not guess dimensions or sockets; rely strictly on the data returned by your tools."
    ),
    result_type=FullBuild
)

# Mock database/Redis for simulation purposes
MOCK_REDIS_CACHE = {}

@architect_agent.tool
async def search_component_prices(ctx: RunContext, category: str, query: str) -> str:
    """
    Simulates scraping live pricing from vendors (Amazon, Newegg) and accessing a Redis cache.
    Also implements the Price Alert Arbitrage logic.
    """
    logger.info(f"Searching for {category}: {query}")
    
    # In a production environment, this triggers aiohttp calls to retailer APIs.
    # For demonstration, we return mocked JSON strings representing live data.
    
    # Mocked dataset based on 2026 market realities
    market_data = {
        "CPU":,
        "MOBO":
        # Additional categories omitted for brevity in documentation
    }
    
    results = market_data.get(category.upper(),)
    
    # Price Arbitrage Logic
    threshold = float(os.getenv("PRICE_ALERT_THRESHOLD_PERCENT", "15"))
    for part in results:
        historical_avg = part["price"] * 1.2  # Simulating that current price is lower
        discount = ((historical_avg - part["price"]) / historical_avg) * 100
        if discount >= threshold:
            part["arbitrage_alert"] = f"ARBITRAGE: {part['vendor']} price is {discount:.1f}% below 30-day average."
            logger.info(part["arbitrage_alert"])

    return json.dumps(results)

@architect_agent.tool
def validate_current_draft(ctx: RunContext, build_draft: FullBuild) -> str:
    """
    Exposes the deterministic BuildValidator to the LLM agent.
    The agent must call this tool before finalizing its response.
    """
    is_valid, errors = BuildValidator.validate_build(build_draft)
    
    if is_valid:
        return json.dumps({"status": "SUCCESS", "message": "Build is 100% mathematically compatible."})
    else:
        return json.dumps({"status": "FAILED", "errors": errors})

class AgentSession:
    """Manages multi-turn conversation state to prevent constraint forgetting."""
    def __init__(self):
        self.message_history =

    async def chat(self, user_input: str) -> FullBuild | str:
        try:
            result = await architect_agent.run(
                user_input, 
                message_history=self.message_history
            )
            self.message_history = result.all_messages()
            return result.data
        except Exception as e:
            logger.error(f"Agent reasoning error: {str(e)}")
            return "I need more specific clarification regarding your component constraints before proceeding."