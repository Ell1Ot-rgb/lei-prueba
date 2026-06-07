"""
ResolutionAgent (A_res) — Agente de Resolución de Conflictos para MemGraphRAG
==============================================================================

Implementa el Agente de Resolución A_res descrito en el paper:
  "MemGraphRAG: Memory-based Multi-Agent System for Graph RAG"
  Sección 4.2.2 — Consistency Maintenance via Global Adjudication

Función principal:
    Cuando A_det identifica un conjunto de conflictos F_conf, A_res:
    1. Recupera los pasajes de evidencia de M_pas para cada hecho conflictivo
       (función ψ: fact → passage)
    2. Compara la evidencia textual para determinar cuál hecho es más válido
    3. Aplica acciones correctivas:
       a) FILTRAR: Desactivar hechos inválidos o sin evidencia
       b) FUSIONAR: Combinar tripletas redundantes en una más precisa
       c) PRIORIZAR: Mantener el hecho con mayor confianza/evidencia

Principio del paper:
    "A_res leverages fact-evidence grounding to retrieve the provenance
    passages from M_pas and adjudicates conflicts by comparing the
    corresponding textual evidence."

Referencia: Section 4.2.2 + Appendix D.3.2 del paper
"""

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Tuple

from ..global_memory import GlobalMemory, Fact, Passage
from .detection_agent import Conflicto, TipoConflicto

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Acciones de resolución
# ─────────────────────────────────────────────────────────────────────────────

class AccionResolucion(Enum):
    FILTRAR_NUEVO = auto()       # El hecho nuevo es el inválido — filtrar
    FILTRAR_EXISTENTE = auto()   # El hecho existente es el inválido — desactivar
    FUSIONAR = auto()            # Ambos son válidos pero redundantes — fusionar
    PRIORIZAR_NUEVO = auto()     # Priorizar el hecho nuevo (mayor confianza)
    PRIORIZAR_EXISTENTE = auto() # Priorizar el hecho existente (mayor confianza)
    MANTENER_AMBOS = auto()      # Ambos son válidos — no hay conflicto real
    ESCALAR = auto()             # Conflicto ambiguo — requiere LLM para resolver


@dataclass
class ResultadoResolucion:
    """Resultado de la resolución de un conflicto."""
    conflicto: Conflicto
    accion: AccionResolucion
    razon: str
    confianza_resolucion: float
    
    def fue_resuelto(self) -> bool:
        return self.accion != AccionResolucion.ESCALAR

    def to_dict(self) -> Dict:
        return {
            "tipo_conflicto": self.conflicto.tipo.name,
            "accion": self.accion.name,
            "razon": self.razon,
            "confianza_resolucion": self.confianza_resolucion,
            "hecho_nuevo_id": self.conflicto.hecho_nuevo_id,
            "hechos_conflictivos": self.conflicto.hechos_conflictivos,
        }


