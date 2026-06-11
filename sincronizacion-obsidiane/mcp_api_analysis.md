# Análisis de Conectividad IA: Model Context Protocol (MCP) vs API Directa

Este documento analiza cómo una Inteligencia Artificial (como tu asistente actual u otras IAs con capacidades agenticas) puede conectarse e interactuar en tiempo real con tu infraestructura actual de contenedores: **LightRAG/Graphiti, Memgraph, Neo4j y n8n**.

Existen dos vías principales para que una IA interactúe con estos sistemas:
1. **Vía API Directa (Ejecución Tradicional):** La IA utiliza herramientas genéricas de consola (como `curl` o scripts de Python) para comunicarse con los puertos expuestos de los contenedores.
2. **Vía MCP (Model Context Protocol):** Un estándar emergente creado por Anthropic que permite exponer bases de datos y herramientas como "servidores estandarizados" que la IA entiende nativamente como extensiones de su propio cerebro.

A continuación, el análisis detallado para cada componente de tu arquitectura.

---

## 1. Neo4j (BBDD de Grafos Primaria)

### Vía API Directa (Bolt / HTTP)
- **Método:** La IA puede escribir y ejecutar scripts de Python utilizando la librería `neo4j` oficial, conectándose al puerto `7690` o `7687` vía protocolo `bolt://`.
- **Ventaja:** Acceso total, puede usar scripts complejos de analítica de datos.
- **Desventaja:** Requiere escribir el script y ejecutarlo en cada interacción, lo cual consume tiempo de razonamiento y tokens.

### Vía MCP (Recomendado)
- **Método:** Existe un servidor MCP oficial/comunitario para Neo4j (`neo4j-mcp`). 
- **Cómo funciona:** Levantas un contenedor ligero que se conecta a Neo4j. Este servidor MCP le expone a la IA herramientas nativas como `execute_cypher_query` o `get_graph_schema`.
- **Experiencia:** Cuando le preguntes a la IA *"¿Qué nodos están conectados al concepto X?"*, la IA no tiene que programar nada; simplemente usa su herramienta MCP nativa, lanza la query en 1 segundo y te responde.

---

## 2. Memgraph (Grafo en Memoria / C++ y RAG Ágil)

### Vía API Directa
- **Método:** Funciona idéntico a Neo4j, ya que Memgraph implementa el protocolo **Bolt** y el lenguaje **Cypher**. La IA usa `mgclient` o el driver de Neo4j para consultarlo en el puerto `7687`.

### Vía MCP
- **Método:** Dado que la interfaz de Memgraph es Cypher/Bolt, **el mismo servidor MCP de Neo4j suele funcionar para Memgraph** cambiando únicamente los datos de conexión (`MEMGRAPH_HOST`).
- **Alternativa:** Crear un servidor MCP muy sencillo en Python (usando el SDK oficial de MCP) que exponga herramientas específicas para MemgraphRAG (por ejemplo, una herramienta `search_memgraph_path` para algoritmos de grafos nativos de Memgraph como PageRank o BFS).

---

## 3. LightRAG / Graphiti (Orquestación de RAG)

### Vía API Directa (REST)
- **Método:** La IA se conecta enviando payloads JSON mediante `POST` o `GET` al puerto `8000` o `8002` (FastAPI). Por ejemplo, enviando una petición a `http://localhost:8000/query` para hacer una pregunta semántica.
- **Uso actual:** Así es como se comunican actualmente n8n y LightRAG. Es un puente sólido y estándar.

### Vía MCP (Integración de Alto Nivel)
- **Método:** Puedes programar un "LightRAG MCP Server" en Python. 
- **Cómo funciona:** En lugar de darle a la IA comandos REST, el MCP expone una herramienta llamada `query_knowledge_graph(pregunta, modo="global")`. 
- **Impacto Estratégico:** Esto convierte a tu clúster de RAG en una **extensión de la memoria de la IA**. Si la IA no sabe algo, puede decidir de manera autónoma usar esta herramienta para buscar en tus archivos de Obsidian que ya fueron ingeridos.

---

## 4. n8n (Orquestador de Workflows)

### Integración Mixta
- **Controlar a n8n vía API:** La IA puede lanzar workflows enviando peticiones a los Webhooks de n8n.
- **n8n como Cliente MCP:** n8n soporta actuar *como cliente* de MCP. Esto significa que **el propio n8n** puede usar servidores MCP para hablar con herramientas sin necesidad de programar nodos HTTP, usando nodos basados en IA que descubren los "endpoints" del protocolo MCP.

---

## 🏗️ Propuesta de Arquitectura Híbrida

Para llevar tu sistema al siguiente nivel ("Agentic RAG"), la mejor configuración es una arquitectura híbrida donde expones **Servidores MCP (SSE o STDIO)** al lado de tus contenedores:

1. Mantienes los contenedores actuales tal cual en tu `docker-compose.rag.yml`.
2. Agregas un contenedor ligero llamado `mcp_gateway`.
3. Este contenedor ejecuta scripts de MCP en Python usando `mcp[cli]`. Expone estas herramientas vía Server-Sent Events (SSE) a través de un puerto HTTP interno.
4. **Cualquier IA** (sea local o en la nube) que soporte MCP y esté conectada a tu red, al iniciar sesión, leerá el manifiesto de MCP y automáticamente adquirirá "superpoderes" para:
   - Leer/Escribir en Neo4j usando Cypher.
   - Ejecutar consultas vectoriales en LightRAG.
   - Consultar memoria a corto plazo en Memgraph.

### Resumen de Decisión
* Usa **API Directa** para la comunicación M2M (Machine to Machine), como por ejemplo que n8n hable con LightRAG o Neo4j.
* Usa **MCP** para la comunicación A2M (AI to Machine), permitiendo que la IA que asiste a tu desarrollo converse orgánicamente con tus bases de datos sin necesidad de escribir y ejecutar scripts como intermediarios.
