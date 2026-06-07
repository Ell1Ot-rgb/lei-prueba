"""
HierarchicalGraph — Constructor del Grafo Jerárquico de Indexación para MemGraphRAG
=====================================================================================

Implementa la construcción del Hierarchical Indexing Graph (G) descrita en el paper:
  "MemGraphRAG: Memory-based Multi-Agent System for Graph RAG"
  Sección 4.2.3 — Structural Unification via Memory-Guided Bridging

El grafo jerárquico G = {G_ont, G_fac, G_pas} tiene 3 vistas interconectadas:

    G_ont — Semantic Ontology Graph:
        Nodos: tipos de entidades (schema types)
        Aristas: relaciones válidas entre tipos (esquemas estables)
        Función: backbone lógico — define la estructura de tipos permitidos

    G_fac — Fact Graph:
        Nodos: entidades concretas (e.g., "Einstein", "Alemania")
        Aristas: hechos instanciados (tripletas activas de M_fac)
        Función: habilita razonamiento multi-hop sobre hechos concretos
        Bridging edges: conecta entidades del mismo tipo y similitud

    G_pas — Source Evidence Graph:
        Nodos: pasajes textuales de M_pas + entidades de G_fac
        Aristas: vinculan entidades/hechos a sus pasajes originales
        Función: garantiza trazabilidad — toda ruta tiene evidencia textual

Tecnología de almacenamiento: Memgraph (Bolt/Cypher)
    Con Memgraph: persiste el grafo en el servidor de grafos
    Sin Memgraph: mantiene el grafo en memoria RAM (NetworkX-compatible)

Referencia: Section 4.2.3 + Appendix D.2 del paper
"""

import logging
import os
from typing import Any, Dict, List, Optional, Set, Tuple

from .global_memory import GlobalMemory, Schema, Fact, Passage
from .memgraph_client import MemGraphClient

logger = logging.getLogger(__name__)


