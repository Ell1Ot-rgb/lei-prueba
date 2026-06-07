"""
Motor de Lógica Pura y Mundos Hipotéticos
==========================================

Este módulo permite la creación y razonamiento sobre mundos abstractos
definidos puramente por lógica y relaciones simbólicas, sin necesidad
de input sensorial (Capa 1).

Componentes:
- mundo_hipotetico.py: Definición de universos cerrados
- motor_hipotetico.py: Motor de inferencia y razonamiento
- instancia_abstracta.py: Representación de objetos lógicos
- motor_axiomas.py: Procesador de lógica de primer orden
"""

__version__ = "1.0.0"

from .mundo_hipotetico import MundoHipotetico
from .motor_hipotetico import MotorHipotetico
from .instancia_abstracta import InstanciaAbstracta
from .motor_axiomas import MotorAxiomas

__all__ = [
    "MundoHipotetico",
    "MotorHipotetico",
    "InstanciaAbstracta",
    "MotorAxiomas"
]
