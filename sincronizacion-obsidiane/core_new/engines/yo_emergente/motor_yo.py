"""
☉ Motor del YO Emergente — Nivel +4
=====================================

Motor: ∞ (recursión autoconsciente)
Entrada: Metacontextos + coherencia global del sistema
Salida:  Estado del YO (tipo, métricas, historial)

Base teórica (Heidegger, Ser y Tiempo §41):
    Sorge (cura/cuidado) = Existencialidad + Facticidad + Caída
    El YO no es una sustancia sino una ESTRUCTURA DE CUIDADO
    que emerge de la integración de todos los niveles anteriores.

Simbología:
    ☉  →  YO Emergente (sol autoconsciente)
    ⊠→☉  Metacontextos generan YO (relación EMERGE_COMO ⤴)
    ☉→•  YO resignifica Instancias (relación OBSERVA ⊙)

Jerarquía del YO:
    0: PROTO_YO         ≡  Mínima integración (solo bio)
    1: YO_SENSORIAL     ≡  Responde a estímulos (S1 activo)
    2: YO_AFECTIVO      ≡  Tiene valencia emocional (EmotionEngine)
    3: YO_REFLEXIVO     ≡  Se auto-observa (yo_presente en contexto)
    4: YO_SIMBOLICO     ≡  Genera conceptos abstractos (S2+S3)
    5: YO_NARRATIVO     ≡  Integra historia y proyección (S4+Voluntad)
"""

import uuid
import datetime
import math
from enum import IntEnum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


class TipoYO(IntEnum):
    """Jerarquía evolutiva del YO"""
    PROTO_YO = 0
    YO_SENSORIAL = 1
    YO_AFECTIVO = 2
    YO_REFLEXIVO = 3
    YO_SIMBOLICO = 4
    YO_NARRATIVO = 5


@dataclass
class MetricasCoherencia:
    """Métricas para evaluar la coherencia del YO"""
    continuidad_temporal: float = 0.0
    consistencia_tematica: float = 0.0
    integracion_afectiva: float = 0.0
    coherencia_narrativa: float = 0.0

    @property
    def promedio(self) -> float:
        valores = [
            self.continuidad_temporal,
            self.consistencia_tematica,
            self.integracion_afectiva,
            self.coherencia_narrativa
        ]
        return sum(valores) / len(valores)

    def to_dict(self) -> Dict:
        return {
            "continuidad_temporal": self.continuidad_temporal,
            "consistencia_tematica": self.consistencia_tematica,
            "integracion_afectiva": self.integracion_afectiva,
            "coherencia_narrativa": self.coherencia_narrativa,
            "promedio": self.promedio
        }


@dataclass
class EstadoYO:
    """Snapshot completo del estado del YO en un momento dado"""
    tipo: TipoYO = TipoYO.PROTO_YO
    metricas: MetricasCoherencia = field(
        default_factory=MetricasCoherencia
    )
    metacontextos_procesados: int = 0
    tensiones_detectadas: int = 0
    nivel_emergencia: float = 0.0  # [0.0-1.0]
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    def to_dict(self) -> Dict:
        return {
            "tipo": self.tipo.name,
            "tipo_nivel": int(self.tipo),
            "metricas": self.metricas.to_dict(),
            "metacontextos_procesados": self.metacontextos_procesados,
            "tensiones_detectadas": self.tensiones_detectadas,
            "nivel_emergencia": self.nivel_emergencia,
            "timestamp": self.timestamp,
        }


