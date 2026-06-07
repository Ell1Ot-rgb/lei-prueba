# Documento Técnico Integral

**Proyecto:** YO Estructural · Fenomenología Computacional v3.0  
**Fecha:** 31/10/2025  
**Responsable:** Sistema Automatizado + n8n + Neo4j  
**Alcance:** Este documento describe la arquitectura completa del sistema, componentes principales, flujos de datos, integración con Neo4j y la orquestación automatizada mediante n8n para procesamiento fenomenológico.

---

## 1. Visión General del Sistema

```
┌─────────────────┐        ┌───────────────────┐        ┌──────────────────────┐
│  Entrada Bruta  │ ─────► │  Procesamiento    │ ─────► │  Grafo Fenomenológico │
│  (textos, etc.) │        │  YO Estructural   │        │  Neo4j (YO emergente) │
└─────────────────┘        ├──────────┬────────┘        └──────────────────────┘
                            │          │
                            │          ▼
                            │    ┌──────────────┐
                            │    │    n8n       │
                            │    │  Automatiza  │
                            ▼    │  Ingesta &   │
                      ┌────────┐ │  Transform   │
                      │Python  │ │  (PowerShell)│
                      │Integr. │ └──────────────┘
                      └────────┘
```

- **Fenomenología Computacional**: procesamiento jerárquico (niveles -4 a +4) que evalúa el YO emergente según coherencia narrativa, contradicciones y tensiones.
- **Neo4j**: almacena nodos contextuales, gradientes, vohexistencias, fenómenos y versiones del YO; se sincroniza automática y orgánicamente.
- **n8n**: motor de orquestación headless ejecutado desde PowerShell, encargado de ingestión de archivos, enriquecimiento semántico y sincronización con Neo4j.
- **PowerShell**: despliegue y validación completa mediante scripts (`deploy-n8n-complete.ps1`, `install-n8n-complete.ps1`, `validate-installation.ps1`).

---

## 2. Estructura de Directorios Relevante

```
YO estructural/
├── main.py                     # API FastAPI/Neo4j para pruebas
├── database.py                 # Gestor de conexión Neo4j
├── configuracion/
│   └── config.yaml             # Archivo maestro (pipelines, Neo4j, n8n, seguridad)
├── motor_yo/
│   └── sistema_yo_emergente.py # Núcleo de lógica fenomenológica
├── integraciones/
│   └── n8n_config.py           # Clase N8nIntegrator (webhooks, API, ejecución)
├── n8n_setup/
│   ├── deploy-n8n-complete.ps1 # Orquestador (entry point)
│   ├── install-n8n-complete.ps1# Instalador detallado n8n
│   ├── validate-installation.ps1
│   ├── workflow_1_monitor_archivos.json
│   ├── workflow_2_sync_neo4j.json
│   ├── workflow_3_text_processing.json
│   ├── START_HERE.txt + docs   # Guías de instalación y operación
└── ... (procesado/, logs_sistema/, analizador_textos/, diagnósticos/)
```

---

## 3. Componentes Principales

### 3.1 Procesamiento Fenomenológico (`motor_yo/sistema_yo_emergente.py`)
- **Estados y Métricas**: `TipoYO`, `EstadoEstructural`, `EstadoAfectivo`, `MetricasCoherencia`.
- **Funciones Clave**:
  - `_analizar_coherencia_narrativa()`: continuidad temporal, consistencia temática, integración afectiva.
  - `_detectar_tensiones_estructurales()`: tensiones temporales, afectivas y de estabilidad.
  - `_actualizar_tipo_yo()`: jerarquía del YO (Proto → Sensorial → Afectivo → Reflexivo → Simbólico → Narrativo).
  - `sincronizar_con_neo4j()`: persiste estados y nodos; maneja reconexiones.
  - Callbacks y auditoría para modo diagnóstico.

