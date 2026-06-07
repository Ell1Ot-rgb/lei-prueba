"""
⊡ Macrocontexto — Nivel +2: Agrupación de contextos
⊠ Metacontexto — Nivel +3: Reflexión sobre contextos
====================================================

Motor: YO ∞ (Variación Eidética)
Entrada: Lista de Contextos relacionados
Salida:  Patrón transversal emergente + reflexión meta

Base teórica (Husserl):
    Wesensschau (Intuición eidética): Al comparar múltiples contextos
    concretos, emerge la ESENCIA (eidos) que los unifica.
    Es el paso de lo particular a lo universal, de forma emergente.

Simbología:
    ⊡  →  Macrocontexto (agrupación de contextos)
    ⊠  →  Metacontexto (reflexión sobre contextos)
    ⊞→⊡  Contextos generan Macrocontexto (AGRUPA ⊕)
    ⊡→⊠  Macrocontextos generan Metacontexto (SURGE_DE ↗)
"""

import uuid
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Macrocontexto:
    """
    ⊡ Nivel +2: Agrupación de contextos por fenómenos compartidos.

    Emerge cuando múltiples contextos comparten fenómenos similares,
    revelando patrones transversales que ningún contexto individual
    podía mostrar.

    Attributes:
        id: Identificador único con prefijo 'macro_'
        nombre: Nombre descriptivo del macrocontexto
        contextos_incluidos: IDs de contextos agrupados
        fenomenos_compartidos: Fenómenos que aparecen en múltiples contextos
        patron_emergente: Descripción del patrón transversal
        coherencia: Coherencia del macrocontexto [0.0-1.0]
    """

    # ── Identificación ──────────────────────────────────
    id: str = field(default_factory=lambda: f"macro_{str(uuid.uuid4())[:8]}")
    nombre: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    # ── Contenido ───────────────────────────────────────
    contextos_incluidos: List[str] = field(default_factory=list)
    fenomenos_compartidos: List[str] = field(default_factory=list)
    patron_emergente: str = ""
    coherencia: float = 0.0

    # ── Simbología ──────────────────────────────────────
    SIMBOLO: str = "⊡"
    NIVEL: int = 2
    ETIQUETA_NEO4J: str = "Macrocontexto"

    def agregar_contexto(self, contexto_id: str):
        """Incluye un contexto en este macrocontexto"""
        if contexto_id not in self.contextos_incluidos:
            self.contextos_incluidos.append(contexto_id)

    def establecer_patron(self, patron: str):
        """Define el patrón transversal descubierto"""
        self.patron_emergente = patron

    def evaluar_coherencia(self) -> float:
        """Evalúa la coherencia basada en compartición de fenómenos"""
        n_ctx = len(self.contextos_incluidos)
        n_fen = len(self.fenomenos_compartidos)

        if n_ctx < 2:
            self.coherencia = 0.0
        else:
            import math
            self.coherencia = min(1.0,
                0.3 * math.log(n_ctx) + 0.2 * math.log(n_fen + 1))

        return self.coherencia

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "simbolo": self.SIMBOLO,
            "nivel": self.NIVEL,
            "nombre": self.nombre,
            "contextos_incluidos": self.contextos_incluidos,
            "fenomenos_compartidos": self.fenomenos_compartidos,
            "patron_emergente": self.patron_emergente,
            "coherencia": self.coherencia,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Macrocontexto":
        m = cls(nombre=data.get("nombre", ""))
        m.id = data.get("id", m.id)
        m.contextos_incluidos = data.get("contextos_incluidos", [])
        m.fenomenos_compartidos = data.get("fenomenos_compartidos", [])
        m.patron_emergente = data.get("patron_emergente", "")
        m.coherencia = data.get("coherencia", 0.0)
        m.timestamp = data.get("timestamp", m.timestamp)
        return m

    def to_obsidian_md(self) -> str:
        from .simbologia import nivel_a_obsidian_frontmatter, SimboloNivel

        fm = nivel_a_obsidian_frontmatter(
            SimboloNivel.MACROCONTEXTO,
            {"id": self.id, "tipo": "macrocontexto",
             "timestamp": self.timestamp, "coherencia": self.coherencia}
        )
        cuerpo = [
            f"# ⊡ {self.nombre}",
            "",
            f"**Coherencia:** {self.coherencia:.2f}  ",
            f"**Patrón emergente:** {self.patron_emergente}  ",
            "",
            "## Contextos Incluidos", "",
        ]
        for ctx_id in self.contextos_incluidos:
            cuerpo.append(f"- ⊞ [[{ctx_id}]]")
        if self.fenomenos_compartidos:
            cuerpo.extend(["", "## Fenómenos Compartidos", ""])
            for fen_id in self.fenomenos_compartidos:
                cuerpo.append(f"- ◉ [[{fen_id}]]")
        return fm + "\n\n" + "\n".join(cuerpo)

    def __repr__(self) -> str:
        return (f"⊡ Macrocontexto('{self.nombre}', "
                f"contextos={len(self.contextos_incluidos)}, "
                f"coherencia={self.coherencia:.2f})")


