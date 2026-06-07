# 🔗 Guía Completa: Integración n8n + Gemini + Generador Máximo Relacional

## 📋 Índice
1. [Resumen](#resumen)
2. [Arquitectura](#arquitectura)
3. [Configuración Inicial](#configuración-inicial)
4. [Despliegue con Docker](#despliegue-con-docker)
5. [Configurar n8n](#configurar-n8n)
6. [Configurar Gemini API](#configurar-gemini-api)
7. [Probar Integración](#probar-integración)
8. [Flujos de Trabajo](#flujos-de-trabajo)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Resumen

Esta integración conecta **tres sistemas**:

| Sistema | Función | Puerto |
|---------|---------|--------|
| **Generador de Rutas** | Genera 5 rutas fenomenológicas | API :8000 |
| **Gemini (Google)** | Analiza convergencia con IA | API externa |
| **n8n** | Orquesta workflows automáticos | :5678 |

### ¿Qué hace?

```
Usuario/Sistema → n8n webhook → API Generador → 5 Rutas Fenomenológicas
                                       ↓
                                  ¿Convergen?
                                       ↓
                              Gemini analiza convergencia
                                       ↓
                           ¿Es Máximo Relacional (99%+)?
                                       ↓
                                 Neo4j guarda
                                       ↓
                              n8n notifica resultado
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     WORKFLOW N8N                            │
│                                                             │
│  Webhook → Validar → API Generador → ¿Es Máximo?          │
│                            ↓              ↓        ↓        │
│                         Gemini        Neo4j    Respuesta    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              CONTENEDORES DOCKER                            │
│                                                             │
│  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐     │
│  │  Neo4j  │  │   API    │  │  n8n   │  │  Redis   │     │
│  │  :7687  │  │  :8000   │  │ :5678  │  │  :6379   │     │
│  └─────────┘  └──────────┘  └────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               COMPONENTES PYTHON                            │
│                                                             │
│  • GeneradorRutasFenomenologicas (procesadores/)           │
│  • GeminiEnriquecedor (procesadores/gemini_integration.py) │
│  • N8nIntegrator (integraciones/n8n_config.py)            │
│  • FastAPI (api_generador_maximo.py)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuración Inicial

### Paso 1: Configurar Variables de Entorno

Copia el archivo de ejemplo:
```bash
cd /workspaces/-...Raiz-Dasein/YO\ estructural/
cp .env.example .env
```

Edita `.env` con tus credenciales:
```bash
nano .env
```

**Variables CRÍTICAS:**
```bash
# Neo4j (ya configurado)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=fenomenologia2024

# ⭐ Gemini API (REQUERIDO)
# Obtener en: https://makersuite.google.com/app/apikey
GOOGLE_GEMINI_API_KEY=AIzaSy...TU_API_KEY_AQUI

# n8n (configuración interna)
N8N_WEBHOOK_URL=http://n8n:5678/webhook
N8N_API_KEY=  # Se genera automáticamente
N8N_BASE_URL=http://n8n:5678
```

### Paso 2: Obtener API Key de Gemini

1. **Ir a Google AI Studio:**
   - URL: https://makersuite.google.com/app/apikey
   - Iniciar sesión con tu cuenta de Google

2. **Crear API Key:**
   - Click en "Get API Key"
   - Click en "Create API Key in new project" (o usar proyecto existente)
   - Copiar la API key generada (empieza con `AIzaSy...`)

3. **Agregar al .env:**
   ```bash
   GOOGLE_GEMINI_API_KEY=AIzaSy...TU_CLAVE_REAL
   ```

⚠️ **IMPORTANTE:** 
- La API key de Gemini es GRATUITA con límites generosos
- NO compartas tu API key públicamente
- NO la subas a GitHub (ya está en `.gitignore`)

### Paso 3: Instalar Dependencias

```bash
# Instalar dependencias Python (incluye google-generativeai)
pip install -r requirements.txt

# O solo las nuevas:
pip install google-generativeai==0.3.2
pip install sentence-transformers==2.2.2
```

---

## 🐳 Despliegue con Docker

### Opción A: Despliegue Completo (Recomendado)

Levanta TODOS los servicios (Neo4j, API, n8n, Redis, etc.):

```bash
cd /workspaces/-...Raiz-Dasein/YO\ estructural/

# Construir imágenes
docker-compose build

# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

**Servicios disponibles:**
| Servicio | URL | Usuario | Contraseña |
|----------|-----|---------|------------|
| n8n | http://localhost:5678 | admin | fenomenologia2024 |
| API Generador | http://localhost:8000/docs | - | - |
| Neo4j Browser | http://localhost:7474 | neo4j | fenomenologia2024 |
| Prometheus | http://localhost:9090 | - | - |
| Grafana | http://localhost:3000 | admin | fenomenologia2024 |

### Opción B: Solo n8n + API (Mínimo)

Si solo quieres probar n8n con la API:

```bash
# Levantar solo Neo4j, API y n8n
docker-compose up -d neo4j yo_estructural_api n8n

# Verificar que estén corriendo
docker ps
```

### Verificar Estado

```bash
# Ver logs de n8n
docker logs -f yo_estructural_n8n

# Ver logs de API
docker logs -f yo_estructural_api

# Verificar salud de servicios
curl http://localhost:8000/health
```

---

## 🎛️ Configurar n8n

### Paso 1: Acceder a n8n

1. Abrir navegador: http://localhost:5678
2. Login:
   - Usuario: `admin`
   - Contraseña: `fenomenologia2024`

### Paso 2: Configurar Credenciales

#### A) Credencial Neo4j

1. Click en "Settings" (⚙️) → "Credentials"
2. Click en "Add Credential"
3. Buscar "Neo4j"
4. Configurar:
   ```
   Credential Name: Neo4j YO Estructural
   Host: neo4j
   Port: 7687
   User: neo4j
   Password: fenomenologia2024
   ```
5. Click en "Save"

#### B) Credencial Gemini

1. Click en "Add Credential"
2. Buscar "Google Gemini API"
3. Configurar:
   ```
   Credential Name: Google Gemini API
   API Key: [TU_GOOGLE_GEMINI_API_KEY]
   ```
4. Click en "Test" para verificar
5. Click en "Save"

### Paso 3: Importar Workflow

1. En n8n, click en "Workflows"
2. Click en "+ Add workflow"
3. Click en "..." (tres puntos) → "Import from File"
4. Seleccionar: 
   ```
   /workspaces/-...Raiz-Dasein/YO estructural/n8n_setup/workflows/workflow_5_generador_maximo_relacional.json
   ```
5. Click en "Import"

### Paso 4: Configurar Credenciales en Workflow

El workflow tiene 2 nodos que necesitan credenciales:

**Nodo "Neo4j: Guardar Máximo":**
- Click en el nodo
- En "Credential to connect with": Seleccionar "Neo4j YO Estructural"

**Nodo "Gemini: Analizar Convergencia":**
- Click en el nodo
- En "Credential to connect with": Seleccionar "Google Gemini API"

### Paso 5: Activar Workflow

1. Click en el switch "Inactive" → "Active" (arriba derecha)
2. El workflow ahora está escuchando en:
   ```
   http://localhost:5678/webhook/generar-maximo
   ```

---

## 🧪 Probar Integración

### Prueba 1: Verificar API

```bash
# Verificar que la API esté corriendo
curl http://localhost:8000/health

# Respuesta esperada:
{
  "status": "healthy",
  "componentes": {
    "generador": "ok",
    "gemini": "ok",
    "n8n": "ok"
  }
}
```

### Prueba 2: Generar Máximo Relacional (Directo a API)

```bash
# Llamada directa a la API
curl -X POST http://localhost:8000/api/generador/rutas \
  -H "Content-Type: application/json" \
  -d '{
    "concepto": "SOPORTE",
    "usar_neo4j": true,
    "usar_gemini": true,
    "enviar_a_n8n": false
  }'
```

**Respuesta esperada (simplificada):**
```json
{
  "concepto": "SOPORTE",
  "es_maximo_relacional": true,
  "certeza_combinada": 0.9923,
  "similitud_promedio": 0.9801,
  "rutas": [...5 rutas...],
  "gemini_analisis": {
    "convergen": true,
    "razon": "Las 5 rutas apuntan al mismo núcleo semántico...",
    "definicion_unificada": "Elemento que sostiene...",
    "confianza": 0.98
  },
  "neo4j_guardado": true,
  "tiempo_procesamiento_ms": 3456
}
```

### Prueba 3: Vía Webhook n8n

```bash
# Llamada al workflow de n8n
curl -X POST http://localhost:5678/webhook/generar-maximo \
  -H "Content-Type: application/json" \
  -d '{
    "concepto": "ESTRUCTURA"
  }'
```

**Esto activa el workflow completo:**
1. Webhook recibe "ESTRUCTURA"
2. Valida entrada
3. Llama a API del generador
4. API genera 5 rutas
5. Gemini analiza convergencia
6. Si es máximo (99%+):
   - Guarda en Neo4j
   - Conecta con conceptos similares
   - Combina resultados
7. Responde con resultado completo

### Prueba 4: Verificar en Neo4j

```bash
# Conectar a Neo4j Browser: http://localhost:7474
# Ejecutar Cypher:
MATCH (m:MAXIMO_RELACIONAL)
RETURN m.concepto, m.certeza_combinada, m.similitud_promedio
ORDER BY m.certeza_combinada DESC
```

---

## 🔄 Flujos de Trabajo

### Flujo 1: Procesamiento Batch de Conceptos

**Caso de uso:** Tienes una lista de 100 conceptos para analizar.

**Solución con n8n:**

1. Crear workflow con nodos:
   - **Code Node:** Lee archivo CSV con conceptos
   - **Split in Batches:** Procesa de 5 en 5 (no saturar API)
   - **HTTP Request:** Llama a `/api/generador/rutas` por cada concepto
   - **IF Node:** Filtra solo los que son máximo relacional
   - **Webhook Response:** Notifica cuando termina

2. Ejemplo de código en Code Node:
   ```javascript
   const conceptos = [
     "SOPORTE", "ESTRUCTURA", "FUNDAMENTO",
     "RELACION", "EXISTENCIA", "DASEIN"
   ];
   
   return conceptos.map(c => ({
     json: { concepto: c }
   }));
   ```

### Flujo 2: Monitoreo Continuo

**Caso de uso:** Quieres generar máximos relacionales cada vez que se agrega un nuevo texto.

**Solución con n8n:**

1. Workflow con nodos:
   - **Schedule Trigger:** Cada 1 hora
   - **HTTP Request:** Consulta nuevos textos en Supabase
   - **Code Node:** Extrae conceptos clave del texto
   - **HTTP Request:** Llama a generador por cada concepto
   - **Neo4j Node:** Conecta texto con máximos detectados

### Flujo 3: API Pública con Rate Limiting

**Caso de uso:** Exponer generador como API pública.

**Solución con n8n:**

1. Webhook público
2. **Rate Limit Node:** Máximo 10 requests/minuto
3. **Code Node:** Valida API key del usuario
4. **HTTP Request:** Llama a generador
5. **Response Node:** Retorna resultado

---

## 🔧 Troubleshooting

### Problema 1: "Gemini no disponible"

**Síntomas:**
```json
{
  "componentes": {
    "gemini": "no_configurado"
  }
}
```

**Soluciones:**

1. **Verificar API key:**
   ```bash
   # Ver si está configurada
   echo $GOOGLE_GEMINI_API_KEY
   
   # Si está vacío:
   export GOOGLE_GEMINI_API_KEY="AIzaSy...TU_KEY"
   ```

2. **Verificar instalación:**
   ```bash
   pip show google-generativeai
   
   # Si no está instalado:
   pip install google-generativeai==0.3.2
   ```

3. **Probar Gemini manualmente:**
   ```bash
   python /workspaces/-...Raiz-Dasein/YO\ estructural/procesadores/gemini_integration.py
   ```

### Problema 2: "n8n no puede conectar con API"

**Síntomas:**
- Workflow falla en nodo "API: Generar Rutas"
- Error: "Connection refused"

**Soluciones:**

1. **Verificar que API esté corriendo:**
   ```bash
   docker ps | grep yo_estructural_api
   curl http://localhost:8000/health
   ```

2. **Verificar red Docker:**
   ```bash
   # Ver si están en la misma red
   docker network inspect yo_estructural_network
   ```

3. **URL correcta en workflow:**
   - Dentro de Docker: `http://yo_estructural_api:8000`
   - Desde host: `http://localhost:8000`

### Problema 3: "Neo4j connection failed"

**Síntomas:**
- Error: "Unable to connect to bolt://neo4j:7687"

**Soluciones:**

1. **Verificar que Neo4j esté corriendo:**
   ```bash
   docker ps | grep neo4j
   docker logs yo_estructural_neo4j
   ```

2. **Verificar credenciales:**
   ```bash
   # Desde dentro del contenedor
   docker exec -it yo_estructural_neo4j cypher-shell -u neo4j -p fenomenologia2024
   
   # Ejecutar:
   RETURN 1;
   ```

3. **Reiniciar Neo4j:**
   ```bash
   docker-compose restart neo4j
   ```

### Problema 4: "Workflow falla en Gemini Node"

**Síntomas:**
- Error: "Invalid API key"
- Error: "Quota exceeded"

**Soluciones:**

1. **Verificar API key en credenciales n8n:**
   - Settings → Credentials → Google Gemini API
   - Click en "Test"

2. **Verificar cuota:**
   - Ir a: https://makersuite.google.com/app/apikey
   - Ver "Usage" (límite gratuito: 60 requests/minuto)

3. **Agregar retry en workflow:**
   - Click en nodo Gemini
   - Settings → "Continue on Fail": ON
   - "Retry on Fail": 3 veces

### Problema 5: "Timeout en generación de rutas"

**Síntomas:**
- Error: "Request timeout after 30000ms"

**Soluciones:**

1. **Aumentar timeout en workflow:**
   ```javascript
   // En nodo HTTP Request
   "options": {
     "timeout": 60000  // 60 segundos
   }
   ```

2. **Optimizar modelo de embeddings:**
   ```python
   # En generador_rutas_fenomenologicas.py
   # Cambiar a modelo más ligero:
   modelo_embeddings="sentence-transformers/all-MiniLM-L6-v2"  # 80MB vs 420MB
   ```

3. **Deshabilitar Gemini temporalmente:**
   ```json
   {
     "concepto": "CONCEPTO",
     "usar_gemini": false  // Más rápido
   }
   ```

---

## 📊 Monitoreo

### Ver Ejecuciones en n8n

1. En n8n: Click en "Executions"
2. Ver historial completo de ejecuciones
3. Click en una ejecución para ver:
   - Input/Output de cada nodo
   - Tiempo de ejecución
   - Errores

### Logs de Contenedores

```bash
# Logs de API
docker logs -f yo_estructural_api

# Logs de n8n
docker logs -f yo_estructural_n8n

# Logs de Neo4j
docker logs -f yo_estructural_neo4j
```

### Métricas de Gemini

Ver uso de API en:
- https://makersuite.google.com/app/apikey
- Tab "Usage"

---

## 🚀 Próximos Pasos

### 1. Agregar Más Workflows

Ejemplos para crear:

**Workflow: Expansión de Ontología**
```
Trigger: Cron cada noche
→ Obtener todos MAXIMO_RELACIONAL de Neo4j
→ Por cada concepto:
  → Buscar conceptos relacionados en textos
  → Generar máximo de conceptos relacionados
  → Conectar en Neo4j con relación DERIVA_DE
```

**Workflow: Validación Humana**
```
Webhook recibe concepto
→ Genera máximo relacional
→ Si certeza < 99.5%:
  → Envía email a revisor humano
  → Espera aprobación/rechazo
  → Actualiza Neo4j con validación
```

### 2. Integrar con Google Cloud

Habilita APIs en Google Cloud Console:

- **Cloud Storage:** Almacenar rutas generadas
- **BigQuery:** Análisis de estadísticas
- **Cloud Functions:** Triggers serverless
- **Vertex AI:** Modelos custom

### 3. Dashboard Personalizado

Crea visualización en Grafana:
- Total de máximos relacionales por día
- Certeza promedio
- Tiempo de procesamiento
- Uso de API Gemini

---

## 📚 Referencias

- **n8n Docs:** https://docs.n8n.io/
- **Gemini API:** https://ai.google.dev/docs
- **Neo4j Cypher:** https://neo4j.com/docs/cypher-manual/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Sentence Transformers:** https://www.sbert.net/

---

## 🆘 Soporte

Si tienes problemas:

1. **Revisar logs:**
   ```bash
   docker-compose logs -f
   ```

2. **Verificar servicios:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:5678/healthz
   ```

3. **Reiniciar todo:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

✅ **¡Integración completa!** Ahora tienes un sistema automatizado para detectar máximos relacionales con IA.
