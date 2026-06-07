"""
Generador de Relaciones Fenomenológicas — 12 Tipos
====================================================

Motor: Transversal a todos los motores
Entrada: Pares de entidades + embeddings + marcadores textuales
Salida:  Relaciones tipificadas con pesos y simbología

Los 12 tipos de relaciones con su simbología:
    ≈  SE_PARECE_A     Similitud semántica           (bidireccional)
    ⊕  AGRUPA          Inclusión coexistencial        (unidireccional)
    ↗  SURGE_DE        Emergencia jerárquica          (unidireccional)
    ⊘  CONTRADICE      Tensión dialéctica            (bidireccional)
    ⊙  OBSERVA         Auto-observación del YO        (unidireccional)
    →  ACTUA_EN        Acción de la voluntad          (unidireccional)
    ⊃  INCLUYE         Contención contextual          (unidireccional)
    —  RELACION        Gradiente general              (unidireccional)
    ⇒  TRANSFORMA_EN   Metamorfosis ontológica        (unidireccional)
    ⤴  EMERGE_COMO     Emergencia de nivel superior   (unidireccional)
    ⊳  GENERA          Producción de nuevos niveles   (unidireccional)
    ⊶  DECIDE          Decisión existencial           (unidireccional)
"""

import datetime
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class RelacionFenomenologica:
    """Una relación fenomenológica entre dos entidades del sistema"""
    tipo: str
    simbolo: str
    origen_id: str
    destino_id: str
    peso: float
    contexto: str = ""
    bidireccional: bool = False
    nivel_origen: int = 0
    nivel_destino: int = 0
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    def to_dict(self) -> Dict:
        return {
            "tipo": self.tipo,
            "simbolo": self.simbolo,
            "origen_id": self.origen_id,
            "destino_id": self.destino_id,
            "peso": self.peso,
            "contexto": self.contexto,
            "bidireccional": self.bidireccional,
            "nivel_origen": self.nivel_origen,
            "nivel_destino": self.nivel_destino,
            "timestamp": self.timestamp,
        }

    def to_neo4j_query(self) -> str:
        """Genera la query Cypher para Neo4j"""
        return (
            f"MATCH (a {{id: '{self.origen_id}'}}), "
            f"(b {{id: '{self.destino_id}'}}) "
            f"MERGE (a)-[r:{self.tipo} {{"
            f"peso: {self.peso}, "
            f"simbolo: '{self.simbolo}', "
            f"contexto: '{self.contexto}', "
            f"timestamp: '{self.timestamp}'"
            f"}}]->(b)"
        )

    def to_obsidian_link(self) -> str:
        """Genera un enlace Obsidian con contexto"""
        return (
            f"- {self.simbolo} {self.tipo} → [[{self.destino_id}]] "
            f"(peso: {self.peso:.2f})"
        )


