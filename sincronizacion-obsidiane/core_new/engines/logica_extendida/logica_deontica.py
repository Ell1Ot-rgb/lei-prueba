"""
Lógica Deóntica - Sistema Hexagonal (Nivel Metacontexto y Voluntad)
Normas, Obligaciones y Permisos del ente cibernético.
"""
from typing import Callable, Any, List

class MotorDeontico:
    """Regula las obligaciones normativas del autómata."""
    
    def __init__(self):
        self.obligaciones = [] # lista de fns
        self.prohibiciones = [] # lista de fns
        
    def agregar_obligacion(self, regla_fn: Callable[[Any], bool]):
        """O P: Es obligatorio que P"""
        self.obligaciones.append(regla_fn)
        
    def agregar_prohibicion(self, regla_fn: Callable[[Any], bool]):
        """F P: Está prohibido P"""
        self.prohibiciones.append(regla_fn)
        
    def es_permitido(self, evento: Any) -> bool:
        """
        P P: Está permitido P. (No está prohibido).
        """
        return not any(prohibicion(evento) for prohibicion in self.prohibiciones)
    
    def auditar_estado(self, estado: Any) -> List[str]:
        """Verifica si el estado actual cumple con las obligaciones."""
        violaciones = []
        for i, ob in enumerate(self.obligaciones):
            if not ob(estado):
                violaciones.append(f"Obligacion {i} no cumplida temporalmente.")
        return violaciones
