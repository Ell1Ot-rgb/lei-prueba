"""
MemGraphRetrieval — Recuperación Jerárquica con Memoria para MemGraphRAG
=========================================================================

Implementa el algoritmo de recuperación Memory-guided descrito en el paper:
  "MemGraphRAG: Memory-based Multi-Agent System for Graph RAG"
  Sección 4.3 — Memory-guided Online Retrieval

El pipeline de recuperación tiene 3 fases (paper, Sección 4.3):

    Fase 1 — Multi-Layer Memory Filtering (Sección 4.3.1):
        - Consulta en paralelo M_ont, M_fac y M_pas
        - Retiene solo candidatos con similitud(q, x) > τ (umbral)
        - Si F_ret ∪ S_ret = ∅ → fallback a RAG clásico (búsqueda vectorial)

    Fase 2 — Structure-Aware Node Initialization (Sección 4.3.2):
        - Asigna pesos iniciales P_init(v) a cada nodo del grafo
        - Entity nodes: media de similitud sobre hechos recuperados F_e ⊆ F_ret
        - Type nodes: similitud de los esquemas recuperados
        - Passage nodes: similitud directa con el query

    Fase 3 — Personalized PageRank (Sección 4.3.3):
        - Propaga P_init por el grafo heterogéneo G
        - PPR con factor de amortiguación α (personalizado)
        - Ranking global de nodos y pasajes importantes para el LLM

Referencia: Section 4.3 + Appendix D (prompts de recuperación) del paper
"""

import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .global_memory import GlobalMemory, Fact, Passage, Schema
from .memgraph_client import MemGraphClient
from .hierarchical_graph import HierarchicalGraph

logger = logging.getLogger(__name__)


@dataclass
class NodoRankeado:
    """Nodo del grafo con su puntuación PPR."""
    id: str
    tipo: str          # "entity", "schema", "passage"
    nombre: str
    score_ppr: float   # Puntuación Personalized PageRank
    evidencia: str = field(default="")  # Texto del pasaje (si tipo="passage")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "nombre": self.nombre,
            "score_ppr": self.score_ppr,
            "evidencia": self.evidencia[:300] if self.evidencia else "",
        }


