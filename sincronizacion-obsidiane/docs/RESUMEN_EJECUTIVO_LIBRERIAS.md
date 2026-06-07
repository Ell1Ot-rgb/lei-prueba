# 📊 RESUMEN EJECUTIVO - DISTRIBUCIÓN DE LIBRERÍAS

## 🎯 Respuesta Rápida: ¿Dónde va cada librería?

### PC 1 - DUAL-CORE AMD (Procesadores Ligeros) ✅

| # | Librería | Versión | Instalación | Categoría |
|:---:|:---|:---:|:---|:---|
| 1 | `python-dotenv` | 1.0.0 | pip | Configuración |
| 2 | `PyYAML` | 6.0.1 | pip | Configuración |
| 3 | `toml` | 0.10.2 | pip | Configuración |
| 4 | `spacy` | 3.7.2 | pip + `python -m spacy download es_core_news_sm` | NLP |
| 5 | `nltk` | 3.8.1 | pip | NLP |
| 6 | `sentence-transformers` | 2.2.2 | pip | Embeddings |
| 7 | `numpy` | 1.26.4 | pip | Computación |
| 8 | `scipy` | 1.11.4 | pip | Computación |
| 9 | `pandas` | 2.1.4 | pip | Datos |
| 10 | `scikit-learn` | 1.3.2 | pip | ML/Clustering |
| 11 | `requests` | 2.31.0 | pip | HTTP |
| 12 | `httpx` | 0.24.1 | pip | HTTP |
| 13 | `aiohttp` | 3.9.1 | pip | HTTP Async |
| 14 | `websockets` | 12.0 | pip | WebSockets |
| 15 | `neo4j` | 5.15.0 | pip | BD (cliente remoto) |
| 16 | `psycopg2-binary` | 2.9.9 | pip | PostgreSQL |
| 17 | `python-dateutil` | 2.8.2 | pip | Fechas |
| 18 | `pytz` | 2023.3 | pip | Zonas horarias |
| 19 | `loguru` | 0.7.2 | pip | Logging |
| 20 | `psutil` | 5.9.6 | pip | Monitoreo |
| 21 | `tqdm` | 4.66.1 | pip | Barras progreso |
| 22 | `click` | 8.1.7 | pip | CLI |
| 23 | `rich` | 13.7.0 | pip | Formato terminal |
| 24 | `typer` | 0.9.0 | pip | CLI |
| 25 | `pydantic` | 2.5.0 | pip | Validación |
| 26 | `jsonschema` | 4.20.0 | pip | JSON Schema |
| 27 | `marshmallow` | 3.20.1 | pip | Serialización |
| 28 | `cachetools` | 5.3.2 | pip | Cache |
| 29 | `zstandard` | 0.22.0 | pip | Compresión |
| 30 | `redis` | 5.0.1 | pip | Cache Redis |
| 31 | `Pillow` | 10.1.0 | pip | Imágenes |
| 32 | `python-multipart` | 0.0.6 | pip | Form parsing |
| 33 | `python-magic` | 0.4.27 | pip | Tipos archivo |
| 34 | `openpyxl` | 3.1.2 | pip | Excel |
| 35 | `librosa` | 0.10.1 | pip | Audio (opt) |
| 36 | `SpeechRecognition` | 3.10.0 | pip | Voz (opt) |
| 37 | `google-api-python-client` | 2.108.0 | pip | Google APIs |
| 38 | `google-auth` | 2.23.4 | pip | Google Auth |
| 39 | `google-auth-oauthlib` | 1.1.0 | pip | OAuth Google |
| 40 | `google-auth-httplib2` | 0.1.1 | pip | HTTP Google |
| 41 | `supabase` | 2.1.1 | pip | Supabase |
| 42 | `pytest` | 7.4.3 | pip | Testing (dev) |
| 43 | `pytest-asyncio` | 0.21.1 | pip | Testing async (dev) |
| 44 | `black` | 23.11.0 | pip | Formato (dev) |
| 45 | `flake8` | 6.1.0 | pip | Linter (dev) |

**Total PC 1:** 45 librerías | ~650 MB

---

### PC 2 - COMPUTADOR POTENTE (Neo4j + Análisis) 🔧

