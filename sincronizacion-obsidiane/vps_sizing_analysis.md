# 🧠 Análisis de Dimensionamiento de VPS: Sistema Vivo Hexagonal v4.0

Este informe técnico analiza los requisitos de infraestructura necesarios para hospedar la arquitectura del **Sistema Vivo Hexagonal v4.0** (que incluye Memgraph, Neo4j, LightRAG, n8n y los servicios personalizados) en un Servidor Virtual Privado (VPS), evitando bloqueos por falta de memoria (*Swap Locks*) u *Out-Of-Memory (OOM)* como el experimentado recientemente en Azure (640MB RAM / 1 CPU).

---

## 🗺️ Inventario de Contenedores y Demanda de Recursos

El sistema se compone de varios servicios que ejecutan bases de datos especializadas y modelos de Machine Learning (Embeddings) locales. A continuación, se detalla el consumo real y proyectado de cada uno:

| Contenedor / Servicio | Rol en el Sistema | RAM Mínima | RAM Recomendada | CPU (Perfil) |
| :--- | :--- | :--- | :--- | :--- |
| **`sistema_vivo_memgraph`** | Grafo en memoria para MemGraphRAG y PPR | 1.0 GB | 2.0 - 4.0 GB | Alto (Picos en algoritmos MAGE/PageRank) |
| **`neo4j_lightrag`** (o `yo-neo4j`) | Persistencia semántica de conceptos y Graffiti | 1.5 GB | 3.0 - 4.0 GB | Medio (Consultas y estructuración) |
| **`lightrag_server`** | API REST de LightRAG (Embeddings locales y tokenizadores) | 1.0 GB | 2.0 GB | Alto (Computación de embeddings en CPU) |
| **`n8n_organismo`** | Orquestación de workflows y sincronización de Obsidian | 512 MB | 1.0 GB | Bajo - Medio (Picos en ejecuciones) |
| **`organismo_vivo_v100`** | Cerebro y procesamiento fenomenológico principal | 256 MB | 512 MB | Alto (Uso intensivo de CPU por eventos) |
| **`memgraph_rag_server`** | API REST de enlace RAG | 128 MB | 256 MB | Bajo |
| **Sistema Operativo + Docker** | Kernel Linux, Docker Daemon y monitoreo (Prometheus/Grafana) | 512 MB | 1.0 GB | Bajo |
| **TOTAL ESTIMADO** | | **~5.0 GB** | **~10.0 - 13.0 GB** | **Mínimo 2-4 vCPUs** |

---

## 📊 Escenarios de Configuración de VPS

Dependiendo del presupuesto y del nivel de uso, se sugieren tres perfiles de VPS:

### 🥉 Escenario 1: Desarrollo / Económico (Ajustado)
> [!WARNING]
> Este escenario requiere habilitar **Swap (memoria de intercambio)** y optimizar agresivamente las variables de entorno de Neo4j y Memgraph para no colapsar. No es apto para cargas concurrentes o procesamiento masivo de datos.
* **Especificaciones del VPS**:
  * **vCPU**: 2 Cores
  * **RAM**: 8 GB
  * **Almacenamiento**: 50 GB SSD
  * **Swap recomendado**: 4 GB a 8 GB en disco SSD.
* **Parámetros de Configuración**:
  * Limitar Neo4j en `.env`: `NEO4J_server_memory_heap_max__size=1G` y `NEO4J_server_memory_pagecache_size=512M`.
  * Limitar Memgraph en Docker Compose a `memory: 1.5G`.
  * LightRAG con solo `LIGHTRAG_WORKERS=1`.

### 🥈 Escenario 2: Producción Estable (Recomendado)
> [!NOTE]
> Permite correr el sistema de forma holgada. Los embeddings locales se procesan con fluidez y las consultas de grafos en Neo4j y Memgraph no sufren latencia por falta de cache.
* **Especificaciones del VPS**:
  * **vCPU**: 4 Cores (Preferiblemente optimizados para computación)
  * **RAM**: 16 GB
  * **Almacenamiento**: 80 - 100 GB SSD/NVMe
* **Parámetros de Configuración**:
  * Neo4j: `NEO4J_server_memory_heap_max__size=3G` y `NEO4J_server_memory_pagecache_size=1G`.
  * Memgraph: Asignación de hasta `3G` - `4G` de RAM.
  * LightRAG: `LIGHTRAG_WORKERS=2` (para procesamiento paralelo rápido).

### 🥇 Escenario 3: Alto Rendimiento / stress-test (Máxima Fluidez)
> [!TIP]
> Ideal si planeas procesar ráfagas constantes de miles de eventos феноmenológicos o si deseas correr modelos locales más potentes de embeddings y LLMs ligeros en la misma máquina.
* **Especificaciones del VPS**:
  * **vCPU**: 8 Cores
  * **RAM**: 32 GB
  * **Almacenamiento**: 160 GB NVMe
* **Parámetros de Configuración**:
  * Neo4j y Memgraph corriendo sin restricciones severas de memoria.
  * Permite levantar el perfil de Monitoreo (`prometheus` y `grafana`) para supervisar el rendimiento en tiempo real sin degradar las consultas.

---

## 🛠️ Recomendaciones clave para el Hospedaje en VPS

1. **Evitar Compilaciones Directas en VPS Pequeños**:
   Como se observó en Azure, compilar imágenes de Python que arrastran dependencias pesadas como PyTorch consume mucha CPU y memoria. **Se debe compilar localmente (como en el Codespace) y exportar las imágenes** mediante `docker save` y `docker load`, o bien usar un registro privado de Docker (Docker Hub o GitHub Container Registry).
2. **Configuración de Swap Obligatoria**:
   Incluso en un VPS de 8 GB o 16 GB, se recomienda configurar un archivo swap de al menos 4 GB para prevenir reinicios abruptos de contenedores si ocurre un pico de indexación masiva.
3. **Optimización de Embeddings Locales**:
   Si el VPS no cuenta con GPU (lo cual es lo habitual en VPS económicos), el parámetro de LightRAG `EMBEDDING_MODEL=paraphrase-MiniLM-L3-v2` es excelente porque solo pesa ~60MB y consume poca memoria. Evita usar modelos de embeddings más grandes (como `bge-large-en`) a menos que tengas el Escenario 3.
4. **Elección de Proveedor**:
   Proveedores como **Hetzner (especialmente sus servidores cloud dedicados)**, **DigitalOcean**, o **Linode/Akamai** suelen ofrecer una relación rendimiento/precio superior para estas cargas (por ejemplo, un VPS de 16 GB RAM / 4 vCPUs cuesta aprox. $15 - $20 USD/mes en Hetzner, mientras que en Azure o AWS puede duplicar o triplicar ese precio).

---

## 🧭 Conclusión y Decisión
Para alojar todo el stack actual de forma segura y estable, **el mínimo técnico absoluto son 8 GB de RAM (con Swap adicional) y 2 vCPUs**, pero **el punto ideal de estabilidad y rendimiento son 16 GB de RAM y 4 vCPUs**.
