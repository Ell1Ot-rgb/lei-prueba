import uuid
import datetime
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class PreInstancia:
    """Nivel -4: Dato crudo sin contexto ni relación"""
    
    def __init__(self, dato_crudo: Any, origen: str = "desconocido"):
        self.id = f"ø_{str(uuid.uuid4())[:8]}"
        self.dato_crudo = dato_crudo
        self.origen = origen
        self.timestamp = datetime.datetime.now().isoformat()
        self.procesado = False
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "dato_crudo": str(self.dato_crudo),
            "origen": self.origen,
            "timestamp": self.timestamp,
            "procesado": self.procesado
        }
    
    def marcar_procesado(self):
        """Marca la preinstancia como procesada"""
        self.procesado = True