class HierarchicalGraph:
    """
    Construye y mantiene el Hierarchical Indexing Graph (G) en Memgraph.
    
    El grafo es la materialización de la Global Memory en una estructura
    de grafo navegable con soporte para:
    - Multi-hop traversal (via G_fac)
    - Schema-guided filtering (via G_ont)
    - Evidence tracing (via G_pas)
    - Bridging connections (similaridad de embeddings + tipos compartidos)
    """

    # Umbral de similitud para crear bridging edges
    UMBRAL_BRIDGING_SIMILITUD = 0.7

    def __init__(
        self,
        memoria: GlobalMemory,
        cliente: MemGraphClient,
    ):
        """
        Args:
            memoria: Referencia a la Global Memory compartida
            cliente: Cliente de conexión a Memgraph
        """
        self.memoria = memoria
        self.cliente = cliente
        
        # Si Memgraph no está disponible, usar grafo en memoria (dict-based)
        self._grafo_memoria: Dict[str, Any] = {
            "nodos": {},    # id → {tipo, propiedades}
            "aristas": []   # [{"from": id, "to": id, "tipo": tipo, "props": {}}]
        }

        logger.info("[HierarchicalGraph] Constructor inicializado")

    def construir_grafo_completo(self) -> Dict:
        """
        Construye las 3 vistas del grafo desde la Global Memory.
        
        Orden de construcción:
        1. G_ont desde M_ont (esquemas estables)
        2. G_fac desde M_fac (hechos activos)
        3. G_pas desde M_pas (pasajes de evidencia)
        4. Bridging edges (conexiones de unificación estructural)

        Returns:
            Estadísticas de construcción
        """
        logger.info("[HierarchicalGraph] Iniciando construcción del grafo completo")
        
        stats = {
            "nodos_ont": 0,
            "aristas_ont": 0,
            "nodos_fac": 0,
            "aristas_fac": 0,
            "nodos_pas": 0,
            "aristas_pas": 0,
            "bridging_edges": 0,
        }

        # ── 1. Construir G_ont ──
        stats.update(self._construir_g_ont())

        # ── 2. Construir G_fac ──
        stats.update(self._construir_g_fac())

        # ── 3. Construir G_pas ──
        stats.update(self._construir_g_pas())

        # ── 4. Crear bridging edges ──
        n_bridging = self._crear_bridging_edges()
        stats["bridging_edges"] = n_bridging

        logger.info(
            f"[HierarchicalGraph] Grafo construido — "
            f"G_ont: {stats['nodos_ont']} nodos / {stats['aristas_ont']} aristas, "
            f"G_fac: {stats['nodos_fac']} nodos / {stats['aristas_fac']} aristas, "
            f"G_pas: {stats['nodos_pas']} nodos / {stats['aristas_pas']} aristas, "
            f"Bridging: {stats['bridging_edges']} aristas"
        )
        return stats

    def _construir_g_ont(self) -> Dict:
        """
        Construye G_ont — Grafo de ontología semántica.
        
        Nodos: tipos de entidades
        Aristas: esquemas estables (tipo_head → tipo_tail)
        """
        schemas_estables = self.memoria.obtener_schemas_estables()
        tipos_creados: Set[str] = set()
        aristas = 0

        for schema in schemas_estables:
            # Crear nodo tipo_head
            if schema.tipo_head not in tipos_creados:
                self._crear_nodo_tipo(schema.tipo_head)
                tipos_creados.add(schema.tipo_head)

            # Crear nodo tipo_tail
            if schema.tipo_tail not in tipos_creados:
                self._crear_nodo_tipo(schema.tipo_tail)
                tipos_creados.add(schema.tipo_tail)

            # Crear arista de schema
            self._crear_arista_schema(schema)
            aristas += 1

        return {
            "nodos_ont": len(tipos_creados),
            "aristas_ont": aristas,
        }

    def _construir_g_fac(self) -> Dict:
        """
        Construye G_fac — Grafo de hechos (entity-relation triples).
        
        Nodos: entidades concretas
        Aristas: hechos activos de M_fac
        """
        hechos_activos = self.memoria.obtener_hechos_activos()
        entidades_creadas: Set[str] = set()
        aristas = 0

        for hecho in hechos_activos:
            # Crear nodo entidad head
            if hecho.entidad_head not in entidades_creadas:
                # Obtener tipo desde el schema
                schema = self.memoria.obtener_schema_por_id(hecho.schema_id)
                tipo = schema.tipo_head if schema else "entidad"
                self._crear_nodo_entidad(hecho.entidad_head, tipo)
                entidades_creadas.add(hecho.entidad_head)

            # Crear nodo entidad tail
            if hecho.entidad_tail not in entidades_creadas:
                schema = self.memoria.obtener_schema_por_id(hecho.schema_id)
                tipo = schema.tipo_tail if schema else "entidad"
                self._crear_nodo_entidad(hecho.entidad_tail, tipo)
                entidades_creadas.add(hecho.entidad_tail)

            # Crear arista del hecho
            self._crear_arista_hecho(hecho)
            aristas += 1

        return {
            "nodos_fac": len(entidades_creadas),
            "aristas_fac": aristas,
        }

    def _construir_g_pas(self) -> Dict:
        """
        Construye G_pas — Grafo de evidencia fuente.
        
        Nodos: pasajes textuales
        Aristas: vinculan hechos/entidades a sus pasajes de evidencia
        """
        aristas = 0
        nodos_pas = 0

        for pasaje in self.memoria.M_pas.values():
            # Crear nodo pasaje
            self._crear_nodo_pasaje(pasaje)
            nodos_pas += 1

            # Crear aristas hecho → pasaje
            fact_ids = self.memoria._passage_to_facts.get(pasaje.id, set())
            for fact_id in fact_ids:
                hecho = self.memoria.M_fac.get(fact_id)
                if hecho and hecho.activo:
                    self._crear_arista_evidencia(hecho, pasaje)
                    aristas += 1

        return {
            "nodos_pas": nodos_pas,
            "aristas_pas": aristas,
        }

    def _crear_bridging_edges(self) -> int:
        """
        Crea bridging edges para unificación estructural.
        
        Dos tipos de bridging edges (del paper, Sección 4.2.3):
        1. Type-based: entidades del mismo tipo comparten arista IS_SAME_TYPE
        2. Similarity-based: entidades con alto embedding similarity (si disponible)
        
        Returns:
            Número de bridging edges creados
        """
        bridging_count = 0
        hechos_activos = self.memoria.obtener_hechos_activos()

        # ── Bridging basado en tipo (más simple, sin embeddings) ──
        # Agrupa entidades por tipo de schema y crea conexiones ligeras
        entidades_por_tipo: Dict[str, List[str]] = {}
        for hecho in hechos_activos:
            schema = self.memoria.obtener_schema_por_id(hecho.schema_id)
            if schema:
                for tipo, entidad in [
                    (schema.tipo_head, hecho.entidad_head),
                    (schema.tipo_tail, hecho.entidad_tail),
                ]:
                    if tipo not in entidades_por_tipo:
                        entidades_por_tipo[tipo] = []
                    if entidad not in entidades_por_tipo[tipo]:
                        entidades_por_tipo[tipo].append(entidad)

        # Crear IS_SAME_TYPE edges (máximo 50 por tipo para no saturar el grafo)
        for tipo, entidades in entidades_por_tipo.items():
            entidades = entidades[:10]  # Máximo 10 entidades por tipo
            for i, ent_a in enumerate(entidades):
                for ent_b in entidades[i+1:]:
                    self._crear_bridging_edge(ent_a, ent_b, tipo)
                    bridging_count += 1

        logger.debug(f"[HierarchicalGraph] {bridging_count} bridging edges creados")
        return bridging_count

    # ─── Operaciones sobre Memgraph (Cypher) ──────────────────────────────────

    def _crear_nodo_tipo(self, tipo: str) -> None:
        """Crea un nodo de tipo en G_ont."""
        if self.cliente._modo_memoria:
            self._grafo_memoria["nodos"][f"tipo:{tipo}"] = {
                "label": "Schema",
                "tipo": tipo,
            }
            return

        query = """
        MERGE (t:Schema {tipo: $tipo})
        ON CREATE SET t.creado = timestamp()
        """
        self.cliente.ejecutar_cypher_write(query, {"tipo": tipo})

    def _crear_arista_schema(self, schema: Schema) -> None:
        """Crea una arista de esquema en G_ont."""
        if self.cliente._modo_memoria:
            self._grafo_memoria["aristas"].append({
                "from": f"tipo:{schema.tipo_head}",
                "to": f"tipo:{schema.tipo_tail}",
                "tipo": "SCHEMA_RELATION",
                "props": {
                    "relacion": schema.relacion,
                    "frecuencia": schema.frecuencia,
                    "schema_id": schema.id,
                }
            })
            return

        query = """
        MATCH (h:Schema {tipo: $tipo_head})
        MATCH (t:Schema {tipo: $tipo_tail})
        MERGE (h)-[r:SCHEMA_RELATION {relacion: $relacion}]->(t)
        ON CREATE SET 
            r.frecuencia = $frecuencia,
            r.schema_id = $schema_id,
            r.creado = timestamp()
        ON MATCH SET
            r.frecuencia = $frecuencia
        """
        self.cliente.ejecutar_cypher_write(query, {
            "tipo_head": schema.tipo_head,
            "tipo_tail": schema.tipo_tail,
            "relacion": schema.relacion,
            "frecuencia": schema.frecuencia,
            "schema_id": schema.id,
        })

    def _crear_nodo_entidad(self, nombre: str, tipo: str) -> None:
        """Crea un nodo de entidad en G_fac."""
        if self.cliente._modo_memoria:
            self._grafo_memoria["nodos"][f"ent:{nombre}"] = {
                "label": "Entity",
                "nombre": nombre,
                "tipo": tipo,
            }
            return

        # Etiqueta dinámica según el tipo de dominio
        etiqueta = tipo.capitalize() if tipo else "Entity"
        query = f"""
        MERGE (e:Entity:{etiqueta} {{nombre: $nombre}})
        ON CREATE SET 
            e.tipo = $tipo,
            e.creado = timestamp(),
            e.peso_inicial = 0.0
        ON MATCH SET
            e.tipo = $tipo
        """
        self.cliente.ejecutar_cypher_write(query, {
            "nombre": nombre,
            "tipo": tipo,
        })

    def _crear_arista_hecho(self, hecho: Fact) -> None:
        """Crea una arista de hecho en G_fac."""
        if self.cliente._modo_memoria:
            self._grafo_memoria["aristas"].append({
                "from": f"ent:{hecho.entidad_head}",
                "to": f"ent:{hecho.entidad_tail}",
                "tipo": hecho.relacion.upper().replace(" ", "_"),
                "props": {
                    "fact_id": hecho.id,
                    "confianza": hecho.confianza,
                    "timestamp": hecho.timestamp,
                }
            })
            return

        # Sanitizar nombre de relación para Cypher
        relacion_cypher = hecho.relacion.upper().replace(" ", "_").replace("-", "_")

        query = f"""
        MATCH (h:Entity {{nombre: $entidad_head}})
        MATCH (t:Entity {{nombre: $entidad_tail}})
        MERGE (h)-[r:{relacion_cypher} {{fact_id: $fact_id}}]->(t)
        ON CREATE SET
            r.confianza = $confianza,
            r.schema_id = $schema_id,
            r.passage_id = $passage_id,
            r.timestamp = $timestamp,
            r.activo = true
        """
        self.cliente.ejecutar_cypher_write(query, {
            "entidad_head": hecho.entidad_head,
            "entidad_tail": hecho.entidad_tail,
            "fact_id": hecho.id,
            "confianza": hecho.confianza,
            "schema_id": hecho.schema_id,
            "passage_id": hecho.passage_id,
            "timestamp": hecho.timestamp,
        })

    def _crear_nodo_pasaje(self, pasaje: Passage) -> None:
        """Crea un nodo de pasaje en G_pas."""
        if self.cliente._modo_memoria:
            self._grafo_memoria["nodos"][f"pas:{pasaje.id}"] = {
                "label": "Passage",
                "id": pasaje.id,
                "texto": pasaje.texto[:200],
                "fuente": pasaje.fuente,
            }
            return

        query = """
        MERGE (p:Passage {passage_id: $passage_id})
        ON CREATE SET
            p.texto = $texto,
            p.fuente = $fuente,
            p.tipo_fuente = $tipo_fuente,
            p.timestamp = $timestamp
        """
        self.cliente.ejecutar_cypher_write(query, {
            "passage_id": pasaje.id,
            "texto": pasaje.texto[:500],  # Limitar tamaño en DB
            "fuente": pasaje.fuente,
            "tipo_fuente": pasaje.tipo_fuente,
            "timestamp": pasaje.timestamp,
        })

    def _crear_arista_evidencia(self, hecho: Fact, pasaje: Passage) -> None:
        """Crea arista hecho/entidad → pasaje en G_pas (función ψ materializada)."""
        if self.cliente._modo_memoria:
            self._grafo_memoria["aristas"].append({
                "from": f"ent:{hecho.entidad_head}",
                "to": f"pas:{pasaje.id}",
                "tipo": "HAS_EVIDENCE",
                "props": {"fact_id": hecho.id}
            })
            return

        query = """
        MATCH (e:Entity {nombre: $entidad_head})
        MATCH (p:Passage {passage_id: $passage_id})
        MERGE (e)-[r:HAS_EVIDENCE {fact_id: $fact_id}]->(p)
        """
        self.cliente.ejecutar_cypher_write(query, {
            "entidad_head": hecho.entidad_head,
            "passage_id": pasaje.id,
            "fact_id": hecho.id,
        })

    def _crear_bridging_edge(self, entidad_a: str, entidad_b: str, tipo: str) -> None:
        """Crea una bridging edge IS_SAME_TYPE entre dos entidades del mismo tipo."""
        if self.cliente._modo_memoria:
            self._grafo_memoria["aristas"].append({
                "from": f"ent:{entidad_a}",
                "to": f"ent:{entidad_b}",
                "tipo": "IS_SAME_TYPE",
                "props": {"tipo_compartido": tipo}
            })
            return

        query = """
        MATCH (a:Entity {nombre: $entidad_a})
        MATCH (b:Entity {nombre: $entidad_b})
        MERGE (a)-[r:IS_SAME_TYPE]->(b)
        ON CREATE SET r.tipo_compartido = $tipo
        """
        self.cliente.ejecutar_cypher_write(query, {
            "entidad_a": entidad_a,
            "entidad_b": entidad_b,
            "tipo": tipo,
        })

    def actualizar_nodo(self, hecho: Fact) -> None:
        """Actualiza un nodo/arista cuando un hecho es modificado por A_res."""
        if not hecho.activo:
            # Desactivar arista en el grafo
            if not self.cliente._modo_memoria:
                relacion_cypher = hecho.relacion.upper().replace(" ", "_").replace("-", "_")
                query = f"""
                MATCH (:Entity)-[r:{relacion_cypher} {{fact_id: $fact_id}}]->(:Entity)
                SET r.activo = false
                """
                self.cliente.ejecutar_cypher_write(query, {"fact_id": hecho.id})

    def obtener_vecinos(self, entidad: str, profundidad: int = 2) -> List[Dict]:
        """
        Retorna los vecinos de una entidad en G_fac.
        Usado por el algoritmo de retrieval para expansión del grafo.
        """
        if self.cliente._modo_memoria:
            # Versión en memoria: busca en las aristas del grafo local
            clave = f"ent:{entidad}"
            vecinos = []
            for arista in self._grafo_memoria["aristas"]:
                if arista["from"] == clave:
                    nodo_dest = arista["to"].replace("ent:", "")
                    vecinos.append({
                        "entidad": nodo_dest,
                        "relacion": arista["tipo"],
                        "props": arista.get("props", {}),
                    })
            return vecinos

        query = f"""
        MATCH (e:Entity {{nombre: $entidad}})-[r*1..{profundidad}]-(vecino:Entity)
        RETURN DISTINCT vecino.nombre AS entidad, 
               type(last(r)) AS relacion,
               last(r).confianza AS confianza
        ORDER BY confianza DESC
        LIMIT 50
        """
        return self.cliente.ejecutar_cypher(query, {"entidad": entidad})

    def estadisticas_grafo(self) -> Dict:
        """Retorna estadísticas del grafo construido."""
        if self.cliente._modo_memoria:
            return {
                "modo": "memoria_local",
                "total_nodos": len(self._grafo_memoria["nodos"]),
                "total_aristas": len(self._grafo_memoria["aristas"]),
            }
        return self.cliente.obtener_estadisticas()
