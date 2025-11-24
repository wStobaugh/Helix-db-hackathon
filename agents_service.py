# agents_service.py
import os
from typing import Any

from agents import Agent, Runner  # from openai-agents :contentReference[oaicite:4]{index=4}


def init_agent() -> Agent:
    """
    Create a simple agent for your app.
    Make sure OPENAI_API_KEY is set in your environment.
    """
    # You can make this more specific for Helix/RAG workflows.
    instructions = (
        "You are a helpful assistant for a HelixDB-powered app. "
        "Reply concisely and explain what you are doing when asked."
    )

    agent = Agent(
        name="HackathonAssistant",
        instructions=instructions,
    )
    return agent


def run_agent(agent: Agent, message: str) -> str:
    """
    Run a single-turn interaction with the agent synchronously.
    """
    result = Runner.run_sync(agent, message)
    # result.final_output contains the final string response. :contentReference[oaicite:5]{index=5}
    return str(result.final_output)
