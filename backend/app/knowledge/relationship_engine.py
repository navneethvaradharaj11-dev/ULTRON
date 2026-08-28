import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ULTRON.RelationshipEngine")


class RelationshipEngine:
    """Infers relationships between entities with strict provenance tracking."""

    @staticmethod
    def infer_relationships(entities: List[Dict[str, Any]], source_filename: str) -> List[Dict[str, Any]]:
        if len(entities) < 2:
            return []

        relationships = []
        for i in range(len(entities) - 1):
            e1 = entities[i]
            e2 = entities[i + 1]
            rel_type = "RELATED_TO"
            if e1["entity_type"] == "TECHNOLOGY" and e2["entity_type"] == "CONCEPT":
                rel_type = "USED_FOR"
            elif e1["entity_type"] == "PERSON_OR_ORG" and e2["entity_type"] == "TECHNOLOGY":
                rel_type = "CREATED_BY"

            relationships.append({
                "source_entity": e1["name"],
                "target_entity": e2["name"],
                "relation_type": rel_type,
                "provenance": f"Co-occurred in {source_filename}",
                "confidence": 0.85
            })

        return relationships
