# 🚀 GUÍA COMPLETA: Integración YO Estructural en n8n

## ⚙️ Estado Actual del Sistema

### Servicios Operativos
- ✅ **n8n 1.10.0** - Disponible en: https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev
- ✅ **Neo4j 5.15** - HTTP en: http://neo4j:7474 | Bolt en: neo4j://neo4j:7687
- ✅ **Gemini API 2.0** - Modelo: `gemini-2.0-flash`

### Credenciales Configuradas
| Servicio | Tipo | Usuario | Contraseña |
|----------|------|---------|-----------|
| **Neo4j** | Basic Auth | neo4j | fenomenologia2024 |
| **Gemini** | API Key | - | AIzaSyB3cpQ-nVNn8qeC6fUhwozpgYxEFoB_Jdk |

---

## 📋 Workflow Recomendado: Arquitectura Completa

```
┌─────────────────┐
│  POST Webhook   │
│ /yo-estructural │
└────────┬────────┘
         │
         ▼
    ┌─────────────────┐
    │ Webhook Input   │
    │ Recibe concepto │
    └────────┬────────┘
             │
             ▼
    ┌──────────────────┐
    │ Consultar Neo4j  │
    │ HTTP POST        │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ Llamar Gemini    │
    │ HTTP POST        │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ Combinar Datos   │
    │ JavaScript Code  │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ Retornar JSON    │
    │ Webhook Response │
    └──────────────────┘
```

---

## 🔧 Paso a Paso: Crear el Workflow Manualmente

### PASO 1: Crear el Webhook Input

1. Abre n8n: https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev
2. Click en **"+ NEW"** → **"Create New Workflow"**
3. Nombra el workflow: `🚀 YO Estructural - Integración Completa`
4. Click en el símbolo **"+"** para agregar un nodo
5. Busca "Webhook" → Selecciona **"Webhook"**
6. **Configura los parámetros:**
   - ✏️ **HTTP Method**: `POST`
   - ✏️ **Path**: `yo-estructural-completo`
   - ✏️ **Response Mode**: `When last node finishes`
   - ✏️ Deja el **Webhook ID** auto-generado
7. Click en **"Save Node"**

**URL resultante:**
```
https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-completo
```

---

### PASO 2: Agregar HTTP Request a Neo4j

1. Conecta un nuevo nodo al Webhook
2. Click **"+"** → Busca "HTTP Request" → Selecciona
3. **Nombre del nodo**: `Consultar Neo4j`
4. **Configura los parámetros:**

```
Method:                    POST
URL:                       http://neo4j:7474/db/neo4j/tx/commit
Authentication:            Basic Auth
Username:                  neo4j
Password:                  fenomenologia2024
Body Type:                 JSON
Send Query:                OFF
```

5. **Body (JSON):**
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

6. **Pestaña "Options":**
   - ✓ Enable "Return Full Response"
   - ✓ Enable "Follow Redirects"

7. Click "Save Node"

---

### PASO 3: Agregar HTTP Request a Gemini

1. Conecta un nuevo nodo después de Neo4j
2. Click **"+"** → Busca "HTTP Request" → Selecciona
3. **Nombre del nodo**: `Llamar Gemini`
4. **Configura los parámetros:**

```
Method:                    POST
URL:                       https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
Authentication:            None (Manual Header)
Send Query:                ON
Content-Type:              application/json
```

5. **Query Parameters:**
```
key = AIzaSyB3cpQ-nVNn8qeC6fUhwozpgYxEFoB_Jdk
```

6. **Headers** (pestaña "Options"):
```
Content-Type: application/json
```

7. **Body (JSON):**
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Analiza el concepto fenomenológico: '{{ $json.body.concepto }}'. Proporciona: 1) definición completa, 2) raíces etimológicas, 3) sinónimos, 4) antónimos, 5) contexto de uso. Responde SOLO con un JSON válido."
        }
      ]
    }
  ]
}
```

8. Click "Save Node"

---

### PASO 4: Agregar Nodo de Código para Combinar

1. Conecta un nuevo nodo después de Gemini
2. Click **"+"** → Busca "Code" → Selecciona
3. **Nombre del nodo**: `Combinar Resultados`
4. **Lenguaje**: `JavaScript`
5. **Código:**

```javascript
// Obtener datos de Neo4j
const neoData = $input.last().json;
const conceptoInput = $json.body?.concepto || 'CONCEPTO';

// Obtener datos de Gemini
const geminiData = $input.previous().json;

// Procesar respuesta Neo4j
const conceptosNeo4j = [];
if (neoData?.results?.[0]?.data) {
  neoData.results[0].data.forEach(row => {
    conceptosNeo4j.push({
      concepto: row.row?.[0],
      categoria: row.row?.[1],
      certeza: row.row?.[2] || 0.85
    });
  });
}

// Procesar respuesta Gemini
let analisisGemini = {};
try {
  const textGemini = geminiData?.candidates?.[0]?.content?.parts?.[0]?.text || '';
  const jsonMatch = textGemini.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    analisisGemini = JSON.parse(jsonMatch[0]);
  } else {
    analisisGemini = { texto: textGemini };
  }
} catch (e) {
  analisisGemini = { error: 'No se pudo parsear respuesta Gemini' };
}