class ResolutionAgent:
    """
    Agente de Resolución de Conflictos (A_res) del framework MemGraphRAG.

    Aplica resolución basada en evidencia textual:
    1. Recupera los pasajes de evidencia de M_pas para cada hecho en conflicto
    2. Compara la calidad y especificidad de la evidencia
    3. Aplica la acción correctiva apropiada

    Estrategias de resolución por tipo de conflicto:
    - REDUNDANCIA: Fusionar en el hecho con mayor confianza
    - EXCLUSION_MUTUA: Priorizar según confianza; si igual, mantener ambos con nota
    - CONFLICTO_TEMPORAL: Filtrar el que contradice la causalidad más obvia
    - CONFLICTO_VALOR: Comparar longitud/especificidad de pasajes de evidencia
    """

    def __init__(
        self,
        memoria: GlobalMemory,
        llm_func: Optional[Callable] = None,
    ):
        """
        Args:
            memoria: Referencia a la Global Memory compartida
            llm_func: LLM para resoluciones complejas (opcional)
        """
        self.memoria = memoria
        self.llm_func = llm_func
        self._historial_resoluciones: List[ResultadoResolucion] = []
        logger.info("[A_res] Agente de Resolución inicializado")

    def resolver_conflictos(
        self,
        hecho_nuevo: Fact,
        conflictos: List[Conflicto],
    ) -> List[ResultadoResolucion]:
        """
        Función principal — Resuelve una lista de conflictos detectados.
        
        Para cada conflicto en F_conf (del paper):
        1. Recuperar evidencia de M_pas via ψ(f) = p
        2. Adjudicar basándose en la evidencia
        3. Aplicar acción correctiva

        Args:
            hecho_nuevo: El hecho que triggereó la detección de conflictos
            conflictos: Lista de conflictos a resolver (de A_det)

        Returns:
            Lista de resultados de resolución aplicados
        """
        resultados = []

        for conflicto in conflictos:
            # Obtener pasajes de evidencia para todos los hechos involucrados
            evidencia_nueva = self.memoria.obtener_pasajes_de_hecho(
                conflicto.hecho_nuevo_id
            )
            evidencias_conflictivas = [
                (fid, self.memoria.obtener_pasajes_de_hecho(fid))
                for fid in conflicto.hechos_conflictivos
            ]

            # Aplicar estrategia de resolución según tipo de conflicto
            resultado = self._aplicar_estrategia(
                conflicto=conflicto,
                hecho_nuevo=hecho_nuevo,
                evidencia_nueva=evidencia_nueva,
                evidencias_conflictivas=evidencias_conflictivas,
            )

            # Ejecutar la acción de resolución
            self._ejecutar_accion(resultado, hecho_nuevo)

            self._historial_resoluciones.append(resultado)
            resultados.append(resultado)

            logger.info(
                f"[A_res] Conflicto resuelto — tipo={conflicto.tipo.name}, "
                f"acción={resultado.accion.name}, "
                f"confianza={resultado.confianza_resolucion:.2f}"
            )

        return resultados

    def _aplicar_estrategia(
        self,
        conflicto: Conflicto,
        hecho_nuevo: Fact,
        evidencia_nueva: Optional[Passage],
        evidencias_conflictivas: List[Tuple[str, Optional[Passage]]],
    ) -> ResultadoResolucion:
        """
        Selecciona y aplica la estrategia de resolución apropiada.
        """
        # Obtener el hecho existente principal en conflicto
        fact_id_existente = (
            conflicto.hechos_conflictivos[0]
            if conflicto.hechos_conflictivos else None
        )
        hecho_existente = (
            self.memoria.M_fac.get(fact_id_existente)
            if fact_id_existente else None
        )
        evidencia_existente = (
            evidencias_conflictivas[0][1] if evidencias_conflictivas else None
        )

        # ── REDUNDANCIA: Fusionar el más confiable ──
        if conflicto.tipo == TipoConflicto.REDUNDANCIA:
            return self._resolver_redundancia(
                conflicto, hecho_nuevo, hecho_existente,
                evidencia_nueva, evidencia_existente,
            )

        # ── EXCLUSIÓN MUTUA: Priorizar por confianza/evidencia ──
        elif conflicto.tipo == TipoConflicto.EXCLUSION_MUTUA:
            return self._resolver_exclusion(
                conflicto, hecho_nuevo, hecho_existente,
                evidencia_nueva, evidencia_existente,
            )

        # ── CONFLICTO TEMPORAL: Filtrar ciclo ──
        elif conflicto.tipo == TipoConflicto.CONFLICTO_TEMPORAL:
            return self._resolver_temporal(
                conflicto, hecho_nuevo, hecho_existente,
                evidencia_nueva, evidencia_existente,
            )

        # ── CONFLICTO DE VALOR: Comparar especificidad ──
        elif conflicto.tipo == TipoConflicto.CONFLICTO_VALOR:
            return self._resolver_valor(
                conflicto, hecho_nuevo, hecho_existente,
                evidencia_nueva, evidencia_existente,
            )

        # ── Por defecto: mantener ambos ──
        return ResultadoResolucion(
            conflicto=conflicto,
            accion=AccionResolucion.MANTENER_AMBOS,
            razon="Tipo de conflicto no catalogado — manteniendo ambos hechos",
            confianza_resolucion=0.5,
        )

    def _resolver_redundancia(
        self,
        conflicto: Conflicto,
        hecho_nuevo: Fact,
        hecho_existente: Optional[Fact],
        ev_nueva: Optional[Passage],
        ev_existente: Optional[Passage],
    ) -> ResultadoResolucion:
        """
        Resuelve redundancia fusionando los hechos.
        Se mantiene el que tiene mayor confianza; el otro se desactiva.
        """
        if hecho_existente is None:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.MANTENER_AMBOS,
                razon="Hecho existente no encontrado en M_fac",
                confianza_resolucion=0.3,
            )

        conf_nueva = hecho_nuevo.confianza
        conf_existente = hecho_existente.confianza

        # Ponderar por longitud de evidencia (más texto = más específico)
        if ev_nueva:
            conf_nueva += 0.1 * min(len(ev_nueva.texto) / 200, 0.5)
        if ev_existente:
            conf_existente += 0.1 * min(len(ev_existente.texto) / 200, 0.5)

        if conf_nueva >= conf_existente:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.FILTRAR_EXISTENTE,
                razon=(
                    f"Fusión por redundancia: el hecho nuevo tiene mayor confianza "
                    f"({conf_nueva:.2f} vs {conf_existente:.2f})"
                ),
                confianza_resolucion=0.80,
            )
        else:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.FILTRAR_NUEVO,
                razon=(
                    f"Fusión por redundancia: el hecho existente tiene mayor confianza "
                    f"({conf_existente:.2f} vs {conf_nueva:.2f})"
                ),
                confianza_resolucion=0.80,
            )

    def _resolver_exclusion(
        self,
        conflicto: Conflicto,
        hecho_nuevo: Fact,
        hecho_existente: Optional[Fact],
        ev_nueva: Optional[Passage],
        ev_existente: Optional[Passage],
    ) -> ResultadoResolucion:
        """
        Resuelve exclusión mutua emocional.
        
        Principio fenomenológico: La ambivalencia es válida (alegría Y tristeza
        pueden coexistir en experiencias complejas). Si el conflicto tiene
        baja confianza (< 0.75), mantener ambos. Si alta, priorizar por evidencia.
        """
        if conflicto.confianza < 0.75:
            # Ambivalencia emocional — fenómeno válido
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.MANTENER_AMBOS,
                razon=(
                    "Ambivalencia emocional detectada — coexistencia válida "
                    f"(confianza conflicto={conflicto.confianza:.2f})"
                ),
                confianza_resolucion=0.70,
            )

        if hecho_existente is None:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.MANTENER_AMBOS,
                razon="Hecho existente no disponible para comparación",
                confianza_resolucion=0.4,
            )

        # Priorizar el hecho con evidencia más específica
        len_ev_nueva = len(ev_nueva.texto) if ev_nueva else 0
        len_ev_existente = len(ev_existente.texto) if ev_existente else 0

        if hecho_nuevo.confianza > hecho_existente.confianza or len_ev_nueva > len_ev_existente:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.PRIORIZAR_NUEVO,
                razon=(
                    f"Exclusión mutua: priorizando hecho nuevo por mayor evidencia "
                    f"(longitud evidencia: {len_ev_nueva} vs {len_ev_existente})"
                ),
                confianza_resolucion=0.65,
            )
        else:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.PRIORIZAR_EXISTENTE,
                razon=(
                    f"Exclusión mutua: priorizando hecho existente por mayor evidencia "
                    f"(longitud evidencia: {len_ev_existente} vs {len_ev_nueva})"
                ),
                confianza_resolucion=0.65,
            )

    def _resolver_temporal(
        self,
        conflicto: Conflicto,
        hecho_nuevo: Fact,
        hecho_existente: Optional[Fact],
        ev_nueva: Optional[Passage],
        ev_existente: Optional[Passage],
    ) -> ResultadoResolucion:
        """
        Resuelve conflictos temporales/causales (ciclos A→B y B→A).
        
        El hecho con mayor timestamp (más reciente) suele ser más preciso
        porque incorpora información posterior.
        """
        if hecho_existente is None:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.MANTENER_AMBOS,
                razon="Hecho existente no disponible — no se puede determinar precedencia",
                confianza_resolucion=0.3,
            )

        if hecho_nuevo.timestamp >= hecho_existente.timestamp:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.FILTRAR_EXISTENTE,
                razon=(
                    "Conflicto temporal: el hecho nuevo es más reciente — "
                    "eliminando el hecho temporal anterior"
                ),
                confianza_resolucion=0.70,
            )
        else:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.FILTRAR_NUEVO,
                razon=(
                    "Conflicto temporal: el hecho existente es más reciente — "
                    "filtrando el nuevo hecho conflictivo"
                ),
                confianza_resolucion=0.70,
            )

    def _resolver_valor(
        self,
        conflicto: Conflicto,
        hecho_nuevo: Fact,
        hecho_existente: Optional[Fact],
        ev_nueva: Optional[Passage],
        ev_existente: Optional[Passage],
    ) -> ResultadoResolucion:
        """
        Resuelve conflictos de valor comparando especificidad de evidencia.
        
        El hecho con evidencia más específica (mayor longitud y detalle)
        se considera más preciso.
        """
        if hecho_existente is None:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.MANTENER_AMBOS,
                razon="Sin hecho existente — manteniendo ambos valores",
                confianza_resolucion=0.4,
            )

        # Calcular "especificidad" de cada evidencia
        especificidad_nueva = (
            len(ev_nueva.texto.split()) if ev_nueva else 0
        ) * hecho_nuevo.confianza

        especificidad_existente = (
            len(ev_existente.texto.split()) if ev_existente else 0
        ) * hecho_existente.confianza

        if especificidad_nueva > especificidad_existente:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.PRIORIZAR_NUEVO,
                razon=(
                    f"Conflicto de valor: hecho nuevo más específico "
                    f"(especificidad={especificidad_nueva:.1f} vs {especificidad_existente:.1f})"
                ),
                confianza_resolucion=0.60,
            )
        elif especificidad_existente > especificidad_nueva * 1.2:
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.PRIORIZAR_EXISTENTE,
                razon=(
                    f"Conflicto de valor: hecho existente más específico "
                    f"(especificidad={especificidad_existente:.1f} vs {especificidad_nueva:.1f})"
                ),
                confianza_resolucion=0.60,
            )
        else:
            # Similitud suficiente — mantener ambos (pueden ser perspectivas distintas)
            return ResultadoResolucion(
                conflicto=conflicto,
                accion=AccionResolucion.MANTENER_AMBOS,
                razon=(
                    "Conflicto de valor ambiguo — ambas perspectivas son igualmente válidas"
                ),
                confianza_resolucion=0.50,
            )

    def _ejecutar_accion(
        self,
        resultado: ResultadoResolucion,
        hecho_nuevo: Fact,
    ) -> None:
        """
        Ejecuta la acción de resolución modificando M_fac.
        """
        accion = resultado.accion
        conflicto = resultado.conflicto

        if accion == AccionResolucion.FILTRAR_EXISTENTE:
            for fact_id in conflicto.hechos_conflictivos:
                self.memoria.desactivar_hecho(
                    fact_id,
                    razon=f"Resolución por {conflicto.tipo.name}: {resultado.razon}",
                )

        elif accion == AccionResolucion.FILTRAR_NUEVO:
            self.memoria.desactivar_hecho(
                conflicto.hecho_nuevo_id,
                razon=f"Resolución por {conflicto.tipo.name}: {resultado.razon}",
            )

        elif accion == AccionResolucion.PRIORIZAR_EXISTENTE:
            # Reducir confianza del nuevo sin desactivarlo
            if hecho_nuevo.id in self.memoria.M_fac:
                self.memoria.M_fac[hecho_nuevo.id].confianza *= 0.6

        elif accion == AccionResolucion.PRIORIZAR_NUEVO:
            # Reducir confianza del existente sin desactivarlo
            for fact_id in conflicto.hechos_conflictivos:
                if fact_id in self.memoria.M_fac:
                    self.memoria.M_fac[fact_id].confianza *= 0.6

        elif accion in [AccionResolucion.MANTENER_AMBOS, AccionResolucion.FUSIONAR]:
            pass  # No acción inmediata

    def obtener_historial(self) -> List[Dict]:
        """Retorna el historial de resoluciones aplicadas."""
        return [r.to_dict() for r in self._historial_resoluciones]

    def estadisticas(self) -> Dict:
        """Estadísticas de las resoluciones realizadas."""
        total = len(self._historial_resoluciones)
        por_accion: Dict[str, int] = {}
        resueltos = 0

        for r in self._historial_resoluciones:
            nombre = r.accion.name
            por_accion[nombre] = por_accion.get(nombre, 0) + 1
            if r.fue_resuelto():
                resueltos += 1

        return {
            "total_resoluciones": total,
            "resueltos_automaticamente": resueltos,
            "escalados": total - resueltos,
            "por_accion": por_accion,
        }
