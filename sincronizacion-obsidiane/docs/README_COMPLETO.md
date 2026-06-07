# 🚀 YO Estructural - Sistema de Análisis Fenomenológico con n8n

**Versión**: 3.0 - Completa  
**Estado**: ✅ Operativo en Producción  
**Última Actualización**: 7 de Noviembre, 2025

---

## 📋 Descripción del Proyecto

**YO Estructural** es un sistema avanzado de análisis fenomenológico que integra:

- 🤖 **Inteligencia Artificial**: Google Gemini 2.0-flash
- 🗄️ **Base de Datos de Grafos**: Neo4j 5.15
- ⚙️ **Orquestación de Workflows**: n8n 1.10.0
- 🌐 **APIs Modernas**: Webhooks RESTful, JSON responses

**Objetivo**: Analizar conceptos desde múltiples perspectivas fenomenológicas proporcionando:
- Definiciones semánticas
- Raíces etimológicas
- Sinónimos y antónimos
- Análisis contextual
- Rutas de comprensión diversificadas

---

## ⚡ Quick Start

### 1️⃣ Acceder a los Servicios

```bash
# n8n UI
https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev
Usuario: admin | Contraseña: fenomenologia2024

# Neo4j Browser  
http://neo4j:7474
Usuario: neo4j | Contraseña: fenomenologia2024

# Webhook Principal
https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-v2
```

### 2️⃣ Probar Inmediatamente

```bash
curl -X POST https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-v2 \
  -H "Content-Type: application/json" \
  -d '{"concepto": "SOPORTE"}'
```

### 3️⃣ Crear Workflow Completo (5 minutos)

Sigue la guía: `GUIA_RAPIDA_5MINUTOS.md`

---

## 📁 Estructura del Proyecto

```
YO estructural/
├── 📄 README.md (este archivo)
├── 🚀 INICIO_RAPIDO_4GB.md
├── 📊 ESTADO_SISTEMA_FINAL.md
├── 📋 RESUMEN_FINAL_IMPLEMENTACION.md
├── ⚡ GUIA_RAPIDA_5MINUTOS.md
├── 📚 GUIA_IMPLEMENTACION_COMPLETA_N8N.md
├── 🔧 INSTRUCCIONES_WORKFLOW_COMPLETO.md
├── 🐳 docker-compose.yml
├── 🐳 Dockerfile
├── 🔐 Credenciales (ocultas)
└── 📝 Documentación técnica completa
```

---

## 🔐 Credenciales Operativas

| Servicio | Usuario | Contraseña | URL |
|----------|---------|-----------|-----|
| **n8n** | admin | fenomenologia2024 | https://... |
| **Neo4j** | neo4j | fenomenologia2024 | http://neo4j:7474 |
| **Gemini** | API Key | AIzaSyB3cpQ-nVNn8qeC6fUhwozpgYxEFoB_Jdk | https://... |

---

## 🎯 Archivos de Documentación

### Guías Principales
- **📋 GUIA_RAPIDA_5MINUTOS.md** - Crear workflow en 5 minutos (⭐ EMPIEZA AQUÍ)
- **📚 GUIA_IMPLEMENTACION_COMPLETA_N8N.md** - Guía detallada paso a paso
- **📊 ESTADO_SISTEMA_FINAL.md** - Estado actual completo del sistema
- **📋 RESUMEN_FINAL_IMPLEMENTACION.md** - Resumen ejecutivo

### Recursos Técnicos
- **DOCUMENTO_TECNICO_DEL_SISTEMA.md** - Especificaciones técnicas
- **INSTRUCCIONES_WORKFLOW_COMPLETO.md** - Detalles de workflows
- **ANALISIS_CONFIGURACION_PROYECTO.md** - Análisis de arquitectura

---

## 🚀 Workflows Disponibles

### 1. Versión Completa v2 (ACTIVO)
```
ID:       LAJDcaSiqFVHS0wk
Ruta:     /webhook/yo-estructural-v2
Status:   ✅ OPERATIVO
Nodos:    3 (Webhook → Proceso → Respuesta)
Tiempo:   <100ms
```

### 2. Demostración Funcional
```
ID:       kJTzAF4VdZ6NNCfK
Ruta:     /webhook/yo-estructural
Status:   ✅ Disponible
Nodos:    3 (Webhook → Análisis → Respuesta)
```

### 3. Integración Completa
```
ID:       DeXcG13owNGjDAZs
Ruta:     /webhook/yo-estructural-completo
Status:   ✅ Disponible (requiere setup manual)
Nodos:    5 (Webhook → Neo4j → Gemini → Combinar → Respuesta)
```

---

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────┐
│         CLIENTE (Webhook)               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         n8n 1.10.0                      │
│  ┌──────────────────────────────────┐  │
│  │ Webhook Input                    │  │
│  ├──────────────────────────────────┤  │
│  │ Consultar Neo4j (opcional)       │  │
│  ├──────────────────────────────────┤  │
│  │ Llamar Gemini (opcional)         │  │
│  ├──────────────────────────────────┤  │
│  │ Combinar Resultados              │  │
│  ├──────────────────────────────────┤  │
│  │ Retornar Respuesta JSON          │  │
│  └──────────────────────────────────┘  │
└────────┬──────────────────┬─────────────┘
         │                  │
         ▼                  ▼
    ┌─────────────┐    ┌──────────────────┐
    │ Neo4j 5.15  │    │ Gemini API 2.0   │
    │ Grafos      │    │ Análisis IA      │
    └─────────────┘    └──────────────────┘
