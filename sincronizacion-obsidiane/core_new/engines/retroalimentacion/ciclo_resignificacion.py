"""
⟳ Ciclo de Retroalimentación YO → Instancias
=============================================

Motor: ∞ (recursión autoconsciente)
Relación: OBSERVA ⊙ (YO resignifica instancias originales)

Base teórica (Heidegger, Ser y Tiempo §32):
    "Toda interpretación se funda en la comprensión previa."
    El YO emergente RESIGNIFICA las instancias que lo generaron,
    creando un ciclo hermenéutico que enriquece el sistema.

    Ciclo:  Instancias → ... → YO → OBSERVA → Instancias (resignificadas)

Simbología:
    ⟳  →  Retroalimentación (ciclo hermenéutico)
    ☉→•  YO observa Instancia (OBSERVA ⊙)
    •*   Instancia resignificada (nueva capa de significado)
"""

import datetime
from typing import Dict, List, Generator, Any
from dataclasses import dataclass, field


@dataclass
class Resignificacion:
    """Una resignificación producida por el YO sobre una instancia"""
    instancia_id: str
    yo_id: str
    tipo_yo: str
    significado_original: str
    significado_nuevo: str
    perspectiva: str
    peso_resignificacion: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    def to_dict(self) -> Dict:
        return {
            "instancia_id": self.instancia_id,
            "yo_id": self.yo_id,
            "tipo_yo": self.tipo_yo,
            "significado_original": self.significado_original,
            "significado_nuevo": self.significado_nuevo,
            "perspectiva": self.perspectiva,
            "peso_resignificacion": self.peso_resignificacion,
            "timestamp": self.timestamp,
        }


class CicloResignificacion:
    """
    ⟳ Implementa la retroalimentación YO → Instancias.

    Después de emerger el YO, este resignifica las instancias
    que lo generaron, creando nuevas capas de significado.

    El ciclo hermenéutico produce:
    1. Relaciones OBSERVA (⊙) desde el YO hacia instancias
    2. Resignificaciones que enriquecen cada instancia
    3. Nuevas propiedades que pueden alterar evaluaciones futuras
    """

    SIMBOLO = "⟳"

    def __init__(self):
        self.resignificaciones: List[Resignificacion] = []
        self.ciclos_completados: int = 0

    def resignificar(
        self,
        yo_estado: Dict,
        instancias_origen: List[Dict],
    ) -> Generator[Dict, None, None]:
        """
        Genera resignificaciones para cada instancia de origen.

        Args:
            yo_estado: Estado actual del YO (tipo, métricas)
            instancias_origen: Lista de instancias que generaron al YO

        Yields:
            Dict con relación OBSERVA y resignificación
        """
        yo_id = yo_estado.get("id", "yo_desconocido")
        tipo_yo = yo_estado.get("estado", {}).get("tipo", "PROTO_YO")
        coherencia = yo_estado.get("estado", {}).get(
            "metricas", {}
        ).get("promedio", 0.0)

        for instancia in instancias_origen:
            inst_id = instancia.get("id", "")
            contenido = instancia.get("propiedades", {})

            # ── Generar resignificación ─────────────────
            sig_original = str(contenido)[:100]
            sig_nuevo = self._generar_resignificacion(
                tipo_yo, contenido, coherencia
            )

            resignificacion = Resignificacion(
                instancia_id=inst_id,
                yo_id=yo_id,
                tipo_yo=tipo_yo,
                significado_original=sig_original,
                significado_nuevo=sig_nuevo,
                perspectiva=f"Vista desde {tipo_yo}",
                peso_resignificacion=min(1.0, coherencia * 0.8 + 0.2),
            )

            self.resignificaciones.append(resignificacion)

            # ── Emitir relación OBSERVA ─────────────────
            yield {
                "tipo": "OBSERVA",
                "simbolo": "⊙",
                "desde": yo_id,
                "hacia": inst_id,
                "perspectiva": tipo_yo,
                "resignificacion": resignificacion.to_dict(),
                "propiedades_nuevas": {
                    f"resignificado_por_{tipo_yo}": True,
                    "perspectiva_yo": sig_nuevo,
                    "peso_resignificacion": resignificacion.peso_resignificacion,
                },
            }

        self.ciclos_completados += 1

    def _generar_resignificacion(
        self,
        tipo_yo: str,
        contenido: Dict,
        coherencia: float,
    ) -> str:
        """
        Genera el nuevo significado contextual según el tipo de YO.

        Perspectivas fenomenológicas por tipo de YO:
            PROTO_YO:       Solo registra existencia
            YO_SENSORIAL:   Percibe cualidades sensibles
            YO_AFECTIVO:    Evalúa valencia emocional
            YO_REFLEXIVO:   Analiza estructura y relaciones
            YO_SIMBOLICO:   Abstrae y categoriza conceptos
            YO_NARRATIVO:   Integra en historia y proyección
        """
        perspectivas = {
            "PROTO_YO": "Existencia registrada sin interpretación",
            "YO_SENSORIAL": f"Percibido como dato sensible (coherencia={coherencia:.2f})",
            "YO_AFECTIVO": f"Evaluado emocionalmente (valencia estimada={coherencia:.1f})",
            "YO_REFLEXIVO": f"Analizado estructuralmente: {len(contenido)} propiedades",
            "YO_SIMBOLICO": f"Categorizado como concepto abstracto (certeza={coherencia:.2f})",
            "YO_NARRATIVO": f"Integrado en narrativa existencial (coherencia={coherencia:.2f})",
        }

        return perspectivas.get(tipo_yo, f"Observado desde {tipo_yo}")

    def obtener_resumen(self) -> Dict:
        """Resumen del ciclo de retroalimentación"""
        return {
            "ciclos_completados": self.ciclos_completados,
            "total_resignificaciones": len(self.resignificaciones),
            "por_tipo_yo": self._contar_por_tipo(),
        }

    def _contar_por_tipo(self) -> Dict[str, int]:
        conteo: Dict[str, int] = {}
        for r in self.resignificaciones:
            conteo[r.tipo_yo] = conteo.get(r.tipo_yo, 0) + 1
        return conteo

    def to_obsidian_md(self) -> str:
        """Genera nota Obsidian del ciclo de retroalimentación"""
        lineas = [
            "---",
            "tags:",
            "  - sistema/retroalimentacion",
            "  - ciclo/hermeneutico",
            "---",
            "",
            "# ⟳ Ciclo de Retroalimentación YO → Instancias",
            "",
            f"**Ciclos completados:** {self.ciclos_completados}  ",
            f"**Total resignificaciones:** {len(self.resignificaciones)}  ",
            "",
            "## Resignificaciones Recientes",
            "",
        ]

        for r in self.resignificaciones[-10:]:
            lineas.extend([
                f"### ⊙ [[{r.instancia_id}]] visto desde {r.tipo_yo}",
                f"> **Original:** {r.significado_original[:60]}...  ",
                f"> **Nuevo:** {r.significado_nuevo}  ",
                f"> **Peso:** {r.peso_resignificacion:.2f}  ",
                "",
            ])

        return "\n".join(lineas)
