import pytest
from app.autonomy.cooldown import CooldownManager


def test_cooldown_windows():
    rule_id = "test_rule_cooldown_123"
    assert CooldownManager.is_in_cooldown(rule_id, 300) is False

    CooldownManager.mark_executed(rule_id)
    assert CooldownManager.is_in_cooldown(rule_id, 300) is True