| # | Librería / Servicio | Versión | Instalación | Ubicación |
|:---:|:---|:---:|:---|:---|
| 1 | **Neo4j Server** | 5.15 | `apt` / `docker` / `brew` | Servidor |
| 2 | **APOC Plugin** | (builtin 5.x) | Copiar JAR a `plugins/` | Neo4j |
| 3 | **GDS Plugin** | 2.x | Copiar JAR a `plugins/` | Neo4j |
| 4 | `neo4j` (driver) | 5.15.0 | pip | Python |
| 5 | `numpy` | 1.26.4 | pip | Python |
| 6 | `scipy` | 1.11.4 | pip | Python |
| 7 | `pandas` | 2.1.4 | pip | Python |
| 8 | `scikit-learn` | 1.3.2 | pip | Python |
| 9 | `concepts` | 0.9.2 | pip | FCA |
| 10 | `thefuzz` | 0.20.0 | pip | Fuzzy matching |
| 11 | `python-Levenshtein` | 0.21.1 | pip | Acelerador thefuzz |
| 12 | `PyYAML` | 6.0.1 | pip | Configuración |
| 13 | `python-dotenv` | 1.0.0 | pip | Configuración |
| 14 | `tqdm` | 4.66.1 | pip | Progreso |
| 15 | `loguru` | 0.7.2 | pip | Logging |
| 16 | `psutil` | 5.9.6 | pip | Monitoreo |
| 17 | `networkx` | (latest) | pip | Graph analysis |
| 18 | `matplotlib` | 3.8.2 | pip | Visualización |
| 19 | `plotly` | 5.17.0 | pip | Gráficos |
| 20 | `pytest` | 7.4.3 | pip | Testing |
| 21 | `pytest-asyncio` | 0.21.1 | pip | Testing async |

**Total PC 2:** 21 librerías + Neo4j server | ~500 MB (sin Neo4j)

---

### ☁️ SERVICIOS EXTERNOS (No requieren instalación)

| Servicio | Librería Cliente | Versión | Protocolo |
|:---|:---:|:---:|:---|
| **Google Drive** | google-api-python-client | 2.108.0 | OAuth2 + REST |
| **Supabase (PostgreSQL)** | supabase | 2.1.1 | SQL + REST |
| **n8n (Automation)** | requests | 2.31.0 | HTTP REST |

---

## 📈 Estadísticas de Distribución

### Cantidad de librerías
```
PC 1: 45 librerías (65%)
PC 2: 21 librerías (30%)
Externos: 3 servicios (5%)
───────────────────────
TOTAL: 69 componentes
```

### Tamaño de instalación
```
PC 1: ~650 MB (incluyendo modelos ligeros)
PC 2: ~500 MB (sin Neo4j server)
────────────────────────────────────────
TOTAL: ~1.15 GB (optimizado)

Nota: Original era ~1.8 GB (64% más grande)
```

### Categorías principales
```
NLP & Embeddings:          6 librerías
Data Science & ML:         6 librerías
Networking & HTTP:         4 librerías
Database Drivers:          2 librerías
Logging & Monitoring:      3 librerías
Validación & Formato:      4 librerías
Utilidades:                8 librerías
Google Cloud APIs:         4 librerías
Testing (dev):             5 librerías
Otros:                     22 librerías
────────────────────────
TOTAL: 64 librerías pip
```

---

## 🚀 Instalación Rápida (Copia y Pega)

### PC 1: Dual-Core AMD
```bash
# Crear entorno
python3.8 -m venv venv_pc1
source venv_pc1/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install \
  python-dotenv PyYAML toml \
  spacy nltk sentence-transformers \
  numpy scipy pandas scikit-learn \
  requests httpx aiohttp websockets neo4j psycopg2-binary \
  python-dateutil pytz \
  loguru psutil tqdm click rich typer \
  pydantic jsonschema marshmallow \
  cachetools zstandard redis \
  Pillow python-multipart python-magic openpyxl \
  librosa SpeechRecognition \
  google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 \
  supabase \
  pytest pytest-asyncio black flake8

# Descargar modelo spaCy
python -m spacy download es_core_news_sm

# Verificar
python -c "import spacy, sentence_transformers, sklearn; print('✅ PC1 OK')"
```

### PC 2: Potente (Neo4j + FCA)
```bash
# Crear entorno
python3.8 -m venv venv_neo4j
source venv_neo4j/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install \
  neo4j numpy scipy pandas scikit-learn \
  concepts thefuzz python-Levenshtein \
  PyYAML python-dotenv \
  tqdm loguru psutil \
  networkx matplotlib plotly \
  pytest pytest-asyncio

# Instalar Neo4j (Ubuntu/Debian)
sudo apt install neo4j

# O con Docker
docker run -d \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.15

# Verificar
python -c "from neo4j import GraphDatabase; import concepts; print('✅ PC2 OK')"
neo4j --version
```

---

## ⚠️ Librerías a EVITAR en Dual-Core

