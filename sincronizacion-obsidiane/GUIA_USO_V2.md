# Guía de Uso: n8n Agente Omnisciente (Versión 2)

Este flujo unifica todas las capacidades del sistema de Inteligencia Artificial (Graphiti + Neo4j) sin requerir Docker local ni integraciones MCP externas. Todo el tráfico y lógica se ejecutan de manera nativa mediante herramientas HTTP de n8n comunicándose con DigitalOcean.

## 📦 Importar el Flujo

1. Abre tu instancia local de n8n (Web UI).
2. Ve al menú superior derecho de tu lienzo y selecciona **Import from File...**
3. Selecciona el archivo `n8n_unificado_nativo_v2.json` que se encuentra en esta carpeta.
4. El lienzo revelará 4 zonas maestras.

---

## ⚙️ Las 4 Zonas de Arquitectura

### Zona 1: El Agente IA (Tu Cerebro Interactivo)
Es el core central. Conectado al modelo Groq, posee 3 herramientas activas:
- **Consultar Grafo**: Hace búsquedas sobre el índice de Neo4j Graphiti (Puerto 8000).
- **Indexar Conocimiento**: Agrega pensamientos y contexto al grafo (Puerto 8000).
- **Neo4j Cypher**: Ejecuta métricas analíticas nativas (Puerto 7474).
*Uso:* Abre el chat inferior de n8n ("Chat") e invoca al agente para consultas directas.

### Zona 2: Sincronización Automática con Obsidian
Vigila tus notas Markdown y las envía al Cerebro.
*Configuración Requerida:*
- Haz doble clic en el nodo **"Obsidian Trigger"**.
- En la propiedad `Path`, escribe la ruta absoluta de tu carpeta local de Obsidian (ejemplo: `/Users/tu_usuario/Documentos/Obsidian Vault/`).
- Enciende el Workflow (Toggle a "Active") para que empiece a escuchar archivos nuevos.

### Zona 3: Reporte Diario Automático ("Morning Briefing")
Todos los días a las 8:00 AM, el sistema extraerá las memorias del día anterior y creará un archivo nuevo.
*Configuración Requerida:*
- Haz doble clic en el nodo **"Write Daily Report"**.
- En la propiedad `File Name`, asegúrate de que la ruta apunte a tu bóveda local de Obsidian (ejemplo: `/Users/tu_usuario/Documentos/Obsidian Vault/Reportes/Reporte_Diario_{{ $now.format('yyyy-MM-dd') }}.md`).

### Zona 4: Conserje de Colisiones (Mantenimiento del Grafo)
Cada domingo a las 2:00 AM se ejecutará una limpieza. Busca entidades con nombres idénticos que se hayan duplicado y utiliza `apoc.refactor.mergeNodes` para fusionarlas automáticamente, asegurando que tu sistema neuromórfico se mantenga estable y unificado. No requiere configuración.

---

## 🔒 Credenciales y Puertos
- **DigitalOcean IP:** `159.203.164.103`
- **Puerto 8000 (LightRAG / Graphiti):** Usado para ingesta y query semántico.
- **Puerto 7474 (Neo4j REST API):** Usado para inyección pura de Cypher (Autenticación Basic pre-configurada).

*¡Disfruta tu nuevo Sistema Organismo Despierto v2!*
