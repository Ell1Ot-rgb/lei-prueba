# MemGraphRAG — Módulo de Integración para Sistema Vivo v4.0

> **Paper:** MemGraphRAG: Memory-based Multi-Agent System for Graph Retrieval-Augmented Generation  
> **Fuente:** arXiv:2606.00610 | KDD 2026 | XMUDeepLIT, Xiamen University  
> **Repositorio oficial:** https://github.com/XMUDeepLIT/MemGraphRAG

---

## Descripción

Este módulo integra el framework **MemGraphRAG** al Sistema Vivo Hexagonal v4.0 como un **adaptador outbound adicional**, sin modificar ningún módulo existente. Coexiste con LightRAG/Graffiti RAG añadiendo un segundo grafo de conocimiento con capacidades únicas:

- **Global Memory de 3 capas** — ontología, hechos y pasajes de evidencia
- **Multi-Agent Group** — 3 agentes colaborativos (A_ext, A_det, A_res)
- **Grafo Jerárquico** — G_ont + G_fac + G_pas en Memgraph (graph DB)
- **Recuperación con PPR** — Personalized PageRank memory-aware

---

## Arquitectura del Módulo

```
adapters/outbound/memgraph_rag/
├── __init__.py                    # Exportaciones del módulo
├── memgraph_rag_adapter.py        # Adaptador principal (interfaz pública)
├── memgraph_client.py             # Conexión Bolt a Memgraph
├── global_memory.py               # Memoria global 3 capas (M_ont/M_fac/M_pas)
├── hierarchical_graph.py          # Constructor G_ont + G_fac + G_pas
├── retrieval.py                   # PPR + Multi-layer filtering
└── agents/
    ├── __init__.py
    ├── extraction_agent.py        # A_ext — Extrae esquemas/hechos/pasajes
    ├── detection_agent.py         # A_det — Detecta conflictos en M_fac
    └── resolution_agent.py        # A_res — Resuelve conflictos con evidencia
```

---

## Instalación

### 1. Instalar Memgraph con Docker

```bash
# Opción A — Un solo comando (recomendado para desarrollo rápido)
docker run -d \
  -p 7687:7687 \
  -p 3000:3000 \
  -p 7444:7444 \
  --name sistema_vivo_memgraph \
  memgraph/memgraph-platform:latest

# Opción B — Docker Compose (recomendado para producción, con persistencia)
docker-compose -f docker-compose.memgraph.yml up -d

# Verificar que Memgraph está corriendo
docker ps
# Acceder a Memgraph Lab UI: http://localhost:3000
```

### 2. Instalar dependencias Python

```bash
pip install -r requirements_memgraph.txt
```

### 3. Configurar variables de entorno (en `.env`)

```env
# MemGraphRAG Configuration
MEMGRAPH_HOST=localhost
MEMGRAPH_PORT=7687
MEMGRAPH_USERNAME=
MEMGRAPH_PASSWORD=
MEMGRAPH_RAG_ENABLED=true
MEMGRAPH_RAG_PORT=7688
SCHEMA_FREQ_THRESHOLD=2
MEMGRAPH_PPR_ALPHA=0.85
MEMGRAPH_PPR_TOP_K=10
MEMGRAPH_SIM_THRESHOLD=0.1
```

---

## Uso Básico

```python
from adapters.outbound.memgraph_rag import MemGraphRAGAdapter

# Inicializar (con o sin Memgraph activo)
rag = MemGraphRAGAdapter()

# Indexar una experiencia
resultado = rag.indexar(
    texto="Sentí una profunda angustia al despertar. El cuerpo pesaba mucho.",
    fuente="diario_2025-01-15",
    tipo_fuente="diario",
    metadata={"fecha": "2025-01-15"},
)
print(resultado)
# → {"estado": "ok", "hechos_nuevos": 3, "conflictos_detectados": 0, ...}

# Consultar el grafo de conocimiento
respuesta = rag.consultar("¿Cuáles son mis patrones de ansiedad recurrentes?")
print(respuesta["contexto"])

# Ver estadísticas
print(rag.estadisticas())
```

