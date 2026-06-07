# ⚡ Inicio Rápido: n8n + Gemini + Generador Máximo Relacional

## 🎯 ¿Qué hace esto?

Conecta **tu generador de rutas fenomenológicas** con:
- **n8n**: Automatización de workflows (webhooks, tareas programadas, etc.)
- **Gemini (Google)**: IA que analiza si las rutas convergen al 99%+
- **Neo4j**: Almacena los máximos relacionales detectados

## 🚀 Inicio en 3 Pasos

### 1. Obtén tu API Key de Gemini (GRATIS)

Ve a: https://makersuite.google.com/app/apikey

- Inicia sesión con tu cuenta Google
- Click en "Create API Key"
- Copia la key (empieza con `AIzaSy...`)

### 2. Configura el .env

```bash
cd "/workspaces/-...Raiz-Dasein/YO estructural/"
cp .env.example .env
nano .env
```

Agrega tu API key:
```bash
GOOGLE_GEMINI_API_KEY=AIzaSy...TU_KEY_AQUI
```

Guarda y cierra (Ctrl+X, Y, Enter)

### 3. Ejecuta el script

```bash
./iniciar_n8n_gemini.sh
```

El script automáticamente:
- ✅ Verifica configuración
- ✅ Instala dependencias Python
- ✅ Construye contenedores Docker
- ✅ Levanta Neo4j, n8n y API
- ✅ Verifica que todo funcione

## 🎛️ Servicios Disponibles

| Servicio | URL | Usuario | Contraseña |
|----------|-----|---------|------------|
| **n8n** | http://localhost:5678 | admin | fenomenologia2024 |
| **API Docs** | http://localhost:8000/docs | - | - |
| **Neo4j** | http://localhost:7474 | neo4j | fenomenologia2024 |

## 🔧 Configurar n8n (Una sola vez)

### Paso 1: Acceder
Abre: http://localhost:5678
Login: admin / fenomenologia2024

### Paso 2: Importar Workflow
1. Click en "Workflows"
2. "+ Add workflow"
3. "..." → "Import from File"
4. Selecciona: `n8n_setup/workflows/workflow_5_generador_maximo_relacional.json`

### Paso 3: Configurar Credenciales

**A) Neo4j:**
- Settings → Credentials → Add → Neo4j
- Host: `neo4j`
- Port: `7687`
- User: `neo4j`
- Password: `fenomenologia2024`

**B) Gemini:**
- Settings → Credentials → Add → Google Gemini API
- API Key: `[TU_GOOGLE_GEMINI_API_KEY]`

### Paso 4: Asignar Credenciales al Workflow
- Abrir workflow importado
- Nodo "Neo4j: Guardar Máximo" → Seleccionar credencial Neo4j
- Nodo "Gemini: Analizar Convergencia" → Seleccionar credencial Gemini

### Paso 5: Activar
- Switch "Inactive" → "Active" (arriba derecha)

## 🧪 Probar

### Opción A: Vía n8n Webhook

```bash
curl -X POST http://localhost:5678/webhook/generar-maximo \
  -H "Content-Type: application/json" \
  -d '{"concepto": "SOPORTE"}'
```

### Opción B: Directamente a la API

```bash
curl -X POST http://localhost:8000/api/generador/rutas \
  -H "Content-Type: application/json" \
  -d '{
    "concepto": "ESTRUCTURA",
    "usar_neo4j": true,
    "usar_gemini": true
  }'
```

### Verificar en Neo4j

1. Abre: http://localhost:7474
2. Login: neo4j / fenomenologia2024
3. Ejecuta:
   ```cypher
   MATCH (m:MAXIMO_RELACIONAL)
   RETURN m.concepto, m.certeza_combinada
   ORDER BY m.certeza_combinada DESC
   ```

## 📊 Ver Qué Está Pasando

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Solo n8n
docker logs -f yo_estructural_n8n

# Solo API
docker logs -f yo_estructural_api

# Ver estado
curl http://localhost:8000/health
```

## 🛑 Detener Todo

```bash
docker-compose down
```

## 📚 Documentación Completa

Ver: `GUIA_INTEGRACION_N8N_GEMINI.md` (80+ páginas con troubleshooting, ejemplos, etc.)

## ❓ Troubleshooting

### "Gemini no disponible"
- Verifica que agregaste `GOOGLE_GEMINI_API_KEY` en `.env`
- Ejecuta: `python procesadores/gemini_integration.py` para probar

### "n8n no conecta con API"
- Verifica que la URL en el workflow sea: `http://yo_estructural_api:8000`
- No uses `localhost` dentro de workflows n8n

### "Neo4j connection failed"
- Espera 30 segundos después de `docker-compose up`
- Verifica: `docker logs yo_estructural_neo4j`

## 🆘 Ayuda

1. Revisa logs: `docker-compose logs -f`
2. Reinicia todo: `docker-compose restart`
3. Lee documentación completa: `GUIA_INTEGRACION_N8N_GEMINI.md`

---

✅ **¡Listo!** Ahora tienes automatización completa con IA para detectar máximos relacionales.
