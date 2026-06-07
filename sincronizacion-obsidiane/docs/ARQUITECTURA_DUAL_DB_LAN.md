# Arquitectura Dual Database + LAN - Sistema YO Estructural v3.0

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA COMPLETA                         │
└─────────────────────────────────────────────────────────────────┘

PC PRINCIPAL (Dual Core - Este equipo)
├── 📁 Carpeta "datos_brutos/" ← UI sube archivos aquí
├── 🌐 UI Web (puerto 3000) ← Usuario hace
├── 🔄 n8n (puerto 5678) ← Monitorea datos_brutos/
├── 🐍 Python Backend (puerto 8000)
├── 💾 SQLite/PostgreSQL Local ← Metadata + logs
└── ☁️ Supabase ← Vectores + backup

          │
          │ LAN Ethernet (sin internet)
          │ 192.168.1.x
          ▼

PC REMOTA (i5 Core - Router LAN)
├── 🕸️ Neo4j (puerto 7687) ← IP: 192.168.1.50
├── 🧠 LightRAG ← Integrado con Neo4j
└── 📊 Graph Data Science (GDS)
```

---

## 📊 Estrategia Dual Database

### Distribución de Datos

| Tipo de Dato | Supabase | SQLite Local | Neo4j (LAN) |
|--------------|----------|--------------|-------------|
| **Vectores embeddings** | ✅ Principal | ❌ | ✅ Backup |
| **Metadata archivos** | ✅ | ✅ Principal | ❌ |
| **Logs procesamiento** | ❌ | ✅ Principal | ❌ |
| **Instancias fenomenológicas** | ❌ | ✅ | ✅ Principal |
| **Grafo relacional** | ❌ | ❌ | ✅ Principal |
| **Vohexistencias** | ❌ | ✅ | ✅ Principal |
| **Eventos (Ereignis)** | ❌ | ✅ | ✅ Principal |
| **Augenblicks** | ❌ | ✅ | ✅ Principal |

**Razón de la distribución**:
- **Supabase**: Vectores (búsqueda rápida, escalable, backup cloud)
- **SQLite Local**: Metadata rápida, logs, sin dependencia de red
- **Neo4j LAN**: Grafo fenomenológico completo, GraphRAG

---

## 🗂️ Estructura de Carpetas

```
YO estructural/
├── datos_brutos/              # ← UI SUBE AQUÍ
│   ├── texto/
│   ├── imagenes/
│   ├── audio/
│   ├── video/
│   ├── documentos/
│   └── otros/
│
├── datos_procesados/          # Output de n8n
│   ├── ereignis/
│   ├── augenblick/
│   ├── instancias/
│   └── embeddings/
│
├── base_datos_local/
│   └── yo_estructural.db      # SQLite
│
└── logs_sistema/
    ├── procesamiento/
    ├── n8n/
    └── errores/
```

---

## ⚙️ Configuración Actualizada

### 1. Variables de Entorno (.env)

```env
# ============================================================
# PC PRINCIPAL (Dual Core)
# ============================================================

# Rutas locales
DATOS_BRUTOS_PATH=C:\Users\Public\#...Raíz Dasein\REFERENCIA\YO estructural\datos_brutos
DATOS_PROCESADOS_PATH=C:\Users\Public\#...Raíz Dasein\REFERENCIA\YO estructural\datos_procesados

# Base de datos local
LOCAL_DB_TYPE=sqlite  # sqlite | postgresql
SQLITE_PATH=C:\Users\Public\#...Raíz Dasein\REFERENCIA\YO estructural\base_datos_local\yo_estructural.db

# PostgreSQL local (alternativa a SQLite)
# LOCAL_POSTGRES_HOST=localhost
# LOCAL_POSTGRES_PORT=5432
# LOCAL_POSTGRES_DB=yo_estructural
# LOCAL_POSTGRES_USER=postgres
# LOCAL_POSTGRES_PASSWORD=

