from typing import List, Dict, Any, Optional
from backend.models.schemas import BrowserActionSchema


class TaskMemory:
    def __init__(self, task_id: str, instruction: str):
        self.task_id = task_id
        self.instruction = instruction
        self.current_url: str = ""
        self.current_step_idx: int = 0
        self.plan_steps: List[str] = []
        self.completed_actions: List[Dict[str, Any]] = []
        self.failed_actions: List[Dict[str, Any]] = []
        self.extracted_data: Dict[str, Any] = {}
        self.extracted_text_history: List[str] = []
        self.pending_approval_action: Optional[BrowserActionSchema] = None

    def record_action_success(self, action: BrowserActionSchema, result_data: Dict[str, Any], url: str):
        self.current_url = url
        self.completed_actions.append({
            "action": action.action,
            "params": action.model_dump(exclude_none=True),
            "result": result_data,
            "status": "success"
        })

    def record_action_failure(self, action: BrowserActionSchema, error_message: str):
        self.failed_actions.append({
            "action": action.action,
            "params": action.model_dump(exclude_none=True),
            "error": error_message,
            "status": "failed"
        })

    def add_extracted_data(self, key_data: Dict[str, Any]):
        self.extracted_data.update(key_data)

    def is_sensitive_action(self, action: BrowserActionSchema) -> bool:
        """
        Detects if an action requires Human-in-the-Loop user approval.
        """
        if action.action == "require_approval":
            return True

        sensitive_keywords = [
            "buy", "purchase", "checkout", "pay", "payment",
            "delete", "remove", "drop",
            "send email", "submit order", "transfer",
            "password", "credit card", "bank"
        ]

        action_text = f"{action.action} {action.text or ''} {action.reason or ''} {action.url or ''}".lower()
        for kw in sensitive_keywords:
            if kw in action_text:
                return True
        return False

    def to_summary(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "instruction": self.instruction,
            "current_url": self.current_url,
            "step_progress": f"{self.current_step_idx + 1}/{len(self.plan_steps)}",
            "completed_actions_count": len(self.completed_actions),
            "failed_actions_count": len(self.failed_actions),
            "extracted_data_keys": list(self.extracted_data.keys())
        }
