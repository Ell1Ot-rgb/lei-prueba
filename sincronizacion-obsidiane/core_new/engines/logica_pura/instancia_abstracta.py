"""
Instancia Abstracta - Lógica Pura
"""
from typing import Dict, Any
import uuid

class InstanciaAbstracta:
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
        self.coherencia = coherencia
        self.relaciones = []
        
    def agregar_relacion(self, tipo: str, destino_id: str, props: Dict = None):
        self.relaciones.append({
            "tipo": tipo,
            "destino": destino_id,
            "propiedades": props or {}
        })
        
    def cumple_predicado(self, predicado: str, valor: Any = True) -> bool:
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
