"""
Lógica Modal - Sistema Hexagonal Nivel Metacontexto
Maneja mundos posibles (Posibilidad y Necesidad).
"""
from typing import List, Callable, Any

class MotorModal:
    """Implementa Kripke semantics para mundos lógicos."""
    
    def __init__(self):
        self.mundos_accesibles = {}
    
    def definir_accesibilidad(self, mundo_origen: str, mundo_destino: str):
        if mundo_origen not in self.mundos_accesibles:
            self.mundos_accesibles[mundo_origen] = []
        self.mundos_accesibles[mundo_origen].append(mundo_destino)
        
    def evaluar_necesidad(self, proposicion_fn: Callable[[str], bool], mundo_actual: str) -> bool:
        """
        □P (Necesariamente P): P es verdad en TODOS los mundos accesibles desde el actual.
        """
        accesibles = self.mundos_accesibles.get(mundo_actual, [])
        if not accesibles:
            return True # Verdad vacua
        return all(proposicion_fn(m) for m in accesibles)
    
    def evaluar_posibilidad(self, proposicion_fn: Callable[[str], bool], mundo_actual: str) -> bool:
        """
        ◇P (Posiblemente P): P es verdad en AL MENOS un mundo accesible.
        """
        accesibles = self.mundos_accesibles.get(mundo_actual, [])
        return any(proposicion_fn(m) for m in accesibles)
