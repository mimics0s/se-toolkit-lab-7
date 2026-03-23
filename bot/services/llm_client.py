"""LLM client for tool-based intent routing.

Communicates with the LLM API to process natural language queries.
The LLM receives tool definitions and decides which tools to call.
"""

import json
import sys
from typing import Any

import httpx


class LLMClient:
    """Client for LLM API with tool calling support.

    The LLM receives:
    - System prompt with instructions
    - User message
    - List of tool schemas

    The LLM returns tool calls in a structured format.
    """

    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the LLM client.

        Args:
            api_key: API key for authentication.
            base_url: Base URL of the LLM API.
            model: Model name to use.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool schemas.

        Returns:
            LLM response dict with 'content' and/or 'tool_calls'.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]

    def execute_tool_call(
        self,
        tool_call: dict[str, Any],
        tools_registry: dict[str, callable],
    ) -> Any:
        """Execute a single tool call.

        Args:
            tool_call: Tool call dict from LLM with 'function' key.
            tools_registry: Dict mapping tool names to functions.

        Returns:
            Result of the tool execution.
        """
        func = tool_call["function"]
        tool_name = func["name"]
        args = json.loads(func["arguments"])

        if tool_name not in tools_registry:
            return f"Error: Unknown tool '{tool_name}'"

        try:
            tool_func = tools_registry[tool_name]
            return tool_func(**args)
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"

    def route(
        self,
        user_message: str,
        tools: list[dict[str, Any]],
        tools_registry: dict[str, callable],
        system_prompt: str | None = None,
    ) -> str:
        """Route a user message through the LLM tool-calling loop.

        This implements the full tool-calling loop:
        1. Send user message + tools to LLM
        2. LLM returns tool calls
        3. Execute tools and collect results
        4. Feed results back to LLM
        5. LLM produces final answer

        Args:
            user_message: The user's natural language query.
            tools: List of tool schemas for the LLM.
            tools_registry: Dict mapping tool names to executable functions.
            system_prompt: Optional system prompt (uses default if None).

        Returns:
            Final response from the LLM.
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call LLM
            response = self.chat(messages, tools)

            # Check if LLM wants to call tools
            tool_calls = response.get("tool_calls", [])

            if not tool_calls:
                # LLM produced final answer
                return response.get("content", "I don't have enough information to answer that.")

            # Execute tool calls and collect results
            for tool_call in tool_calls:
                func = tool_call["function"]
                tool_name = func["name"]
                args_str = func["arguments"]

                # Debug output to stderr
                print(f"[tool] LLM called: {tool_name}({args_str})", file=sys.stderr)

                result = self.execute_tool_call(tool_call, tools_registry)

                # Debug output to stderr
                result_preview = str(result)[:200]
                if len(str(result)) > 200:
                    result_preview += "..."
                print(f"[tool] Result: {result_preview}", file=sys.stderr)

                # Add tool result to conversation
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call],
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result) if not isinstance(result, str) else result,
                })

            print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

        return "Error: Maximum iterations reached while processing your request."

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the intent router."""
        return """You are a helpful assistant for a Learning Management System (LMS).
You have access to various tools that fetch data from the backend API.

IMPORTANT RULES:
1. If the user's message is a greeting (hello, hi, hey) or doesn't make sense (gibberish, random letters), respond helpfully WITHOUT calling any tools. Just be friendly and explain what you can do.
2. If the user's message is ambiguous (like just "lab 4"), ask what they want to know about it.
3. Only call tools when the user asks a specific question that requires data from the LMS.
4. When you call tools, use the results to formulate your answer with actual numbers and names.

For greetings or unclear queries, respond helpfully and mention what you can do:
- List available labs
- Show scores and pass rates
- Compare groups
- Find top learners
- Show completion rates

Examples of when NOT to call tools:
- "hello" -> Just greet and offer help
- "asdfgh" -> Say you didn't understand and offer help
- "thanks" -> Just acknowledge

Examples of when TO call tools:
- "what labs are available?" -> call get_items
- "show me scores for lab 4" -> call get_pass_rates(lab="lab-04")
- "which lab has the lowest pass rate?" -> call get_items, then get_pass_rates for each lab
"""
