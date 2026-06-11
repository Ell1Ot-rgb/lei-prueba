# Manual Rápido: Conectar IA en n8n vía MCP

Hemos implementado un Gateway MCP (`mcp_gateway`) nativo en tu infraestructura Docker. Este Gateway traduce las conexiones de tus grafos (LightRAG y Memgraph) a un lenguaje estandarizado que cualquier Inteligencia Artificial puede consumir como "herramientas".

Dado que la última versión de n8n funciona como **Cliente MCP**, ahora puedes crear *Workflows con Inteligencia Artificial autónoma* que consulten todo tu cerebro digital sin programar peticiones HTTP complejas.

---

## 1. Configurar la Conexión MCP en n8n

Para que n8n se comunique con el Gateway:

1. Abre tu instancia local de **n8n**.
2. Ve a la sección de **Configuración** (Settings) > **MCP Servers** (Servidores MCP).
   - *Nota: Si no ves esta opción, busca "MCP Server" al agregar un nodo en un Workflow, n8n pedirá crear las credenciales.*
3. Añade un nuevo Servidor MCP y configúralo de la siguiente manera:
   - **Type (Tipo):** `SSE` (Server-Sent Events)
   - **URL:** `http://mcp_gateway:8005/sse`
   - *No requiere tokens ni contraseñas adicionales porque corre en tu red privada de Docker (`RAG_network`).*

---

## 2. Crear un Workflow con IA para consultar la información

Sigue estos pasos para crear el workflow:

1. **Añade un nodo desencadenador:** Por ejemplo, un *Webhook* o *Chat Trigger* (para chatear directamente en n8n).
2. **Añade el nodo "AI Agent":**
   - Búscalo en la lista de nodos bajo la categoría de "Advanced AI".
   - Conéctalo al desencadenador.
3. **Conecta un Modelo de Lenguaje (LLM):**
   - Arrastra un nodo de modelo (ej. `Groq Chat Model`, `AWS Bedrock`, `OpenAI`, etc.) a la entrada de "Model" del AI Agent.
   - Configura las credenciales de ese modelo.
4. **Agrega la Herramienta MCP (¡La magia!):**
   - En la entrada llamada "Tools" del *AI Agent*, arrastra el nodo llamado **"MCP Tool"**.
   - Al seleccionar este nodo, verás que puedes elegir las herramientas expuestas por tu servidor:
     - `query_knowledge_graph` (Para preguntar a LightRAG / Graphiti).
     - `execute_cypher_memgraph` (Para ejecutar Cypher en Memgraph).

### ¿Cómo funciona la IA dentro de n8n ahora?
Cuando tú (o un mensaje entrante) le pregunta al AI Agent: *"¿Cuáles son las conexiones fenomenológicas más fuertes?"*, la IA automáticamente razonará lo siguiente:
1. *"No tengo ese dato en mi contexto."*
2. *"Veo que dispongo de la herramienta `query_knowledge_graph` conectada vía MCP."*
3. Formula la consulta ideal en segundo plano.
4. Obtiene el resultado del Grafo, redacta una respuesta humana coherente y te la devuelve.

---

## 3. Ejemplo Práctico de Instrucciones (Prompt) para el Agente AI

Dentro del nodo **AI Agent** en n8n, puedes configurar su *System Message* (Mensaje del Sistema) de esta forma:

> "Eres un asistente de investigación de conocimiento profundo. Tienes acceso al Cerebro Digital del usuario a través de grafos semánticos. Cuando se te pregunte cualquier cosa, utiliza SIEMPRE tus herramientas MCP (`query_knowledge_graph` o `execute_cypher_memgraph`) para extraer la información. Si usas LightRAG, el modo por defecto es 'global'. Después de obtener la información de las bases de datos, sintetiza los hallazgos en un informe fenomenológico."

---

## 4. Ventajas de esta implementación

- **Cero mantenimiento de API:** Si mañana agregamos funciones nuevas al grafo, solo se actualiza el `mcp_gateway`. Tu n8n las descubrirá automáticamente sin reescribir workflows.
- **Autonomía:** La IA decide **cómo** y **cuándo** hacer las consultas para encontrar tu información en Obsidian.
- **Consultas Multi-Salto:** Si una consulta en Memgraph devuelve resultados ambiguos, el Agente AI en n8n puede decidir por sí solo hacer una segunda consulta para aclarar la información antes de darte la respuesta final.
