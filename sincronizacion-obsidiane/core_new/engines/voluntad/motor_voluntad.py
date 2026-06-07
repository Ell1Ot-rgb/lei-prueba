"""
Voluntad — Adaptador de S4 ⊗ para el Nivel +4
===============================================

Motor: YO ∞ + S4 ⊗
Entrada: Estado del YO + Predicciones tensoriales de S4
Salida:  Proyección intencional (Entwurf heideggeriano)

Base teórica (Heidegger, Ser y Tiempo §31):
    Entwurf (Proyecto): El Dasein ES sus posibilidades.
    La voluntad no es un "acto de la mente" sino la APERTURA
    hacia el futuro que define al existente.

Simbología:
    →  Voluntad (acción, ACTUA_EN)
    ☉→⊗→→  YO usa S4 para proyectar y actuar
"""

import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Proyeccion:
    """Una proyección intencional generada por la Voluntad"""
    id: str = ""
    direccion: str = ""
    intensidad: float = 0.0
    prediccion: str = ""
    acciones_sugeridas: List[str] = field(default_factory=list)
    fundamento: str = ""  # Qué datos del YO fundamentan la proyección
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "direccion": self.direccion,
            "intensidad": self.intensidad,
            "prediccion": self.prediccion,
            "acciones_sugeridas": self.acciones_sugeridas,
            "fundamento": self.fundamento,
            "timestamp": self.timestamp,
        }


class MotorVoluntad:
    """
    → Motor de Voluntad (Nivel +4 avanzado)

    Conecta el YO Emergente (☉) con S4 (⊗) para generar
    proyecciones intencionales (Entwurf).

    El motor de voluntad:
    1. Recibe el estado actual del YO
    2. Usa la predicción tensorial de S4 (si disponible)
    3. Genera acciones sugeridas basadas en la coherencia
    4. Emite proyecciones que el sistema puede ejecutar
    """

    SIMBOLO = "→"
    NIVEL = 4
    MOTOR = "⊗"

    def __init__(self):
        self.proyecciones: List[Proyeccion] = []

    def proyectar(
        self,
        estado_yo: Dict,
        prediccion_s4: Optional[Any] = None,
        contextos_activos: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Genera una proyección intencional (Entwurf).

        Args:
            estado_yo: Estado actual del YO (tipo, métricas)
            prediccion_s4: Vector de predicción de S4 (np.ndarray o None)
            contextos_activos: Contextos activamente procesados

        Returns:
            Proyección con dirección, intensidad y acciones
        """
        tipo_yo = estado_yo.get("estado", {}).get("tipo", "PROTO_YO")
        coherencia = estado_yo.get("estado", {}).get(
            "metricas", {}
        ).get("promedio", 0.0)
        emergencia = estado_yo.get("estado", {}).get(
            "nivel_emergencia", 0.0
        )

        # ── 1. Determinar dirección ────────────────────
        direccion = self._interpretar_direccion(
            tipo_yo, coherencia, contextos_activos
        )

        # ── 2. Calcular intensidad ─────────────────────
        intensidad = self._calcular_intensidad(emergencia, coherencia)

        # ── 3. Generar predicción semántica ─────────────
        prediccion = self._extraer_prediccion(
            tipo_yo, prediccion_s4, coherencia
        )

        # ── 4. Generar acciones sugeridas ───────────────
        acciones = self._generar_acciones(
            tipo_yo, coherencia, contextos_activos
        )

        # ── 5. Crear proyección ─────────────────────────
        import uuid
        proyeccion = Proyeccion(
            id=f"proy_{str(uuid.uuid4())[:8]}",
            direccion=direccion,
            intensidad=intensidad,
            prediccion=prediccion,
            acciones_sugeridas=acciones,
            fundamento=f"YO={tipo_yo}, coherencia={coherencia:.2f}",
        )

        self.proyecciones.append(proyeccion)

        return proyeccion.to_dict()

    def _interpretar_direccion(
        self,
        tipo_yo: str,
        coherencia: float,
        contextos: Optional[List[Dict]],
    ) -> str:
        """Interpreta la dirección de la proyección"""
        if coherencia > 0.8:
            return "expansion"  # Sistema estable, expandir
        elif coherencia > 0.5:
            return "consolidacion"  # Consolidar lo existente
        elif coherencia > 0.3:
            return "exploracion"  # Buscar nuevos patrones
        else:
            return "reconfiguración"  # Sistema inestable

    def _calcular_intensidad(
        self, emergencia: float, coherencia: float
    ) -> float:
        """La intensidad refleja la fuerza del proyecto existencial"""
        return min(1.0, emergencia * 0.6 + coherencia * 0.4)

    def _extraer_prediccion(
        self,
        tipo_yo: str,
        prediccion_s4: Optional[Any],
        coherencia: float,
    ) -> str:
        """Genera predicción semántica basada en tipo de YO"""
        predicciones = {
            "PROTO_YO": "Sistema en estado basal, recopilar más datos",
            "YO_SENSORIAL": "Procesando estímulos, emergencia sensorial inminente",
            "YO_AFECTIVO": "Evaluación emocional en curso, consolidar valencia",
            "YO_REFLEXIVO": "Auto-observación activa, buscar coherencia",
            "YO_SIMBOLICO": "Abstracción en progreso, emerger conceptos",
            "YO_NARRATIVO": f"Narrativa integrada (coherencia={coherencia:.2f}), proyectar futuro",
        }
        return predicciones.get(tipo_yo, "Estado indefinido")

    def _generar_acciones(
        self,
        tipo_yo: str,
        coherencia: float,
        contextos: Optional[List[Dict]],
    ) -> List[str]:
        """Genera acciones sugeridas para el sistema"""
        acciones = []

        if coherencia < 0.3:
            acciones.append("Recopilar más datos de entrada")
            acciones.append("Activar exploración en S1")

        if coherencia < 0.5:
            acciones.append("Buscar patrones en S2")
            acciones.append("Ejecutar ciclo de emergencia conceptual")

        if tipo_yo in ("YO_REFLEXIVO", "YO_SIMBOLICO", "YO_NARRATIVO"):
            acciones.append("Ejecutar retroalimentación YO→Instancias")

        if tipo_yo == "YO_NARRATIVO":
            acciones.append("Generar informe de coherencia narrativa")
            acciones.append("Persistir estado en Neo4j")

        if not acciones:
            acciones.append("Mantener observación pasiva")

        return acciones

    def to_obsidian_md(self) -> str:
        """Genera nota Obsidian con las proyecciones"""
        lineas = [
            "---",
            "tags:",
            "  - sistema/voluntad",
            "  - nivel/proyeccion",
            "---",
            "",
            "# → Voluntad (Motor de Proyección)",
            "",
            f"**Proyecciones totales:** {len(self.proyecciones)}  ",
            "",
            "## Proyecciones Recientes",
            "",
        ]

        for p in self.proyecciones[-5:]:
            lineas.extend([
                f"### 📌 {p.direccion.upper()} — {p.timestamp}",
                f"**Intensidad:** {p.intensidad:.2f}  ",
                f"**Predicción:** {p.prediccion}  ",
                f"**Fundamento:** {p.fundamento}  ",
                "",
                "**Acciones sugeridas:**",
            ])
            for a in p.acciones_sugeridas:
                lineas.append(f"- [ ] {a}")
            lineas.append("")

        return "\n".join(lineas)
