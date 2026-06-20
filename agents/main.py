"""Main agent module for LLM integration."""

import os
import json
import time
from collections import deque
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


class Agent:
    """Main agent class that interfaces with OpenAI-compatible LLM endpoints."""

    def __init__(self):
        """Initialize the agent with environment configuration."""
        self.api_base = os.environ.get("LLM_API_BASE", "http://localhost:8080/v1")
        self.api_key = os.environ.get("LLM_API_KEY", "not-needed-for-local")
        self.model = os.environ.get("LLM_MODEL", "default-model")
        self.temperature = float(os.environ.get("LLM_TEMPERATURE", "0.7"))

        # Initialize tools and guardrails
        from agents.tools import MarketResearchTools
        from agents.guardrails import SafetyGuardrails

        self.tools = MarketResearchTools()
        self.guardrails = SafetyGuardrails()

        # In-process sliding-window of recent request timestamps. This tracks
        # the request rate for a single process only; a shared store (e.g. the
        # Redis service defined in docker-compose) is required for rate limiting
        # across multiple workers/replicas in production.
        self.rate_limit_window_seconds = 60
        self._request_times: deque = deque()

        # Initialize LLM client if openai is available
        self.client = None
        if OpenAI is not None:
            try:
                self.client = OpenAI(
                    base_url=self.api_base,
                    api_key=self.api_key,
                )
            except Exception as e:
                print(f"Warning: Could not initialize LLM client: {e}")

    def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send a chat request to the LLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.

        Returns:
            Dictionary containing the response and metadata.
        """
        # Validate input through guardrails
        for msg in messages:
            if "content" in msg:
                validation = self.guardrails.validate_input(msg["content"])
                if not validation["valid"]:
                    return {
                        "error": "input_blocked",
                        "reason": validation["reason"],
                        "response": None
                    }

        # Check rate limit using an in-process sliding window. Evict timestamps
        # older than the window, then count the requests remaining in it.
        now = time.monotonic()
        window_start = now - self.rate_limit_window_seconds
        while self._request_times and self._request_times[0] < window_start:
            self._request_times.popleft()

        request_count = len(self._request_times)
        if not self.guardrails.check_rate_limit(
            request_count, window_seconds=self.rate_limit_window_seconds
        ):
            return {
                "error": "rate_limited",
                "response": None
            }

        # Record this request only once it is admitted.
        self._request_times.append(now)

        # If client is available, use it; otherwise return placeholder response
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature
                )
                content = response.choices[0].message.content

                # Validate output through guardrails
                validation = self.guardrails.validate_output(content)
                if not validation["valid"]:
                    return {
                        "error": "output_blocked",
                        "reason": validation["reason"],
                        "response": None
                    }

                return {
                    "response": content,
                    "model": self.model,
                    "status": "success"
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "response": None
                }

        # Fallback: return a placeholder response for testing without LLM
        return {
            "response": self._generate_fallback_response(messages),
            "model": self.model,
            "status": "success"
        }

    def _generate_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a fallback response when LLM is not available.

        Args:
            messages: List of message dictionaries.

        Returns:
            A placeholder response string.
        """
        if not messages:
            return "Hello! I'm an agent ready to help with market research."

        last_message = messages[-1].get("content", "")
        return f"I received your request about '{last_message[:50]}'. This is a fallback response since no LLM endpoint is configured."

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific tool with given parameters.

        Args:
            tool_name: Name of the tool to execute.
            **kwargs: Tool-specific arguments.

        Returns:
            Dictionary containing tool results.
        """
        # Map tool names to methods
        tool_map = {
            "search_market_trends": self.tools.search_market_trends,
            "analyze_competitor": self.tools.analyze_competitor,
            "get_industry_metrics": self.tools.get_industry_metrics,
            "track_product_mentions": self.tools.track_product_mentions,
            "generate_market_report": self.tools.generate_market_report,
        }

        if tool_name not in tool_map:
            return {
                "error": f"unknown_tool:{tool_name}",
                "available_tools": list(tool_map.keys())
            }

        try:
            result = tool_map[tool_name](**kwargs)
            # Validate output through guardrails
            if isinstance(result, dict):
                result_str = json.dumps(result)
                validation = self.guardrails.validate_output(result_str)
                if not validation["valid"]:
                    return {
                        "error": "output_blocked",
                        "reason": validation["reason"]
                    }
            return result
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names.

        Returns:
            List of available tool names.
        """
        return [
            "search_market_trends",
            "analyze_competitor",
            "get_industry_metrics",
            "track_product_mentions",
            "generate_market_report"
        ]


def main():
    """Main entry point for the agent."""
    agent = Agent()

    # Example: Run a simple chat
    messages = [
        {"role": "user", "content": "Hello, can you help me with market research?"}
    ]
    response = agent.chat(messages)
    print(f"Chat Response: {response}")

    # Example: Use a tool
    tool_result = agent.execute_tool("search_market_trends", query="AI market trends")
    print(f"Tool Result: {tool_result}")


if __name__ == "__main__":
    main()
