# Guía de Uso: n8n Agente Omnisciente (Versión 3 - Expansión Máxima)

Esta tercera versión expande tu ecosistema nativo para hacerlo omnipresente. Ahora incluye integración móvil, ingesta automática de sitios web y más herramientas nativas en n8n conectadas a tu cerebro en DigitalOcean.

## 📦 Importar el Flujo

1. En tu instancia local de n8n, haz clic en **Import from File...**
2. Selecciona el archivo `n8n_unificado_nativo_v3.json`.
3. Activa las credenciales de Telegram si vas a usar la Zona 5.

---

## ⚙️ Las Zonas de Arquitectura

*(Las Zonas 1 a 4 permanecen activas: Chatbot n8n, Auto-Sync Obsidian, Reporte Diario 8 AM, Mantenimiento de Colisiones)*

### 📱 Zona 5: Interfaz Móvil (Telegram Bot) [¡NUEVO!]
Tu sistema ahora te acompaña en el bolsillo. He replicado el Cerebro IA (conectado a tus mismas herramientas de DigitalOcean) pero con gatillo directo a Telegram.
* **Flujo:** Envías un mensaje por Telegram -> El Agente busca en Neo4j/Graphiti -> Te responde por Telegram.
* **Configuración Requerida:**
  - Crea un bot con el [BotFather](https://t.me/botfather) en Telegram.
  - Pega el **Token** en las credenciales del nodo **Telegram Trigger**.
  - Selecciona tus mismas credenciales de Groq en el modelo.

### 🕸️ Zona 6: Ingesta Web (Auto-Scraping de URLs) [¡NUEVO!]
Tus notas en Obsidian ya no son estáticas. Si creas una nota con URLs, n8n las visitará, leerá su contenido web y lo inyectará directamente al cerebro de Graphiti.
* **Flujo:** Guardas un link en Obsidian -> n8n hace un HTTP GET a la URL -> Extrae el texto HTML puro -> Lo inyecta a `8000/refinar`.
* **Configuración Requerida:**
  - En **"Obsidian URL Monitor"**, asigna la carpeta de Obsidian donde sueles guardar enlaces (ej. `/Documentos/Obsidian/Inbox Links/`).

## 🔮 Funcionalidades Futuras Potenciales
Basado en el análisis de tu ecosistema actual, he identificado estas próximas expansiones naturales que podemos añadir:
1. **Auto-Etiquetado (Tagging) LLM:** Cuando agregas una nota a Obsidian, n8n puede pedirle al LLM que lea el contenido, derive 3 etiquetas (`#tags`) utilizando taxonomía Neo4j, y sobreescriba tu archivo local de Obsidian agregándolas al inicio.
2. **Transcripción Whisper Memos:** Un nodo que lea archivos de audio locales en tu PC y use la API nativa para convertirlos a texto y dispararlos a Graphiti, permitiéndote "hablarle" a tu bóveda local de Obsidian sin teclear.

## 🔒 Credenciales y Puertos
- **DigitalOcean IP:** `159.203.164.103`
- **Puerto 8000 (LightRAG / Graphiti):** Ingesta, query semántico y scraper destination.
- **Puerto 7474 (Neo4j REST API):** Cypher analítico y mantenimiento.
