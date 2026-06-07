"""
Motor de Axiomas - Lógica Pura
"""
from typing import List, Dict, Any
import re

class Axioma:
    def __init__(self, regla: str):
        self.regla_raw = regla
        self.parsed = self._parse(regla)
        
    def _parse(self, regla: str) -> Dict[str, Any]:
        if "->" in regla or "→" in regla:
            parts = re.split(r'->|→', regla)
            if len(parts) == 2:
                premisa = self._extract_predicate(parts[0])
                conclusion = self._extract_predicate(parts[1])
                return {
                    "tipo": "implicacion",
                    "premisa": premisa,
                    "conclusion": conclusion
                }
        return {"tipo": "desconocido", "raw": regla}
    
    def _extract_predicate(self, text: str) -> str:
        match = re.search(r'(\w+)\(', text)
        if match:
            return match.group(1)
        return text.strip()

class MotorAxiomas:
    def __init__(self):
        self.axiomas = []
        
    def agregar_axioma(self, regla: str):
        self.axiomas.append(Axioma(regla))
        
    def inferir_propiedades(self, instancia) -> Dict[str, Any]:
        nuevas_props = {}
        cambio = True
        while cambio:
            cambio = False
            for axioma in self.axiomas:
                if axioma.parsed["tipo"] == "implicacion":
                    premisa = axioma.parsed["premisa"]
                    conclusion = axioma.parsed["conclusion"]
                    
                    cumple_premisa = (
                        instancia.propiedades.get(premisa) is True or
                        nuevas_props.get(premisa) is True
                    )
                    
                    if cumple_premisa:
                        ya_tiene_conclusion = (
                            instancia.propiedades.get(conclusion) is True or
                            nuevas_props.get(conclusion) is True
                        )
                        
                        if not ya_tiene_conclusion:
                            nuevas_props[conclusion] = True
                            cambio = True
                            
        return nuevas_props
