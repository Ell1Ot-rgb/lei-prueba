"""
◉ Fenómeno — Nivel 0: Lo que se muestra en sí mismo
=====================================================

Motor: S2 ∫ (emerge de la acumulación de vohexistencias)
Entrada: Vohexistencias con peso_coexistencial > umbral
Salida:  Fenómeno discreto con tipo (visual|sensorial|emocional|cognitivo)

Base teórica (Heidegger, Ser y Tiempo §7):
    "Fenómeno = aquello que se muestra en sí mismo, lo manifiesto."
    No es un dato interno de la conciencia sino lo que APARECE
    cuando un conjunto de vohexistencias se estabiliza.

Simbología:
    ◉  →  Fenómeno (núcleo visible)
    ◊→◉  Vohexistencia genera Fenómeno (relación EMERGE_COMO ⤴)
"""

import uuid
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Fenomeno:
    """
    ◉ Nivel 0: Núcleo conceptual emergente por frecuencia de vohexistencias.

    Un fenómeno es el punto de articulación donde lo pre-consciente
    (niveles -4 a -1) se vuelve manifiesto. Es el equivalente
    computacional de la Erscheinung husserliana.

    Attributes:
        id: Identificador único con prefijo 'fen_'
        contenido: Descripción textual del fenómeno
        tipo: Clasificación (visual|sensorial|emocional|cognitivo|general)
        intensidad: Fuerza fenomenológica [0.0-1.0]
        es_nucleo: Si es un núcleo conceptual estable
        vohexistencias_origen: IDs de las vohexistencias que lo generaron
        frecuencia: Cantidad de veces que ha co-ocurrido
        validacion_fenomenologica: Score de validación [0.0-1.0]
        relaciones: Relaciones con otros elementos del sistema
        propiedades: Metadatos adicionales
        timestamp: Momento de creación (ISO 8601)
    """

    # ── Identificación ──────────────────────────────────
    id: str = field(default_factory=lambda: f"fen_{str(uuid.uuid4())[:8]}")
    contenido: str = ""
    tipo: str = "general"  # visual|sensorial|emocional|cognitivo|general
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    # ── Propiedades fenomenológicas ─────────────────────
    intensidad: float = 0.0
    es_nucleo: bool = False
    frecuencia: int = 0
    validacion_fenomenologica: float = 0.0

    # ── Orígenes y relaciones ───────────────────────────
    vohexistencias_origen: List[str] = field(default_factory=list)
    relaciones: List[Dict] = field(default_factory=list)
    propiedades: Dict[str, Any] = field(default_factory=dict)

    # ── Simbología ──────────────────────────────────────
    SIMBOLO: str = "◉"
    NIVEL: int = 0
    ETIQUETA_NEO4J: str = "Fenomeno"

    # ─────────────────────────────────────────────────────
    # MÉTODOS DE EVALUACIÓN
    # ─────────────────────────────────────────────────────

    def evaluar_nuclearidad(self, umbral_frecuencia: int = 3,
                           umbral_intensidad: float = 0.6) -> bool:
        """
        Evalúa si el fenómeno es un núcleo conceptual estable.

        Un fenómeno se convierte en núcleo cuando:
        1. Aparece con frecuencia suficiente (frecuencia ≥ umbral)
        2. Su intensidad supera el umbral
        3. Tiene al menos 2 vohexistencias de origen

        Returns:
            bool: True si cumple criterios de nuclearidad
        """
        self.es_nucleo = (
            self.frecuencia >= umbral_frecuencia
            and self.intensidad >= umbral_intensidad
            and len(self.vohexistencias_origen) >= 2
        )
        return self.es_nucleo

    def incrementar_frecuencia(self, peso: float = 1.0):
        """Incrementa la frecuencia y recalcula intensidad"""
        self.frecuencia += 1
        # Intensidad crece logarítmicamente con la frecuencia
        import math
        self.intensidad = min(1.0, 0.3 * math.log(self.frecuencia + 1))

    def agregar_vohexistencia_origen(self, vohex_id: str):
        """Registra una vohexistencia como origen de este fenómeno"""
        if vohex_id not in self.vohexistencias_origen:
            self.vohexistencias_origen.append(vohex_id)

    def agregar_relacion(self, tipo: str, destino_id: str,
                         peso: float, contexto: str = ""):
        """Agrega una relación fenomenológica"""
        self.relaciones.append({
            "tipo": tipo,
            "destino": destino_id,
            "peso": peso,
            "contexto": contexto,
            "timestamp": datetime.datetime.now().isoformat()
        })

    # ─────────────────────────────────────────────────────
    # SERIALIZACIÓN
    # ─────────────────────────────────────────────────────

    def to_dict(self) -> Dict:
        """Serialización completa a diccionario"""
        return {
            "id": self.id,
            "simbolo": self.SIMBOLO,
            "nivel": self.NIVEL,
            "contenido": self.contenido,
            "tipo": self.tipo,
            "intensidad": self.intensidad,
            "es_nucleo": self.es_nucleo,
            "frecuencia": self.frecuencia,
            "validacion_fenomenologica": self.validacion_fenomenologica,
            "vohexistencias_origen": self.vohexistencias_origen,
            "relaciones": self.relaciones,
            "propiedades": self.propiedades,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Fenomeno":
        """Deserialización desde diccionario"""
        fen = cls(
            contenido=data.get("contenido", ""),
            tipo=data.get("tipo", "general"),
        )
        fen.id = data.get("id", fen.id)
        fen.intensidad = data.get("intensidad", 0.0)
        fen.es_nucleo = data.get("es_nucleo", False)
        fen.frecuencia = data.get("frecuencia", 0)
        fen.validacion_fenomenologica = data.get(
            "validacion_fenomenologica", 0.0
        )
        fen.vohexistencias_origen = data.get("vohexistencias_origen", [])
        fen.relaciones = data.get("relaciones", [])
        fen.propiedades = data.get("propiedades", {})
        fen.timestamp = data.get("timestamp", fen.timestamp)
        return fen

    def to_obsidian_md(self) -> str:
        """Genera nota Markdown para Obsidian en formato Zettelkasten"""
        from .simbologia import nivel_a_obsidian_frontmatter, SimboloNivel

        frontmatter = nivel_a_obsidian_frontmatter(
            SimboloNivel.FENOMENO,
            {
                "id": self.id,
                "tipo": self.tipo,
                "timestamp": self.timestamp,
                "peso": self.intensidad,
            }
        )

        cuerpo = [
            f"# ◉ {self.contenido}",
            "",
            f"**Tipo:** {self.tipo}  ",
            f"**Intensidad:** {self.intensidad:.2f}  ",
            f"**Núcleo:** {'✅' if self.es_nucleo else '❌'}  ",
            f"**Frecuencia:** {self.frecuencia}  ",
            "",
            "## Orígenes (Vohexistencias)",
            "",
        ]

        for vohex_id in self.vohexistencias_origen:
            cuerpo.append(f"- ◊ [[{vohex_id}]]")

        if self.relaciones:
            cuerpo.append("")
            cuerpo.append("## Relaciones")
            cuerpo.append("")
            for rel in self.relaciones:
                cuerpo.append(
                    f"- {rel['tipo']} → [[{rel['destino']}]] "
                    f"(peso: {rel['peso']:.2f})"
                )

        return frontmatter + "\n\n" + "\n".join(cuerpo)

    def __repr__(self) -> str:
        return (
            f"◉ Fenomeno('{self.contenido}', tipo={self.tipo}, "
            f"intensidad={self.intensidad:.2f}, nucleo={self.es_nucleo})"
        )
