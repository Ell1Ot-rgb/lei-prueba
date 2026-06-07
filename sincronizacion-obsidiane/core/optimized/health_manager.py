"""
Health Manager - Fusión de Apoptosis + Immune + Governance
==========================================================

ESPECIFICACIÓN:
- Componentes monitoreados: hasta 1000
- Salud: float16 (2 bytes por componente)
- Políticas: hasta 50 reglas simples
- Memoria total: 2 KB (salud) + 10 KB (políticas) = 12 KB
"""

import numpy as np
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Any
from collections import defaultdict


@dataclass
class Policy:
    """Política de gobernanza."""
    name: str
    condition: Callable[[Dict[str, float]], bool]
    action: Callable[[], None]
    priority: int = 0


class HealthManager:
    """
    Gestor unificado de salud del sistema.
    Combina funcionalidades de:
    - Apoptosis (eliminación de componentes defectuosos)
    - Immune Engine (protección contra amenazas)
    - Governance (aplicación de políticas)
    """
    
    def __init__(self, max_components: int = 1000, 
                 theta: float = 0.3, h_min: float = 0.8):
        self.max_components = max_components
        self.theta = theta  # Umbral de apoptosis
        self.h_min = h_min  # Salud mínima de reemplazo
        
        # Salud de componentes (float16 para ahorrar memoria)
        self.health = np.full(max_components, 0.8, dtype=np.float16)
        self.active = np.zeros(max_components, dtype=np.bool_)
        self.active_count = 0
        
        # Políticas de gobernanza
        self.policies: List[Policy] = []
        
        # Métricas para immune engine
        self.event_counts = defaultdict(int)
        self.last_reset = time.time()
        self.rate_limit = 100  # eventos por segundo
    
    def register_component(self) -> int:
        """Registrar nuevo componente, retorna ID."""
        if self.active_count >= self.max_components:
            # Buscar componente para reciclar
            min_idx = int(np.argmin(np.where(self.active, self.health, np.inf)))
            self.health[min_idx] = self.h_min
            return min_idx
        
        idx = int(np.argmax(~self.active))
        self.active[idx] = True
        self.health[idx] = self.h_min
        self.active_count += 1
        return idx
    
    def update_health(self, component_id: int, delta: float):
        """Actualizar salud de un componente."""
        if 0 <= component_id < self.max_components and self.active[component_id]:
            self.health[component_id] = np.clip(
                float(self.health[component_id]) + delta, 0.0, 1.0
            )
    
    def run_apoptosis(self):
        """Ejecutar ciclo de apoptosis."""
        # Degradación natural
        self.health[self.active] *= 0.995
        
        # Detectar componentes para eliminar
        to_remove = self.active & (self.health < self.theta)
        
        if to_remove.any():
            # Reemplazar con componentes frescos
            n_remove = int(to_remove.sum())
            self.health[to_remove] = self.h_min + np.random.rand(n_remove) * (1 - self.h_min)
    
    def check_rate_limit(self, source: str) -> bool:
        """Immune engine: verificar rate limiting."""
        current = time.time()
        if current - self.last_reset > 1.0:
            self.event_counts.clear()
            self.last_reset = current
        
        self.event_counts[source] += 1
        return self.event_counts[source] <= self.rate_limit
    
    def add_policy(self, policy: Policy):
        """Registrar política de gobernanza."""
        if len(self.policies) < 50:
            self.policies.append(policy)
            self.policies.sort(key=lambda p: -p.priority)
    
    def evaluate_policies(self, metrics: Dict[str, float]) -> List[str]:
        """Evaluar políticas y ejecutar acciones."""
        triggered = []
        for policy in self.policies:
            try:
                if policy.condition(metrics):
                    policy.action()
                    triggered.append(policy.name)
            except Exception:
                pass  # Ignorar errores en políticas
        return triggered
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema."""
        active_health = self.health[self.active]
        return {
            'active_components': int(self.active_count),
            'avg_health': float(active_health.mean()) if len(active_health) > 0 else 0.0,
            'min_health': float(active_health.min()) if len(active_health) > 0 else 0.0,
            'max_health': float(active_health.max()) if len(active_health) > 0 else 0.0,
            'policies_count': len(self.policies)
        }