# Supabase (vectores + backup)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_TABLE_EMBEDDINGS=yo_embeddings
SUPABASE_TABLE_METADATA=yo_metadata

# Python Backend
PYTHON_BACKEND_URL=http://localhost:8000

# n8n
N8N_PORT=5678
N8N_WEBHOOK_URL=http://localhost:5678

# ============================================================
# PC REMOTA (i5 Core - LAN)
# ============================================================

# Neo4j (conexión LAN)
NEO4J_URI=bolt://192.168.1.50:7687
NEO4J_HTTP=http://192.168.1.50:7474
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# LightRAG (conexión LAN)
LIGHTRAG_HOST=192.168.1.50
LIGHTRAG_PORT=9000  # Puerto donde corre LightRAG
LIGHTRAG_API_URL=http://192.168.1.50:9000

# ============================================================
# APIs Externas (si hay internet ocasional)
# ============================================================
GOOGLE_GEMINI_API_KEY=
OPENAI_API_KEY=
OPENROUTER_API_KEY=
```

---

## 🗄️ Schema SQLite Local

```sql
-- base_datos_local/schema.sql

-- ============================================================
-- TABLA: archivos_brutos
-- ============================================================
CREATE TABLE IF NOT EXISTS archivos_brutos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_archivo TEXT NOT NULL,
    ruta_completa TEXT NOT NULL,
    tipo_archivo TEXT NOT NULL,  -- texto, imagen, audio, video, documento
    mime_type TEXT,
    tamaño_bytes INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP,
    hash_sha256 TEXT UNIQUE,  -- Para detectar duplicados
    estado_proceso TEXT DEFAULT 'pendiente',  -- pendiente, procesando, completado, error
    n8n_execution_id TEXT,
    metadata_json TEXT  -- JSON con metadata extra
);

CREATE INDEX idx_archivos_estado ON archivos_brutos(estado_proceso);
CREATE INDEX idx_archivos_tipo ON archivos_brutos(tipo_archivo);
CREATE INDEX idx_archivos_hash ON archivos_brutos(hash_sha256);

-- ============================================================
-- TABLA: ereignis_local
-- ============================================================
CREATE TABLE IF NOT EXISTS ereignis_local (
    id TEXT PRIMARY KEY,
    archivo_id INTEGER REFERENCES archivos_brutos(id),
    timestamp_extraccion TIMESTAMP,
    texto_original TEXT,
    phenomenal_resolution REAL,
    contamination_strength REAL,
    qualia_type TEXT,
    rem_id TEXT,
    neo4j_synced BOOLEAN DEFAULT 0,
    supabase_synced BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ereignis_archivo ON ereignis_local(archivo_id);

-- ============================================================
-- TABLA: augenblick_local
-- ============================================================
CREATE TABLE IF NOT EXISTS augenblick_local (
    id TEXT PRIMARY KEY,
    ereignis_id TEXT REFERENCES ereignis_local(id),
    estado_fenomenologico TEXT,
    coherencia_interna REAL,
    complejidad_semantica REAL,
    intencionalidad TEXT,
    ego_involvement REAL,
    neo4j_synced BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: instancias_local
-- ============================================================
CREATE TABLE IF NOT EXISTS instancias_local (
    id TEXT PRIMARY KEY,
    augenblick_id TEXT REFERENCES augenblick_local(id),
    tipo_yo TEXT,
    coherencia_narrativa REAL,
    densidad_conceptual REAL,
    neo4j_node_id INTEGER,  -- ID del nodo en Neo4j
    neo4j_synced BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: embeddings_metadata (referencia a Supabase)
-- ============================================================
CREATE TABLE IF NOT EXISTS embeddings_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instancia_id TEXT REFERENCES instancias_local(id),
    supabase_vector_id TEXT,  -- ID en Supabase
    embedding_model TEXT,
    embedding_dimension INTEGER,
    supabase_synced BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: logs_procesamiento
-- ============================================================
CREATE TABLE IF NOT EXISTS logs_procesamiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nivel TEXT,  -- INFO, WARNING, ERROR, DEBUG
    componente TEXT,  -- n8n, python, neo4j, supabase
    mensaje TEXT,
    archivo_id INTEGER REFERENCES archivos_brutos(id),
    stack_trace TEXT,
    metadata_json TEXT
);

CREATE INDEX idx_logs_timestamp ON logs_procesamiento(timestamp);
CREATE INDEX idx_logs_nivel ON logs_procesamiento(nivel);

-- ============================================================
-- TABLA: sync_status (estado de sincronización)
-- ============================================================
CREATE TABLE IF NOT EXISTS sync_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabla_origen TEXT,
    registro_id TEXT,
    destino TEXT,  -- neo4j, supabase
    ultimo_sync TIMESTAMP,
    estado TEXT,  -- synced, pending, error
    intentos INTEGER DEFAULT 0,
    ultimo_error TEXT
);

CREATE INDEX idx_sync_destino ON sync_status(destino, estado);
```

---

## 📊 Schema Supabase (Vectores)

```sql
-- En Supabase SQL Editor

-- ============================================================
-- TABLA: yo_embeddings (vectores)
-- ============================================================
CREATE TABLE yo_embeddings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    instancia_id text NOT NULL,
    embedding vector(768),  -- Dimension de sentence-transformers
    modelo text DEFAULT 'paraphrase-multilingual-mpnet-base-v2',
    created_at timestamp with time zone DEFAULT now()
);

