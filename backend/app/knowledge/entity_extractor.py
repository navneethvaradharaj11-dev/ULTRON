import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("ULTRON.EntityExtractor")

ENTITY_PATTERNS = [
    (re.compile(r'\b(Python|JavaScript|TypeScript|FastAPI|Dart|Flutter|SQL|MySQL|C\+\+|Java|Docker|Git)\b', re.IGNORECASE), "TECHNOLOGY"),
    (re.compile(r'\b(CPU|RAM|GPU|Scheduling|Algorithm|Process|Thread|Memory|Network)\b', re.IGNORECASE), "CONCEPT"),
    (re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'), "PERSON_OR_ORG"),
]


class EntityExtractor:
    """Extracts entities (People, Technologies, Concepts, Organizations) from knowledge chunks."""

    @staticmethod
    def extract_entities(content: str) -> List[Dict[str, Any]]:
        if not content:
            return []

        extracted = []
        seen = set()

        for pattern, ent_type in ENTITY_PATTERNS:
            matches = pattern.findall(content)
            for m in matches:
                clean_m = m.strip()
                if clean_m.lower() not in seen and len(clean_m) > 2:
                    seen.add(clean_m.lower())
                    extracted.append({
                        "name": clean_m,
                        "entity_type": ent_type,
                        "confidence": 0.9,
                        "evidence": f"Found match '{clean_m}' in text segment"
                    })

        return extracted
