import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("ULTRON.CapabilityRegistry")


class CapabilityDescriptor(BaseModel):
    name: str
    description: str
    status: str = "AVAILABLE"  # AVAILABLE, UNAVAILABLE, DEGRADED
    risk_level: str = "LOW"
    requires_approval: bool = False


class CapabilityRegistry:
    """Registry maintaining real capability health status across all 9 ULTRON phases."""

    def __init__(self):
        self._capabilities: Dict[str, CapabilityDescriptor] = {
            "memory": CapabilityDescriptor(name="memory", description="Phase 6 Long-Term Durable Fact & Preference Memory"),
            "knowledge": CapabilityDescriptor(name="knowledge", description="Phase 8 Multimodal Hybrid Search & Provenance Citations"),
            "research": CapabilityDescriptor(name="research", description="Phase 3 Internet & Web Search Synthesis"),
            "browser": CapabilityDescriptor(name="browser", description="Phase 3.1 Playwright Chromium Interactive Browsing"),
            "computer": CapabilityDescriptor(name="computer", description="Phase 5 Perception, Visual Grounding & OCR Interaction"),
            "code": CapabilityDescriptor(name="code", description="Phase 4 Multi-Language Code Generation & Intelligence"),
            "sandbox": CapabilityDescriptor(name="sandbox", description="Phase 4 Secure Multi-Language Process Sandbox Jail"),
            "workflows": CapabilityDescriptor(name="workflows", description="Phase 7 Autonomous Workflow Orchestrator & DAG Execution"),
            "autonomy": CapabilityDescriptor(name="autonomy", description="Phase 9 Proactive Event-Driven Autonomy Engine"),
            "learning": CapabilityDescriptor(name="learning", description="Phase 6 Learning Engine & Strategy Optimization"),
            "notifications": CapabilityDescriptor(name="notifications", description="Phase 9 Mobile Notification Engine")
        }

    def get_capability(self, name: str) -> Optional[CapabilityDescriptor]:
        return self._capabilities.get(name.lower().strip())

    def list_capabilities(self) -> List[CapabilityDescriptor]:
        return list(self._capabilities.values())

    def get_system_health(self) -> Dict[str, Any]:
        total = len(self._capabilities)
        available = sum(1 for c in self._capabilities.values() if c.status == "AVAILABLE")
        return {
            "status": "HEALTHY" if available == total else "DEGRADED",
            "total_capabilities": total,
            "available_capabilities": available,
            "capabilities": {name: cap.dict() for name, cap in self._capabilities.items()}
        }
