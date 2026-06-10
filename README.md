# 🧬 Sistema Vivo Hexagonal & Arquitectura RAG de Grafos

Este repositorio consolida la infraestructura, configuraciones y pipelines cognitivos del **Sistema Vivo Fenomenológico Hexagonal (v4.0)**, integrando bases de datos de grafos avanzadas, pipelines RAG híbridos y automatización de flujos de trabajo.

---

## 🏗️ Arquitectura General del Sistema

El ecosistema se distribuye en dos infraestructuras principales y modulares:

### 1. Pila de Integración y RAG de Grafos (`sincronizacion-obsidiane`)
Esta pila orquesta el procesamiento del conocimiento y el almacenamiento en grafos, comunicados con una bóveda digital en Obsidian mediante n8n:
* **Memgraph Platform:** Base de datos de grafos en memoria ultrarrápida optimizada para el algoritmo PageRank personalizado (PPR) de **MemGraphRAG**.
* **Neo4j Server:** Base de datos persistente utilizada para el almacenamiento jerárquico de **LightRAG** / **Graffiti RAG**.
* **LightRAG Server (FASTAPI):** API REST personalizada con parches de Cypher Neo4j y soporte preventivo de límites de tasa (*rate limit*) para Groq/Gemini.
* **MemGraphRAG Server:** Servidor HTTP independiente que interactúa con la base de datos Memgraph y maneja el pipeline relacional.
* **n8n Organismo:** Motor de flujos de trabajo que sincroniza las entradas y salidas fenomenológicas en la carpeta del Vault.

*Configuración asociada:* [docker-compose.rag.yml](file:///workspaces/lei-prueba/sincronizacion-obsidiane/docker-compose.rag.yml)

### 2. Pila de Producción y Núcleo Biológico (`deploy_docker`)
Una versión compacta e independiente diseñada para la validación y ejecución de scripts integrales de checkeo del sistema:
* **Organismo Vivo:** Contenedor Python central que procesa la lógica fenomenológica molecular de 9 niveles.
* **Base de Datos Neo4j (bio_database):** Persistencia aislada mapeada en puertos alternos para evitar colisiones con el entorno de desarrollo.

*Configuración asociada:* [docker-compose.yml](file:///workspaces/lei-prueba/deploy_docker/docker-compose.yml)

---

## 🛠️ Guía de Inicio Rápido

### 1. Configurar Entorno
Copia el archivo de plantilla a tu archivo de configuración de variables de entorno local:
```bash
cp .env.template .env
```
Abre el archivo `.env` recién creado y rellena tus claves de API (`GOOGLE_GEMINI_API_KEY`, `GROQ_API_KEY`).

### 2. Inicializar Pila RAG (Desarrollo y Obsidian)
Levanta los contenedores de bases de datos, APIs RAG y n8n:
```bash
docker-compose -f sincronizacion-obsidiane/docker-compose.rag.yml up -d
```
Acceso a las consolas de control:
* **Memgraph Lab UI:** [http://localhost:3000](http://localhost:3000)
* **Neo4j Web UI:** [http://localhost:7474](http://localhost:7474) (Usuario: `neo4j` / Clave: `fenomenologia2024`)
* **LightRAG REST API:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **n8n Web UI:** [http://localhost:5678](http://localhost:5678)

### 3. Inicializar Pila de Producción (Organismo)
Si deseas levantar la lógica pura del organismo aislado y correr los tests de consistencia biológica:
```bash
docker-compose -f deploy_docker/docker-compose.yml up -d
```

---

## 📂 Archivos Críticos y Referencias

* **Manual de Conexión del Clúster:** [MANUAL_CONEXION.md](file:///workspaces/lei-prueba/INFRA_BACKUP/MANUAL_CONEXION.md) (Azure, AWS y DigitalOcean).
* **Servidor Personalizado de Ingesta:** [lightrag_custom_server.py](file:///workspaces/lei-prueba/sincronizacion-obsidiane/lightrag_custom_server.py).
* **Documento Técnico de Convergencia:** [convergencia_sistema_vivo.md](file:///workspaces/lei-prueba/convergencia_sistema_vivo.md).

---

## 🔒 Seguridad y Buenas Prácticas
* **Claves SSH:** Las llaves privadas (`*.pem`, `id_ed25519`) están protegidas y excluidas de Git. Nunca las subas ni remuevas las exclusiones en [.gitignore](file:///workspaces/lei-prueba/.gitignore).
* **Límites de Tasa (Rate Limits):** La API de Groq gratuita tiene restricciones estrictas. Los servidores cuentan con un retraso preventivo de 3 segundos entre llamadas de indexación para evitar bloqueos por HTTP 429.
