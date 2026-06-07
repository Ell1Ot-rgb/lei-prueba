"""
Core Package - Sistema YO Estructural v3.0
"""

from .sistema_principal import SistemaYoEstructural
from .database import Neo4jConnection

__all__ = [
    'SistemaYoEstructural',
    'Neo4jConnection'
]

__version__ = '3.0.0'
