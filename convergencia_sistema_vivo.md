# 🧠 Bitácora de Convergencia: Memoria Cognitiva y Bases de Datos (Memgraph, Neo4j, Graffiti)

Este documento centraliza el diagnóstico, las modificaciones realizadas y el estado de la integración de los sistemas de memoria del **Sistema Vivo Hexagonal v4.0** (Obsidian Sync, Memgraph RAG y Graffiti RAG) tanto en el entorno **Local** como en el **Servidor de Azure (`20.125.88.188`)**.

---

## 🗺️ Mapa de la Arquitectura de Memoria (Convergencia)

El sistema utiliza tres pilares fundamentales de memoria cognitiva para la fenomenología y el almacenamiento de hechos:

1. **Memoria Fáctica Jerárquica (Memgraph RAG)**:
   * **Base de datos**: Memgraph.
   * **Propósito**: Almacenamiento de fragmentos (Chunks) y hechos con algoritmos de grafos (PageRank, PPR).
   * **Conexión**: Protocolo Bolt (`bolt://localhost:7687` interno).
2. **Memoria Semántica y Episódica (Graffiti RAG)**:
   * **Base de datos**: Neo4j.
   * **Propósito**: Almacenamiento de entidades (`:Entity`) y episodios (`:Episode`) con parches de vectores.
   * **Conexión**: Protocolo Bolt (`bolt://neo4j:7687` en red Docker).
3. **Pipeline Fenomenológico (Sistema Vivo v4)**:
   * **Base de datos**: Neo4j.
   * **Propósito**: Almacenamiento de ontologías abstractas (`:Concepto`, `:DefinicionRuta`).

---

## 💻 1. Estado y Diagnóstico del Entorno Local

* **Memgraph RAG Server**: Se detectó una condición de carrera donde el servidor local (`memgraph_rag_server.py`) arrancaba antes de que Memgraph estuviera listo, lo que causaba un fallback a memoria local volátil.
* **Acción ejecutada**: Reiniciamos el contenedor de `memgraph_rag_server` local.
* **Resultado**: **CONECTADO Y OPERATIVO**. El servidor local ahora escribe y lee directamente desde el motor Memgraph.

---

## ☁️ 2. Diagnóstico y Modificaciones en Azure (La Bóveda)

El servidor de Azure (`20.125.88.188`) es una máquina virtual con recursos limitados (**640 MB de RAM y 1 CPU**). Se realizaron integraciones dinámicas y no destructivas (zero-downtime) para conectar la memoria sin modificar los contenedores originales.

### A. Integración de Neo4j (`bunker-neo4j`)
* **Problema**: El contenedor original de Neo4j estaba aislado en la red virtual `bridge` por defecto y no podía comunicarse con `sistema_vivo_v4`.
* **Acción ejecutada**: Conectamos dinámicamente `bunker-neo4j` a la red de la aplicación `bunker_default` y le inyectamos el alias DNS `neo4j`.
* **Resultado**: **CONECTADO**. El pipeline principal y el nuevo Graffiti pueden resolver `neo4j:7687` directamente.

### B. Despliegue de Memgraph en Azure
* **Problema**: No existía base de datos Memgraph en Azure. El puerto Bolt por defecto (`7687`) colisionaba con Neo4j en el host.
* **Solución aplicada**: 
  1. Levantamos un contenedor de Memgraph Platform (`sistema_vivo_memgraph`) en la red `bunker_default`.
  2. Mapeamos la consola web (Memgraph Lab) al puerto host `3001` y mantuvimos el puerto Bolt `7687` como interno dentro de la red Docker.
  3. Escribimos un **proxy TCP socket** en `/tmp/memgraph_proxy.py` dentro del contenedor `sistema_vivo_v4` para redirigir el tráfico de `localhost:7687` a `sistema_vivo_memgraph:7687`.
  4. Reiniciamos el proceso de `memgraph_rag_server.py` (PID 8) matándolo con `os.kill(8, SIGKILL)` y relanzándolo en caliente.
* **Resultado**: **OPERATIVO**. Las llamadas a `/health` y `/estadisticas` confirman la conectividad exitosa del RAG fáctico con Memgraph en Azure.

---

## 🎨 3. Despliegue de Graffiti / LightRAG en Azure

Para integrar Graffiti sin saturar los recursos de Azure, implementamos una estrategia de compilación local y transferencia.

### A. Compilación Local Eficiente
* Evitamos compilar la imagen en Azure ya que la instalación de PyTorch CUDA (2GB) congelaba la máquina.
* Modificamos el Dockerfile local (`Dockerfile.lightrag`) para instalar **PyTorch CPU-only** (150MB) e inyectar el servidor personalizado `lightrag_custom_server.py`.
* Compilamos localmente en el Codespace en **4.9 segundos**.

### B. Transferencia de la Imagen
* Exportamos la imagen local a un archivo comprimido de **563 MB** (`lightrag.tar.gz`).
* Transferimos exitosamente el archivo a la máquina de Azure a través de `scp`.

### C. Estado de Congelamiento por I/O (Límite de la VM)
* Al ejecutar el comando para desempaquetar la imagen (`gunzip -c lightrag.tar.gz | docker load`), la máquina de Azure sufrió un **Swap Lock** (bloqueo por uso masivo de memoria de intercambio para procesar los 2.8 GB de imagen descomprimida).
* **Estado actual**: El sistema está temporalmente lento y el servicio de SSH (`sshd`) no responde a nuevas solicitudes de banner. Se requiere un **Reinicio (Reboot)** de la máquina virtual desde el portal de Azure.

---

## 📋 Pasos para Finalizar la Integración (Post-Reinicio)

Una vez que reinicies la VM en el portal de Azure, ejecutaremos los siguientes comandos finales:

1. **Cargar la imagen de Graffiti (ya copiada en el host)**:
   ```bash
   gunzip -c /home/azureuser/lightrag.tar.gz | docker load
   ```
2. **Iniciar el contenedor de Graffiti**:
   ```bash
   docker run -d --name lightrag_server \
     --network bunker_default \
     --restart unless-stopped \
     -p 8001:8000 \
     -e LIGHTRAG_API_KEY=your_api_key_default \
     -e LIGHTRAG_PORT=8000 \
     -e NEO4J_URL=bolt://neo4j:7687 \
     -e NEO4J_USER=neo4j \
     -e NEO4J_PASSWORD=fenomenologia2024 \
     -e EMBEDDING_MODEL=paraphrase-MiniLM-L3-v2 \
     -e TOKENIZER_MODEL=gpt2 \
     sincronizacion-obsidiane-lightrag:latest
   ```
3. **Levantar el Proxy redireccionador de Graffiti**:
   Dentro de `sistema_vivo_v4`, iniciaremos un script de socket para redirigir `localhost:8000` (puerto de Graffiti) a `lightrag_server:8000`.
4. **Verificación**:
   Comprobar que el healthcheck de `sistema_vivo_v4` pasa a **Healthy** en Docker.