### 3.2 Configuración Central (`configuracion/config.yaml`)
- Contiene parámetros para procesado de textos, umbrales, niveles fenomenológicos, rutas, seguridad y gatillos de automatización.
- Sección `n8n`: URLs, API key, workflows esperados y triggers.
- Plantilla YAML para generación automática de nodos con metadatos, relaciones y trazabilidad.

### 3.3 Integración con n8n (`integraciones/n8n_config.py`)
- `N8nIntegrator` envía datos a webhooks, consulta workflows, activa/ejecuta flujos.
- Usa variables de entorno (`N8N_WEBHOOK_URL`, `N8N_API_KEY`, etc.) generadas por el instalador.

### 3.4 Automatización n8n (`n8n_setup/`)
- Scripts PowerShell permiten instalación reproducible 100% sin interfaz gráfica.
- Workflows JSON preconfigurados (ver sección 5).
- Documentación completa orientada a operación y soporte técnico.

---

## 4. Neo4j como Sistema Nervioso

- **Esquema lógico**: nodos `PreInstancia`, `Instancia`, `Gradiente`, `Vohexistencia`, `Fenomeno`, `Contexto`, `Metacontexto`, `YO`, `Voluntad`.
- **Relaciones**: `SE_PARECE_A`, `AGRUPA`, `SURGE_DE`, `OBSERVA`, `CONTRADICE`, `ACTUA_EN` (entre otras).
- **Metadatos**: cada nodo lleva `peso_existencial`, `coherencia_narrativa`, `emociones_detectadas`, `intensidad_fenomenologica`.
- **Sincronización**: Workflow 2 de n8n canaliza la escritura en Neo4j usando consultas `MERGE` + `RELATE` con parámetros seguros.

---

## 5. Orquestación n8n · Diseño del Flujo

### 5.1 Objetivos
1. **Ingesta automática** de archivos fenomenológicos (textos Markdown, JSON, TXT).
2. **Procesamiento semántico** para enriquecer los datos (métricas, keywords, embeddings, YAML).
3. **Sincronización con Neo4j** sin intervención manual.
4. **Escalabilidad**: poder agregar nuevos pasos o fuentes con mínimo impacto.

### 5.2 Workflows Implementados

#### Workflow 1 · Monitor Archivos (`workflow_1_monitor_archivos.json`)
```
[Watch Folder] → [Read File] → [Detect Type] → [Log Neo4j]
                                            └─► [Router] → http POST a Workflow 2 o 3
```
- Vigila `LOCAL_DATA_PATH`.
- Detecta tipo (markdown, json, texto plano) y toma decisiones:
  - `.md` → enviar a procesamiento Obsidian (hook especial).
  - `.json` → sincronización directa.
  - Texto → enviar a Workflow 3 para enriquecimiento.
- Registra evento en log interno + opcional en Neo4j vía hook.

#### Workflow 2 · Sync Neo4j (`workflow_2_sync_neo4j.json`)
```
[Webhook /sync-neo4j] → [Preparar Data] → [MERGE Nodo] → [Crear Relaciones] → [Registrar CSV] → [Responder]
```
- Recibe payloads estructurados (desde Workflow 3 u otros sistemas).
- Normaliza campos, asigna etiquetas, construye queries Bolt.
- Ejecuta `MERGE` y relaciones con parámetros (evita duplicados).
- Guarda eventos en `neo4j_sync_log.csv` para auditoría.
- Responde JSON con estado (`status`, `nodes_created`, `relationships_created`).

#### Workflow 3 · Text Processing (`workflow_3_text_processing.json`)
```
[Webhook /process-text] → [Analyser] → [Keywords] → [Embeddings] → [Generar YAML]
                                                      └─► [HTTP Request → /sync-neo4j]
                                                      └─► [Save File YAML]
```
- Recibe texto y metadatos (origen, ID, contexto).
- Calcula métricas (longitud, complejidad, densidad conceptual).
- Extrae keywords con TF-IDF (simulado) y genera embeddings (mock de 32 dimensiones, reemplazable).
- Construye YAML siguiendo la plantilla de `config.yaml` y lo guarda en `YAML_OUTPUT_PATH`.
- Llama a Workflow 2 para asegurar persistencia en Neo4j.
- Devuelve respuesta con resumen del análisis y rutas generadas.

