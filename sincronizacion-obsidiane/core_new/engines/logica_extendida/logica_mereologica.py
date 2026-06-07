"""
Lógica Mereológica - Sistema Hexagonal (Ontología Formal Fundacional)
Relaciones Parte-Todo.
"""
from typing import Dict, List, Set

class MotorMereologico:
    """Implementa composición y fragmentación ontológica."""
    
    def __init__(self):
        self.partes_de: Dict[str, Set[str]] = {} # Todo -> Partes
        
    def registrar_composicion(self, todo_id: str, parte_id: str):
        """Añade una parte a un todo."""
        if todo_id not in self.partes_de:
            self.partes_de[todo_id] = set()
        self.partes_de[todo_id].add(parte_id)
        
    def es_parte_propia(self, parte: str, todo: str) -> bool:
        """
        x es parte propia de y si x es parte de y pero x != y.
        Se evalúa transitividad.
        """
        if parte == todo:
            return False
            
        visitados = set()
        def buscar_recursivo(objetivo_todo, actual_parte):
            if objetivo_todo in visitados: return False
            visitados.add(objetivo_todo)
            componentes = self.partes_de.get(objetivo_todo, set())
            if actual_parte in componentes: return True
            for sub_todo in componentes:
                if buscar_recursivo(sub_todo, actual_parte):
                    return True
            return False
            
        return buscar_recursivo(todo, parte)
    
    def fusion_mereologica(self, nombre_nuevo: str, particulas_id: List[str]):
        """Genera un nuevo todo a partir de las particulas entregadas."""
        self.partes_de[nombre_nuevo] = set(particulas_id)
        return nombre_nuevo
