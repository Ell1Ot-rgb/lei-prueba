# 📊 Análisis y Documentación de Graffiti RAG / Graphiti RAG

Este documento detalla la investigación realizada en internet y en la estructura del código sobre el componente denominado **Graffiti RAG** (o **Graphiti**), resolviendo la falta de documentación detallada en el repositorio.

---

## 1. ¿Qué es "Graphiti" en el Estado del Arte (Internet)?
En el desarrollo moderno de sistemas de Inteligencia Artificial y arquitecturas RAG, **Graphiti** (desarrollado por **Zep AI**) es un framework open-source diseñado como capa de memoria persistente y dinámica para agentes de IA.

### Características Principales:
*   **Grafo de Conocimiento Temporal:** A diferencia de RAG convencional que es estático, Graphiti añade marcas de tiempo y ventanas de validez a las entidades y sus relaciones (ej: *El usuario antes prefería X, ahora prefiere Y*).
*   **Actualizaciones Incrementales:** Inserta nuevos hechos y relaciones en tiempo real sin tener que reconstruir la totalidad del grafo de conocimiento.
*   **Mitigación de Conflictos:** Cuando hay información contradictoria, invalida la relación anterior manteniéndola en el historial temporal, en lugar de sobreescribirla.
*   **Persistencia:** Utiliza **Neo4j** como base de datos nativa de grafos.

---

## 2. El porqué de "Graffiti RAG" en este Proyecto
En la estructura de código del **Sistema Vivo Hexagonal v4.0**, existen únicamente dos menciones a este término:
1.  En `docker-compose.rag.yml`: `# ─── NEO4J (Para LightRAG/Graffiti RAG) ───`
2.  En `adapters/outbound/memgraph_rag/README.md`: `Coexiste con LightRAG/Graffiti RAG...`

### Análisis del Conflicto de Nombres:
*   **Error Tipográfico (Typo):** Es evidente que el desarrollador original quería referirse al framework **Graphiti** de Zep AI que usa Neo4j, escribiendo por error "Graffiti RAG" en los comentarios y documentación.
*   **Implementación Equivalente:** Aunque en los comentarios se menciona "Graffiti RAG", el servicio que levanta el docker-compose de RAG es **LightRAG** configurado para conectarse al contenedor de **Neo4j** (en la red local `sistema_vivo_rag_network`).
*   **Propósito:** Este motor actúa como refinador semántico de definiciones conceptuales generadas por el pipeline hexagonal. Utiliza la base de datos Neo4j para estructurar las rutas relacionales e indexar el conocimiento fenomenológico.

---

## 3. Arquitectura del Componente en el Entorno Local
El subsistema de refinamiento semántico ("Graffiti RAG") se compone de:

*   **Motor de Base de Datos (Neo4j):** Contenedor `neo4j_lightrag` ejecutando la imagen `neo4j:5.12.0`. Expone el puerto `7474` (Consola Web) y `7690` (Protocolo Bolt de conexión externa).
*   **Servidor Semántico Custom (LightRAG API):** Contenedor `lightrag_server` ejecutando nuestro servidor personalizado `lightrag_custom_server.py`. Este servidor recibe peticiones semánticas complejas en el puerto `8000` y ofrece los endpoints:
    *   `POST /refinar`: Refina definiciones conceptuales usando la API de Gemini (o algoritmos de respaldo locales).
    *   `POST /validar_convergencia`: Evalúa la coherencia y validez de las 5 rutas fenomenológicas generadas por el sistema.

---

## 4. Conclusiones y Equivalencias
Al consultar o integrar el "Graffiti RAG" del sistema, se debe interactuar con los endpoints del puerto `8000` (`http://localhost:8000`) o bien a través de la librería `ExtensionLightRAG` del adaptador outbound Neo4j. 

*   **Graphiti (Zep AI):** Concepto de Grafo Temporal en Neo4j.
*   **Graffiti RAG (Local):** Implementación híbrida de Neo4j + LightRAG customizado para refinamiento conceptual en el pipeline del YO Estructural.