### 5.3 Funcionamiento Coordinado

1. **Entrada**: un nuevo archivo en `LOCAL_DATA_PATH` o una invocación desde Python (`N8nIntegrator.enviar_datos_webhook`).
2. **Workflow 1** detecta y enruta.
3. **Workflow 3** crea enriquecimientos (si el contenido lo requiere).
4. **Workflow 2** asegura persistencia consistente en Neo4j.
5. **Sistema YO** puede consultar Neo4j y continuar con evaluaciones (`evaluar_emergencia`, `sincronizar_con_neo4j`).

---

## 6. Despliegue y Operación

### 6.1 Instalación n8n (PowerShell)

1. Abrir PowerShell como Administrador.
2. Ejecutar:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   cd "C:\ruta\a\YO estructural"
   .\n8n_setup\deploy-n8n-complete.ps1
   ```
3. Script instala Node.js 18 LTS, n8n, genera `.env`, importa workflows y valida.
4. Verificar con `.
8n_setup\validate-installation.ps1`.

### 6.2 Variables de Entorno Generadas (`%USERPROFILE%\.n8n\.env`)
- `N8N_PORT`, `N8N_API_KEY`, `N8N_ENCRYPTION_KEY`, `N8N_WEBHOOK_URL`.
- `NEO4J_HOST`, `NEO4J_PORT`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`.
- `LOCAL_DATA_PATH`, `YAML_OUTPUT_PATH` (configurables).

### 6.3 Puesta en Marcha
- Iniciar servicio: `n8n start --env-file $env:USERPROFILE\.n8n\.env`.
- Acceder a interfaz (opcional): `http://localhost:5678`.
- Activar workflows si es necesario (`n8n activate:workflow --id ...`).
- Monitorear logs: `tail -f $env:USERPROFILE\.n8n\logs\*`.

---

## 7. Integración con Python / YO Estructural

### 7.1 Uso del Integrador (`integraciones/n8n_config.py`)

```python
from integraciones.n8n_config import N8nIntegrator

n8n = N8nIntegrator()
resultado = n8n.enviar_datos_webhook({
    "id_documento": "doc_001",
    "contenido": texto_fenomenologico,
    "fuente": "motor_yo",
    "metadatos": {...}
})
```

- Se apalanca del webhook principal (Workflow 3).
- Respuestas incluyen `success`, `status_code`, `response` con resultados de Lean n8n.

### 7.2 Ciclo Completo
1. **Sistema Python** genera/recibe texto.
2. Envía a n8n → Workflow 3 lo enriquece y lo guarda.
3. Workflow 3 llama a Workflow 2 → Neo4j se actualiza.
4. `SistemaYoEmergente.sincronizar_con_neo4j()` recupera datos actualizados.
5. Se evalúan coherencia, tensiones y emergencia del YO.

---

## 8. Métricas y Validación

- **validate-installation.ps1** verifica Node.js, n8n, `.env`, rutas, conectividad Neo4j y endpoints.
- Neo4j se puede testear con `Test-NetConnection 192.168.1.37 -Port 7687`.
- `logs_sistema/` guarda estadísticas detalladas (YAML con análisis fenomenológicos).
- `diagnosticos_sistema_*/` contiene snapshots del estado de emergencias y tensiones.

---

## 9. Recomendaciones Operativas

- Nunca versionar `.env` ni `n8n.db` (contenido sensible).
- Hacer backup frecuente de workflows (`n8n export:workflow --all`).
- Revisar documentación de `n8n_setup/` para soporte en producción (`START_HERE.txt`, `SETUP_GUIDE.md`).
- Mantener Neo4j actualizado y con monitorización (`monitoreo.dashboard_url`).
- Ajustar `LOCAL_DATA_PATH` y `YAML_OUTPUT_PATH` según despliegue.

