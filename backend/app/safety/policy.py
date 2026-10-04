from enum import Enum
from typing import Dict, Any, Optional


class RiskLevel(str, Enum):
    LOW = "low"
    SENSITIVE = "sensitive"
    HIGH_RISK = "high_risk"


class SafetyPolicy:
    SENSITIVE_KEYWORDS = [
        "buy", "purchase", "checkout", "pay", "payment", "credit card", "bank",
        "delete", "remove", "drop", "purge",
        "send email", "send message", "post comment",
        "submit form", "register", "signup", "subscribe",
        "change password", "update settings", "transfer"
    ]

    def evaluate_action_risk(self, action_name: str, params: Dict[str, Any]) -> RiskLevel:
        """
        Evaluates the risk level of a proposed browser action based on tool type and parameter context.
        """
        if action_name in ["open_url", "scroll", "extract_text", "extract_links", "screenshot", "get_current_url", "get_page_title"]:
            return RiskLevel.LOW

        # Combine text content and selector strings to check for sensitive operations
        combined_str = f"{action_name} {params.get('selector', '')} {params.get('text', '')} {params.get('reason', '')}".lower()

        for kw in self.SENSITIVE_KEYWORDS:
            if kw in combined_str:
                return RiskLevel.SENSITIVE

        if action_name == "type" and any(field in combined_str for field in ["password", "token", "ssn", "cvv"]):
            return RiskLevel.HIGH_RISK

        return RiskLevel.LOW


safety_policy = SafetyPolicy()
