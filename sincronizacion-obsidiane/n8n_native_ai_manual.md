# Manual Definitivo: IA Nativa en n8n (Sin Docker ni MCP Externos)

Dado que planeas migrar a un entorno donde no tendrás Docker, la mejor estrategia es descartar completamente los scripts externos de Python (servidores MCP) y usar la potencia **100% nativa de n8n**.

n8n tiene una función increíble llamada **"Custom n8n Tools"** (Herramientas personalizadas de n8n) para sus Agentes de Inteligencia Artificial. Esto permite que la IA ejecute nodos normales de n8n (como nodos HTTP o de bases de datos) como si fueran sus propias herramientas.

De esta forma, cuando migres tu n8n a cualquier lado (n8n Cloud, n8n Desktop, o un servidor sin Docker), todo tu sistema de inteligencia artificial seguirá funcionando intacto.

---

## 1. Arquitectura de la Solución (Todo dentro de n8n)

En lugar de tener un "Servidor MCP" separado, construiremos el razonamiento directamente en el lienzo (canvas) de n8n. Necesitas los siguientes componentes en tu flujo:

1. **AI Agent (El cerebro):** Recibe la pregunta del usuario.
2. **Call n8n Workflow Tool (Las manos de la IA):** Este nodo le dice a la IA: *"Si necesitas buscar en el grafo, ejecuta este otro flujo de n8n"*.
3. **Sub-Workflows (Las acciones):** Flujos secundarios de n8n que hacen las llamadas a LightRAG (vía HTTP) o a Memgraph (vía el nodo nativo de Neo4j).

---

## 2. Creando la Herramienta para consultar Memgraph (Cypher)

Memgraph utiliza exactamente el mismo lenguaje y protocolo que Neo4j. Por lo tanto, ¡podemos usar el nodo oficial de Neo4j dentro de n8n!

### Paso 2.1: Crear el Sub-Workflow de la Herramienta
1. Crea un **nuevo Workflow** en n8n y llámalo `Herramienta: Consultar Memgraph`.
2. Añade el nodo desencadenador **"Execute Workflow Trigger"**.
3. Añade el nodo oficial de **"Neo4j"**.
   - Configura las credenciales (Host: la IP de tu VPS `bolt://159.203.164.103:7687`, usuario y contraseña).
   - Operation: **Execute Query**.
   - Query: `= {{ $json.query }}` (Esta variable se la enviará la IA).
4. Guarda este workflow.

### Paso 2.2: Conectar la Herramienta a la IA
1. Vuelve a tu workflow principal donde tienes al **AI Agent**.
2. Conecta un nodo llamado **"Call n8n Workflow Tool"** en la entrada *Tools* del AI Agent.
3. Selecciona el sub-workflow que creamos en el paso anterior (`Herramienta: Consultar Memgraph`).
4. **¡Muy Importante!** Define la descripción de la herramienta para que la IA sepa cuándo usarla:
   - *Description:* `Ejecuta una consulta Cypher directamente en la base de datos de grafos Memgraph. Usa esta herramienta para analizar conexiones, contar nodos o ver esquemas.`
   - *Schema:* Define una variable llamada `query` de tipo `string`.

---

## 3. Creando la Herramienta para consultar LightRAG / Graphiti

Haremos exactamente lo mismo, pero usando el nodo **HTTP Request** de n8n.

### Paso 3.1: Crear el Sub-Workflow de LightRAG
1. Crea un **nuevo Workflow** en n8n y llámalo `Herramienta: Consultar LightRAG`.
2. Añade el nodo **"Execute Workflow Trigger"**.
3. Añade un nodo **"HTTP Request"**:
   - Method: `POST`
   - URL: `http://159.203.164.103:8000/query` (La IP de tu VPS).
   - Body Parameters (JSON): 
     ```json
     {
       "query": "={{ $json.pregunta_semantica }}",
       "mode": "global"
     }
     ```
4. Guarda este workflow.

### Paso 3.2: Conectar la Herramienta a la IA
1. En tu workflow principal, añade otro nodo **"Call n8n Workflow Tool"** y conéctalo al *AI Agent*.
2. Selecciona el sub-workflow `Herramienta: Consultar LightRAG`.
3. Define la descripción de la herramienta:
   - *Description:* `Busca información abstracta, notas y conceptos fenomenológicos en el sistema semántico RAG.`
   - *Schema:* Define una variable llamada `pregunta_semantica` de tipo `string`.

---

## 4. ¿Cómo funciona esto en la práctica?

1. Tú le preguntas a n8n: *"¿Qué es el Bosque Fenomenológico y cuántos nodos existen en total en la red?"*
2. El **AI Agent** razona: *"Para responder la primera parte, necesito invocar la Herramienta Consultar LightRAG. Para contar los nodos, necesito invocar la Herramienta Consultar Memgraph."*
3. La IA ejecuta **automáticamente** los dos sub-workflows nativos de n8n. Los sub-workflows hacen las peticiones a tu VPS.
4. Los sub-workflows le devuelven la información bruta a la IA.
5. La IA consolida los datos y te responde en lenguaje natural.

### Beneficio Supremo de esta Arquitectura
- **Cero dependencias externas:** No necesitas Python, ni MCP, ni Docker locales. Todo está guardado visualmente en la base de datos de n8n.
- **Portabilidad Total:** Si mañana exportas tus flujos de n8n en un archivo `.json` y los importas en n8n Desktop en Windows, **todo funcionará a la perfección**, porque los nodos HTTP y Neo4j son universales.
