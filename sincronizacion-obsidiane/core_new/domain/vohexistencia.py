import uuid
import datetime
import yaml
import os
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Vohexistencia:
    """Nivel -1: Agrupación de instancias con patrón compartido"""
    
    def __init__(self, nombre: str = "", descripcion: str = ""):
        self.id = f"vohex_{str(uuid.uuid4())[:8]}"
        self.nombre = nombre
        self.descripcion = descripcion
        self.instancias = []  # IDs de instancias participantes
        self.constante_emergente = ""  # Patrón compartido
        self.peso_coexistencial = 0.0
        self.ejes_relacionales = []  # Tipos de relación
        self.timestamp = datetime.datetime.now().isoformat()
    
    def agregar_instancia(self, instancia_id: str, peso_contribucion: float = 1.0):
        """Agrega una instancia a la vohexistencia"""
        if instancia_id not in [i["id"] for i in self.instancias]:
            self.instancias.append({
                "id": instancia_id,
                "peso_contribucion": peso_contribucion,
                "timestamp_agregado": datetime.datetime.now().isoformat()
            })
            self._recalcular_peso_coexistencial()
    
    def establecer_constante_emergente(self, constante: str):
        """Define el patrón emergente de la vohexistencia"""
        self.constante_emergente = constante
    
    def agregar_eje_relacional(self, eje: str):
        """Agrega un eje de relación"""
        if eje not in self.ejes_relacionales:
            self.ejes_relacionales.append(eje)
    
    def _recalcular_peso_coexistencial(self):
        """Recalcula el peso basado en las instancias participantes"""
        if not self.instancias:
            self.peso_coexistencial = 0.0
            return
        
        # Peso basado en número de instancias y sus contribuciones
        peso_total = sum(inst["peso_contribucion"] for inst in self.instancias)
        factor_cohesion = min(1.0, len(self.instancias) / 5.0)  # Máximo con 5 instancias
        
        self.peso_coexistencial = (peso_total / len(self.instancias)) * factor_cohesion
    
    def evaluar_coherencia(self) -> float:
        """Evalúa la coherencia interna de la vohexistencia"""
        if len(self.instancias) < 2:
            return 0.0
        
        # Coherencia basada en peso y número de ejes relacionales
        coherencia_peso = self.peso_coexistencial
        coherencia_relacional = min(1.0, len(self.ejes_relacionales) / 3.0)
        
        return (coherencia_peso + coherencia_relacional) / 2
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "instancias": self.instancias,
            "constante_emergente": self.constante_emergente,
            "peso_coexistencial": self.peso_coexistencial,
            "ejes_relacionales": self.ejes_relacionales,
            "coherencia": self.evaluar_coherencia(),
            "timestamp": self.timestamp
        }
    
    def guardar(self, ruta_base: str) -> str:
        """Guarda la vohexistencia en formato YAML"""
        ruta_archivo = os.path.join(ruta_base, f"{self.id}.yaml")
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
        return ruta_archivo