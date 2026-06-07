# 🔄 Análisis del Flujo n8n: Groq + LightRAG

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLUJO n8n LOCAL                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   Chat Trigger   ┌─────────────────┐                      │
│  │   Usuario   │ ─────────────────►│  Agente Groq    │                      │
│  │   (Chat)    │                   │  (V4 FIXED)     │                      │
│  └─────────────┘                   └────────┬────────┘                      │
│                                             │                               │
│                         ┌───────────────────┼───────────────────┐           │
│                         │                   │                   │           │
│                         ▼                   ▼                   ▼           │
│            ┌─────────────────┐  ┌───────────────┐  ┌───────────────┐       │
│            │ Modelo Groq     │  │ Memoria       │  │ Herramienta   │       │
│            │ llama-3.3-70b   │  │ Buffer Window │  │ LightRAG      │       │
│            └─────────────────┘  └───────────────┘  └───────┬───────┘       │
│                                                            │               │
│                                                POST /webhook/lightrag      │
│                                                            │               │
│  ════════════════════════════════════════════════════════════════════════  │
│                          WORKFLOW: LightRAG HTTP + SQL                      │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                            │               │
│         ┌───────────────┐      ┌───────────────┐          │               │
│         │ MCP Trigger   │      │Webhook Trigger│◄─────────┘               │
│         │ /lightrag-query│      │ /lightrag     │                          │
│         └───────┬───────┘      └───────┬───────┘                          │
│                 └──────────┬───────────┘                                   │
│                            ▼                                                │
│                 ┌───────────────────┐                                      │
│                 │  Normalize Input  │                                      │
│                 │  (Set Node)       │                                      │
│                 └────────┬──────────┘                                      │
│                          │                                                  │
│            ┌─────────────┴─────────────┐                                   │
│            ▼                           ▼                                    │
│  ┌───────────────────┐      ┌───────────────────┐                          │
│  │ Query LightRAG API│      │ Log to SQLite     │                          │
│  │ GET :9621/query   │      │ (executeCommand)  │                          │
│  └─────────┬─────────┘      └───────────────────┘                          │
│            │                                                                │
│            ▼                                                                │
│  ┌───────────────────┐                                                     │
│  │ Respond to MCP    │ ────────────────────────────► Respuesta al Agente   │
│  └───────────────────┘                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                    ╔═══════════════════════════════╗
                    ║   LightRAG API (PC2)          ║
                    ║   http://192.168.1.37:9621    ║
                    ╚═══════════════════════════════╝
```

---

## Workflows Identificados

### 1️⃣ Agente Estructural (Groq V4 - FIXED)

**Archivo**: `YO estructural/agente_groq_v4.json`

| Componente | Tipo | Configuración |
|:-----------|:-----|:--------------|
| **Chat Trigger** | chatTrigger v1.1 | Entrada de usuario |
| **Agente Estructural** | agent v1.7 | Orquestador principal |
| **Modelo Chat Groq** | lmChatGroq v1 | llama-3.3-70b-versatile, temp=0.1 |
| **Ventana de Memoria** | memoryBufferWindow v1.3 | Sesión persistente |
| **Herramienta LightRAG** | toolHttpRequest v1.1 | POST localhost:5678/webhook/lightrag |

**System Prompt**:
```
Eres un asistente inteligente encargado de ayudar a comprender y consultar 
la estructura del sistema 'Yo Estructural'.

TIENES ACCESO A UNA HERRAMIENTA MUY IMPORTANTE LLAMADA 'consultar_lightrag'.

REGLA CRÍTICA: SIEMPRE que el usuario pregunte por algo relacionado con 
definiciones, conexiones, nodos, grafos, ontología o 'qué es X', 
DEBES USAR la herramienta 'consultar_lightrag'.

IMPORTANTE: Al usar la herramienta, DEBES PROPORCIONAR EL ARGUMENTO 'query'.
NUNCA llames a la herramienta con argumentos vacíos o nulos.
```

---

### 2️⃣ LightRAG via n8n (HTTP + SQL)

**Archivo**: `YO estructural/lightrag_http_sql.json`
**ID**: `aijLVlTQoWrbgpAz`
**Estado**: `active: true`

| Nodo | Tipo | Función |
|:-----|:-----|:--------|
| **MCP Trigger** | mcpTrigger v1 | Path: /lightrag-query |
| **Webhook Trigger** | webhook v1 | POST /lightrag |
| **Normalize Input** | set v2 | Extrae y sanitiza query |
| **Query LightRAG API** | httpRequest v4.1 | GET 192.168.1.37:9621/query |
| **Log to SQLite** | executeCommand v1 | python log_query.py |
| **Respond to MCP** | respondToWebhook v1 | Retorna JSON |

**Query Cypher**:
```cypher
MATCH (n) 
WHERE n.text CONTAINS '{{ $json.query }}' 
   OR n.name CONTAINS '{{ $json.query }}' 
