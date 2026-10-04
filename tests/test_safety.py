import pytest
from backend.app.safety.policy import safety_policy, RiskLevel
from backend.app.safety.approval import approval_manager, AgentMode
from backend.app.safety.validator import input_validator


def test_safety_policy_risk_evaluation():
    risk_low = safety_policy.evaluate_action_risk("open_url", {"url": "https://google.com"})
    assert risk_low == RiskLevel.LOW

    risk_sensitive = safety_policy.evaluate_action_risk("click", {"text": "Buy Now $499"})
    assert risk_sensitive == RiskLevel.SENSITIVE


def test_approval_manager_modes():
    approval_manager.mode = AgentMode.ASSISTED
    assert approval_manager.requires_approval("open_url", {}) is False
    assert approval_manager.requires_approval("click", {"text": "Confirm Payment"}) is True

    approval_manager.mode = AgentMode.OBSERVE
    assert approval_manager.requires_approval("click", {"text": "Any Button"}) is True


def test_input_validator_ssrf_and_filename():
    valid, url = input_validator.validate_url("https://example.com")
    assert valid is True

    invalid, msg = input_validator.validate_url("file:///etc/passwd")
    assert invalid is False

    sanitized = input_validator.sanitize_filename("../../etc/passwd")
    assert "/" not in sanitized and "\\" not in sanitized
