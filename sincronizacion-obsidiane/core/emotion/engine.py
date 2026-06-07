from __future__ import annotations
import structlog
from dataclasses import dataclass
from typing import Dict, Tuple

logger = structlog.get_logger()

@dataclass
class PADState:
    pleasure: float = 0.0  # -1.0 to 1.0
    arousal: float = 0.0   # -1.0 to 1.0
    dominance: float = 0.0 # -1.0 to 1.0

class EmotionEngine:
    """
    Affective engine using the PAD (Pleasure-Arousal-Dominance) model.
    Modulates system behavior based on emotional state.
    """
    __slots__ = ('current_state', 'decay_rate')
    
    def __init__(self, decay_rate: float = 0.05):
        self.current_state = PADState()
        self.decay_rate = decay_rate

    def update(self, stimulus: Dict[str, float]):
        """
        Update emotional state based on stimulus vector.
        Stimulus should contain 'valency', 'intensity', 'control'.
        """
        # Integrate stimulus
        self.current_state.pleasure += stimulus.get('valency', 0.0) * 0.1
        self.current_state.arousal += stimulus.get('intensity', 0.0) * 0.1
        self.current_state.dominance += stimulus.get('control', 0.0) * 0.1
        
        # Clamp values
        self.current_state.pleasure = max(-1.0, min(1.0, self.current_state.pleasure))
        self.current_state.arousal = max(-1.0, min(1.0, self.current_state.arousal))
        self.current_state.dominance = max(-1.0, min(1.0, self.current_state.dominance))
        
        logger.debug('emotion_updated', state=self.current_state)

    def decay(self):
        """Return to homeostasis (neutral state) over time."""
        self.current_state.pleasure *= (1.0 - self.decay_rate)
        self.current_state.arousal *= (1.0 - self.decay_rate)
        self.current_state.dominance *= (1.0 - self.decay_rate)

    def get_mood(self) -> str:
        """Classify current PAD state into a named emotion."""
        p, a, d = self.current_state.pleasure, self.current_state.arousal, self.current_state.dominance
        
        if p > 0 and a > 0 and d > 0: return "Exuberant"
        if p > 0 and a > 0 and d < 0: return "Dependent"
        if p > 0 and a < 0 and d > 0: return "Relaxed"
        if p > 0 and a < 0 and d < 0: return "Docile"
        if p < 0 and a > 0 and d > 0: return "Hostile"
        if p < 0 and a > 0 and d < 0: return "Anxious"
        if p < 0 and a < 0 and d > 0: return "Disdainful"
        if p < 0 and a < 0 and d < 0: return "Bored"
        return "Neutral"