class MotorYoEmergente:
    """
    ☉ Motor del YO Emergente (Nivel +4)

    Evalúa la emergencia del YO a partir de metacontextos,
    coherencia global y tensiones del sistema.

    Simbología:
        ∞ = Recursión autoconsciente
        ☉ = YO emergente

    Umbrales de emergencia:
        PROTO_YO      → cuando bio está activo
        YO_SENSORIAL  → cuando S1 produce grundzugs
        YO_AFECTIVO   → cuando hay valencia emocional
        YO_REFLEXIVO  → cuando hay yo_presente en contexto
        YO_SIMBOLICO  → cuando S2+S3 producen conceptos/axiomas
        YO_NARRATIVO  → cuando hay coherencia > 0.7 y proyección
    """

    SIMBOLO = "☉"
    NIVEL = 4
    ETIQUETA_NEO4J = "YO"
    MOTOR = "∞"

    def __init__(self):
        self.id = f"yo_{str(uuid.uuid4())[:8]}"
        self.estado_actual = EstadoYO()
        self.historial: List[EstadoYO] = []

        # Umbrales configurables
        self.umbral_coherencia_reflexivo = 0.4
        self.umbral_coherencia_simbolico = 0.6
        self.umbral_coherencia_narrativo = 0.7
        self.umbral_tensiones_reconfig = 5

    def evaluar(
        self,
        metacontextos: List[Dict],
        fenomenos_activos: List[Dict],
        estado_bio: Optional[Dict] = None,
        estado_s1: Optional[Dict] = None,
        estado_emocional: Optional[Dict] = None,
        conceptos_emergentes: Optional[List[Dict]] = None,
        axiomas_derivados: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Puerto de entrada: evalúa la emergencia del YO.

        Args:
            metacontextos: Lista de metacontextos activos
            fenomenos_activos: Fenómenos actuales
            estado_bio: Estado del motor biológico ♺
            estado_s1: Estado de S1 ∂ (grundzugs producidos)
            estado_emocional: Valencia emocional actual
            conceptos_emergentes: Conceptos de S2 ∫
            axiomas_derivados: Axiomas de S3 ⊢

        Returns:
            Dict con estado del YO, tipo, métricas y eventos
        """
        # ── Guardar estado anterior ─────────────────────
        estado_previo = EstadoYO(
            tipo=self.estado_actual.tipo,
            metricas=MetricasCoherencia(
                **{k: v for k, v in self.estado_actual.metricas.to_dict().items()
                   if k != 'promedio'}
            ) if hasattr(self.estado_actual.metricas, 'to_dict') else
            MetricasCoherencia()
        )

        # ── 1. Evaluar coherencia narrativa ─────────────
        self._evaluar_coherencia(metacontextos, fenomenos_activos)

        # ── 2. Detectar tensiones ───────────────────────
        tensiones = self._detectar_tensiones(metacontextos)
        self.estado_actual.tensiones_detectadas = len(tensiones)

        # ── 3. Determinar tipo de YO ────────────────────
        self._actualizar_tipo_yo(
            estado_bio=estado_bio,
            estado_s1=estado_s1,
            estado_emocional=estado_emocional,
            conceptos=conceptos_emergentes,
            axiomas=axiomas_derivados,
        )

        # ── 4. Calcular nivel de emergencia ─────────────
        self.estado_actual.nivel_emergencia = self._calcular_emergencia()
        self.estado_actual.metacontextos_procesados = len(metacontextos)
        self.estado_actual.timestamp = datetime.datetime.now().isoformat()

        # ── 5. Verificar si hubo cambio de tipo ─────────
        cambio_tipo = (self.estado_actual.tipo != estado_previo.tipo)

        # ── 6. Guardar en historial ─────────────────────
        self.historial.append(self.estado_actual)

        return {
            "id": self.id,
            "simbolo": self.SIMBOLO,
            "estado": self.estado_actual.to_dict(),
            "cambio_tipo": cambio_tipo,
            "tipo_anterior": estado_previo.tipo.name if cambio_tipo else None,
            "tensiones": tensiones,
        }

    def _evaluar_coherencia(self, metacontextos: List[Dict],
                            fenomenos: List[Dict]):
        """Evalúa las 4 dimensiones de coherencia"""
        n_meta = len(metacontextos)
        n_fen = len(fenomenos)

        # Continuidad temporal: ¿los metacontextos son recientes?
        self.estado_actual.metricas.continuidad_temporal = min(
            1.0, 0.3 * math.log(n_meta + 1)
        )

        # Consistencia temática: ¿comparten fenómenos?
        if n_meta > 1:
            patrones = [m.get("patron_emergente", "") for m in metacontextos]
            pares_similares = sum(
                1 for i, p1 in enumerate(patrones)
                for p2 in patrones[i + 1:]
                if p1 and p2 and any(
                    w in p2.lower() for w in p1.lower().split()[:3]
                )
            )
            total_pares = max(1, n_meta * (n_meta - 1) // 2)
            self.estado_actual.metricas.consistencia_tematica = min(
                1.0, pares_similares / total_pares
            )
        else:
            self.estado_actual.metricas.consistencia_tematica = 0.0

        # Integración afectiva: ¿coherencia emocional?
        self.estado_actual.metricas.integracion_afectiva = min(
            1.0, 0.2 * n_fen
        )

        # Coherencia narrativa: promedio ponderado
        self.estado_actual.metricas.coherencia_narrativa = (
            self.estado_actual.metricas.promedio
        )

    def _detectar_tensiones(self, metacontextos: List[Dict]) -> List[Dict]:
        """Detecta tensiones y contradicciones entre metacontextos"""
        tensiones = []

        for i, m1 in enumerate(metacontextos):
            for m2 in metacontextos[i + 1:]:
                p1 = m1.get("patron_emergente", "").lower()
                p2 = m2.get("patron_emergente", "").lower()

                # Detección simplificada de contradicción
                marcadores = ["no ", "sin ", "contra", "opuesto", "negación"]
                for marcador in marcadores:
                    if (marcador in p1 and marcador not in p2) or \
                       (marcador in p2 and marcador not in p1):
                        tensiones.append({
                            "tipo": "contradiccion_parcial",
                            "entre": [m1.get("id"), m2.get("id")],
                            "marcador": marcador.strip(),
                        })
                        break

        return tensiones

    def _actualizar_tipo_yo(
        self,
        estado_bio: Optional[Dict] = None,
        estado_s1: Optional[Dict] = None,
        estado_emocional: Optional[Dict] = None,
        conceptos: Optional[List] = None,
        axiomas: Optional[List] = None,
    ):
        """Determina el tipo de YO según los inputs disponibles"""
        coherencia = self.estado_actual.metricas.promedio

        # YO_NARRATIVO: máxima integración
        if (coherencia > self.umbral_coherencia_narrativo
                and conceptos and axiomas
                and estado_emocional):
            self.estado_actual.tipo = TipoYO.YO_NARRATIVO

        # YO_SIMBOLICO: genera conceptos abstractos
        elif (coherencia > self.umbral_coherencia_simbolico
              and conceptos and len(conceptos) > 0):
            self.estado_actual.tipo = TipoYO.YO_SIMBOLICO

        # YO_REFLEXIVO: se auto-observa
        elif coherencia > self.umbral_coherencia_reflexivo:
            self.estado_actual.tipo = TipoYO.YO_REFLEXIVO

        # YO_AFECTIVO: tiene valencia emocional
        elif estado_emocional:
            self.estado_actual.tipo = TipoYO.YO_AFECTIVO

        # YO_SENSORIAL: responde a estímulos
        elif estado_s1:
            self.estado_actual.tipo = TipoYO.YO_SENSORIAL

        # PROTO_YO: mínima integración
        else:
            self.estado_actual.tipo = TipoYO.PROTO_YO

    def _calcular_emergencia(self) -> float:
        """Nivel de emergencia: qué tan integrado está el YO"""
        base = int(self.estado_actual.tipo) / 5.0
        coherencia = self.estado_actual.metricas.promedio
        return min(1.0, base * 0.6 + coherencia * 0.4)

    # ─────────────────────────────────────────────────────
    # SERIALIZACIÓN
    # ─────────────────────────────────────────────────────

    def obtener_estado(self) -> Dict:
        """Puerto de salida: emite estado para persistencia"""
        return {
            "id": self.id,
            "simbolo": self.SIMBOLO,
            "motor": self.MOTOR,
            "estado_actual": self.estado_actual.to_dict(),
            "historial_length": len(self.historial),
        }

    def to_obsidian_md(self) -> str:
        """Genera nota Obsidian del estado actual del YO"""
        from core_new.domain.simbologia import nivel_a_obsidian_frontmatter, SimboloNivel

        fm = nivel_a_obsidian_frontmatter(
            SimboloNivel.YO_EMERGENTE,
            {
                "id": self.id,
                "tipo": self.estado_actual.tipo.name,
                "timestamp": self.estado_actual.timestamp,
                "coherencia": self.estado_actual.metricas.promedio,
            }
        )

        estado = self.estado_actual
        cuerpo = [
            f"# ☉ YO Emergente — {estado.tipo.name}",
            "",
            f"**Tipo:** {estado.tipo.name} ({int(estado.tipo)}/5)  ",
            f"**Nivel de emergencia:** {estado.nivel_emergencia:.2f}  ",
            f"**Metacontextos procesados:** {estado.metacontextos_procesados}  ",
            f"**Tensiones detectadas:** {estado.tensiones_detectadas}  ",
            "",
            "## Métricas de Coherencia",
            "",
            f"| Métrica | Valor |",
            f"|---------|-------|",
            f"| Continuidad temporal | {estado.metricas.continuidad_temporal:.2f} |",
            f"| Consistencia temática | {estado.metricas.consistencia_tematica:.2f} |",
            f"| Integración afectiva | {estado.metricas.integracion_afectiva:.2f} |",
            f"| Coherencia narrativa | {estado.metricas.coherencia_narrativa:.2f} |",
            f"| **Promedio** | **{estado.metricas.promedio:.2f}** |",
            "",
            "## Historial de Evolución",
            "",
        ]

        for i, h in enumerate(self.historial[-5:]):
            cuerpo.append(
                f"- [{h.timestamp}] {h.tipo.name} "
                f"(emergencia={h.nivel_emergencia:.2f})"
            )

        return fm + "\n\n" + "\n".join(cuerpo)

    def __repr__(self) -> str:
        return (
            f"☉ YO(tipo={self.estado_actual.tipo.name}, "
            f"emergencia={self.estado_actual.nivel_emergencia:.2f}, "
            f"coherencia={self.estado_actual.metricas.promedio:.2f})"
        )