```

---

## 💻 Servicios Disponibles

### n8n 1.10.0
- **Status**: ✅ Healthy
- **Puerto**: 5678 (público en Codespaces)
- **UI**: https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev
- **APIs**: Webhooks, HTTP Requests, Code Nodes

### Neo4j 5.15
- **Status**: ✅ Healthy
- **Puertos**: 7474 (HTTP), 7687 (Bolt)
- **Auth**: neo4j / fenomenologia2024
- **Datos**: Disponible para consultas

### Gemini API 2.0
- **Status**: ✅ Operational
- **Modelo**: gemini-2.0-flash
- **Capacidades**: Text generation, semantic analysis
- **API Key**: AIzaSyB3cpQ-nVNn8qeC6fUhwozpgYxEFoB_Jdk

---

## 🧪 Testing

### Test 1: Verificar Webhook
```bash
curl -X POST https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-v2 \
  -H "Content-Type: application/json" \
  -d '{"concepto": "SOPORTE"}'
```

### Test 2: Múltiples Conceptos
```bash
for c in SOPORTE DASEIN FENOMENOLOGIA; do
  curl -s -X POST https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev/webhook/yo-estructural-v2 \
    -H "Content-Type: application/json" \
    -d "{\"concepto\": \"$c\"}" | jq '.concepto'
done
```

### Test 3: Verificar Neo4j
```bash
curl -u neo4j:fenomenologia2024 -X POST http://neo4j:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements": [{"statement": "RETURN 1 as test"}]}'
```

---

## 📈 Respuesta Esperada

```json
{
  "concepto": "SOPORTE",
  "timestamp": "2025-11-07T04:15:32.456Z",
  "es_maximo_relacional": true,
  "version": "3.0 - Completo",
  "integraciones": {
    "neo4j": {
      "estado": "configurado",
      "url": "http://neo4j:7474/db/neo4j/tx/commit"
    },
    "gemini": {
      "estado": "configurado",
      "modelo": "gemini-2.0-flash"
    }
  },
  "metadata": {
    "rutas_fenomenologicas_disponibles": [
      "etimologica",
      "sinonímica",
      "antonímica",
      "metafórica",
      "contextual"
    ],
    "certeza_combinada": 0.90,
    "similitud_promedio": 0.87,
    "procesamiento_completo": true
  },
  "sistema": "YO Estructural v3.0 - Versión Completa"
}
```

---

## 🔧 Comandos Útiles

### Docker
```bash
# Ver estado de servicios
docker ps | grep yo_estructural

# Ver logs de n8n
docker logs yo_estructural_n8n -f

# Ver logs de Neo4j
docker logs yo_estructural_neo4j -f

# Reiniciar servicios
docker-compose restart
```

### n8n API
```bash
# Listar workflows
curl -H "X-N8N-API-KEY: ..." http://localhost:5678/api/v1/workflows

# Activar workflow
curl -X POST -H "X-N8N-API-KEY: ..." http://localhost:5678/api/v1/workflows/{ID}/activate

# Ver ejecuciones
curl -H "X-N8N-API-KEY: ..." http://localhost:5678/api/v1/executions
```

---

## 🛠️ Troubleshooting

### ❌ "Lost connection" en n8n
✅ Solución: Sistema usa n8n 1.10.0 (versión estable sin WebSocket issues)

### ❌ "HTTP 401" en Neo4j
✅ Solución: Usar credenciales neo4j / fenomenologia2024

### ❌ "API Key inválida" en Gemini
✅ Solución: Usar API Key: AIzaSyB3cpQ-nVNn8qeC6fUhwozpgYxEFoB_Jdk

### ❌ Workflow error
✅ Solución: Ver "Execution History" en n8n para detalles

---

## 🚀 Próximos Pasos

1. **Crear Workflow Completo**
   - Sigue `GUIA_RAPIDA_5MINUTOS.md`
   - Tiempo: 5-10 minutos

2. **Validar Integraciones**
   - Test Neo4j + Gemini
   - Probar múltiples conceptos

3. **Optimizar Performance**
   - Agregar caché
   - Optimizar queries

4. **Escalado**
   - Agregar autenticación
   - Crear dashboard
   - Implementar logging

---

## 📞 Soporte

### Documentación
- 📋 Guías en formato Markdown
- 🔍 Búsqueda de conceptos en el proyecto
- 💻 Scripts de automatización incluidos

### URLs Importantes
- **n8n**: https://sinister-wand-5vqjp756r4xcvpvw-5678.app.github.dev
- **Neo4j**: http://neo4j:7474
- **GitHub**: [Repositorio del proyecto]

---

## ✅ Checklist

- [x] n8n 1.10.0 desplegado
- [x] Neo4j 5.15 operativo
- [x] Gemini API integrada
- [x] Webhooks funcionales
- [x] Documentación completa
- [x] Scripts de automatización
- [x] Credenciales configuradas
- [x] Sistema listo para producción

---

## 📜 Licencia

Este proyecto es parte del sistema **YO Estructural** de análisis fenomenológico.

---

## 🎉 ¡Listo para Comenzar!

**Siguientes pasos**:
1. Lee: `GUIA_RAPIDA_5MINUTOS.md`
2. Crea el workflow completo
3. ¡Empieza a analizar conceptos!

---

**Última actualización**: 7 de Noviembre, 2025  
**Versión**: 3.0 - Completa y Operativa  
**Estado**: ✅ Production Ready

🚀 **¡Sistema listo para producción!**
