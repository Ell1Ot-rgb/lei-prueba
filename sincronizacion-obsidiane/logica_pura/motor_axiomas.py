"""
Motor de Axiomas - Lógica Pura
===============================

Procesa reglas lógicas y realiza inferencias deductivas.
"""

from typing import List, Dict, Any
import re


class Axioma:
    """Representa una regla lógica formal."""
    def __init__(self, regla: str):
        self.regla_raw = regla
        self.parsed = self._parse(regla)
        
    def _parse(self, regla: str) -> Dict[str, Any]:
        """
        Parsea una regla simple de tipo:
        "∀x (P(x) -> Q(x))"
        """
        # Implementación simplificada para demostración
        # Detectar implicación simple: propiedad1 -> propiedad2
        if "->" in regla or "→" in regla:
            parts = re.split(r'->|→', regla)
            if len(parts) == 2:
                # Extraer nombres de predicados (muy simplificado)
                premisa = self._extract_predicate(parts[0])
                conclusion = self._extract_predicate(parts[1])
                return {
                    "tipo": "implicacion",
                    "premisa": premisa,
                    "conclusion": conclusion
                }
        return {"tipo": "desconocido", "raw": regla}
    
    def _extract_predicate(self, text: str) -> str:
        """Extrae 'comestible' de 'comestible(x)'."""
        match = re.search(r'(\w+)\(', text)
        if match:
            return match.group(1)
        return text.strip()


class MotorAxiomas:
    """
    Motor de inferencia lógica.
    """
    
    def __init__(self):
        self.axiomas = []
        
    def agregar_axioma(self, regla: str):
        """Agrega un nuevo axioma al motor."""
        self.axiomas.append(Axioma(regla))
        
    def inferir_propiedades(self, instancia) -> Dict[str, Any]:
        """
        Deduce nuevas propiedades para una instancia basándose en axiomas.
        """
        nuevas_props = {}
        
        # Iterar hasta que no haya nuevos cambios (punto fijo)
        cambio = True
        while cambio:
            cambio = False
            for axioma in self.axiomas:
                if axioma.parsed["tipo"] == "implicacion":
                    premisa = axioma.parsed["premisa"]
                    conclusion = axioma.parsed["conclusion"]
                    
                    # Verificar si cumple premisa (en props originales o inferidas)
                    cumple_premisa = (
                        instancia.propiedades.get(premisa) is True or
                        nuevas_props.get(premisa) is True
                    )
                    
                    # Si cumple premisa y no tiene conclusión, inferir
                    if cumple_premisa:
                        ya_tiene_conclusion = (
                            instancia.propiedades.get(conclusion) is True or
                            nuevas_props.get(conclusion) is True
                        )
                        
                        if not ya_tiene_conclusion:
                            nuevas_props[conclusion] = True
                            cambio = True
                            
        return nuevas_props