-- Índice para búsqueda vectorial
CREATE INDEX ON yo_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================================
-- TABLA: yo_metadata (metadata de archivos)
-- ============================================================
CREATE TABLE yo_metadata (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    archivo_nombre text NOT NULL,
    archivo_tipo text,
    texto_extraido text,
    ereignis_id text,
    augenblick_id text,
    instancia_id text,
    tipo_yo text,
    coherencia_narrativa real,
    created_at timestamp with time zone DEFAULT now(),
    metadata jsonb  -- Metadata adicional
);

CREATE INDEX idx_metadata_instancia ON yo_metadata(instancia_id);
CREATE INDEX idx_metadata_tipo ON yo_metadata(tipo_yo);

-- ============================================================
-- FUNCIÓN: búsqueda vectorial
-- ============================================================
CREATE OR REPLACE FUNCTION match_embeddings(
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  instancia_id text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    yo_embeddings.id,
    yo_embeddings.instancia_id,
    1 - (yo_embeddings.embedding <=> query_embedding) as similarity
  FROM yo_embeddings
  WHERE 1 - (yo_embeddings.embedding <=> query_embedding) > match_threshold
  ORDER BY yo_embeddings.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

---

## 🔄 Workflow n8n Adaptado

### Workflow: Monitor Carpeta Datos Brutos

```json
{
  "name": "Monitor Datos Brutos",
  "nodes": [
    {
      "name": "Watch Folder",
      "type": "n8n-nodes-base.localFileTrigger",
      "parameters": {
        "path": "{{$env.DATOS_BRUTOS_PATH}}",
        "triggerOn": "add",
        "recursive": true
      }
    },
    {
      "name": "Calcular Hash",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "language": "javascript",
        "jsCode": "const crypto = require('crypto');\nconst fs = require('fs');\n\nconst filePath = $input.item.binary.data.filePath;\nconst fileBuffer = fs.readFileSync(filePath);\nconst hash = crypto.createHash('sha256').update(fileBuffer).digest('hex');\n\nreturn {\n  json: {\n    ...json: $input.item.json,\n    hash_sha256: hash,\n    tamaño_bytes: fileBuffer.length\n  }\n};"
      }
    },
    {
      "name": "Verificar Duplicado SQLite",
      "type": "n8n-nodes-base.sqlite",
      "parameters": {
        "operation": "executeQuery",
        "databasePath": "{{$env.SQLITE_PATH}}",
        "query": "SELECT id FROM archivos_brutos WHERE hash_sha256 = '{{$json.hash_sha256}}'"
      }
    },
    {
      "name": "Si No Duplicado",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{$json.length}}",
              "operation": "equal",
              "value2": 0
            }
          ]
        }
      }
    },
    {
      "name": "Insertar en SQLite",
      "type": "n8n-nodes-base.sqlite",
      "parameters": {
        "operation": "insert",
        "databasePath": "{{$env.SQLITE_PATH}}",
        "table": "archivos_brutos",
        "columns": "nombre_archivo, ruta_completa, tipo_archivo, mime_type, tamaño_bytes, hash_sha256, estado_proceso",
        "values": "={{$json.nombre}}, ={{$json.ruta}}, ={{$json.tipo}}, ={{$json.mimeType}}, ={{$json.tamaño_bytes}}, ={{$json.hash_sha256}}, 'pendiente'"
      }
    },
    {
      "name": "Clasificador Tipo",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// (código de clasificador del diseño anterior)"
      }
    },
    {
      "name": "Procesamiento Multimodal",
      "type": "n8n-nodes-base.switch"
      // (switch del diseño anterior)
    }
  ]
}
```

### Workflow: Dual Persistence (Supabase + SQLite)

```json
{
  "name": "Dual Persistence",
  "nodes": [
    {
      "name": "Parallel Split",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 1
      }
    },
    {
      "name": "Save to SQLite",
      "type": "n8n-nodes-base.sqlite",
      "parameters": {
        "operation": "insert",
        "databasePath": "{{$env.SQLITE_PATH}}",
        "table": "instancias_local",
        "columns": "id, augenblick_id, tipo_yo, coherencia_narrativa, densidad_conceptual",
        "values": "={{$json.instancia.id}}, ={{$json.augenblick.id}}, ={{$json.instancia.tipo_yo}}, ={{$json.instancia.coherencia}}, ={{$json.instancia.densidad}}"
      }
    },
    {
      "name": "Save Embedding to Supabase",
      "type": "n8n-nodes-base.supabase",
      "parameters": {
        "operation": "insert",
        "tableId": "yo_embeddings",
        "fields": {
          "instancia_id": "={{$json.instancia.id}}",
          "embedding": "={{$json.embeddings.vector}}",
          "modelo": "paraphrase-multilingual-mpnet-base-v2"
        }
      }
    },
    {
      "name": "Save Metadata to Supabase",
      "type": "n8n-nodes-base.supabase",
      "parameters": {
        "operation": "insert",
        "tableId": "yo_metadata",
        "fields": {
          "archivo_nombre": "={{$json.archivo.nombre}}",
          "archivo_tipo": "={{$json.archivo.tipo}}",
          "texto_extraido": "={{$json.texto}}",
          "ereignis_id": "={{$json.ereignis.id}}",
          "augenblick_id": "={{$json.augenblick.id}}",
          "instancia_id": "={{$json.instancia.id}}",
          "tipo_yo": "={{$json.instancia.tipo_yo}}",
          "coherencia_narrativa": "={{$json.instancia.coherencia}}",
          "metadata": "={{JSON.stringify($json.metadata)}}"
        }
      }
    },
    {
      "name": "Save to Neo4j (LAN)",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "{{$env.NEO4J_HTTP}}/db/{{$env.NEO4J_DATABASE}}/tx/commit",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpBasicAuth",
        "body": {
          "statements": [
            {
              "statement": "MERGE (i:Instancia {id: $id}) SET i.tipo_yo = $tipo_yo, i.coherencia = $coherencia, i.embedding = $embedding RETURN i",
              "parameters": {
                "id": "={{$json.instancia.id}}",
                "tipo_yo": "={{$json.instancia.tipo_yo}}",
                "coherencia": "={{$json.instancia.coherencia}}",
                "embedding": "={{$json.embeddings.vector}}"
              }
            }
          ]
        }
      }
    },
    {
      "name": "Update SQLite Sync Status",
      "type": "n8n-nodes-base.sqlite",
      "parameters": {
        "operation": "update",
        "databasePath": "{{$env.SQLITE_PATH}}",
        "table": "instancias_local",
        "updateColumn": "neo4j_synced",
        "updateValue": "1",
        "where": "id = '{{$json.instancia.id}}'"
      }
    }
  ],
  "connections": {
    "Parallel Split": {
      "main": [
        [{ "node": "Save to SQLite", "type": "main", "index": 0 }],
        [{ "node": "Save Embedding to Supabase", "type": "main", "index": 0 }],
        [{ "node": "Save to Neo4j (LAN)", "type": "main", "index": 0 }]
      ]
    }
  }
}
```

---

## 🧠 Integración LightRAG (LAN)

### Endpoint Python para LightRAG

```python
# En tu Python backend (puerto 8000)

import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/lightrag")

LIGHTRAG_URL = os.getenv("LIGHTRAG_API_URL", "http://192.168.1.50:9000")

@router.post("/query")
async def lightrag_query(query: str, top_k: int = 10):
    """
    Query a LightRAG en la PC remota (LAN)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LIGHTRAG_URL}/query",
            json={
                "query": query,
                "top_k": top_k,
                "mode": "hybrid"  # local + global retrieval
            },
            timeout=30.0
        )
        
        return response.json()

@router.post("/insert")
async def lightrag_insert(text: str, metadata: dict):
    """
    Insertar texto en LightRAG
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LIGHTRAG_URL}/insert",
            json={
                "text": text,
                "metadata": metadata
            },
            timeout=30.0
        )
        
        return response.json()
```

### Nodo n8n para LightRAG

```json
{
  "name": "LightRAG Insert",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "{{$env.LIGHTRAG_API_URL}}/insert",
    "body": {
      "text": "={{$json.texto_extraido}}",
      "metadata": {
        "instancia_id": "={{$json.instancia.id}}",
        "tipo_yo": "={{$json.instancia.tipo_yo}}",
        "timestamp": "={{$json.timestamp}}"
      }
    },
    "options": {
      "timeout": 30000
    }
  }
}
```

---

## 🌐 Configuración UI → Datos Brutos

### Estructura para UI

```javascript
// Frontend (UI que haces tú)
// Ejemplo de upload a carpeta datos_brutos

// HTML
<input type="file" id="fileInput" multiple>
<button onclick="uploadFiles()">Subir Archivos</button>

// JavaScript
async function uploadFiles() {
    const files = document.getElementById('fileInput').files;
    const formData = new FormData();
    
    for(let file of files) {
        formData.append('files', file);
    }
    
    // Endpoint Python que guarda en datos_brutos/
    const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    console.log('Archivos subidos:', result);
}
```

### Endpoint Python para Upload

```python
# api/endpoints/upload.py

from fastapi import APIRouter, UploadFile, File
from typing import List
import shutil
from pathlib import Path
import hashlib

router = APIRouter(prefix="/api/upload")

DATOS_BRUTOS = Path(os.getenv("DATOS_BRUTOS_PATH"))

@router.post("/")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Recibe archivos desde UI y los guarda en datos_brutos/
    n8n los detectará automáticamente
    """
    resultados = []
    
    for file in files:
        # Determinar subcarpeta según tipo
        content_type = file.content_type
        if content_type.startswith('text'):
            subcarpeta = "texto"
        elif content_type.startswith('image'):
            subcarpeta = "imagenes"
        elif content_type.startswith('audio'):
            subcarpeta = "audio"
        elif content_type.startswith('video'):
            subcarpeta = "video"
        elif 'pdf' in content_type or 'document' in content_type:
            subcarpeta = "documentos"
        else:
            subcarpeta = "otros"
        
        # Crear ruta destino
        destino_dir = DATOS_BRUTOS / subcarpeta
        destino_dir.mkdir(parents=True, exist_ok=True)
        
        destino_archivo = destino_dir / file.filename
        
        # Guardar archivo
        with open(destino_archivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Calcular hash
        with open(destino_archivo, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        resultados.append({
            "filename": file.filename,
            "path": str(destino_archivo),
            "size": destino_archivo.stat().st_size,
            "type": content_type,
            "hash": file_hash,
            "subcarpeta": subcarpeta
        })
    
    return {
        "success": True,
        "files_uploaded": len(resultados),
        "files": resultados
    }
```

---

## 🔧 Script de Inicialización

```python
# scripts/init_databases.py

import sqlite3
import os
from pathlib import Path

def init_sqlite():
    """Inicializa base de datos SQLite local"""
    db_path = Path(os.getenv("SQLITE_PATH"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Leer schema
    with open("base_datos_local/schema.sql", "r") as f:
        schema = f.read()
    
    conn.executescript(schema)
    conn.commit()
    conn.close()
    
    print(f"✅ SQLite inicializado: {db_path}")

def init_directories():
    """Crea estructura de carpetas"""
    dirs = [
        "datos_brutos/texto",
        "datos_brutos/imagenes",
        "datos_brutos/audio",
        "datos_brutos/video",
        "datos_brutos/documentos",
        "datos_brutos/otros",
        "datos_procesados/ereignis",
        "datos_procesados/augenblick",
        "datos_procesados/instancias",
        "datos_procesados/embeddings",
        "base_datos_local",
        "logs_sistema/procesamiento",
        "logs_sistema/n8n",
        "logs_sistema/errores"
    ]
    
    base = Path("c:/Users/Public/#...Raíz Dasein/REFERENCIA/YO estructural")
    
    for dir_path in dirs:
        (base / dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Estructura de carpetas creada")

if __name__ == "__main__":
    init_directories()
    init_sqlite()
    print("\n✅ Sistema inicializado correctamente")
```

---

## 📋 Checklist de Configuración

### 1. Setup Bases de Datos
- [ ] SQLite creado y schema aplicado
- [ ] Supabase project creado
- [ ] Tablas Supabase creadas (yo_embeddings, yo_metadata)
- [ ] Extensión pgvector habilitada en Supabase
- [ ] Neo4j en PC remota accesible vía LAN

### 2. Setup LAN
- [ ] IP estática configurada en PC remota (192.168.1.50)
- [ ] Neo4j escuchando en 0.0.0.0 (no solo localhost)
- [ ] Firewall permite puertos 7687, 7474
- [ ] LightRAG corriendo en PC remota (puerto 9000)
- [ ] Conectividad LAN verificada (ping 192.168.1.50)

### 3. Setup Local
- [ ] Carpetas datos_brutos/ creadas
- [ ] Python backend corriendo (puerto 8000)
- [ ] n8n corriendo (puerto 5678)
- [ ] Variables de entorno configuradas (.env)
- [ ] Script init_databases.py ejecutado

### 4. Setup n8n
- [ ] Workflow "Monitor Datos Brutos" importado
- [ ] Workflow "Dual Persistence" importado
- [ ] Credenciales Supabase configuradas en n8n
- [ ] Credenciales Neo4j (LAN) configuradas en n8n
- [ ] Test de workflows ejecutado

---

## 🚀 Comandos de Inicio

```powershell
# 1. Inicializar bases de datos
python scripts/init_databases.py

# 2. Iniciar Python backend
cd "c:\Users\Public\#...Raíz Dasein\REFERENCIA\YO estructural"
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 3. Iniciar n8n
n8n start

# 4. Verificar conectividad Neo4j (LAN)
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://192.168.1.50:7687', auth=('neo4j', 'password')); driver.verify_connectivity(); print('✅ Neo4j LAN OK')"

# 5. Tu UI (puerto 3000)
# (tú la inicias según tu configuración)
```

---

**Archivo creado**: Configuración completa para arquitectura dual database + LAN
**Próximo**: ¿Quieres que cree los archivos de configuración y scripts de inicialización?