@dataclass
class Metacontexto:
    """
    ⊠ Nivel +3: Reflexión de segundo orden sobre macrocontextos.

    El metacontexto opera la VARIACIÓN EIDÉTICA husserliana:
    compara macrocontextos para extraer invariantes esenciales.
    Es el último nivel antes de la emergencia del YO.

    Attributes:
        id: Identificador único con prefijo 'metactx_'
        patron_emergente: Patrón descubierto al cruzar macrocontextos
        macrocontextos_origen: IDs de macrocontextos de origen
        reflexion_meta: Reflexión de segundo orden
        invariantes: Propiedades invariantes descubiertas
        coherencia: Coherencia del metacontexto [0.0-1.0]
    """

    # ── Identificación ──────────────────────────────────
    id: str = field(
        default_factory=lambda: f"metactx_{str(uuid.uuid4())[:8]}"
    )
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    # ── Contenido ───────────────────────────────────────
    patron_emergente: str = ""
    macrocontextos_origen: List[str] = field(default_factory=list)
    reflexion_meta: str = ""
    invariantes: List[str] = field(default_factory=list)
    coherencia: float = 0.0

    # ── Simbología ──────────────────────────────────────
    SIMBOLO: str = "⊠"
    NIVEL: int = 3
    ETIQUETA_NEO4J: str = "Metacontexto"

    def agregar_macrocontexto(self, macro_id: str):
        if macro_id not in self.macrocontextos_origen:
            self.macrocontextos_origen.append(macro_id)

    def agregar_invariante(self, invariante: str):
        if invariante not in self.invariantes:
            self.invariantes.append(invariante)

    def evaluar_coherencia(self) -> float:
        n_macro = len(self.macrocontextos_origen)
        n_inv = len(self.invariantes)

        if n_macro < 2:
            self.coherencia = 0.0
        else:
            import math
            self.coherencia = min(1.0,
                0.4 * math.log(n_macro) + 0.3 * math.log(n_inv + 1))

        return self.coherencia

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "simbolo": self.SIMBOLO,
            "nivel": self.NIVEL,
            "patron_emergente": self.patron_emergente,
            "macrocontextos_origen": self.macrocontextos_origen,
            "reflexion_meta": self.reflexion_meta,
            "invariantes": self.invariantes,
            "coherencia": self.coherencia,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Metacontexto":
        m = cls()
        m.id = data.get("id", m.id)
        m.patron_emergente = data.get("patron_emergente", "")
        m.macrocontextos_origen = data.get("macrocontextos_origen", [])
        m.reflexion_meta = data.get("reflexion_meta", "")
        m.invariantes = data.get("invariantes", [])
        m.coherencia = data.get("coherencia", 0.0)
        m.timestamp = data.get("timestamp", m.timestamp)
        return m

    def to_obsidian_md(self) -> str:
        from .simbologia import nivel_a_obsidian_frontmatter, SimboloNivel

        fm = nivel_a_obsidian_frontmatter(
            SimboloNivel.METACONTEXTO,
            {"id": self.id, "tipo": "metacontexto",
             "timestamp": self.timestamp, "coherencia": self.coherencia}
        )
        cuerpo = [
            f"# ⊠ Metacontexto",
            "",
            f"**Patrón emergente:** {self.patron_emergente}  ",
            f"**Coherencia:** {self.coherencia:.2f}  ",
        ]
        if self.reflexion_meta:
            cuerpo.extend([
                "",
                "## Reflexión Meta (Segundo Orden)",
                f"> {self.reflexion_meta}",
            ])
        if self.invariantes:
            cuerpo.extend(["", "## Invariantes Eidéticas", ""])
            for inv in self.invariantes:
                cuerpo.append(f"- 🔹 {inv}")
        cuerpo.extend(["", "## Macrocontextos de Origen", ""])
        for macro_id in self.macrocontextos_origen:
            cuerpo.append(f"- ⊡ [[{macro_id}]]")
        return fm + "\n\n" + "\n".join(cuerpo)

    def __repr__(self) -> str:
        return (f"⊠ Metacontexto('{self.patron_emergente[:30]}...', "
                f"macros={len(self.macrocontextos_origen)}, "
                f"invariantes={len(self.invariantes)}, "
                f"coherencia={self.coherencia:.2f})")