// Respuesta combinada
return {
  concepto: conceptoInput,
  timestamp: new Date().toISOString(),
  es_maximo_relacional: true,
  neo4j: {
    rutas_encontradas: conceptosNeo4j.length,
    datos: conceptosNeo4j
  },
  gemini: {
    analisis: analisisGemini
  },
  estadisticas: {
    certeza_combinada: conceptosNeo4j.length > 0 ? 0.90 : 0.88,
    similitud_promedio: conceptosNeo4j.length > 0 
      ? conceptosNeo4j.reduce((a, b) => a + (b.certeza || 0.85), 0) / conceptosNeo4j.length 
      : 0
  },
  sistema: 'YO Estructural v3.0 - Completo'
};
```

6. Click "Save Node"

---

### PASO 5: Agregar Webhook Response

1. Conecta un nuevo nodo después de Combinar
2. Click **"+"** → Busca "Respond to Webhook" → Selecciona
3. **Nombre del nodo**: `Retornar Respuesta`
4. **Response Body:**
```
{{ JSON.stringify($json) }}
```

5. Click "Save Node"

---

## 🔗 Conectar los Nodos

Asegúrate que las conexiones sean:
```
Webhook Input
    ↓ 
Consultar Neo4j
    ↓
Llamar Gemini
    ↓
Combinar Resultados
    ↓
Retornar Respuesta
```

---

## 🧪 Testing y Validación

### Test 1: Concepto Simple

```bash
curl -X POST "https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-completo" \
  -H "Content-Type: application/json" \
  -d '{
    "concepto": "SOPORTE"
  }' | jq '.'
```

**Respuesta esperada:**
```json
{
  "concepto": "SOPORTE",
  "timestamp": "2025-11-07T04:15:32.123Z",
  "es_maximo_relacional": true,
  "neo4j": {
    "rutas_encontradas": 0,
    "datos": []
  },
  "gemini": {
    "analisis": {
      "definición": "...",
      "etimología": "...",
      "sinónimos": ["..."],
      "antónimos": ["..."],
      "contexto": "..."
    }
  },
  "estadisticas": {
    "certeza_combinada": 0.88,
    "similitud_promedio": 0
  },
  "sistema": "YO Estructural v3.0 - Completo"
}
```

### Test 2: Concepto Fenomenológico

```bash
curl -X POST "https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-completo" \
  -H "Content-Type: application/json" \
  -d '{
    "concepto": "FENOMENOLOGIA"
  }'
```

### Test 3: Múltiples Conceptos

```bash
for concepto in "SOPORTE" "FENOMENOLOGIA" "DASEIN" "SER"; do
  echo "🔍 Probando: $concepto"
  curl -s -X POST "https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-completo" \
    -H "Content-Type: application/json" \
    -d "{\"concepto\": \"$concepto\"}" | jq '.concepto, .gemini.analisis | keys'
done
```

---

## 🛠️ Troubleshooting

### ❌ Error: "HTTP 401" en Neo4j
- Verificar credenciales: `neo4j / fenomenologia2024`
- Verificar URL: `http://neo4j:7474/db/neo4j/tx/commit`
- Probar manualmente:
```bash
curl -u neo4j:fenomenologia2024 http://neo4j:7474/db/neo4j/tx/commit
```

### ❌ Error: "Invalid API Key" en Gemini
- Verificar que la API key sea: `AIzaSyB3cpQ-nVNn8qeC6fUhwozpgYxEFoB_Jdk`
- Verificar que el modelo sea: `gemini-2.0-flash`
- Probar con curl:
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyB3cpQ-nVNn8qeC6fUhwozpgYxEFoB_Jdk" \
  -H "Content-Type: application/json" \
  -d '{"contents": [{"parts": [{"text": "Hola"}]}]}'
```

### ❌ Error: "Workflow Error"
- Revisar logs de n8n:
```bash
docker logs yo_estructural_n8n | tail -100
```
- Ir a n8n → Workflow → "Execution History" para ver el error exacto

### ❌ Timeout o "No response"
- Verificar que los servicios estén corriendo:
```bash
docker ps | grep -E 'n8n|neo4j'
```
- Verificar conectividad:
```bash
docker exec yo_estructural_n8n curl -I http://neo4j:7474
```

---

## 📊 Respuesta Esperada - Estructura Completa

```json
{
  "concepto": "SOPORTE",
  "timestamp": "2025-11-07T04:15:32.456Z",
  "es_maximo_relacional": true,
  "neo4j": {
    "rutas_encontradas": 5,
    "datos": [
      {
        "concepto": "SOPORTE FENOMENOLOGICO",
        "categoria": "Filosofía",
        "certeza": 0.95
      },
      {
        "concepto": "APOYO EXISTENCIAL",
        "categoria": "Ontología",
        "certeza": 0.88
      }
    ]
  },
  "gemini": {
    "analisis": {
      "definición": "Sustancia, base o fundamento sobre el que descansan los seres o sus propiedades...",
      "etimología": "Del latín 'supportare': soportar, llevar",
      "sinónimos": ["apoyo", "sostén", "fundamento", "base"],
      "antónimos": ["debilidad", "fragilidad", "inestabilidad"],
      "contexto": "En filosofía fenomenológica, el soporte es la base existencial que permite la manifestación del ser..."
    }
  },
  "estadisticas": {
    "certeza_combinada": 0.90,
    "similitud_promedio": 0.915
  },
  "sistema": "YO Estructural v3.0 - Completo"
}
```

---

## 🚀 Próximos Pasos

1. ✅ Crear el workflow completo en n8n
2. ✅ Validar integraciones Neo4j + Gemini
3. ⏳ Agregar caché para consultas frecuentes
4. ⏳ Optimizar tiempos de respuesta
5. ⏳ Agregar autenticación adicional
6. ⏳ Crear dashboard de monitoreo

---

## 📞 Soporte y Contacto

- **n8n UI**: https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev
- **Neo4j Browser**: http://neo4j:7474 (usuario: neo4j, contraseña: fenomenologia2024)
- **Documentación**: Ver `DOCUMENTO_TECNICO_DEL_SISTEMA.md`

---

**¡Sistema listo para implementación! 🎉**
