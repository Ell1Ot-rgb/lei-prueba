# Guía de Conexión al VPS DigitalOcean y Configuración NDS Nativo n8n

Esta guía contiene la arquitectura para un entorno de red aislado, los pasos para conectarse al servidor en la nube (VPS) y las configuraciones de red para n8n.

## 1. Conexión al VPS (DigitalOcean Droplet)

Tu "Cerebro Remoto" (LightRAG y Memgraph) está alojado en DigitalOcean.

- **IP Pública (El "ID" de conexión):** `159.203.164.103`
- **Puertos Abiertos:** `8000` (LightRAG) y `7687` (Memgraph)

### ¿Cómo ingresar por consola (SSH)?
Desde cualquier terminal en tu sistema local, ejecuta:
```bash
ssh root@159.203.164.103
```
*Acepta la huella de seguridad (yes) e introduce tu contraseña o llave SSH.*

---

## 2. Configuración de Red para Entornos Aislados

Si tu n8n está en un entorno local aislado (como un servidor privado, firewall corporativo o intranet local), estas son las **Reglas de Red de Salida (Outbound)** obligatorias:

1. **Destino `159.203.164.103`, Puerto `TCP 8000`:** Para la comunicación semántica (Insertar y Preguntar).
2. **Destino `159.203.164.103`, Puerto `TCP 7687`:** Para enviar lenguaje Cypher nativo a Memgraph.
3. **Destino `api.groq.com`, Puerto `TCP 443`:** Para el cerebro del Agente IA (LLM).

**En el VPS:** Recomendable bloquear todos los puertos en el firewall de DigitalOcean y solo permitir entrada a los puertos 8000 y 7687 desde la IP Pública de tu casa/oficina.

---

## 3. Configuración del Workflow Maestro (Sin Docker)

El archivo `n8n_arquitectura_red.json` consolida el pipeline de ingesta local y el Agente de Inteligencia Artificial que consume información remota. Todo en un solo lienzo.

### ¿Cómo importar a tu nuevo n8n nativo?
1. Abre n8n.
2. Crea un nuevo Workflow en blanco.
3. Arriba a la derecha, haz clic en **... (Options)** > **Import from File**.
4. Selecciona el archivo `n8n_arquitectura_red.json`.
5. Reconfigura tus credenciales:
   - Doble clic en el nodo **Groq Chat Model** y selecciona/agrega tu `API KEY` de Groq.
   - Ajusta las rutas del nodo **Local File Trigger** (`/ruta/local/50_Entrada`) a las rutas exactas del servidor donde corra n8n.

### Explicación de los Nodos Críticos

- **HTTP Request Tool:** Es la herramienta de Inteligencia Artificial que se conecta directamente al VPS (`http://159.203.164.103:8000/query`).
- **Agente de IA:** Mantiene la memoria conversacional y entiende cuándo debe invocar la Herramienta HTTP para investigar conceptos en LightRAG.
- **Local File Trigger:** Sigue monitoreando tu bóveda de Obsidian local para la auto-ingesta.

> *Nota sobre Memgraph:* Memgraph usa el protocolo Bolt. Para que la IA consulte Memgraph, n8n requiere que el nodo oficial "Neo4j" se empaquete en un sub-workflow y se utilice el nodo "Call n8n Workflow Tool". Por simplicidad nativa y al evitar Docker/MCP, todo el razonamiento semántico primario fluye ahora por LightRAG vía la herramienta HTTP.
