# ⚡ GUÍA RÁPIDA - Crear Workflow Completo en 5 Minutos

**Objetivo**: Integrar Neo4j + Gemini en un workflow de n8n  
**Tiempo**: 5-10 minutos  
**Dificultad**: Fácil  

---

## 🚀 INICIO RÁPIDO

### Paso 1: Abrir n8n (30 segundos)

```
URL: https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev
Usuario: admin
Contraseña: fenomenologia2024
```

Haz click en **"+ NEW"** → **"Create New Workflow"**

---

### Paso 2: Crear Webhook Input (1 minuto)

1. Click en **"+"** → Busca **"Webhook"**
2. Selecciona **"Webhook"** (el primero)
3. **Configura:**
   ```
   HTTP Method:    POST
   Path:           yo-estructural-completo
   Response Mode:  When last node finishes
   ```
4. Click "Save Node"

---

### Paso 3: Agregar Consulta Neo4j (2 minutos)

1. Conecta un **"+"** al Webhook
2. Busca **"HTTP Request"** → Selecciona
3. **Nombre**: `Consultar Neo4j`
4. **Configura:**
   ```
   Method:           POST
   URL:              http://neo4j:7474/db/neo4j/tx/commit
   Authentication:   Basic Auth
   Username:         neo4j
   Password:         fenomenologia2024
   Body Type:        JSON
   ```
5. **Body (copia exactamente):**
```json
{
  "statements": [
    {
      "statement": "MATCH (c:Concepto) WHERE c.nombre CONTAINS $concepto RETURN c.nombre as concepto, c.categoria as categoria, c.certeza as certeza LIMIT 5",
      "parameters": {
        "concepto": "{{ $json.body.concepto }}"
      }
    }
  ]
}
```
6. Click "Save Node"

---

### Paso 4: Agregar Llamada Gemini (2 minutos)

1. Conecta **"+"** al nodo Neo4j
2. Busca **"HTTP Request"** → Selecciona
3. **Nombre**: `Llamar Gemini`
4. **Configura:**
   ```
   Method:        POST
   URL:           https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
   Authentication: None
   Send Query:    ON
   ```
5. **Query Parameters (en pestaña "Options"):**
   ```
   key = AIzaSyB3cpQ-nVNn8qeC6fUhwozpgYxEFoB_Jdk
   ```
6. **Headers (agregar):**
   ```
   Content-Type: application/json
   ```
7. **Body (copia exactamente):**
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Analiza el concepto: '{{ $json.body.concepto }}'. Proporciona: 1) definición, 2) etimología, 3) sinónimos, 4) antónimos, 5) contexto. SOLO JSON."
        }
      ]
    }
  ]
}
```
8. Click "Save Node"

---

### Paso 5: Combinar Resultados (1 minuto)

1. Conecta **"+"** al nodo Gemini
2. Busca **"Code"** → Selecciona
3. **Nombre**: `Combinar Resultados`
4. **Lenguaje**: JavaScript
5. **Código (copia exactamente):**

```javascript
const concepto = $json.body?.concepto || 'CONCEPTO';
const neoResult = $json;
const geminiResult = $json;

return {
  concepto: concepto,
  timestamp: new Date().toISOString(),
  es_maximo_relacional: true,
  neo4j: {
    rutas_encontradas: neoResult.results?.[0]?.data?.length || 0,
    datos: neoResult.results?.[0]?.data || []
  },
  gemini: {
    analisis: geminiResult.candidates?.[0]?.content?.parts?.[0]?.text || ''
  },
  sistema: 'YO Estructural v3.0 - Completo'
};
```

6. Click "Save Node"

---

### Paso 6: Retornar Respuesta (30 segundos)

1. Conecta **"+"** al nodo Código
2. Busca **"Respond to Webhook"** → Selecciona
3. **Nombre**: `Retornar Respuesta`
4. **Response Body:**
   ```
   {{ JSON.stringify($json) }}
   ```
5. Click "Save Node"

---

### Paso 7: Guardar y Activar (30 segundos)

1. Click en **"Save"** (esquina arriba)
2. Click en el **toggle ON/OFF** para activar el workflow
3. ✅ ¡Listo!

---

## 🧪 PROBAR EL WORKFLOW

### Test Local

```bash
curl -X POST http://localhost:5678/webhook/yo-estructural-completo \
  -H "Content-Type: application/json" \
  -d '{"concepto": "SOPORTE"}'
```

### Test Remoto (desde cualquier lugar)

```bash
curl -X POST https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-completo \
  -H "Content-Type: application/json" \
  -d '{"concepto": "SOPORTE"}'
```

### Respuesta Esperada

```json
{
  "concepto": "SOPORTE",
  "timestamp": "2025-11-07T...",
  "es_maximo_relacional": true,
  "neo4j": {
    "rutas_encontradas": 0,
    "datos": []
  },
  "gemini": {
    "analisis": "Sustancia, base o fundamento..."
  },
  "sistema": "YO Estructural v3.0 - Completo"
}
```

---

## 🆘 TROUBLESHOOTING RÁPIDO

### Error "HTTP 401" en Neo4j
✓ Usuario: `neo4j`  
✓ Contraseña: `fenomenologia2024`  
✓ URL: `http://neo4j:7474/db/neo4j/tx/commit`

### Error "API Key inválida" en Gemini
✓ Key: `AIzaSyB3cpQ-nVNn8qeC6fUhwozpgYxEFoB_Jdk`  
✓ Modelo: `gemini-2.0-flash`

### Error "Workflow Error"
1. Click en "Execution History"
2. Revisa el error exacto
3. Si es en nodo específico, expande ese nodo

### No recibe respuesta
1. Verifica que workflow esté "ON" (toggle verde)
2. Verifica que el webhook tenga URL correcta
3. Revisa logs: `docker logs yo_estructural_n8n`

---

## 📊 RESULTADOS ESPERADOS

| Concepto | Neo4j Rutas | Gemini Respuesta |
|----------|-------------|-----------------|
| SOPORTE | 0-5 | Definición + análisis |
| DASEIN | 0-3 | Concepto fenomenológico |
| FENOMENOLOGIA | 0-10 | Análisis completo |

---

## 💡 TIPS

- ✅ Guarda el workflow frecuentemente
- ✅ Usa "Test" en cada nodo para debug
- ✅ Copia exactamente los códigos (espacios importan)
- ✅ Si falla, ve a "Execution History" para ver el error
- ✅ Neo4j tarda ~50ms, Gemini tarda ~1-3s

---

## 🎯 SIGUIENTE PASO

Una vez que funcione el workflow:

1. **Agregar más conceptos de prueba**
   ```bash
   for c in SOPORTE DASEIN FENOMENOLOGIA SER; do
     curl -X POST https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-completo \
       -H "Content-Type: application/json" \
       -d "{\"concepto\": \"$c\"}"
   done
   ```

2. **Optimizar consultas Neo4j**
3. **Agregar caché de resultados**
4. **Crear dashboard de monitoreo**

---

**¡Listo! Deberías tener el workflow completo en ~5-10 minutos ⚡**

*Si tienes dudas, revisa `GUIA_IMPLEMENTACION_COMPLETA_N8N.md` para instrucciones más detalladas.*