RETURN n LIMIT 10
```

---

## Conexiones de Red

| Origen | Destino | Puerto | Protocolo |
|:-------|:--------|:------:|:----------|
| Agente Groq | n8n Webhook | 5678 | HTTP POST |
| n8n | LightRAG API | 9621 | HTTP GET |
| n8n | SQLite | local | execCommand |

---

## Flujo de Datos Detallado

```
1. USUARIO → "¿Qué es una dendrita?"
         │
         ▼
2. CHAT TRIGGER (n8n)
   {chatInput: "¿Qué es una dendrita?"}
         │
         ▼
3. AGENTE ESTRUCTURAL
   ├── LLM: Groq llama-3.3-70b-versatile
   ├── Detecta: pregunta sobre definición
   └── Decide: usar herramienta consultar_lightrag
         │
         ▼
4. HERRAMIENTA LIGHTRAG
   POST http://localhost:5678/webhook/lightrag
   Body: {"query": "dendrita"}
         │
         ▼
5. WEBHOOK TRIGGER (/lightrag)
   Recibe query del agente
         │
         ▼
6. NORMALIZE INPUT
   safe_query = query.replace(/"/g, '\\"')
   query = body.query || json.query
         │
         ├──────────────────────────────┐
         ▼                              ▼
7a. QUERY LIGHTRAG API              7b. LOG TO SQLITE
    GET http://192.168.1.37:9621/query    python log_query.py "dendrita"
    ?cypher=MATCH (n) WHERE...
         │
         ▼
8. RESPOND TO MCP
   {nodes: [...resultados...]}
         │
         ▼
9. AGENTE ESTRUCTURAL
   Recibe respuesta de LightRAG
   Genera respuesta final al usuario
         │
         ▼
10. USUARIO ← "Una dendrita es..."
```

---

## Configuración Local Requerida

### Variables de Entorno

```env
# n8n
N8N_HOST=localhost
N8N_PORT=5678

# Groq API
GROQ_API_KEY=gsk_xxxxxxxxxxxx

# LightRAG (PC2)
LIGHTRAG_HOST=192.168.1.37
LIGHTRAG_PORT=9621
```

### Requisitos

| Servicio | URL | Estado |
|:---------|:----|:------:|
| n8n local | http://localhost:5678 | ✅ activo |
| LightRAG PC2 | http://192.168.1.37:9621 | ⚠️ verificar |
| SQLite log | scripts/log_query.py | ✅ local |

---

## Recomendaciones de Mejora

### 1. Agregar Retry en Query LightRAG

```javascript
// En nodo httpRequest
options: {
    retry: {
        times: 3,
        delay: 1000
    }
}
```

### 2. Cache de Consultas Frecuentes

```javascript
// Agregar nodo de cache antes de Query LightRAG
if (cachedResults[query]) {
    return cachedResults[query];
}
```

### 3. Integrar con S4 para Predicciones

```javascript
// Nuevo nodo después de LightRAG
// POST a S4 para enriquecer con predicciones tensoriales
{
    "url": "http://localhost:5000/s4/predict",
    "body": {
        "query": $json.query,
        "lightrag_results": $json.results
    }
}
```

---

## Prueba Rápida

```bash
# Probar webhook directamente
curl -X POST http://localhost:5678/webhook/lightrag \
  -H "Content-Type: application/json" \
  -d '{"query": "dendrita"}'

# Respuesta esperada
{
    "nodes": [
        {"name": "Dendrita", "text": "Estructura de entrada..."},
        ...
    ]
}
```

---

## Estado Actual

| Componente | Estado | Notas |
|:-----------|:------:|:------|
| Agente Groq V4 | ✅ | Workflow activo |
| LightRAG HTTP+SQL | ✅ | ID: aijLVlTQoWrbgpAz |
| Conexión PC2 | ⚠️ | Depende de red local |
| Log SQLite | ✅ | scripts/log_query.py |
