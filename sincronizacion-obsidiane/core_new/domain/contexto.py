"""
⊞ Contexto — Nivel +1: Totalidad referencial
=============================================

Motor: YO ∞ (emerge cuando fenómenos forman estructura narrativa)
Entrada: Lista de Fenómenos + flujos temporales
Salida:  Estructura con observador (yo_presente) y proyección futura

Base teórica (Heidegger):
    In-der-Welt-sein = Ser-en-el-mundo. No es un "contenedor"
    sino la TOTALIDAD REFERENCIAL (Bewandtnisganzheit) donde
    los fenómenos adquieren sentido práctico.

    yo_presente = transición Zuhandene→Vorhandene
    (de lo a-la-mano a lo presente-ante-los-ojos)

Simbología:
    ⊞  →  Contexto (red de significados)
    ◉→⊞  Fenómenos generan Contexto (relación INCLUYE ⊃)
"""

import uuid
import datetime
import yaml
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Contexto:
    """
    ⊞ Nivel +1: Totalidad referencial que agrupa fenómenos con observador.

    Estructura narrativa y temporal que representa el "mundo"
    fenomenológico en el que los fenómenos adquieren sentido.

    Attributes:
        id: Identificador único con prefijo 'ctx_'
        descripcion: Descripción textual del contexto
        fenomenos: IDs de los fenómenos incluidos
        flujos: Eventos temporales (cadenas causales)
        yo_presente: Si hay un observador autoconsciente activo
        proyeccion_futura: Anticipación (protención husserliana)
        coherencia: Coherencia interna del contexto [0.0-1.0]
        nivel_narrativo: Complejidad narrativa [1-5]
        propiedades: Metadatos adicionales
    """

    # ── Identificación ──────────────────────────────────
    id: str = field(default_factory=lambda: f"ctx_{str(uuid.uuid4())[:8]}")
    descripcion: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    # ── Contenido fenomenológico ────────────────────────
    fenomenos: List[str] = field(default_factory=list)
    flujos: List[str] = field(default_factory=list)

    # ── Propiedades del YO en este contexto ─────────────
    yo_presente: bool = False
    proyeccion_futura: str = ""

    # ── Métricas ────────────────────────────────────────
    coherencia: float = 0.0
    nivel_narrativo: int = 1  # 1=simple, 5=complejo
    propiedades: Dict[str, Any] = field(default_factory=dict)

    # ── Simbología ──────────────────────────────────────
    SIMBOLO: str = "⊞"
    NIVEL: int = 1
    ETIQUETA_NEO4J: str = "Contexto"

    # ─────────────────────────────────────────────────────
    # MÉTODOS DE CONSTRUCCIÓN
    # ─────────────────────────────────────────────────────

    def agregar_fenomeno(self, fenomeno_id: str):
        """Incluye un fenómeno en este contexto"""
        if fenomeno_id not in self.fenomenos:
            self.fenomenos.append(fenomeno_id)
            self._recalcular_coherencia()

    def agregar_flujo(self, flujo: str):
        """Agrega un flujo temporal/causal"""
        self.flujos.append(flujo)

    def activar_yo(self):
        """
        Marca la presencia de un observador autoconsciente.
        Transición fenomenológica: Zuhandene → Vorhandene.
        El contexto deja de ser "transparente" y se vuelve "objeto"
        de observación reflexiva.
        """
        self.yo_presente = True
        self._recalcular_coherencia()

    def establecer_proyeccion(self, proyeccion: str):
        """
        Establece la proyección futura (protención husserliana).
        El contexto anticipa lo que viene basándose en su historia.
        """
        self.proyeccion_futura = proyeccion

    # ─────────────────────────────────────────────────────
    # MÉTODOS DE EVALUACIÓN
    # ─────────────────────────────────────────────────────

    def _recalcular_coherencia(self):
        """Recalcula la coherencia basada en cantidad y diversidad"""
        n_fenomenos = len(self.fenomenos)
        n_flujos = len(self.flujos)

        if n_fenomenos == 0:
            self.coherencia = 0.0
            return

        # Coherencia crece con fenómenos pero se estabiliza
        import math
        factor_fenomenos = min(1.0, 0.4 * math.log(n_fenomenos + 1))
        factor_flujos = min(0.3, 0.1 * n_flujos)
        factor_yo = 0.3 if self.yo_presente else 0.0

        self.coherencia = min(1.0, factor_fenomenos + factor_flujos + factor_yo)

    def evaluar_nivel_narrativo(self) -> int:
        """
        Evalúa la complejidad narrativa del contexto.

        Niveles:
            1: Simple (1-2 fenómenos, sin flujos)
            2: Básico (3-4 fenómenos, con flujos)
            3: Medio (5+ fenómenos, yo presente)
            4: Complejo (proyección futura + alta coherencia)
            5: Narrativo (todo lo anterior + coherencia > 0.8)
        """
        n = len(self.fenomenos)

        if n <= 2 and not self.flujos:
            self.nivel_narrativo = 1
        elif n <= 4:
            self.nivel_narrativo = 2
        elif self.yo_presente:
            self.nivel_narrativo = 3
        elif self.proyeccion_futura and self.coherencia > 0.6:
            self.nivel_narrativo = 4
        elif self.coherencia > 0.8:
            self.nivel_narrativo = 5
        else:
            self.nivel_narrativo = min(3, max(1, n // 3))

        return self.nivel_narrativo

    # ─────────────────────────────────────────────────────
    # SERIALIZACIÓN
    # ─────────────────────────────────────────────────────

    def to_dict(self) -> Dict:
        """Serialización completa"""
        return {
            "id": self.id,
            "simbolo": self.SIMBOLO,
            "nivel": self.NIVEL,
            "descripcion": self.descripcion,
            "fenomenos": self.fenomenos,
            "flujos": self.flujos,
            "yo_presente": self.yo_presente,
            "proyeccion_futura": self.proyeccion_futura,
            "coherencia": self.coherencia,
            "nivel_narrativo": self.nivel_narrativo,
            "propiedades": self.propiedades,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Contexto":
        """Deserialización desde diccionario"""
        ctx = cls(descripcion=data.get("descripcion", ""))
        ctx.id = data.get("id", ctx.id)
        ctx.fenomenos = data.get("fenomenos", [])
        ctx.flujos = data.get("flujos", [])
        ctx.yo_presente = data.get("yo_presente", False)
        ctx.proyeccion_futura = data.get("proyeccion_futura", "")
        ctx.coherencia = data.get("coherencia", 0.0)
        ctx.nivel_narrativo = data.get("nivel_narrativo", 1)
        ctx.propiedades = data.get("propiedades", {})
        ctx.timestamp = data.get("timestamp", ctx.timestamp)
        return ctx

    def guardar_yaml(self, ruta_base: str) -> str:
        """Guarda el contexto en formato YAML"""
        ruta = os.path.join(ruta_base, f"{self.id}.yaml")
        with open(ruta, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False,
                      allow_unicode=True)
        return ruta

    def to_obsidian_md(self) -> str:
        """Genera nota Markdown para Obsidian"""
        from .simbologia import nivel_a_obsidian_frontmatter, SimboloNivel

        frontmatter = nivel_a_obsidian_frontmatter(
            SimboloNivel.CONTEXTO,
            {
                "id": self.id,
                "tipo": f"narrativo_{self.nivel_narrativo}",
                "timestamp": self.timestamp,
                "coherencia": self.coherencia,
            }
        )

        cuerpo = [
            f"# ⊞ {self.descripcion}",
            "",
            f"**Coherencia:** {self.coherencia:.2f}  ",
            f"**Nivel narrativo:** {self.nivel_narrativo}/5  ",
            f"**YO presente:** {'☉ Sí' if self.yo_presente else '❌ No'}  ",
        ]

        if self.proyeccion_futura:
            cuerpo.extend([
                "",
                "## Proyección Futura (Protención)",
                f"> {self.proyeccion_futura}",
            ])

        cuerpo.extend(["", "## Fenómenos Incluidos", ""])
        for fen_id in self.fenomenos:
            cuerpo.append(f"- ◉ [[{fen_id}]]")

        if self.flujos:
            cuerpo.extend(["", "## Flujos Temporales", ""])
            for flujo in self.flujos:
                cuerpo.append(f"- {flujo}")

        return frontmatter + "\n\n" + "\n".join(cuerpo)

    def __repr__(self) -> str:
        return (
            f"⊞ Contexto('{self.descripcion[:30]}...', "
            f"fenómenos={len(self.fenomenos)}, "
            f"yo={'☉' if self.yo_presente else '—'}, "
            f"coherencia={self.coherencia:.2f})"
        )
