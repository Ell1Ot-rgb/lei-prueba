"""
Instancia Abstracta - Lógica Pura
==================================

Representa un objeto o entidad dentro de un mundo hipotético.
A diferencia de una InstanciaFenomenologica, esta no tiene qualia
ni origen sensorial, solo propiedades lógicas.
"""

from typing import Dict, Any
import uuid


class InstanciaAbstracta:
    """
    Objeto puramente lógico dentro de un mundo hipotético.
    """
    
    def __init__(
        self,
        concepto: str,
        propiedades: Dict[str, Any],
        mundo_origen: str,
        tipo_yo: str = "LOGICO",
        coherencia: float = 1.0
    ):
        self.id = str(uuid.uuid4())
        self.concepto = concepto
        self.propiedades = propiedades
        self.mundo_origen = mundo_origen
        self.tipo_yo = tipo_yo
        self.coherencia = coherencia  # En lógica pura suele ser 1.0
        
        # Relaciones con otras instancias
        self.relaciones = []
        
    def agregar_relacion(self, tipo: str, destino_id: str, props: Dict = None):
        """Agrega una relación dirigida hacia otra instancia."""
        self.relaciones.append({
            "tipo": tipo,
            "destino": destino_id,
            "propiedades": props or {}
        })
        
    def cumple_predicado(self, predicado: str, valor: Any = True) -> bool:
        """Verifica si la instancia cumple una propiedad lógica."""
        return self.propiedades.get(predicado) == valor
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "concepto": self.concepto,
            "propiedades": self.propiedades,
            "mundo": self.mundo_origen,
            "tipo": self.tipo_yo,
            "coherencia": self.coherencia
        }
    
    def __repr__(self):
        return f"InstanciaAbstracta('{self.concepto}', props={len(self.propiedades)})"
