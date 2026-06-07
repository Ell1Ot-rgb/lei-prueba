import uuid
import datetime
import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class InstanciaExistencia:
    """Nivel -3: Primera comparación estructurada A ↔ B"""
    
    def __init__(self, propiedades: Dict[str, Any], proto_origen: str = ""):
        self.id = f"inst_{str(uuid.uuid4())[:8]}"
        self.propiedades = propiedades
        self.proto_origen = proto_origen
        self.activacion_actual = 0.0
        self.timestamp = datetime.datetime.now().isoformat()
        self.relaciones = []  # Lista de IDs de otras instancias relacionadas
    
    def calcular_activacion(self, contexto_actual: Dict) -> float:
        """Calcula la activación basada en el contexto actual"""
        activacion = 0.0
        
        # Evaluar coincidencias con contexto
        for prop, valor in self.propiedades.items():
            if prop in contexto_actual:
                if contexto_actual[prop] == valor:
                    activacion += 0.2
                elif self._son_similares(contexto_actual[prop], valor):
                    activacion += 0.1
        
        self.activacion_actual = min(1.0, activacion)
        return self.activacion_actual
    
    def _son_similares(self, valor1: Any, valor2: Any) -> bool:
        """Evalúa similitud básica entre valores"""
        if isinstance(valor1, str) and isinstance(valor2, str):
            return valor1.lower() in valor2.lower() or valor2.lower() in valor1.lower()
        return False
    
    def agregar_relacion(self, instancia_id: str, tipo_relacion: str = "similar"):
        """Agrega una relación con otra instancia"""
        self.relaciones.append({
            "instancia_id": instancia_id,
            "tipo": tipo_relacion,
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "propiedades": self.propiedades,
            "proto_origen": self.proto_origen,
            "activacion_actual": self.activacion_actual,
            "relaciones": self.relaciones,
            "timestamp": self.timestamp
        }
    
    def guardar(self, ruta_base: str) -> str:
        """Guarda la instancia en formato YAML"""
        ruta_archivo = os.path.join(ruta_base, f"{self.id}.yaml")
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
        return ruta_archivo