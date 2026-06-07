"""
MemGraphRAG — Adaptador outbound para Sistema Vivo Hexagonal v4.0
=================================================================

Implementación del framework MemGraphRAG (KDD 2026, arXiv:2606.00610):
  "Memory-based Multi-Agent System for Graph Retrieval-Augmented Generation"
  Wu et al., XMUDeepLIT, Xiamen University

Integrado como adaptador hexagonal outbound, sin modificar ningún módulo existente.

Estructura del módulo:
    MemGraphRAGAdapter  → Clase principal de interfaz
    GlobalMemory        → Memoria global de 3 capas (Ont/Fac/Pas)
    ExtractionAgent     → A_ext: extrae esquemas, hechos y pasajes
    DetectionAgent      → A_det: detecta redundancias y conflictos lógicos
    ResolutionAgent     → A_res: resuelve conflictos con evidencia histórica
    HierarchicalGraph   → Constructor de G_ont, G_fac, G_pas en Memgraph
    MemGraphRetrieval   → PPR + filtrado multi-capa para recuperación
    MemGraphClient      → Conexión Bolt al servidor Memgraph

Uso básico:
    from adapters.outbound.memgraph_rag import MemGraphRAGAdapter

    rag = MemGraphRAGAdapter()
    rag.indexar(texto="Mi experiencia de hoy fue...", metadata={...})
    resultado = rag.consultar("¿Cuáles son los fenómenos más recurrentes?")
"""

from .memgraph_rag_adapter import MemGraphRAGAdapter
from .global_memory import GlobalMemory
from .memgraph_client import MemGraphClient

__all__ = [
    "MemGraphRAGAdapter",
    "GlobalMemory",
    "MemGraphClient",
]

__version__ = "1.0.0"
__paper__ = "arXiv:2606.00610 — MemGraphRAG (KDD 2026)"
