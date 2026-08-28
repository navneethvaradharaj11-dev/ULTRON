import pytest
from app.core.intent_engine import IntentEngine


def test_intent_parsing_research():
    intent = IntentEngine.parse_intent("Research the latest advances in quantum computing")
    assert intent.intent_type == "RESEARCH_AND_ANALYSIS"
    assert "research" in intent.required_capabilities


def test_intent_parsing_code():
    intent = IntentEngine.parse_intent("Create a Python script for array sorting and test it")
    assert intent.intent_type == "CODE_GENERATION_AND_TEST"
    assert "code" in intent.required_capabilities
    assert "sandbox" in intent.required_capabilities


def test_intent_parsing_sensitive():
    intent = IntentEngine.parse_intent("Submit this external form")
    assert intent.risk_level == "HIGH"
    assert intent.required_approval is True
