"""Intent-based natural language router.

Routes user messages through an LLM that decides which tools to call.
No regex or keyword matching — the LLM makes the decision based on tool descriptions.
"""

import json
import sys
from typing import Any

from config import load_config
from services.api_client import LMSAPIClient
from services.llm_client import LLMClient


def get_tool_schemas() -> list[dict[str, Any]]:
    """Get all tool schemas for the LLM.

    These 9 tools cover all backend endpoints the LLM can use.
    The descriptions are specific so the LLM knows when to call each tool.

    Returns:
        List of tool schema dicts.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get all items from the LMS including labs and tasks. Use this to list available labs or find a specific lab by name.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get all enrolled learners/students. Use this to answer questions about student enrollment, how many students there are, or list students.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a specific lab. Use when asked about score distribution or how scores are spread.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task pass rates with average scores and attempt counts for a specific lab. Use when asked about pass rates, difficulty, or how students are performing in a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submission timeline showing submissions per day for a lab. Use when asked about when students submitted or activity over time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab. Use when asked about which group is best, comparing groups, or group performance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab. Use when asked about top students, leaderboard, or best performers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return, default 10",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab. Use when asked about completion rate or what percentage of students finished.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger a data sync from the autochecker to refresh data. Use when asked to refresh, sync, or update the data.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


def get_tools_registry(api_client: LMSAPIClient) -> dict[str, callable]:
    """Get the registry of tool functions.

    Maps tool names to their implementation functions.

    Args:
        api_client: Configured LMS API client.

    Returns:
        Dict mapping tool names to callable functions.
    """
    return {
        "get_items": api_client.get_items,
        "get_learners": api_client.get_learners,
        "get_scores": api_client.get_scores,
        "get_pass_rates": api_client.get_pass_rates,
        "get_timeline": api_client.get_timeline,
        "get_groups": api_client.get_groups,
        "get_top_learners": api_client.get_top_learners,
        "get_completion_rate": api_client.get_completion_rate,
        "trigger_sync": api_client.trigger_sync,
    }


def route_natural_language(message: str) -> str:
    """Route a natural language query through the LLM.

    The LLM receives the message and tool definitions, then decides
    which tools to call. Tool results are fed back and the LLM
    produces the final answer.

    Args:
        message: User's natural language query.

    Returns:
        Response from the LLM with actual backend data.
    """
    config = load_config()

    # Create API client
    api_client = LMSAPIClient(
        base_url=config["lms_api_base_url"],
        api_key=config["lms_api_key"],
    )

    # Create LLM client
    llm_client = LLMClient(
        api_key=config["llm_api_key"],
        base_url=config["llm_api_base_url"],
        model=config["llm_api_model"],
    )

    # Get tool schemas and registry
    tools = get_tool_schemas()
    tools_registry = get_tools_registry(api_client)

    # Route through LLM
    response = llm_client.route(
        user_message=message,
        tools=tools,
        tools_registry=tools_registry,
    )

    return response
