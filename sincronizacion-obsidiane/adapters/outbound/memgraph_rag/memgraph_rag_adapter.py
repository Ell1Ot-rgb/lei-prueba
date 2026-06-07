"""
MemGraphRAGAdapter — Adaptador Outbound Principal para Sistema Vivo v4.0
========================================================================

Clase principal de interfaz que une todos los componentes del subsistema
MemGraphRAG. Implementa el patrón de Adaptador Hexagonal (Outbound Port)
del Sistema Vivo Fenomenológico Hexagonal v4.0.

Arquitectura interna:
    ┌─────────────────────────────────────────────────────────┐
    │                  MemGraphRAGAdapter                     │
    │                                                         │
    │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
    │  │ GlobalMemory │  │ Multi-Agent  │  │ Hierarchical│  │
    │  │   M_ont      │  │  Group:      │  │   Graph:    │  │
    │  │   M_fac      │◄►│  A_ext       │  │  G_ont      │  │
    │  │   M_pas      │  │  A_det       │  │  G_fac      │  │
    │  └──────────────┘  │  A_res       │  │  G_pas      │  │
    │                    └──────────────┘  └─────────────┘  │
    │                                                         │
    │  ┌──────────────┐  ┌──────────────────────────────┐   │
    │  │ MemGraphClient│  │    MemGraphRetrieval         │   │
    │  │  (Bolt 7687)  │  │  PPR + Multi-layer filter    │   │
    │  └──────────────┘  └──────────────────────────────┘   │
    └─────────────────────────────────────────────────────────┘

Integración con el Sistema Vivo (sin modificar código existente):
    El adaptador se conecta de forma OPCIONAL al pipeline_evolucionado.py.
    Si la variable MEMGRAPH_RAG_ENABLED=true en el .env, el adaptador
    se instancia y recibe los mismos datos que Neo4jRepository, añadiendo
    un segundo grafo de conocimiento con capacidades MemGraphRAG.

Uso básico:
    # Indexar una experiencia
    rag = MemGraphRAGAdapter()
    rag.indexar(
        texto="Sentí una profunda angustia cuando...",
        fuente="diario_2025-01-15",
        metadata={"fecha": "2025-01-15", "nivel_s": "S2"},
    )

    # Consultar
    resultado = rag.consultar("¿Cuáles son mis patrones de ansiedad recurrentes?")
    print(resultado["contexto"])
"""

import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional

from .memgraph_client import MemGraphClient
from .global_memory import GlobalMemory
from .hierarchical_graph import HierarchicalGraph
from .retrieval import MemGraphRetrieval
from .agents.extraction_agent import ExtractionAgent
from .agents.detection_agent import DetectionAgent
from .agents.resolution_agent import ResolutionAgent

logger = logging.getLogger(__name__)