---

## 10. Futuras Extensiones

- Integrar nodos personalizados en n8n para cálculo real de embeddings (OpenAI/HuggingFace).
- Añadir Workflow 4 para ingestión desde Google Drive via `integraciones/google_drive_connector.py`.
- Automonitorización de coherencia mediante alertas en n8n (correo/Teams/Slack).
- Integración con Supabase (vía `supabase_connector.py`) para persistencia histórica adicional.

---

## 11. Resumen Ejecutivo

- **Sistema YO Estructural**: núcleo fenomenológico + lógica de coherencia y emergencia.
- **Neo4j**: grafo vivo que refleja instancias, contextos y versiones del YO.
- **n8n**: orquesta ingestión, análisis y sincronización; desplegado 100% desde PowerShell.
- **Documentación y Scripts**: listos para instalación inmediata y operación industrial.

> *Este documento debe acompañarse de `START_HERE.txt` y `SETUP_GUIDE.md` para garantizar que usuarios y operadores comprendan el flujo completo y puedan ejecutar el sistema sin ambigüedades.*
Este mapa mental describe la arquitectura del **Sistema Fenomenológico Computacional YO Estructural**, orquestado por n8n, y adaptado a su infraestructura local de dos computadoras interconectadas, cumpliendo con la finalidad de procesar información multimodal y actualizar el grafo de conocimiento fenomenológico.

---

## MAPA MENTAL DEL SISTEMA FENOMENOLÓGICO COMPUTACIONAL

El sistema se basa en la **Orquestación n8n** para transformar datos brutos de Google Drive en conocimiento estructurado (vectores y YAML) que alimenta el **Proyecto YO Estructural** y la **Base de Datos Neo4j**.

### I. INFRAESTRUCTURA Y COMPONENTES (Despliegue Local)

| Componente | Computadora (Ubicación) | Tipo de Servicio | Finalidad en el Sistema | Citas |
| :--- | :--- | :--- | :--- | :--- |
| **Neo4j** (YO emergente) | **i5 Core (Docker/WSL)** | Base de Datos Gráfica | Almacena nodos contextuales, fenómenos, y versiones del YO. Funciona como el "Sistema Nervioso". | |
| **n8n** (Automatización) | **Dual Core (PowerShell/Local)** | Motor de Orquestación *Headless* | Ingestión de archivos, enriquecimiento semántico y sincronización con Neo4j. Se accede localmente vía `localhost`. | |
| **YO Estructural** | **Dual Core (Python)** | Analizador Fenomenológico | Núcleo de lógica Python que procesa el texto fenomenológico y genera las instancias que evolucionan. | |
| **Red Local** | Interconexión | Protocolo Bolt/HTTP | Conexión entre n8n (Dual Core) y Neo4j (i5 Core). | |

### II. FLUJO DE DATOS Y OBJETIVO (Orquestación n8n)

La finalidad principal se logra mediante un flujo de trabajo central en n8n que combina la **Ingesta Multimodal** con el **Procesamiento Fenomenológico** (utilizando la lógica descrita en `workflow_1`, `workflow_3` y `workflow_2` de la arquitectura).

#### FASE A: INGESTA Y EXTRACCIÓN MULTIMODAL

El flujo comienza al detectar archivos de origen (`Entrada Bruta`) en Google Drive.

