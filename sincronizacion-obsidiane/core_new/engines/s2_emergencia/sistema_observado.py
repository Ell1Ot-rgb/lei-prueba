"""
Sistema Observado - Emergencia de Conceptos
============================================

Representa un sistema cuyas propiedades desconocemos pero que podemos
observar a través de su comportamiento.
"""

from typing import Dict, Any, List
from datetime import datetime
import uuid


class SistemaObservado:
    """
    Sistema con propiedades ocultas que se revelan mediante interacciones.
    
    Ejemplo:
        sistema = SistemaObservado("sistema_A", num_componentes=100)
        # El sistema tiene entropía, pero no lo declaramos
        # Se descubrirá mediante experimentos
    """
    
    def __init__(self, nombre: str, num_componentes: int = 100):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.num_componentes = num_componentes
        
        # Propiedades ocultas (no accesibles directamente)
        self._propiedades_ocultas = {}
        
        # Historial de estados observados
        self.estados_observados = []
        
        # Resultados de experimentos
        self.experimentos_realizados = {}
        
        # Timestamp de creación
        self.creado_en = datetime.now()
        
    def definir_propiedad_oculta(self, nombre: str, valor: Any):
        """
        Define una propiedad que existe ontológicamente pero que
        el sistema debe descubrir mediante observaciones.
        
        Args:
            nombre: Nombre de la propiedad (ej: "entropia", "temperatura")
            valor: Valor de la propiedad
        """
        self._propiedades_ocultas[nombre] = valor
    
    def registrar_estado(self, descripcion: str, datos: Dict[str, Any] = None):
        """
        Registra un estado observable del sistema.
        
        Args:
            descripcion: Descripción textual del estado
            datos: Datos medibles del estado
        """
        estado = {
            "timestamp": datetime.now(),
            "descripcion": descripcion,
            "datos": datos or {}
        }
        self.estados_observados.append(estado)
        return estado
    
    def registrar_experimento(self, experimento_id: str, resultado: Dict[str, Any]):
        """
        Registra el resultado de un experimento sobre este sistema.
        
        Args:
            experimento_id: ID del experimento
            resultado: Resultados observables
        """
        self.experimentos_realizados[experimento_id] = {
            "timestamp": datetime.now(),
            "resultado": resultado
        }
    
    def obtener_comportamientos(self) -> Dict[str, List]:
        """
        Retorna todos los comportamientos observables del sistema.
        
        Returns:
            Diccionario con estados y experimentos
        """
        return {
            "estados": self.estados_observados,
            "experimentos": self.experimentos_realizados
        }
    
    def _verificar_propiedad_oculta(self, nombre: str) -> Any:
        """
        SOLO para validación interna. No debe usarse en el flujo normal.
        Permite verificar si la emergencia fue correcta.
        """
        return self._propiedades_ocultas.get(nombre)
    
    def __repr__(self):
        return f"SistemaObservado('{self.nombre}', componentes={self.num_componentes}, estados={len(self.estados_observados)})"
