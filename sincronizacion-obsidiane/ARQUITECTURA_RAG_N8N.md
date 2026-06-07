# 🧠 Organismo Vivo v4.0 — Arquitectura de Integración (Obsidian + n8n + RAG)

Este documento detalla la arquitectura de contenedores, instalación e interacción del **Sistema Vivo** basado en la convergencia de Obsidian, n8n, Memgraph y Neo4j.

## 🏗️ Arquitectura del Sistema

El sistema opera como un organismo digital con memoria de doble capa y un sistema nervioso central:

1.  **Cuerpo Físico (Vault):** Tu directorio local de Obsidian.
2.  **Sistema Nervioso (n8n):** Orquesta el flujo de información. Vigila Obsidian y distribuye los estímulos a los cerebros.
3.  **Memoria Semántica Rápida (MemgraphRAG):** Procesa hechos y relaciones inmediatas.
4.  **Memoria Estructural Profunda (LightRAG / Graphiti / Neo4j):** Extrae entidades complejas, aplica ontologías y se conecta a LLMs externos (Groq/Gemini).

---

## 🚀 Guía de Instalación y Despliegue

### Requisitos Previos
*   Docker y Docker Compose instalados.
*   Python 3.10+ (opcional, para scripts locales).
*   Cuenta gratuita en Groq y Google Gemini (las API keys ya están parcheadas en el código base actual).

### Pasos de Despliegue

1.  **Levantar la Infraestructura Completa:**
    El ecosistema se despliega con un único comando utilizando el compose file especializado:
    ```bash
    cd sincronizacion-obsidiane
    docker compose -f docker-compose.rag.yml up -d
    ```

2.  **Verificar el Estado Vital:**
    Asegúrate de que los 5 contenedores estén corriendo y saludables:
    ```bash
    docker ps
    ```
    Debes ver: `n8n_organismo`, `lightrag_server`, `memgraph_rag_server`, `sistema_vivo_memgraph`, y `neo4j_lightrag`.

---

## 🔌 Mapa de Puertos e Interfaces

El organismo expone las siguientes interfaces para tu interacción:

### 🖥️ Interfaces Visuales (UI)
*   **n8n (Automatización):** [http://localhost:5678](http://localhost:5678)
*   **Memgraph Lab (Grafo Semántico):** [http://localhost:3000](http://localhost:3000)
*   **Neo4j Browser (Grafo Estructural):** [http://localhost:7474](http://localhost:7474)

### 🧠 Endpoints REST API
*   **LightRAG (Graphiti):** `http://localhost:8000` (Endpoint principal: `/refinar`)
*   **MemgraphRAG:** `http://localhost:7688` (Endpoints: `/indexar`, `/consultar`, `/estadisticas`)

### 💾 Protocolos de Base de Datos (Bolt)
*   **Memgraph:** `bolt://localhost:7687`
*   **Neo4j:** `bolt://localhost:7690` *(Mapeado para evitar colisión local)*

---

## ⚙️ Interacción y Flujo de Trabajo (Workflow)

El sistema está diseñado para ingerir conocimiento automáticamente desde Obsidian usando **n8n**.

### Configurar n8n
1.  Abre [http://localhost:5678](http://localhost:5678) y crea tu usuario local.
2.  Navega a **Workflows** -> **Import from File**.
3.  Importa el archivo `n8n_obsidian_workflow.json` incluido en este repositorio.
4.  Activa el workflow.

### ¿Cómo funciona el Workflow?
*   n8n monitorea la carpeta `/vault/50_Entrada`.
*   Al detectar un nuevo archivo `.md`, n8n lee su contenido.
*   Realiza peticiones POST paralelas a `lightrag_server:8000/refinar` y a `memgraph_rag_server:7688/indexar`.
*   El conocimiento se divide: Memgraph crea las asociaciones rápidas y Neo4j construye la ontología profunda.

---

## 🔧 Parches de Resiliencia Aplicados

El servidor de LightRAG (`lightrag_custom_server.py`) incluye "Monkey Patches" inyectados globalmente en la clase `AsyncCompletions` de OpenAI para garantizar la supervivencia del organismo en entornos gratuitos (Free Tier):

*   **Rate Limit (Error 429):** Se implementó un algoritmo de *Backoff Exponencial* (7 reintentos, base 3s) y un retraso obligatorio entre tareas para respetar los límites de 30 RPM de Groq.
*   **JSON Validation (Error 400):** El parche inyecta automáticamente la instrucción *"Output must be in valid JSON format"* en los prompts del sistema si detecta que la petición requiere el modo `json_object` pero no incluye la palabra clave, evitando errores de validación estrictos de la API.
