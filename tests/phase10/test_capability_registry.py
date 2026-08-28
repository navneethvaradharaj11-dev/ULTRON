import pytest
from app.core.capability_registry import CapabilityRegistry


def test_capability_registry_list():
    reg = CapabilityRegistry()
    caps = reg.list_capabilities()
    assert len(caps) >= 15
    names = [c.name for c in caps]
    assert "memory" in names
    assert "knowledge" in names
    assert "browser" in names
    assert "sandbox" in names
    assert "workflows" in names
    assert "autonomy" in names
    assert "github" in names


def test_capability_health():
    reg = CapabilityRegistry()
    health = reg.get_system_health()
    assert health["status"] == "HEALTHY"
    assert health["total_capabilities"] >= 15