### Integración con el Pipeline del Sistema Vivo

```python
# En pipeline_evolucionado.py (sin modificar el código existente):
# Añadir al método de sincronización DESPUÉS del bloque neo4j existente:

if hasattr(self, '_memgraph_rag') and self._memgraph_rag:
    self._memgraph_rag.indexar_resultado_pipeline(resultado_procesado)
```

---

## API REST

Iniciar el servidor en puerto 7688:

```bash
python memgraph_rag_server.py
```

Endpoints disponibles:

```
POST http://localhost:7688/indexar
  Body: {"texto": "...", "fuente": "...", "metadata": {...}}

POST http://localhost:7688/consultar
  Body: {"query": "¿Cuáles son mis patrones de ansiedad?"}

GET  http://localhost:7688/estadisticas
GET  http://localhost:7688/health
GET  http://localhost:7688/grafo/construir
```

---

## Algoritmos Implementados (del Paper)

### 1. Extracción con Filtrado Temático (Sección 4.2.1)
A_ext extrae tripletas y asigna esquemas candidatos. Un esquema se estabiliza cuando su frecuencia ≥ `SCHEMA_FREQ_THRESHOLD`. Solo hechos de esquemas estables pasan al grafo.

### 2. Mantenimiento de Consistencia (Sección 4.2.2)
- **A_det** detecta: Redundancia, Exclusión Mutua, Conflictos Temporales, Conflictos de Valor
- **A_res** resuelve comparando la evidencia textual (pasajes de M_pas)

### 3. Unificación Estructural con Bridging (Sección 4.2.3)
Después de construir G_fac, se añaden bridging edges:
- **Type-based**: entidades del mismo tipo se conectan con IS_SAME_TYPE
- **Similarity-based**: entidades con alta similitud semántica (cuando hay embeddings)

### 4. Recuperación Memory-Guided (Sección 4.3)
1. **Fase 1** — Filtrado multi-capa: consulta M_ont + M_fac + M_pas en paralelo
2. **Fase 2** — Inicialización estructural: P_init(v) por similitud con el query
3. **Fase 3** — PPR: propagación en el grafo heterogéneo G

---

## Verificación de la Instalación

```bash
# Verificar que Python puede importar el módulo
python -c "from adapters.outbound.memgraph_rag import MemGraphRAGAdapter; print('OK')"

# Verificar conexión a Memgraph
python -c "
from adapters.outbound.memgraph_rag.memgraph_client import MemGraphClient
c = MemGraphClient()
print(f'Conectado: {c.esta_conectado()}')
print(c.obtener_estadisticas())
"

# Test completo de indexación + consulta
python -c "
from adapters.outbound.memgraph_rag import MemGraphRAGAdapter
rag = MemGraphRAGAdapter()
rag.indexar('Sentí angustia al despertar esta mañana. El cuerpo pesaba.', fuente='test')
rag.indexar('La alegría llegó cuando medité por 20 minutos.', fuente='test2')
result = rag.consultar('patrones emocionales')
print('Contexto recuperado:', result['contexto'][:200])
print('Estadísticas:', rag.estadisticas()['memoria_global'])
"
```

---

## Funcionamiento sin Memgraph (Modo Memoria Local)

Si Memgraph no está disponible (Docker no instalado), el módulo opera en **modo memoria local**:
- Los datos se almacenan en RAM (no persisten entre sesiones)
- Todas las funciones de indexación y consulta están disponibles
- El PPR corre de forma iterativa sobre el grafo en memoria
- No hay Memgraph Lab UI disponible

Esto permite desarrollo y pruebas sin necesidad de Docker.

---

## Referencia del Paper

```bibtex
@article{wu2026memgraphrag,
  title={MemGraphRAG: Memory-based Multi-Agent System for Graph Retrieval-Augmented Generation},
  author={Chuanjie Wu and Zhishang Xiang and Yunbo Tang and Zerui Chen and Qinggang Zhang and Jinsong Su},
  booktitle={Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining},
  year={2026},
  url={https://arxiv.org/abs/2606.00610}
}
```