class GeneradorRelaciones:
    """
    ∀ Generador de Relaciones Fenomenológicas

    Genera relaciones entre entidades del sistema usando:
    - Similitud coseno para SE_PARECE_A
    - Marcadores textuales para CONTRADICE
    - Niveles jerárquicos para SURGE_DE / EMERGE_COMO
    - Estado del YO para OBSERVA / ACTUA_EN
    """

    TIPOS = {
        "SE_PARECE_A":    {"simbolo": "≈", "peso_min": 0.3, "bidir": True},
        "CONTRADICE":     {"simbolo": "⊘", "peso_min": 0.5, "bidir": True},
        "AGRUPA":         {"simbolo": "⊕", "peso_min": 0.5, "bidir": False},
        "INCLUYE":        {"simbolo": "⊃", "peso_min": 0.4, "bidir": False},
        "SURGE_DE":       {"simbolo": "↗", "peso_min": 0.6, "bidir": False},
        "OBSERVA":        {"simbolo": "⊙", "peso_min": 0.7, "bidir": False},
        "ACTUA_EN":       {"simbolo": "→", "peso_min": 0.6, "bidir": False},
        "TRANSFORMA_EN":  {"simbolo": "⇒", "peso_min": 0.5, "bidir": False},
        "EMERGE_COMO":    {"simbolo": "⤴", "peso_min": 0.6, "bidir": False},
        "GENERA":         {"simbolo": "⊳", "peso_min": 0.5, "bidir": False},
        "DECIDE":         {"simbolo": "⊶", "peso_min": 0.7, "bidir": False},
        "RELACION":       {"simbolo": "—", "peso_min": 0.1, "bidir": False},
    }

    MARCADORES_CONTRADICCION = [
        "pero", "sin embargo", "no obstante", "aunque", "contrariamente",
        "por el contrario", "a diferencia", "no", "nunca", "jamás",
        "opuesto", "contradice", "niega", "refuta", "invalida"
    ]

    def __init__(self):
        self.relaciones_generadas: List[RelacionFenomenologica] = []

    def generar_similitud(
        self,
        id_a: str, embedding_a: np.ndarray,
        id_b: str, embedding_b: np.ndarray,
        nivel_a: int = 0, nivel_b: int = 0
    ) -> Optional[RelacionFenomenologica]:
        """SE_PARECE_A ≈: similitud coseno entre embeddings"""
        norma_a = np.linalg.norm(embedding_a)
        norma_b = np.linalg.norm(embedding_b)

        if norma_a == 0 or norma_b == 0:
            return None

        similitud = float(
            np.dot(embedding_a, embedding_b) / (norma_a * norma_b)
        )

        if similitud >= self.TIPOS["SE_PARECE_A"]["peso_min"]:
            rel = RelacionFenomenologica(
                tipo="SE_PARECE_A",
                simbolo="≈",
                origen_id=id_a,
                destino_id=id_b,
                peso=similitud,
                bidireccional=True,
                nivel_origen=nivel_a,
                nivel_destino=nivel_b,
            )
            self.relaciones_generadas.append(rel)
            return rel
        return None

    def generar_contradiccion(
        self,
        id_a: str, texto_a: str,
        id_b: str, texto_b: str,
    ) -> Optional[RelacionFenomenologica]:
        """CONTRADICE ⊘: detecta marcadores adversativos"""
        texto_combinado = (texto_a + " " + texto_b).lower()

        marcadores_encontrados = [
            m for m in self.MARCADORES_CONTRADICCION
            if m in texto_combinado
        ]

        if not marcadores_encontrados:
            return None

        peso = min(1.0, 0.3 + 0.15 * len(marcadores_encontrados))

        if peso >= self.TIPOS["CONTRADICE"]["peso_min"]:
            rel = RelacionFenomenologica(
                tipo="CONTRADICE",
                simbolo="⊘",
                origen_id=id_a,
                destino_id=id_b,
                peso=peso,
                contexto=f"Marcadores: {', '.join(marcadores_encontrados)}",
                bidireccional=True,
            )
            self.relaciones_generadas.append(rel)
            return rel
        return None

    def generar_emergencia_jerarquica(
        self,
        id_inferior: str, nivel_inferior: int,
        id_superior: str, nivel_superior: int,
        coherencia: float = 0.0,
    ) -> Optional[RelacionFenomenologica]:
        """SURGE_DE ↗ / EMERGE_COMO ⤴: emergencia entre niveles"""
        if nivel_superior <= nivel_inferior:
            return None

        # Usar SURGE_DE para un salto de 1 nivel, EMERGE_COMO para >1
        if nivel_superior - nivel_inferior == 1:
            tipo = "SURGE_DE"
            simbolo = "↗"
        else:
            tipo = "EMERGE_COMO"
            simbolo = "⤴"

        peso = min(1.0, coherencia + 0.2 * (nivel_superior - nivel_inferior))

        if peso >= self.TIPOS[tipo]["peso_min"]:
            rel = RelacionFenomenologica(
                tipo=tipo,
                simbolo=simbolo,
                origen_id=id_inferior,
                destino_id=id_superior,
                peso=peso,
                nivel_origen=nivel_inferior,
                nivel_destino=nivel_superior,
            )
            self.relaciones_generadas.append(rel)
            return rel
        return None

    def generar_observacion_yo(
        self,
        yo_id: str,
        entidad_id: str,
        nivel_entidad: int,
        perspectiva: str = "",
    ) -> RelacionFenomenologica:
        """OBSERVA ⊙: el YO se auto-observa o observa instancias"""
        rel = RelacionFenomenologica(
            tipo="OBSERVA",
            simbolo="⊙",
            origen_id=yo_id,
            destino_id=entidad_id,
            peso=0.8,
            contexto=perspectiva,
            nivel_origen=4,
            nivel_destino=nivel_entidad,
        )
        self.relaciones_generadas.append(rel)
        return rel

    def generar_inclusion(
        self,
        contenedor_id: str, nivel_contenedor: int,
        contenido_id: str, nivel_contenido: int,
    ) -> RelacionFenomenologica:
        """INCLUYE ⊃: contención contextual"""
        rel = RelacionFenomenologica(
            tipo="INCLUYE",
            simbolo="⊃",
            origen_id=contenedor_id,
            destino_id=contenido_id,
            peso=0.9,
            nivel_origen=nivel_contenedor,
            nivel_destino=nivel_contenido,
        )
        self.relaciones_generadas.append(rel)
        return rel

    def generar_agrupacion(
        self,
        grupo_id: str,
        miembros_ids: List[str],
        peso: float = 0.7,
    ) -> List[RelacionFenomenologica]:
        """AGRUPA ⊕: agrupa múltiples entidades"""
        relaciones = []
        for mid in miembros_ids:
            rel = RelacionFenomenologica(
                tipo="AGRUPA",
                simbolo="⊕",
                origen_id=grupo_id,
                destino_id=mid,
                peso=peso,
            )
            self.relaciones_generadas.append(rel)
            relaciones.append(rel)
        return relaciones

    def obtener_todas(self) -> List[Dict]:
        """Retorna todas las relaciones generadas como dicts"""
        return [r.to_dict() for r in self.relaciones_generadas]

    def obtener_por_tipo(self, tipo: str) -> List[RelacionFenomenologica]:
        """Filtra relaciones por tipo"""
        return [r for r in self.relaciones_generadas if r.tipo == tipo]

    def generar_obsidian_moc(self) -> str:
        """Genera un Map of Content (MOC) de relaciones para Obsidian"""
        lineas = [
            "---",
            "tags:",
            "  - MOC/relaciones",
            "  - sistema/fenomenologia",
            "---",
            "",
            "# 🕸️ Mapa de Relaciones Fenomenológicas",
            "",
            f"**Total de relaciones:** {len(self.relaciones_generadas)}  ",
            "",
        ]

        for tipo, config in self.TIPOS.items():
            rels = self.obtener_por_tipo(tipo)
            if rels:
                lineas.append(
                    f"## {config['simbolo']} {tipo} ({len(rels)} relaciones)"
                )
                lineas.append("")
                for rel in rels[:10]:  # Máximo 10 por tipo
                    lineas.append(rel.to_obsidian_link())
                lineas.append("")

        return "\n".join(lineas)