| Paso | Nodos Clave en n8n | Detalle de la Operación | Resultado/Citas |
| :--- | :--- | :--- | :--- |
| **1. Detección y Trigger** | `Google Drive Trigger` | Escucha los cambios o nuevos archivos (imagen, audio, PDF) en la carpeta de Google Drive configurada. | Archivo binario entrante. |
| **2. Descarga y Conversión** | `Google Drive (Download File)` | Descarga el archivo. Convierte archivos nativos de Google (Docs, Sheets) a formatos procesables (TXT, CSV). | Archivo binario local (ej. PDF, JPG, MP3). |
| **3. Extracción de Contenido (OCR/LLM)** | `Switch` → `HTTP Request` / `Extract From File` / **Agente IA** | **Manejo Multimodal:** Rutas según el tipo de archivo (`doc type`). Para PDF/Imágenes, se requiere **OCR/Análisis Multimodal** (ej., Gemini API a través de `HTTP Request` o `Image analysis via direct API`). | Texto sin formato (`markdown`) del contenido extraído. |
| **4. Enrutamiento del Texto** | `Router` | El texto extraído (texto plano) se envía al **Workflow 3: Text Processing**. | Payload JSON con texto y metadatos (origen, ID, contexto). |

#### FASE B: PROCESAMIENTO FENOMENOLÓGICO Y PERSISTENCIA (Workflow 3)

Este flujo se enfoca en el **enriquecimiento semántico** y la generación de los archivos necesarios para el proyecto Python.

| Paso | Nodos Clave en n8n | Finalidad Específica | Output/Estructura |
| :--- | :--- | :--- | :--- |
| **5. Análisis Fenomenológico** | `Webhook /process-text` → `[Analyser]` | Recibe el texto extraído (desde Fase A). Genera el **texto fenomenológico** (métrica, complejidad, densidad conceptual). | Texto fenomenológico final (Output principal). |
| **6. Vectorización (Embeddings)** | `[Embeddings]` | Genera los **datos vectoriales** a partir del texto fenomenológico (mock de 32 dimensiones, reemplazable). | Vectores asociados al texto, listos para la base de datos vectorial. |
| **7. Generación de Archivos** | `[Generar YAML]` → `[Save File YAML]` | Construye los **identificadores YAML** siguiendo la plantilla de `config.yaml` y los guarda en `YAML_OUTPUT_PATH`. | Archivo `.yml` guardado en disco. |
| **8. Almacenamiento Local (Activación del YO Estructural)** | `[Save File Text]` (simulado) | **Guarda el texto fenomenológico** resultante en la carpeta `LOCAL_DATA_PATH` (entrada ruta del proyecto) para que el sistema Python (`YO estructural.py`) lo procese automáticamente. | Archivo de texto/Markdown en la carpeta de entrada del proyecto. |
| **9. Sincronización Neo4j** | `HTTP Request → /sync-neo4j` | Llama al **Workflow 2** de n8n (que utiliza el nodo `Webhook /sync-neo4j`) con la información estructurada, incluyendo vectores y metadatos. | Trigger del Workflow 2. |

#### FASE C: PERSISTENCIA EN EL GRAFO (Workflow 2 en Neo4j)

El **Workflow 2** se ejecuta y se conecta a la instancia de Neo4j en la computadora **i5 Core** a través de la red local (usando `NEO4J_HOST` y `NEO4J_PORT` definidos en las variables de entorno de n8n).

| Paso | Nodos Clave en n8n | Objetivo | Citas |
| :--- | :--- | :--- | :--- |
| **10. Escritura en Neo4j** | `[Preparar Data]` → `[MERGE Nodo]` → `[Crear Relaciones]` | Normaliza los datos, construye *queries* Cypher (Bolt) con la información fenomenológica. Ejecuta `MERGE` y `RELATE` para crear nodos (`Instancia`, `Fenomeno`, `Contexto`) y las relaciones (`SE_PARECE_A`, `CONTRADICE`). | Persistencia consistente y orgánica en el grafo. |

#### FASE D: PROCESAMIENTO DEL YO ESTRUCTURAL (Python)

El proyecto Python (`YO estructural.py`) monitorea la carpeta de entrada local y utiliza Neo4j.

