from typing import Dict, Any, List, Optional
from backend.browser.page_analyzer import PageAnalysis
from backend.models.schemas import BrowserActionSchema


class RecoveryStrategy:
    def __init__(self, action: BrowserActionSchema, explanation: str):
        self.action = action
        self.explanation = explanation


class FailureRecoveryEngine:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._retry_counts: Dict[str, int] = {}

    def get_recovery_action(
        self,
        failed_action: BrowserActionSchema,
        error_message: str,
        current_page: PageAnalysis,
        action_history: List[Dict[str, Any]]
    ) -> RecoveryStrategy:
        """
        Determines the optimal recovery action when a browser action fails.
        """
        action_key = f"{failed_action.action}_{failed_action.selector or failed_action.url or 'general'}"
        count = self._retry_counts.get(action_key, 0) + 1
        self._retry_counts[action_key] = count

        if count > self.max_retries:
            return RecoveryStrategy(
                action=BrowserActionSchema(action="finish", reason=f"Max retry limit ({self.max_retries}) exceeded for {failed_action.action}: {error_message}"),
                explanation=f"Retry limit exceeded ({count}/{self.max_retries}). Halting loop."
            )

        err_lower = error_message.lower()

        # Strategy 1: Popup or Modal overlay blocking interaction
        if "intercept" in err_lower or "obscured" in err_lower or "modal" in err_lower or "dialog" in err_lower:
            # Try pressing Escape key to dismiss dialog
            return RecoveryStrategy(
                action=BrowserActionSchema(action="press", key="Escape", reason="Attempting to close overlay dialog"),
                explanation="Dismissing popup or modal dialog using Escape key"
            )

        # Strategy 2: Element not found or incorrect selector -> Alternative selector strategy
        if "not found" in err_lower or "timeout" in err_lower or "selector" in err_lower or "visible" in err_lower:
            target_text = failed_action.text or failed_action.selector or ""
            # Try matching by text content in page elements
            for el in current_page.elements:
                if target_text and (target_text.lower() in el.text.lower() or target_text.lower() in el.placeholder.lower() or target_text.lower() in el.name.lower()):
                    return RecoveryStrategy(
                        action=BrowserActionSchema(
                            action=failed_action.action,
                            selector=el.selector,
                            text=failed_action.text,
                            key=failed_action.key,
                            reason=f"Recovered alternative selector: {el.selector}"
                        ),
                        explanation=f"Found alternative visible element matching '{target_text}' with selector '{el.selector}'"
                    )

            # If no alternative selector found, scroll down to bring element into viewport
            return RecoveryStrategy(
                action=BrowserActionSchema(action="scroll", direction="down", amount=400, reason="Scroll page to bring target element into viewport"),
                explanation="Scrolling page down to make element visible"
            )

        # Strategy 3: Navigation timeout or failure
        if "navigation" in err_lower or "net::" in err_lower:
            if failed_action.url:
                return RecoveryStrategy(
                    action=BrowserActionSchema(action="open_url", url=failed_action.url, reason="Retrying page navigation"),
                    explanation=f"Retrying navigation to {failed_action.url}"
                )

        # Fallback default recovery strategy: Scroll & re-examine
        return RecoveryStrategy(
            action=BrowserActionSchema(action="scroll", direction="down", amount=300, reason="Default recovery scroll"),
            explanation=f"Default recovery attempt {count} for failed action {failed_action.action}"
        )

    def reset(self):
        self._retry_counts.clear()


recovery_engine = FailureRecoveryEngine()