class MemGraphRAGAdapter:
    """
    Adaptador Outbound: MemGraphRAG para el Sistema Vivo Hexagonal v4.0.

    Gestiona el ciclo completo de MemGraphRAG:
    1. INDEXACIÓN: A_ext extrae → A_det detecta → A_res resuelve → Grafo actualizado
    2. RECUPERACIÓN: Multi-layer filter → PPR → Contexto enriquecido

    Compatibilidad: funciona tanto con Memgraph activo como en modo memoria local.
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        schema_freq_threshold: int = None,
        llm_func: Optional[Callable] = None,
        auto_conectar: bool = True,
    ):
        """
        Args:
            host: Host de Memgraph (default: env MEMGRAPH_HOST o localhost)
            port: Puerto Bolt de Memgraph (default: env MEMGRAPH_PORT o 7687)
            username: Usuario Memgraph (default: env MEMGRAPH_USERNAME)
            password: Password Memgraph (default: env MEMGRAPH_PASSWORD)
            schema_freq_threshold: Umbral de estabilización de esquemas
            llm_func: Función LLM para extracción avanzada (opcional)
            auto_conectar: Si True, conecta automáticamente a Memgraph
        """
        self._habilitado = os.environ.get("MEMGRAPH_RAG_ENABLED", "true").lower() == "true"
        
        if not self._habilitado:
            logger.info("[MemGraphRAGAdapter] Deshabilitado por variable de entorno")
            return

        # ── 1. Inicializar cliente Bolt ──
        self.cliente = MemGraphClient(
            host=host,
            port=port,
            username=username,
            password=password,
        )

        # ── 2. Inicializar Global Memory ──
        self.memoria = GlobalMemory(
            schema_freq_threshold=schema_freq_threshold,
        )

        # ── 3. Inicializar Multi-Agent Group ──
        self.a_ext = ExtractionAgent(
            memoria=self.memoria,
            llm_func=llm_func,
            usar_reglas_base=True,
        )
        self.a_det = DetectionAgent(memoria=self.memoria)
        self.a_res = ResolutionAgent(
            memoria=self.memoria,
            llm_func=llm_func,
        )

        # ── 4. Inicializar Hierarchical Graph ──
        self.grafo = HierarchicalGraph(
            memoria=self.memoria,
            cliente=self.cliente,
        )

        # ── 5. Inicializar Motor de Recuperación ──
        self.retrieval = MemGraphRetrieval(
            memoria=self.memoria,
            cliente=self.cliente,
            grafo=self.grafo,
        )

        # ── 6. Inicializar esquema en Memgraph si está conectado ──
        if auto_conectar and self.cliente.esta_conectado():
            self.cliente.inicializar_esquema()

        # Estadísticas de uso
        self._stats = {
            "fragmentos_indexados": 0,
            "hechos_extraidos": 0,
            "conflictos_detectados": 0,
            "conflictos_resueltos": 0,
            "consultas_realizadas": 0,
        }

        logger.info(
            f"[MemGraphRAGAdapter] Inicializado — "
            f"Memgraph: {'conectado' if self.cliente.esta_conectado() else 'modo memoria'}, "
            f"Paper: arXiv:2606.00610 (MemGraphRAG KDD 2026)"
        )

    def indexar(
        self,
        texto: str,
        fuente: str = "",
        tipo_fuente: str = "experiencia",
        metadata: Dict = None,
        reconstruir_grafo: bool = False,
    ) -> Dict:
        """
        Indexa un fragmento de texto en el sistema MemGraphRAG.
        
        Pipeline completo de indexación:
        1. A_ext: extrae esquemas, hechos y pasajes
        2. A_det: detecta conflictos en los hechos nuevos
        3. A_res: resuelve conflictos detectados
        4. Actualiza el Hierarchical Graph en Memgraph

        Args:
            texto: Texto a indexar (experiencia, nota, diario, etc.)
            fuente: Identificador de fuente (e.g., "diario_2025-01-15")
            tipo_fuente: Categoría del texto
            metadata: Metadatos adicionales (fecha, nivel_s, tags, etc.)
            reconstruir_grafo: Si True, reconstruye G completo después de indexar

        Returns:
            Resumen de la indexación (schemas, hechos, conflictos)
        """
        if not self._habilitado:
            return {"estado": "deshabilitado"}

        metadata = metadata or {}
        inicio = time.time()

        # ── PASO 1: Extracción (A_ext) ──
        schemas_nuevos, hechos_nuevos, pasaje = self.a_ext.procesar_fragmento(
            texto=texto,
            fuente=fuente,
            tipo_fuente=tipo_fuente,
            metadata=metadata,
        )
        self._stats["fragmentos_indexados"] += 1
        self._stats["hechos_extraidos"] += len(hechos_nuevos)

        # ── PASO 2 y 3: Detección y Resolución de Conflictos ──
        total_conflictos = 0
        total_resoluciones = 0

        for hecho_nuevo in hechos_nuevos:
            # A_det escanea en busca de conflictos
            conflictos = self.a_det.escanear_conflictos(hecho_nuevo)
            
            if conflictos:
                total_conflictos += len(conflictos)
                self._stats["conflictos_detectados"] += len(conflictos)

                # A_res resuelve los conflictos detectados
                resoluciones = self.a_res.resolver_conflictos(hecho_nuevo, conflictos)
                total_resoluciones += len(resoluciones)
                self._stats["conflictos_resueltos"] += len(resoluciones)

        # ── PASO 4: Actualizar Hierarchical Graph ──
        if reconstruir_grafo or hechos_nuevos:
            self._actualizar_grafo_incremental(hechos_nuevos, schemas_nuevos, pasaje)

        duracion = time.time() - inicio

        resultado = {
            "estado": "ok",
            "fuente": fuente,
            "hechos_nuevos": len(hechos_nuevos),
            "schemas_estabilizados": len(schemas_nuevos),
            "conflictos_detectados": total_conflictos,
            "conflictos_resueltos": total_resoluciones,
            "pasaje_id": pasaje.id,
            "duracion_segundos": round(duracion, 3),
        }

        logger.info(
            f"[MemGraphRAGAdapter] Indexado completado — {len(hechos_nuevos)} hechos, "
            f"{total_conflictos} conflictos, {duracion:.2f}s"
        )
        return resultado

    def indexar_resultado_pipeline(self, resultado_pipeline: Dict) -> Dict:
        """
        Interfaz de integración con el PipelineEvolucionado del Sistema Vivo.
        
        Recibe el resultado completo del pipeline y extrae el texto + metadata
        para indexar en MemGraphRAG.

        Args:
            resultado_pipeline: Dict del resultado del PipelineEvolucionado
                con campos típicos: texto_integrado, texto_original, metadata, etc.

        Returns:
            Resultado de la indexación
        """
        if not self._habilitado:
            return {"estado": "deshabilitado"}

        # Extraer texto del resultado del pipeline
        texto = (
            resultado_pipeline.get("texto_integrado")
            or resultado_pipeline.get("texto_original")
            or resultado_pipeline.get("contenido")
            or str(resultado_pipeline.get("resultado", ""))
        )

        if not texto:
            logger.warning("[MemGraphRAGAdapter] No se encontró texto en resultado del pipeline")
            return {"estado": "sin_texto"}

        # Extraer metadata
        metadata = {
            "fecha": resultado_pipeline.get("fecha"),
            "nivel_s": resultado_pipeline.get("nivel_s"),
            "tags": resultado_pipeline.get("tags", []),
            "yo_emergente": resultado_pipeline.get("yo_emergente"),
            "nivel_conciencia": resultado_pipeline.get("nivel_conciencia"),
        }
        metadata = {k: v for k, v in metadata.items() if v is not None}

        fuente = resultado_pipeline.get("fuente", resultado_pipeline.get("id", "pipeline"))
        tipo_fuente = resultado_pipeline.get("tipo_fuente", "pipeline_output")

        return self.indexar(
            texto=texto,
            fuente=fuente,
            tipo_fuente=tipo_fuente,
            metadata=metadata,
        )

    def consultar(
        self,
        query: str,
        max_tokens: int = 2000,
    ) -> Dict:
        """
        Realiza una consulta MemGraphRAG sobre el grafo de conocimiento.
        
        Ejecuta el pipeline de recuperación de 3 fases:
        1. Multi-Layer Memory Filtering
        2. Structure-Aware Node Initialization
        3. Personalized PageRank

        Args:
            query: Consulta en lenguaje natural
            max_tokens: Límite de tokens para el contexto generado

        Returns:
            Diccionario con contexto, nodos rankeados y metadatos
        """
        if not self._habilitado:
            return {
                "contexto": "MemGraphRAG deshabilitado",
                "modo": "deshabilitado",
            }

        self._stats["consultas_realizadas"] += 1
        return self.retrieval.recuperar(query=query, max_tokens_contexto=max_tokens)

    def construir_grafo_completo(self) -> Dict:
        """
        Reconstruye el Hierarchical Indexing Graph completo desde la Global Memory.
        Útil después de un batch de indexaciones o para inicialización.
        """
        if not self._habilitado:
            return {"estado": "deshabilitado"}

        logger.info("[MemGraphRAGAdapter] Reconstruyendo grafo completo...")
        stats = self.grafo.construir_grafo_completo()
        return {"estado": "ok", **stats}

    def _actualizar_grafo_incremental(
        self,
        hechos_nuevos: List,
        schemas_nuevos: List,
        pasaje,
    ) -> None:
        """Actualiza el grafo de forma incremental con los nuevos elementos."""
        # Agregar nuevos tipos de esquemas a G_ont
        for schema in schemas_nuevos:
            self.grafo._crear_nodo_tipo(schema.tipo_head)
            self.grafo._crear_nodo_tipo(schema.tipo_tail)
            self.grafo._crear_arista_schema(schema)

        # Agregar nuevos hechos a G_fac
        for hecho in hechos_nuevos:
            schema = self.memoria.obtener_schema_por_id(hecho.schema_id)
            tipo_head = schema.tipo_head if schema else "entidad"
            tipo_tail = schema.tipo_tail if schema else "entidad"
            
            self.grafo._crear_nodo_entidad(hecho.entidad_head, tipo_head)
            self.grafo._crear_nodo_entidad(hecho.entidad_tail, tipo_tail)
            self.grafo._crear_arista_hecho(hecho)

        # Agregar pasaje a G_pas
        if pasaje:
            self.grafo._crear_nodo_pasaje(pasaje)
            for hecho in hechos_nuevos:
                self.grafo._crear_arista_evidencia(hecho, pasaje)

    def estadisticas(self) -> Dict:
        """Retorna estadísticas completas del subsistema MemGraphRAG."""
        if not self._habilitado:
            return {"estado": "deshabilitado"}

        return {
            "uso": self._stats,
            "memoria_global": self.memoria.estadisticas(),
            "grafo": self.grafo.estadisticas_grafo(),
            "agentes": {
                "deteccion": self.a_det.estadisticas(),
                "resolucion": self.a_res.estadisticas(),
            },
            "conexion_memgraph": {
                "activa": self.cliente.esta_conectado(),
                "modo": "memgraph" if self.cliente.esta_conectado() else "memoria_local",
                "host": f"{self.cliente.host}:{self.cliente.port}",
            },
        }

    def exportar_memoria(self) -> Dict:
        """Exporta toda la Global Memory a un diccionario serializable."""
        if not self._habilitado:
            return {}
        return self.memoria.exportar()

    def __repr__(self) -> str:
        if not self._habilitado:
            return "MemGraphRAGAdapter(estado=deshabilitado)"
        stats = self._stats
        return (
            f"MemGraphRAGAdapter("
            f"fragmentos={stats['fragmentos_indexados']}, "
            f"hechos={stats['hechos_extraidos']}, "
            f"consultas={stats['consultas_realizadas']}, "
            f"memgraph={'conectado' if self.cliente.esta_conectado() else 'local'})"
        )
