"""
Motor de Emergencia de Conceptos Relacionales
==============================================

Este módulo permite que conceptos abstractos (como entropía, momentum, etc.)
emerjan a partir de patrones de interacciones observables, sin necesidad de
sensores directos ni definiciones previas.

Componentes:
- motor_emergencia.py: Orquestador principal
- sistema_observado.py: Sistemas que se estudian
- experimento.py: Experimentos para revelar propiedades
- patron_relacional.py: Detección de patrones
- concepto_emergente.py: Representación de conceptos descubiertos
"""

__version__ = "1.0.0"
__author__ = "YO Estructural v3.0"

from .motor_emergencia import MotorEmergenciaConceptos
from .sistema_observado import SistemaObservado
from .experimento import Experimento, TipoExperimento
from .patron_relacional import PatronRelacional
from .concepto_emergente import ConceptoEmergente

__all__ = [
    "MotorEmergenciaConceptos",
    "SistemaObservado",
    "Experimento",
    "TipoExperimento",
    "PatronRelacional",
    "ConceptoEmergente"
]
