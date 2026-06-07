# 🧠 Análisis de Interacción de Contenedores y Base de Datos Neo4j

Este documento detalla la investigación realizada sobre la arquitectura de contenedores, su interacción con la base de datos de grafos Neo4j, y cómo se alinean con la visión arquitectónica del Sistema Vivo (Omega 21 / v4.0).

---

## 1. Contenedores que interactúan con Neo4j

De acuerdo a los archivos de orquestación (`docker-compose.rag.yml`, despliegues en Azure) y el código fuente, existen tres componentes o subsistemas principales que se conectan e interactúan con Neo4j:

1.  **Sistema Vivo v4 / MemGraphRAG Server:** 
    *   **Contenedor en Azure:** `sistema_vivo_v4` (puertos 5680, 7688).
    *   **Rol:** Actúa como el orquestador principal RAG jerárquico. Aunque la documentación (`adapters/outbound/memgraph_rag/README.md`) especifica que fue diseñado originalmente para Memgraph, el código hace uso del protocolo **Bolt** (puerto 7687), lo que lo hace completamente compatible para usar Neo4j como su motor de almacenamiento de fragmentos (Chunks) y hechos extraídos.

2.  **Servidor Custom Graffiti / LightRAG (Refinamiento Semántico):**
    *   **Puerto:** `8000`.
    *   **Rol:** Se encarga de construir la "memoria a largo plazo orgánica". Interactúa con Neo4j para almacenar "episodios" o recuerdos temporales (basado en Zep AI / Graphiti).
    *   **Nota Técnica:** El código (`lightrag_custom_server.py`) inyecta "Monkey Patches" (expresiones regulares) para modificar las consultas Cypher originales de Graphiti, haciéndolas compatibles con Neo4j 5.12 (por ejemplo, ajustando el guardado de embeddings de `SET n.name_embedding`).

3.  **Pipeline Fenomenológico (El Yo Estructural):**
    *   **Módulo:** `ExtensionNeo4j` (`adapters/outbound/neo4j_repository.py`).
    *   **Rol:** Inserta directamente en Neo4j las "5 Rutas Fenomenológicas" (Física, Lógica, Ontológica, etc.) generadas por el sistema. Además, detecta la certeza conceptual (Máximos Relacionales) utilizando algoritmos de grafos (GDS) como PageRank o Louvain.

*(Nota: El contenedor `engram-service` **NO** interactúa con Neo4j. Tiene su propia base de datos dedicada llamada `engram-postgres` que funciona en una red aislada).*

---

## 2. Gestión de Datos: ¿Comparten Base de Datos?

**Sí. Comparten exactamente la misma base de datos (la misma instancia y archivo).**

Según la investigación en `docs/ANALISIS_GRAFFITI_RAG.md` y `docs/ANALISIS_BASES_DATOS_IA_TENSORES.md`:
*   La versión *Community* de Neo4j (`5.12.0`) desplegada en el ecosistema **no permite crear múltiples bases de datos independientes** (feature exclusiva de la versión Enterprise). Por lo tanto, todos los contenedores escriben obligatoriamente en la única base de datos activa (por defecto, `neo4j`).

### ¿Cómo evitan colisiones?
A pesar de compartir el mismo espacio, los datos **no chocan entre sí** porque Neo4j es una base de datos de grafos *schemaless* (sin esquemas estrictos predefinidos). Cada sistema estructura su información utilizando **Etiquetas (Labels) de Nodos** completamente diferentes, creando tres subgrafos paralelos:

*   **Grafo Fenomenológico (ExtensionNeo4j):** Usa etiquetas como `(:Concepto)`, `(:DefinicionRuta)`, `(:MaximoRelacional)`.
*   **Grafo Temporal y Semántico (Graffiti / Graphiti):** Usa etiquetas como `(:Entity)`, `(:Episode)`.
*   **Grafo Jerárquico RAG (MemGraphRAG Adapter):** Usa etiquetas como `(:Chunk)`, `(:Fact)`.

Actualmente, estos tres cerebros operan de forma paralela en el mismo espacio físico de almacenamiento, pero **no están vinculados semánticamente entre sí**.

---

## 3. Alineación Arquitectónica (Documentación Oficial)

Los documentos oficiales de la nueva estructura del proyecto (`docs/README_NUEVA_ESTRUCTURA.md`, `docs/ARBOL_COMPLETO_SISTEMA.md` y `docs/ARQUITECTURA_OMEGA_21.md`) establecen claramente la visión a futuro para este ecosistema.

El objetivo central de la arquitectura se define como:
**"Convergencia: Neo4j (Grafo de Conocimiento Unificado) 🧠✨"**

La decisión arquitectónica de apuntar todos estos sistemas paralelos a una única instancia de Neo4j **no fue un accidente**, sino una preparación para el futuro. El sistema busca operar como un verdadero organismo vivo ("Omega 21"). 

### La Visión de Convergencia
La alineación ideal documentada dicta que la meta final es **fusionar estos tres subgrafos aislados**. Por ejemplo:
1.  El pipeline fenomenológico genera un nuevo `(:Concepto)`.
2.  Este concepto se envía a "Graffiti", el cual lo desglosa y lo convierte en una `(:Entity)` asociada a un `(:Episode)` temporal.
3.  El RAG jerárquico lo indexa mediante `(:Chunk)` para su recuperación rápida.
4.  Eventualmente, se crearían relaciones nativas cruzadas en Neo4j (ej. un `(:Concepto)` conectado directamente con un `(:Episode)`), consolidando un **Grafo de Conocimiento Unificado**.

---

## 4. Estado Actual en Azure y Siguientes Pasos

En el servidor de despliegue en Azure (`20.125.88.188`), el contenedor `sistema_vivo_v4` se encuentra temporalmente desconectado de `bunker-neo4j` (marcado como *unhealthy* o con fallos de red). Esto se debe a que las variables de entorno intentan apuntar estáticamente a `localhost` o no resuelven la red de Docker correctamente.

**Acciones recomendadas para habilitar la convergencia en Azure:**
1.  **Ajustar Variables de Entorno:** Modificar la configuración del contenedor `sistema_vivo_v4` para que `NEO4J_URL` y `MEMGRAPH_HOST` apunten al nombre del contenedor de la base de datos (ej. `bunker-neo4j`) o a la IP del Gateway de Docker (`172.17.0.1`), permitiendo el cruce entre subredes.
2.  **Corregir el Healthcheck:** Actualizar el comando de monitoreo de salud del contenedor para que evalúe correctamente los puertos activos del orquestador RAG (`7688`) en lugar del heredado (`8000`).