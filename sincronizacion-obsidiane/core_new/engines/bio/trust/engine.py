from __future__ import annotations
import structlog
from typing import Dict

logger = structlog.get_logger()

class TrustEngine:
    """
    Manages trust scores for external entities and internal components.
    """
    __slots__ = ('scores',)
    
    def __init__(self):
        self.scores: Dict[str, float] = {}

    def update_trust(self, entity_id: str, delta: float):
        """Update trust score for an entity."""
        current = self.scores.get(entity_id, 0.5)
        self.scores[entity_id] = max(0.0, min(1.0, current + delta))
        logger.info('trust_updated', entity=entity_id, score=self.scores[entity_id])

    def is_trusted(self, entity_id: str, threshold: float = 0.7) -> bool:
        return self.scores.get(entity_id, 0.5) >= threshold
