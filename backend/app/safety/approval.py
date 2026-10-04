from enum import Enum
from typing import Dict, Any, Optional
from backend.app.safety.policy import safety_policy, RiskLevel


class AgentMode(str, Enum):
    OBSERVE = "observe"
    ASSISTED = "assisted"        # Default mode
    AUTONOMOUS = "autonomous"


class ApprovalManager:
    def __init__(self, default_mode: AgentMode = AgentMode.ASSISTED):
        self.mode = default_mode

    def requires_approval(self, action_name: str, params: Dict[str, Any]) -> bool:
        """
        Determines whether the given action requires Human-in-the-Loop approval based on current AgentMode.
        """
        if self.mode == AgentMode.OBSERVE:
            # In Observe mode, any mutating action requires approval
            return action_name not in ["extract_text", "screenshot", "get_current_url", "get_page_title"]

        risk = safety_policy.evaluate_action_risk(action_name, params)

        if risk in [RiskLevel.SENSITIVE, RiskLevel.HIGH_RISK]:
            return True

        return False


approval_manager = ApprovalManager()
