from __future__ import annotations
import structlog
from typing import Dict, List, Any

logger = structlog.get_logger()

class GovernanceEngine:
    """
    Enforces ethical policies and operational constraints.
    Acts as a 'superego' for the system.
    """
    __slots__ = ('policies', 'violations')
    
    def __init__(self, policies: Dict[str, Any]):
        self.policies = policies
        self.violations: List[Dict] = []

    def check_action(self, action: str, context: Dict) -> bool:
        """
        Verify if an action is permitted under current policies.
        """
        # Example policy: "max_cpu"
        if 'max_cpu' in self.policies:
            if context.get('cpu_usage', 0) > self.policies['max_cpu']:
                self._log_violation(action, "CPU limit exceeded")
                return False
        
        # Example policy: "allowed_ops"
        if 'allowed_ops' in self.policies:
            if action not in self.policies['allowed_ops']:
                self._log_violation(action, "Operation not allowed")
                return False
                
        return True

    def _log_violation(self, action: str, reason: str):
        violation = {"action": action, "reason": reason}
        self.violations.append(violation)
        logger.warning('governance_violation', **violation)