| Paso | Componente | Objetivo | Citas |
| :--- | :--- | :--- | :--- |
| **11. Procesamiento Fenomenológico** | `YO Estructural.py` | Procesa el texto fenomenológico y los identificadores YAML. Analiza la **coherencia narrativa** y detecta **tensiones estructurales**. | |
| **12. Generación de Instancias** | `_actualizar_tipo_yo()` | Genera las **instancias que evolucionan** (jerarquía del YO: Proto → Sensorial → Narrativo, etc.). | |
| **13. Sincronización Final** | `sincronizar_con_neo4j()` | Persiste los estados y métricas del YO emergente en Neo4j. | |

### III. CÓDIGOS DE INTEGRACIÓN Y CONFIGURACIÓN

La instalación local de n8n y la comunicación con Neo4j requieren la configuración de **variables de entorno** y el uso de **scripts PowerShell** (en la Dual Core) y código Python para la integración.

#### A. Despliegue de n8n (Dual Core - PowerShell)

El inicio de la instancia de n8n se realiza mediante scripts de PowerShell, lo que garantiza una instalación reproducible.

```powershell
# Script de Despliegue y Puesta en Marcha
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser 
cd "C:\ruta\a\YO estructural" 
.\n8n_setup\deploy-n8n-complete.ps1 # Instalador que genera el .env

# Puesta en Marcha (usa el .env generado)
n8n start --env-file $env:USERPROFILE\.n8n\.env
```

**Variables de Entorno Cruciales** (para la comunicación entre las dos máquinas):

| Variable | Uso |
| :--- | :--- |
| `NEO4J_HOST` | IP de la computadora i5 Core (en la red local). |
| `NEO4J_PORT` | Puerto de conexión Bolt de Neo4j (típicamente 7687). |
| `LOCAL_DATA_PATH` | Carpeta local donde n8n guarda el texto fenomenológico (`entrada ruta del proyecto`). |
| `YAML_OUTPUT_PATH` | Carpeta local donde n8n guarda los identificadores `.yml`. |

#### B. Integración Python con n8n (YO Estructural Project)

El proyecto `YO Estructural.py` interactúa con n8n, posiblemente para ingresar datos o activar flujos de diagnóstico, a través de la clase `N8nIntegrator`.

```python
# integraciones/n8n_config.py
from integraciones.n8n_config import N8nIntegrator #
n8n = N8nIntegrator()

# Ejemplo de envío de datos al Webhook de procesamiento (Workflow 3)
resultado = n8n.enviar_datos_webhook({
  "id_documento": "doc_001",
  "contenido": texto_fenomenologico,
  "fuente": "motor_yo",
  "metadatos": {...}
}) #
```

#### C. Lógica de Extracción Multimodal (Recomendación n8n)

Para procesar archivos multimodales de Google Drive, n8n debe utilizar capacidades de procesamiento de imágenes y PDF, como las que ofrece Gemini AI o soluciones *self-hosted* (auto-alojadas) si la privacidad es una preocupación.

**Técnica recomendada para el flujo de n8n (dentro del Paso 3, Fase A):**

Para manejar PDF/Imágenes, se usaría un nodo `HTTP Request` para hacer llamadas directas a la API de Gemini (si la privacidad no es una restricción severa, ya que el sistema debe ser capaz de procesar "todo tipo de información").

**Flujo general para la Extracción (dentro del `Switch`):**

1.  **Carga Binaria:** El archivo descargado (binario) se codifica (usando un nodo `Code` o `Set`) si se utiliza el enfoque `inlineData` para cargas útiles pequeñas (< 20 MB).
2.  **Llamada a la API (Gemini):**
    ```json
    { 
      "contents": [{ 
        "parts": [ 
          {"inline_data": {"mime_type": "application/pdf", "data": "BASE64_DEL_ARCHIVO"}}, 
          {"text": "Extrae todo el texto, gráficos y tablas en formato fenomenológico y estructurado."}
        ]
      }]
    } 
    ```
3.  **Resultado:** El texto extraído se normaliza y se envía al siguiente paso del `Workflow 3` para generar *embeddings*.