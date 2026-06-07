"""
Concepto Emergente - Emergencia de Conceptos
=============================================

Representa un concepto abstracto que emerge de patrones relacionales.
"""

from typing import Dict, List, Any
from datetime import datetime
import uuid


class ConceptoEmergente:
    """
    Concepto abstracto (como entropía) que emerge sin definición previa.
    """
    
    def __init__(self, nombre_provisional: str):
        self.id = str(uuid.uuid4())
        self.nombre_provisional = nombre_provisional
        self.nombre_real = None  # Se asigna al hacer grounding
        
        # Definiciones emergentes
        self.definicion_relacional = ""
        self.definicion_formal = None
        
        # Valores medidos para diferentes sistemas
        self.valores = {}  # {sistema_nombre: valor_P}
        
        # Leyes descubiertas
        self.leyes_cualitativas = []
        
        # Predicciones que se pueden hacer
        self.predicciones = []
        
        # Certeza global
        self.certeza = 0.0
        
        # Metadata de emergencia
        self.num_observaciones = 0
        self.num_sistemas_estudiados = 0
        self.creado_en = datetime.now()
        self.grounded_en = None
        
    def asignar_valores(self, sistema_nombre: str, valor: float):
        """
        Asigna un valor de la propiedad P a un sistema específico.
        """
        self.valores[sistema_nombre] = valor
    
    def agregar_ley(self, ley: str):
        """
        Agrega una ley cualitativa descubierta.
        
        Ejemplo:
            concepto.agregar_ley("P nunca decrece espontáneamente")
        """
        self.leyes_cualitativas.append(ley)
    
    def agregar_prediccion(self, prediccion: str):
        """
        Agrega una predicción basada en el concepto.
        """
        self.predicciones.append(prediccion)
    
    def ground_with_theory(
        self,
        nombre_teorico: str,
        formula: str = None,
        certeza_match: float = 0.0
    ):
        """
        Conecta el concepto emergente con teoría conocida.
        
        Args:
            nombre_teorico: Nombre del concepto en la teoría (ej: "ENTROPÍA")
            formula: Fórmula teórica (ej: "S = k ln Ω")
            certeza_match: Qué tan bien coincide (0-1)
        """
        self.nombre_real = nombre_teorico
        self.definicion_formal = formula
        self.certeza = certeza_match
        self.grounded_en = datetime.now()
    
    def generar_reporte(self) -> Dict[str, Any]:
        """
        Genera un reporte completo del concepto emergido.
        """
        return {
            "id": self.id,
            "nombre_provisional": self.nombre_provisional,
            "nombre_real": self.nombre_real or "NO DETERMINADO",
            "definicion_relacional": self.definicion_relacional,
            "definicion_formal": self.definicion_formal,
            
            "valores_medidos": self.valores,
            "num_sistemas": len(self.valores),
            
            "leyes_descubiertas": self.leyes_cualitativas,
            "num_leyes": len(self.leyes_cualitativas),
            
            "predicciones": self.predicciones,
            
            "certeza_global": self.certeza,
            "observaciones_totales": self.num_observaciones,
            
            "emergencia": {
                "creado_en": self.creado_en.isoformat(),
                "grounded_en": self.grounded_en.isoformat() if self.grounded_en else None,
                "tiempo_emergencia": (self.grounded_en - self.creado_en).total_seconds() if self.grounded_en else None
            }
        }
    
    def __repr__(self):
        nombre = self.nombre_real or self.nombre_provisional
        return f"ConceptoEmergente('{nombre}', sistemas={len(self.valores)}, certeza={self.certeza:.2f})"
