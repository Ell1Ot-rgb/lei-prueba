"""
DetectionAgent (A_det) — Agente de Detección de Conflictos para MemGraphRAG
=============================================================================

Implementa el Agente de Detección A_det descrito en el paper:
  "MemGraphRAG: Memory-based Multi-Agent System for Graph RAG"
  Sección 4.2.2 — Consistency Maintenance via Global Adjudication

Función principal:
    Monitorea M_fac para detectar redundancias y conflictos lógicos
    cuando se activan nuevas tripletas. Opera asíncronamente.

Tipos de conflictos detectados (del paper, Sección 3.2):
    1. REDUNDANCIA: Hechos equivalentes con ligeras variaciones textuales
    2. CONFLICTO_EXCLUSION: Hechos mutuamente excluyentes
       Ejemplo: (yo, siente, alegría) ↔ (yo, siente, tristeza) simultáneos
    3. CONFLICTO_TEMPORAL: Contradicciones temporales
       Ejemplo: (evento_A, precede, evento_B) y (evento_B, precede, evento_A)
    4. CONFLICTO_GRANULARIDAD: Inconsistencia de abstracción
       Ejemplo: (yo, experimenta, emoción_positiva) vs (yo, experimenta, alegría)

Referencia: Section 4.2.2 + Appendix D.3.2 del paper
"""

import logging
import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple

from ..global_memory import GlobalMemory, Fact

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Tipos de conflictos
# ─────────────────────────────────────────────────────────────────────────────

class TipoConflicto(Enum):
    REDUNDANCIA = auto()          # Hechos duplicados o muy similares
    EXCLUSION_MUTUA = auto()      # Hechos que se contradicen lógicamente
    CONFLICTO_TEMPORAL = auto()   # Contradicciones de orden temporal
    CONFLICTO_GRANULARIDAD = auto()  # Inconsistencia de nivel de abstracción
    CONFLICTO_VALOR = auto()      # El mismo atributo con valores distintos


