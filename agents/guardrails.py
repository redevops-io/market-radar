"""Safety guardrails for agent operations."""

import os
from typing import Any, Dict, List, Optional


class SafetyGuardrails:
    """Safety guardrails to ensure responsible AI operations."""

    # Default blocked topics/categories
    BLOCKED_TOPICS = {
        "illegal_activities",
        "harmful_content",
        "personal_data_exposure",
        "financial_advice",
        "medical_advice"
    }

    def __init__(self):
        """Initialize safety guardrails with configuration."""
        self.enabled = os.environ.get("GUARDRAILS_ENABLED", "true").lower() == "true"
        self.blocked_topics = self._load_blocked_topics()
        self.sensitive_patterns = self._load_sensitive_patterns()

    def _load_blocked_topics(self) -> set:
        """Load blocked topics from environment or use defaults."""
        env_topics = os.environ.get("BLOCKED_TOPICS", "")
        if env_topics:
            return set(t.strip() for t in env_topics.split(","))
        return self.BLOCKED_TOPICS

    def _load_sensitive_patterns(self) -> List[str]:
        """Load sensitive data patterns to detect."""
        default_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone number
        ]
        return default_patterns

    def validate_input(self, user_input: str) -> Dict[str, Any]:
        """Validate incoming user input against guardrails.

        NOTE: This is a coarse, best-effort content filter, NOT a security
        control. It does a naive substring match against blocked-topic tokens
        (e.g. "illegal_activities"), which real user inputs rarely contain
        verbatim, so it should be treated as advisory only. Do not rely on it
        to block adversarial or malicious input.

        Args:
            user_input: The raw user input string.

        Returns:
            Dictionary with validation result and details.
        """
        if not self.enabled:
            return {"valid": True, "reason": "guardrails_disabled"}

        # Best-effort substring match against blocked-topic tokens (advisory).
        for topic in self.blocked_topics:
            if topic.lower() in user_input.lower():
                return {
                    "valid": False,
                    "reason": f"blocked_topic:{topic}",
                    "input": user_input[:100]  # Truncate for logging
                }

        return {"valid": True, "reason": "passed"}

    def validate_output(self, llm_output: str) -> Dict[str, Any]:
        """Validate LLM output before returning to user.

        Args:
            llm_output: The raw LLM output string.

        Returns:
            Dictionary with validation result and details.
        """
        if not self.enabled:
            return {"valid": True, "reason": "guardrails_disabled"}

        # Check for sensitive data leakage
        import re
        for pattern in self.sensitive_patterns:
            if re.search(pattern, llm_output):
                return {
                    "valid": False,
                    "reason": "sensitive_data_detected",
                    "output_snippet": llm_output[:100]
                }

        # Check for harmful content patterns
        harmful_indicators = [
            "ignore previous instructions",
            "disregard safety",
            "bypass restrictions"
        ]
        output_lower = llm_output.lower()
        for indicator in harmful_indicators:
            if indicator in output_lower:
                return {
                    "valid": False,
                    "reason": "harmful_content_detected",
                    "output_snippet": llm_output[:100]
                }

        return {"valid": True, "reason": "passed"}

    def sanitize_response(self, response: str) -> str:
        """Sanitize a response by removing potentially sensitive information.

        Args:
            response: The raw response string.

        Returns:
            Sanitized response string.
        """
        import re
        sanitized = response

        # Mask potential SSN patterns
        sanitized = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED]", sanitized)

        # Mask email addresses (optional - keep for context if needed)
        # sanitized = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", "[EMAIL]", sanitized)

        return sanitized

    def check_rate_limit(self, request_count: int, window_seconds: int = 60) -> bool:
        """Check if request is within rate limits.

        Args:
            request_count: Number of requests in current window.
            window_seconds: Time window in seconds.

        Returns:
            True if request is allowed, False otherwise.
        """
        max_requests = int(os.environ.get("MAX_REQUESTS_PER_WINDOW", "100"))
        return request_count < max_requests