| Librería | Razón | Alternativa |
|:---|:---|:---|
| `torch` | 500 MB - PyTorch completo | Usar `sentence-transformers` |
| `tensorflow` | 300+ MB - TensorFlow | Usar `scikit-learn` |
| `es_core_news_lg` | 500 MB - spaCy grande | Usar `es_core_news_sm` (50 MB) |
| `transformers` | 200 MB - Hugging Face | Usar `sentence-transformers` |
| `opencv-python` | 100 MB - Computer vision | Usar `Pillow` si solo necesitas imágenes |
| `xgboost` | 50 MB - boosting pesado | Usar `scikit-learn.ensemble` |
| `keras` | Depende de TensorFlow/Theano | Usar `scikit-learn` |

---

## 🔄 Sincronización entre PCs

Después de instalar, sincronizar configuración:

```bash
# En PC 2, sincronizar hacia PC 1
rsync -av /path/to/yo_estructural/config/ \
  usuario@pc1_ip:/path/to/yo_estructural/config/

# O usar git para versionar
git add requirements*.txt config_dualcore.yaml
git commit -m "Dependencias optimizadas para dual-core"
git push
```

---

## 📋 Checklist de Verificación

### ✅ Después de instalar PC 1:
```python
import dotenv; print("✅ dotenv")
import yaml; print("✅ yaml")
import spacy; nlp = spacy.load('es_core_news_sm'); print("✅ spacy")
from sentence_transformers import SentenceTransformer; print("✅ st")
import numpy; print("✅ numpy")
import scipy; print("✅ scipy")
import pandas; print("✅ pandas")
from sklearn.cluster import DBSCAN; print("✅ sklearn")
import neo4j; print("✅ neo4j")
import requests; print("✅ requests")
import pydantic; print("✅ pydantic")
print("\n🎉 ¡PC 1 listo!")
```

### ✅ Después de instalar PC 2:
```python
import neo4j; print("✅ neo4j driver")
from concepts import *; print("✅ concepts")
import networkx; print("✅ networkx")
import matplotlib; print("✅ matplotlib")
from sklearn.cluster import DBSCAN; print("✅ sklearn")
from thefuzz import fuzz; print("✅ thefuzz")
print("\n🎉 ¡PC 2 listo!")
```

```bash
# Verificar Neo4j server
neo4j status
# O con docker
docker ps | grep neo4j
```

---

## 💡 Notas Importantes

1. **Bandwith durante instalación:** Primera instalación en dual-core ~2-3 GB descarga. Usar WiFi estable.

2. **Modelos NLP:** 
   - Primera ejecución descarga modelos (~200 MB adicionales)
   - Se cachean localmente en `~/.cache/` o `~/.spacy/`

3. **Redis (opcional):**
   - Solo si quieres caché distribuido entre PCs
   - Si no lo necesitas, quitá `redis==5.0.1` de requirements

4. **Google APIs:**
   - Necesita archivo `credentials.json` de Google Cloud Console
   - Descargar desde: https://console.cloud.google.com

5. **Supabase:**
   - Necesita URL y API key de proyecto Supabase
   - Configurar en `.env`: `SUPABASE_URL=...`, `SUPABASE_KEY=...`

6. **Neo4j remoto:**
   - PC 1 se conecta a Neo4j en PC 2 via `bolt://ip_pc2:7687`
   - Configurar IP correcta en `config_dualcore.yaml`

7. **Firewall:**
   - Abrir puerto 7687 (Neo4j) entre PCs
   - O usar SSH tunneling: `ssh -L 7687:localhost:7687 user@pc2_ip`

---

## 📞 Soporte Rápido

**Error durante `pip install`:**
```bash
# Actualizar pip
pip install --upgrade pip setuptools wheel

# Instalar dependencias del sistema (Ubuntu)
sudo apt install python3-dev build-essential

# Reintentar
pip install -r requirements_dualcore.txt
```

**Neo4j no conecta desde PC 1:**
```bash
# Verificar conectividad
nc -zv IP_PC2 7687

# Probar con telnet
telnet IP_PC2 7687

# Ver logs Neo4j (PC 2)
tail -f /var/log/neo4j/neo4j.log  # si está instalado
docker logs <container_id>         # si está en Docker
```

**Memoria insuficiente en PC 1:**
```bash
# Ver uso actual
psutil.virtual_memory()

# Reducir batch sizes en config_dualcore.yaml:
batch_size_embeddings: 16  # reducir de 32
chunk_size_preinstancias: 500  # reducir de 1000
```

---

**Última actualización:** 2025-11-06  
**Versión:** YO Estructural 2.3  
**Status:** ✅ Listo para producción