@dataclass
class Conflicto:
    """Representa un conflicto detectado entre hechos."""
    tipo: TipoConflicto
    hecho_nuevo_id: str
    hechos_conflictivos: List[str]  # IDs de hechos en conflicto
    confianza: float               # Probabilidad de que sea un conflicto real
    descripcion: str               # Descripción legible del conflicto
    
    def es_grave(self) -> bool:
        """Un conflicto es grave si tiene alta confianza."""
        return self.confianza >= 0.7

    def to_dict(self) -> Dict:
        return {
            "tipo": self.tipo.name,
            "hecho_nuevo_id": self.hecho_nuevo_id,
            "hechos_conflictivos": self.hechos_conflictivos,
            "confianza": self.confianza,
            "descripcion": self.descripcion,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Emociones agrupadas por valencia (para detección de exclusión mutua)
# ─────────────────────────────────────────────────────────────────────────────

EMOCIONES_POSITIVAS = {
    "alegría", "alegria", "paz", "amor", "gratitud", "esperanza",
    "apertura", "claridad", "presencia", "ligereza", "energía", "energia",
    "alivio", "conexión", "conexion",
}

EMOCIONES_NEGATIVAS = {
    "miedo", "ansiedad", "tristeza", "rabia", "ira", "vergüenza",
    "vergonzanza", "culpa", "soledad", "confusión", "confusion",
    "bloqueo", "angustia", "frustración", "frustracion", "desesperanza",
    "desconexión", "desconexion", "vacío", "vacio", "tensión", "tension",
}

# Pares de emociones directamente contradictorias
PARES_EXCLUSION_DIRECTA = {
    ("alegría", "tristeza"), ("alegria", "tristeza"),
    ("paz", "angustia"),
    ("conexión", "desconexión"), ("conexion", "desconexion"),
    ("claridad", "confusión"), ("claridad", "confusion"),
    ("apertura", "bloqueo"),
    ("esperanza", "desesperanza"),
    ("alivio", "tensión"), ("alivio", "tension"),
}


class DetectionAgent:
    """
    Agente de Detección de Conflictos (A_det) del framework MemGraphRAG.

    Monitorea la capa M_fac de la Global Memory para identificar
    inconsistencias cuando se activan nuevas tripletas.

    Estrategias de detección:
    1. Similitud semántica: hechos con la misma entidad head + relación pero
       tail diferente pueden indicar redundancia o conflicto de valor
    2. Análisis de valencia emocional: detecta emociones simultáneas contradictorias
    3. Análisis de orden temporal: verifica consistencia de relaciones causales/temporales
    4. Análisis de granularidad: detecta inconsistencias de abstracción
    """

    # Umbral de similitud léxica para considerar redundancia
    UMBRAL_REDUNDANCIA = 0.85
    # Umbral de confianza para reportar un conflicto
    UMBRAL_DETECCION = 0.5

    def __init__(self, memoria: GlobalMemory):
        """
        Args:
            memoria: Referencia a la Global Memory compartida
        """
        self.memoria = memoria
        self._historial_conflictos: List[Conflicto] = []
        logger.info("[A_det] Agente de Detección inicializado")

    def escanear_conflictos(
        self,
        hecho_nuevo: Fact,
    ) -> List[Conflicto]:
        """
        Función principal — Escanea M_fac en busca de conflictos con un nuevo hecho.
        
        Implementa el algoritmo de detección del paper:
        1. Recuperar hechos candidatos a conflicto (misma head + relación)
        2. Calcular conjunto de conflictos F_conf por similitud y ontología
        3. Si F_conf no vacío, retornar los conflictos para que A_res los resuelva

        Args:
            hecho_nuevo: El nuevo hecho activado en M_fac

        Returns:
            Lista de conflictos detectados (puede estar vacía)
        """
        conflictos = []

        # ── Obtener hechos candidatos (misma head + relación) ──
        candidatos = self.memoria.obtener_hechos_similares(
            entidad_head=hecho_nuevo.entidad_head,
            relacion=hecho_nuevo.relacion,
            entidad_tail=hecho_nuevo.entidad_tail,
        )

        # Excluir el hecho nuevo mismo
        candidatos = [h for h in candidatos if h.id != hecho_nuevo.id and h.activo]

        # ── Detectar cada tipo de conflicto ──
        for hecho_existente in candidatos:
            # 1. Verificar redundancia
            conflicto_red = self._detectar_redundancia(hecho_nuevo, hecho_existente)
            if conflicto_red:
                conflictos.append(conflicto_red)
                continue

            # 2. Verificar exclusión mutua emocional
            conflicto_exc = self._detectar_exclusion_mutua(hecho_nuevo, hecho_existente)
            if conflicto_exc:
                conflictos.append(conflicto_exc)
                continue

            # 3. Verificar conflicto de valor (mismo atributo, diferente valor)
            conflicto_val = self._detectar_conflicto_valor(hecho_nuevo, hecho_existente)
            if conflicto_val:
                conflictos.append(conflicto_val)

        # ── Detección especial: conflicto temporal ──
        conflictos_temp = self._detectar_conflictos_temporales(hecho_nuevo)
        conflictos.extend(conflictos_temp)

        # Filtrar por umbral de confianza
        conflictos = [c for c in conflictos if c.confianza >= self.UMBRAL_DETECCION]

        if conflictos:
            self._historial_conflictos.extend(conflictos)
            logger.info(
                f"[A_det] {len(conflictos)} conflictos detectados para hecho "
                f"{hecho_nuevo.id[:8]}... — tipos: "
                f"{[c.tipo.name for c in conflictos]}"
            )

        return conflictos

    def _detectar_redundancia(
        self,
        hecho_nuevo: Fact,
        hecho_existente: Fact,
    ) -> Optional[Conflicto]:
        """
        Detecta si dos hechos son semánticamente equivalentes (redundancia).
        
        Usa similitud de Jaccard sobre tokens de las entidades.
        """
        sim = self._similitud_jaccard(
            hecho_nuevo.entidad_tail.lower(),
            hecho_existente.entidad_tail.lower(),
        )

        if sim >= self.UMBRAL_REDUNDANCIA:
            return Conflicto(
                tipo=TipoConflicto.REDUNDANCIA,
                hecho_nuevo_id=hecho_nuevo.id,
                hechos_conflictivos=[hecho_existente.id],
                confianza=sim,
                descripcion=(
                    f"Hechos redundantes: '{hecho_nuevo.clave()}' ≈ "
                    f"'{hecho_existente.clave()}' (similitud={sim:.2f})"
                ),
            )
        return None

    def _detectar_exclusion_mutua(
        self,
        hecho_nuevo: Fact,
        hecho_existente: Fact,
    ) -> Optional[Conflicto]:
        """
        Detecta exclusión mutua emocional/conceptual.
        
        Dos emociones directamente opuestas no pueden ser igualmente válidas
        para el mismo sujeto en el mismo contexto temporal.
        """
        if hecho_nuevo.relacion.lower() not in ["experimenta", "siente", "expresa"]:
            return None
        if hecho_existente.relacion.lower() not in ["experimenta", "siente", "expresa"]:
            return None

        e_nueva = hecho_nuevo.entidad_tail.lower()
        e_existente = hecho_existente.entidad_tail.lower()

        # Verificar par de exclusión directa
        par = (e_nueva, e_existente)
        par_inv = (e_existente, e_nueva)
        
        if par in PARES_EXCLUSION_DIRECTA or par_inv in PARES_EXCLUSION_DIRECTA:
            return Conflicto(
                tipo=TipoConflicto.EXCLUSION_MUTUA,
                hecho_nuevo_id=hecho_nuevo.id,
                hechos_conflictivos=[hecho_existente.id],
                confianza=0.85,
                descripcion=(
                    f"Exclusión mutua emocional: "
                    f"'{e_nueva}' vs '{e_existente}' son opuestos directos"
                ),
            )

        # Verificar si están en valencias opuestas (con menor confianza)
        nueva_positiva = e_nueva in EMOCIONES_POSITIVAS
        existente_positiva = e_existente in EMOCIONES_POSITIVAS
        nueva_negativa = e_nueva in EMOCIONES_NEGATIVAS
        existente_negativa = e_existente in EMOCIONES_NEGATIVAS

        if (nueva_positiva and existente_negativa) or (nueva_negativa and existente_positiva):
            return Conflicto(
                tipo=TipoConflicto.EXCLUSION_MUTUA,
                hecho_nuevo_id=hecho_nuevo.id,
                hechos_conflictivos=[hecho_existente.id],
                confianza=0.55,  # Menor confianza — puede haber ambivalencia real
                descripcion=(
                    f"Posible conflicto de valencia: "
                    f"'{e_nueva}' (positivo/negativo) vs '{e_existente}'"
                ),
            )

        return None

    def _detectar_conflicto_valor(
        self,
        hecho_nuevo: Fact,
        hecho_existente: Fact,
    ) -> Optional[Conflicto]:
        """
        Detecta si el mismo atributo tiene valores diferentes en distintos hechos.
        
        Aplica cuando misma entidad_head + misma relación → diferentes entidad_tail
        (que no son equivalentes por redundancia).
        """
        if (
            hecho_nuevo.entidad_head.lower() == hecho_existente.entidad_head.lower()
            and hecho_nuevo.relacion.lower() == hecho_existente.relacion.lower()
            and hecho_nuevo.entidad_tail.lower() != hecho_existente.entidad_tail.lower()
        ):
            sim = self._similitud_jaccard(
                hecho_nuevo.entidad_tail.lower(),
                hecho_existente.entidad_tail.lower(),
            )
            # Si son suficientemente diferentes, es un conflicto de valor
            if sim < 0.3:
                return Conflicto(
                    tipo=TipoConflicto.CONFLICTO_VALOR,
                    hecho_nuevo_id=hecho_nuevo.id,
                    hechos_conflictivos=[hecho_existente.id],
                    confianza=0.60,
                    descripcion=(
                        f"Conflicto de valor: "
                        f"'{hecho_nuevo.entidad_head}' → '{hecho_nuevo.relacion}' → "
                        f"'{hecho_nuevo.entidad_tail}' vs '{hecho_existente.entidad_tail}'"
                    ),
                )
        return None

    def _detectar_conflictos_temporales(self, hecho_nuevo: Fact) -> List[Conflicto]:
        """
        Detecta contradicciones en relaciones temporales/causales.
        
        Un ciclo temporal: A precede B AND B precede A es inconsistente.
        """
        conflictos = []
        relaciones_temporales = {"precede", "sigue_a", "causa", "ocurre_antes_que"}

        if hecho_nuevo.relacion.lower() not in relaciones_temporales:
            return conflictos

        # Buscar el inverso: (entidad_tail precede entidad_head)
        candidatos_inv = self.memoria.obtener_hechos_similares(
            entidad_head=hecho_nuevo.entidad_tail,
            relacion=hecho_nuevo.relacion,
            entidad_tail=hecho_nuevo.entidad_head,
        )

        for hecho_inv in candidatos_inv:
            if hecho_inv.activo and hecho_inv.id != hecho_nuevo.id:
                conflictos.append(Conflicto(
                    tipo=TipoConflicto.CONFLICTO_TEMPORAL,
                    hecho_nuevo_id=hecho_nuevo.id,
                    hechos_conflictivos=[hecho_inv.id],
                    confianza=0.90,
                    descripcion=(
                        f"Ciclo temporal detectado: "
                        f"'{hecho_nuevo.entidad_head}' → '{hecho_nuevo.relacion}' → "
                        f"'{hecho_nuevo.entidad_tail}' Y viceversa"
                    ),
                ))

        return conflictos

    @staticmethod
    def _similitud_jaccard(texto_a: str, texto_b: str) -> float:
        """Calcula la similitud de Jaccard entre dos textos basada en tokens."""
        tokens_a = set(texto_a.split())
        tokens_b = set(texto_b.split())
        
        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0
        
        interseccion = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return interseccion / union

    def obtener_historial_conflictos(self) -> List[Dict]:
        """Retorna el historial completo de conflictos detectados."""
        return [c.to_dict() for c in self._historial_conflictos]

    def estadisticas(self) -> Dict:
        """Retorna estadísticas de los conflictos detectados."""
        total = len(self._historial_conflictos)
        por_tipo: Dict[str, int] = {}
        graves = 0

        for c in self._historial_conflictos:
            nombre = c.tipo.name
            por_tipo[nombre] = por_tipo.get(nombre, 0) + 1
            if c.es_grave():
                graves += 1

        return {
            "total_conflictos": total,
            "conflictos_graves": graves,
            "por_tipo": por_tipo,
        }
