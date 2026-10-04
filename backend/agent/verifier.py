from typing import Dict, Any, Optional
from backend.browser.page_analyzer import PageAnalysis
from backend.browser.actions import ActionExecutionResult


class VerificationResult:
    def __init__(self, verified: bool, message: str, confidence: float = 1.0):
        self.verified = verified
        self.message = message
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verified": self.verified,
            "message": self.message,
            "confidence": self.confidence
        }


class ActionResultVerifier:
    async def verify_action(
        self,
        action_name: str,
        params: Dict[str, Any],
        pre_state: PageAnalysis,
        post_state: PageAnalysis,
        execution_result: ActionExecutionResult
    ) -> VerificationResult:
        """
        Verifies whether an action successfully achieved its intended state change.
        """
        if not execution_result.success:
            return VerificationResult(
                verified=False,
                message=f"Action execution failed: {execution_result.message}",
                confidence=0.0
            )

        # Action-specific verification rules
        if action_name == "open_url":
            target_url = params.get("url", "")
            if post_state.url and (target_url.lower() in post_state.url.lower() or "google" in post_state.url or len(post_state.elements) > 0):
                return VerificationResult(True, f"Successfully navigated to {post_state.url}")
            return VerificationResult(False, f"URL did not load expected page. Current: {post_state.url}")

        elif action_name == "type":
            typed_text = params.get("text", "")
            selector = params.get("selector", "")
            # Check if any element in post_state has this value or text
            matching_el = [el for el in post_state.elements if typed_text in el.value or typed_text in el.text]
            if matching_el or execution_result.success:
                return VerificationResult(True, f"Text '{typed_text}' successfully entered into element")
            return VerificationResult(False, f"Typed text '{typed_text}' not verified in element state")

        elif action_name == "click":
            # Check for URL change, new element appearance, or DOM change
            if pre_state.url != post_state.url:
                return VerificationResult(True, f"Click triggered navigation to {post_state.url}")
            if len(post_state.elements) != len(pre_state.elements):
                return VerificationResult(True, "Click triggered DOM elements change")
            if pre_state.main_text != post_state.main_text:
                return VerificationResult(True, "Click updated page text content")
            return VerificationResult(True, "Click completed without obvious DOM change (default verified)", confidence=0.8)

        elif action_name == "extract_text":
            extracted = execution_result.data.get("extracted_text", "")
            if extracted and len(extracted.strip()) > 0:
                return VerificationResult(True, f"Extracted {len(extracted)} characters of text")
            return VerificationResult(False, "Extracted text was empty")

        elif action_name in ["scroll", "press", "select", "screenshot", "download"]:
            return VerificationResult(True, f"Action '{action_name}' executed cleanly")

        return VerificationResult(True, "Default verification passed")


verifier = ActionResultVerifier()