class MemGraphRetrieval:
    """
    Motor de recuperación Memory-guided del framework MemGraphRAG.

    Combina búsqueda en las 3 capas de la Global Memory con
    propagación por grafo (Personalized PageRank) para identificar
    los nodos y pasajes más relevantes para una consulta.

    Configuración (via .env):
        MEMGRAPH_PPR_ALPHA: factor de amortiguación PPR (default: 0.85)
        MEMGRAPH_PPR_TOP_K: top-K nodos a retornar (default: 10)
        MEMGRAPH_SIM_THRESHOLD: umbral de similitud (default: 0.1)
    """

    def __init__(
        self,
        memoria: GlobalMemory,
        cliente: MemGraphClient,
        grafo: HierarchicalGraph,
        alpha: float = None,
        top_k: int = None,
        sim_threshold: float = None,
    ):
        self.memoria = memoria
        self.cliente = cliente
        self.grafo = grafo

        self.alpha = float(alpha or os.environ.get("MEMGRAPH_PPR_ALPHA", "0.85"))
        self.top_k = int(top_k or os.environ.get("MEMGRAPH_PPR_TOP_K", "10"))
        self.sim_threshold = float(
            sim_threshold or os.environ.get("MEMGRAPH_SIM_THRESHOLD", "0.1")
        )

        logger.info(
            f"[MemGraphRetrieval] Inicializado — α={self.alpha}, "
            f"top_k={self.top_k}, τ={self.sim_threshold}"
        )

    def recuperar(
        self,
        query: str,
        max_tokens_contexto: int = 2000,
    ) -> Dict:
        """
        Pipeline completo de recuperación para una consulta.

        Returns:
            Diccionario con contexto recuperado y metadatos
        """
        logger.info(f"[MemGraphRetrieval] Recuperando para: '{query[:80]}'")

        # ── FASE 1: Multi-Layer Memory Filtering ──
        esquemas_ret, hechos_ret, pasajes_ret = self._filtrar_memoria_multicapa(query)

        hay_candidatos_struct = bool(esquemas_ret or hechos_ret)

        if not hay_candidatos_struct:
            logger.info("[MemGraphRetrieval] Fallback a RAG clásico")
            return self._fallback_rag_clasico(query, pasajes_ret, max_tokens_contexto)

        # ── FASE 2: Structure-Aware Node Initialization ──
        pesos_iniciales = self._inicializar_nodos(query, esquemas_ret, hechos_ret, pasajes_ret)

        # ── FASE 3: Personalized PageRank ──
        nodos_rankeados = self._personalized_pagerank(pesos_iniciales)

        # ── CONSTRUCCIÓN DEL CONTEXTO ──
        contexto = self._construir_contexto(
            query=query,
            nodos_rankeados=nodos_rankeados,
            pasajes_ret=pasajes_ret,
            max_tokens=max_tokens_contexto,
        )

        return {
            "contexto": contexto,
            "nodos_top": [n.to_dict() for n in nodos_rankeados[:self.top_k]],
            "esquemas_activos": [s.to_dict() for s in esquemas_ret[:5]],
            "hechos_relevantes": [f.to_dict() for f in hechos_ret[:10]],
            "pasajes_directos": [p.to_dict() for p in pasajes_ret[:5]],
            "modo": "memgraph_rag",
            "metadata": {
                "total_nodos_evaluados": len(pesos_iniciales),
                "alpha_ppr": self.alpha,
                "top_k": self.top_k,
            },
        }

    # ─── FASE 1 ────────────────────────────────────────────────────────────────

    def _filtrar_memoria_multicapa(
        self,
        query: str,
    ) -> Tuple[List[Schema], List[Fact], List[Passage]]:
        """Fase 1: Filtrado multi-capa paralelo sobre M_ont, M_fac y M_pas."""
        query_tokens = set(query.lower().split())

        # M_ont: esquemas estables
        esquemas_ret = []
        for schema in self.memoria.obtener_schemas_estables():
            schema_text = f"{schema.tipo_head} {schema.relacion} {schema.tipo_tail}"
            sim = self._similitud_jaccard(query_tokens, set(schema_text.lower().split()))
            if sim > self.sim_threshold:
                esquemas_ret.append(schema)

        # M_fac: hechos activos
        hechos_con_sim = []
        for hecho in self.memoria.obtener_hechos_activos():
            hecho_text = f"{hecho.entidad_head} {hecho.relacion} {hecho.entidad_tail}"
            sim = self._similitud_jaccard(query_tokens, set(hecho_text.lower().split()))
            if sim > self.sim_threshold:
                hechos_con_sim.append((hecho, sim))

        hechos_con_sim.sort(key=lambda x: x[1], reverse=True)
        hechos_ret = [h for h, _ in hechos_con_sim[:self.top_k * 2]]

        # M_pas: pasajes
        pasajes_sim = self.memoria.buscar_pasajes_por_similitud(query, top_k=self.top_k)
        pasajes_ret = [p for p, sim in pasajes_sim if sim > self.sim_threshold * 0.5]

        logger.debug(
            f"[MemGraphRetrieval] Fase1: {len(esquemas_ret)} esquemas, "
            f"{len(hechos_ret)} hechos, {len(pasajes_ret)} pasajes"
        )
        return esquemas_ret, hechos_ret, pasajes_ret

    # ─── FASE 2 ────────────────────────────────────────────────────────────────

    def _inicializar_nodos(
        self,
        query: str,
        esquemas_ret: List[Schema],
        hechos_ret: List[Fact],
        pasajes_ret: List[Passage],
    ) -> Dict[str, float]:
        """Fase 2: Inicialización de pesos P_init(v) para cada nodo."""
        pesos: Dict[str, float] = defaultdict(float)
        query_tokens = set(query.lower().split())

        # Entity nodes (via hechos)
        entidad_a_sims: Dict[str, List[float]] = defaultdict(list)
        for hecho in hechos_ret:
            hecho_text = f"{hecho.entidad_head} {hecho.relacion} {hecho.entidad_tail}"
            sim = self._similitud_jaccard(query_tokens, set(hecho_text.lower().split()))
            entidad_a_sims[hecho.entidad_head].append(sim)
            entidad_a_sims[hecho.entidad_tail].append(sim)

        for entidad, sims in entidad_a_sims.items():
            pesos[f"entity:{entidad}"] = sum(sims) / len(sims)

        # Type nodes (via schemas)
        for schema in esquemas_ret:
            schema_text = f"{schema.tipo_head} {schema.relacion} {schema.tipo_tail}"
            sim = self._similitud_jaccard(query_tokens, set(schema_text.lower().split()))
            pesos[f"schema:{schema.tipo_head}"] = max(pesos.get(f"schema:{schema.tipo_head}", 0), sim)
            pesos[f"schema:{schema.tipo_tail}"] = max(pesos.get(f"schema:{schema.tipo_tail}", 0), sim * 0.8)

        # Passage nodes
        for pasaje in pasajes_ret:
            pasaje_tokens = set(pasaje.texto.lower().split())
            sim = self._similitud_jaccard(query_tokens, pasaje_tokens)
            pesos[f"passage:{pasaje.id}"] = sim

        return dict(pesos)

    # ─── FASE 3 ────────────────────────────────────────────────────────────────

    def _personalized_pagerank(
        self,
        pesos_iniciales: Dict[str, float],
        max_iter: int = 20,
    ) -> List[NodoRankeado]:
        """
        Fase 3: PPR iterativo sobre el grafo heterogéneo.
        
        PPR(v) = (1-α) * P_init(v) + α * Σ PPR(u)/out_degree(u)
        """
        if not pesos_iniciales:
            return []

        total = sum(pesos_iniciales.values())
        if total == 0:
            return []
        pesos_norm = {k: v / total for k, v in pesos_iniciales.items()}

        # Intentar PPR nativo de MAGE en Memgraph
        if not self.cliente._modo_memoria:
            resultado_mage = self._ppr_via_memgraph_mage(pesos_norm)
            if resultado_mage:
                return resultado_mage

        # PPR iterativo en memoria
        scores = dict(pesos_norm)

        # Construir grafo de adyacencia desde aristas en memoria
        adyacente: Dict[str, Set[str]] = defaultdict(set)
        for arista in self.grafo._grafo_memoria.get("aristas", []):
            nodo_from = self._normalizar_id(arista["from"])
            nodo_to = self._normalizar_id(arista["to"])
            adyacente[nodo_from].add(nodo_to)
            adyacente[nodo_to].add(nodo_from)  # Bidireccional

        # Iteraciones PPR
        for _ in range(max_iter):
            nuevos_scores: Dict[str, float] = {}

            # Actualizar nodos con pesos iniciales
            for nodo in set(list(scores.keys()) + list(adyacente.keys())):
                vecinos = adyacente.get(nodo, set())
                vecinos_contrib = 0.0
                for vecino in vecinos:
                    grado = max(len(adyacente.get(vecino, set())), 1)
                    vecinos_contrib += scores.get(vecino, 0.0) / grado

                nuevos_scores[nodo] = (
                    (1 - self.alpha) * pesos_norm.get(nodo, 0.0)
                    + self.alpha * vecinos_contrib
                )

            scores = nuevos_scores

        # Construir lista de NodoRankeado
        resultados: List[NodoRankeado] = []
        for nodo_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if score < 0.001:
                continue

            if nodo_id.startswith("passage:"):
                passage_id = nodo_id[8:]  # quitar "passage:"
                pasaje = self.memoria.M_pas.get(passage_id)
                resultados.append(NodoRankeado(
                    id=nodo_id,
                    tipo="passage",
                    nombre=passage_id,
                    score_ppr=score,
                    evidencia=pasaje.texto if pasaje else "",
                ))
            elif nodo_id.startswith("entity:"):
                entidad = nodo_id[7:]  # quitar "entity:"
                resultados.append(NodoRankeado(
                    id=nodo_id,
                    tipo="entity",
                    nombre=entidad,
                    score_ppr=score,
                ))
            elif nodo_id.startswith("schema:"):
                tipo = nodo_id[7:]  # quitar "schema:"
                resultados.append(NodoRankeado(
                    id=nodo_id,
                    tipo="schema",
                    nombre=tipo,
                    score_ppr=score,
                ))

        return resultados[:self.top_k * 3]

    def _ppr_via_memgraph_mage(self, pesos_norm: Dict[str, float]) -> Optional[List[NodoRankeado]]:
        """Intenta usar PageRank nativo de MAGE si está disponible."""
        try:
            query = """
            CALL pagerank.get()
            YIELD node, rank
            WHERE rank > 0.001
            RETURN node.nombre AS nombre, node.tipo AS tipo, rank
            ORDER BY rank DESC
            LIMIT $top_k
            """
            resultados = self.cliente.ejecutar_cypher(query, {"top_k": self.top_k})
            if not resultados:
                return None

            nodos = []
            for r in resultados:
                nodos.append(NodoRankeado(
                    id=f"entity:{r.get('nombre', '?')}",
                    tipo=r.get("tipo", "entity"),
                    nombre=str(r.get("nombre", "?")),
                    score_ppr=float(r.get("rank", 0)),
                ))
            return nodos if nodos else None

        except Exception:
            return None  # MAGE no disponible, usar PPR iterativo

    # ─── CONSTRUCCIÓN DE CONTEXTO ──────────────────────────────────────────────

    def _construir_contexto(
        self,
        query: str,
        nodos_rankeados: List[NodoRankeado],
        pasajes_ret: List[Passage],
        max_tokens: int = 2000,
    ) -> str:
        """Construye el contexto estructurado para el LLM desde los nodos rankeados."""
        partes_contexto = []
        tokens_usados = 0

        # Hechos de entidades top
        hechos_contexto = []
        entidades_top = [n for n in nodos_rankeados if n.tipo == "entity"][:self.top_k]

        for nodo in entidades_top:
            hechos_rel = self.memoria.obtener_hechos_similares(
                entidad_head=nodo.nombre,
                relacion="",
            )
            for hecho in hechos_rel[:3]:
                hecho_str = (
                    f"• {hecho.entidad_head} [{hecho.relacion}] {hecho.entidad_tail} "
                    f"(confianza: {hecho.confianza:.2f})"
                )
                hechos_contexto.append(hecho_str)

        if hechos_contexto:
            partes_contexto.append(
                "## Hechos relevantes del conocimiento:\n" + "\n".join(hechos_contexto[:10])
            )
            tokens_usados += len(" ".join(hechos_contexto).split())

        # Pasajes de evidencia
        pasajes_top = [n for n in nodos_rankeados if n.tipo == "passage"][:5]
        pasajes_contexto = []

        for pasaje in pasajes_ret[:3]:
            if tokens_usados < max_tokens and pasaje.texto:
                tokens_pasaje = len(pasaje.texto.split())
                if tokens_usados + tokens_pasaje <= max_tokens:
                    pasajes_contexto.append(f"---\n{pasaje.texto}")
                    tokens_usados += tokens_pasaje

        for nodo in pasajes_top:
            if nodo.evidencia and tokens_usados < max_tokens:
                tokens_pasaje = len(nodo.evidencia.split())
                if tokens_usados + tokens_pasaje <= max_tokens:
                    pasajes_contexto.append(f"---\n{nodo.evidencia}")
                    tokens_usados += tokens_pasaje

        if pasajes_contexto:
            partes_contexto.append(
                "## Evidencia textual relevante:\n" + "\n".join(pasajes_contexto)
            )

        if not partes_contexto:
            return "No se encontró contexto suficiente para la consulta en MemGraphRAG."

        return "\n\n".join(partes_contexto)

    def _fallback_rag_clasico(
        self,
        query: str,
        pasajes: List[Passage],
        max_tokens: int,
    ) -> Dict:
        """Fallback a RAG clásico cuando no hay candidatos estructurales."""
        contexto_parts = [p.texto for p in pasajes[:5] if p.texto]
        return {
            "contexto": "\n\n---\n\n".join(contexto_parts) or "Sin contexto disponible",
            "nodos_top": [],
            "esquemas_activos": [],
            "hechos_relevantes": [],
            "pasajes_directos": [p.to_dict() for p in pasajes[:5]],
            "modo": "rag_clasico_fallback",
            "metadata": {"motivo": "sin_candidatos_estructurales"},
        }

    @staticmethod
    def _similitud_jaccard(tokens_a: Set[str], tokens_b: Set[str]) -> float:
        """Similitud de Jaccard entre dos conjuntos de tokens."""
        if not tokens_a or not tokens_b:
            return 0.0
        interseccion = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return interseccion / union if union > 0 else 0.0

    @staticmethod
    def _normalizar_id(raw_id: str) -> str:
        """Normaliza IDs de aristas para el algoritmo PPR."""
        if raw_id.startswith("ent:"):
            return "entity:" + raw_id[4:]
        elif raw_id.startswith("pas:"):
            return "passage:" + raw_id[4:]
        elif raw_id.startswith("tipo:"):
            return "schema:" + raw_id[5:]
        return raw_id
