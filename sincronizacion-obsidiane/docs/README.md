# 🧠 YO Estructural v3.0 - Sistema Fenomenológico Computacional

## 📋 Descripción

Sistema híbrido de procesamiento fenomenológico que integra:
- **Capa 1 (Monje Gemelo)**: Simulación hardware en Renode + métricas físicas
- **Capa 2 (YO Estructural)**: 3 sistemas de procesamiento avanzado
  - **S1**: Sistema Principal (Motor YO + Procesadores)
  - **S2**: Emergencia de Conceptos (aprendizaje incremental)
  - **S3**: Lógica Pura (mundos hipotéticos)

---

## 🚀 Características Principales

### ✅ Integración Completa 3 Sistemas

- **S1 (Principal)**: Procesa vectores fenomenológicos, genera Grundzugs
- **S2 (Emergencia)**: Aprende conceptos progresivamente desde Grundzugs
- **S3 (Lógica)**: Construye mundos lógicos y aprende axiomas

### ✅ Clasificador Avanzado

- Predice emociones/conceptos desde **métricas físicas puras** (sin semántica)
- Features 72D: hash spectral + energía + entropía + ciclos
- Red neuronal con attention layer
- Entrenamiento incremental

### ✅ Tokenizador GPU Optimizado

- Soporte CUDA/ROCm/MPS (detección automática)
- Batch processing (8x más rápido)
- Cache Redis inteligente
- Mixed Precision (AMP)

### ✅ Deployment Docker Completo

- GPU support con NVIDIA Container Toolkit
- Stack: App + Neo4j + Redis + LightRAG
- Monitoreo opcional (Prometheus + Grafana)

---

## 📦 Instalación

### Opción 1: Docker (Recomendado para GPU)

```bash
# 1. Instalar NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# 2. Clonar repositorio
git clone <URL>
cd "YO estructural"

# 3. Configurar .env
cp .env.example .env
nano .env  # Agregar API keys

# 4. Levantar stack
docker-compose -f docker-compose.gpu.yml up -d

# 5. Verificar
docker logs yo-estructural-gpu
curl http://localhost:8000/health
```

Ver **DEPLOYMENT_GPU.md** para guía completa.

### Opción 2: Instalación Local

```bash
# 1. Python 3.11+
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Dependencias
pip install -r requirements-gpu.txt  # Con GPU
# o
pip install -r requirements.txt      # Sin GPU

# 3. Neo4j (Docker)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/yourpassword \
  neo4j:5.14-community

# 4. Redis (Docker)
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# 5. Configurar .env
cp .env.example .env
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│ CAPA 1: Monje Gemelo (Simulación Hardware)         │
│ • Renode (ARM/x86 virtual)                          │
│ • Métricas físicas: hash, energía, entropía        │
│ • Publica en Redis: monje/fenomenologia/*          │
└──────────────────┬──────────────────────────────────┘
                   │ Vector Físico (JSON)
                   ▼
┌─────────────────────────────────────────────────────┐
│ CAPA 2: YO Estructural (Procesamiento)             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌────────────────────────────────────────┐        │
│  │ S1: Sistema Principal                  │        │
│  │ • Motor YO emergente                   │        │
│  │ • Tokenizador fenomenológico (REMForge)│        │
│  │ • Clasificador avanzado (72D → emoción)│        │
│  │ • Generador de Grundzugs               │        │
│  └──────────────┬─────────────────────────┘        │
│                 │ Grundzugs                        │
│                 ├──────────┬──────────┐            │
│                 ▼          ▼          ▼            │
│  ┌────────────────┐ ┌──────────┐ ┌─────────┐      │
│  │ S2: Emergencia │ │ S3:      │ │ Validación│     │
│  │ • Conceptos    │ │ Lógica   │ │ Cruzada  │      │
│  │ • Incremental  │ │ • Mundos │ │ S2 vs S3 │      │
│  │ • Convergencia │ │ • Axiomas│ │          │      │
│  └────────────────┘ └──────────┘ └─────────┘      │
│                                                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ PERSISTENCIA                                        │
│ • Neo4j: Grafos fenomenológicos                     │
│ • Redis: Cache + mensajería                         │
│ • Pickle: Estado S2/S3                              │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 Uso

### Inicialización Básica

```python
from core.sistema_principal import SistemaYoEstructural

# Inicializar sistema
sistema = SistemaYoEstructural("configuracion/config_4gb.yaml")

# Verificar componentes
print(f"S1 activo: {sistema.motor_yo is not None}")
print(f"S2 activo: {sistema.sistema_emergencia is not None}")
print(f"S3 activo: {sistema.sistema_logica is not None}")
```

### Orquestador Completo

```python
from core.orquestador_capa2 import OrquestadorCapa2

# Inicializar orquestador
orq = OrquestadorCapa2("configuracion/config_4gb.yaml")

# Procesar evento físico
evento = {
    'intensidad': 0.72,
    'complejidad': 0.85,
    'tipo_base': 'narrativo',
    'origen_fisico': {
        'hash': 'a7f3e2d9c1b4a8f3',
        'energia_uj': 3420,
        'ciclos': 1250000
    }
}

resultado = orq.procesar_evento_fisico(evento)

print(f"Grundzugs: {resultado['s1_resultado']['grundzugs']}")
print(f"Certeza S2: {resultado['s2_resultado']['patron_certeza']:.3f}")
print(f"Axiomas S3: {resultado['s3_resultado']['axiomas_totales']}")
```

### Tokenizador GPU

```python
from procesadores.tokenizador_fenomenologico_gpu import TokenizadorFenomenologicoGPU

# Inicializar con GPU
tok = TokenizadorFenomenologicoGPU(
    device="cuda",
    modo="ultra",
    precision="mixed",
    batch_size=8
)

# Single text
resultado = tok.forge_text_ultra("Veo un objeto rojo brillante.")

# Batch processing
textos = ["Texto 1", "Texto 2", "Texto 3"]
resultados = tok.forge_batch(textos)

# Estadísticas
stats = tok.obtener_estadisticas()
print(f"GPU: {stats['gpu']['name']}")
print(f"VRAM: {stats['gpu']['vram_allocated_gb']:.2f} GB")
```

### Clasificador Avanzado

```python
from procesadores.clasificador_avanzado import ClasificadorAvanzado

# Inicializar
clf = ClasificadorAvanzado(num_clases=20)

# Predecir desde vector físico
vector = {
    'energia': 3420,
    'entropia': 2847563921,
    'tiempo': 1250000,
    'instrucciones': 45823,
    'hash': 'a7f3e2d9c1b4a8f3'
}

pred = clf.predecir(vector)
print(f"Clase: {pred.clase_predicha}")
print(f"Certeza: {pred.certeza:.2%}")
```

---

## 🧪 Testing

### Test de Integración

```bash
python test_integracion_s1_s2_s3.py
```

Salida esperada:
```
✅ Sistema Principal inicializado
✅ S2: 3 conceptos emergidos
✅ S3: 2 mundos creados
✅ Método ciclo_incremental() disponible
🎉 INTEGRACIÓN S1+S2+S3 COMPLETADA Y VERIFICADA
```

### Test Individual

```bash
# S2: Emergencia
python emergencia_concepto/simulacion_entropia.py

# S3: Lógica
python demo_aprendizaje_incremental.py
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [DEPLOYMENT_GPU.md](DEPLOYMENT_GPU.md) | Guía completa de deployment Docker + GPU |
| [VERIFICACION_INTEGRACION_S1_S2_S3.md](VERIFICACION_INTEGRACION_S1_S2_S3.md) | Verificación de integración |
| [RESUMEN_IMPLEMENTACION_COMPLETA.md](RESUMEN_IMPLEMENTACION_COMPLETA.md) | Resumen de todos los componentes |
| [PLAN_CLASIFICADOR_AVANZADO.md](PLAN_CLASIFICADOR_AVANZADO.md) | Plan del clasificador 72D |
| [MEJORAS_APRENDIZAJE_INCREMENTAL.md](MEJORAS_APRENDIZAJE_INCREMENTAL.md) | Mejoras S2/S3 |
| [FLUJO_DATOS_CAPA1.md](FLUJO_DATOS_CAPA1.md) | Cómo llegan datos desde Monje |

---

## 🔧 Configuración

### `.env` (Obligatorio)

```env
# Neo4j
NEO4J_PASSWORD=yourpassword

# API Keys
OPENROUTER_API_KEY=sk-or-v1-xxxxx
GEMINI_API_KEY=AIzaSyxxxxx

# GPU
CUDA_VISIBLE_DEVICES=0
TOKENIZER_DEVICE=cuda
TOKENIZER_MODE=ultra
CLASIFICADOR_DEVICE=cuda
```

### `config_4gb.yaml` (Opcional)

```yaml
emergencia:
  state_file: "estado_emergencia.pkl"
  
logica_pura:
  state_file: "estado_logica_pura.pkl"
  
remforge:
  modo: "ultra"
  device: "auto"
```

---

## 📊 Servicios (Docker)

| Servicio | Puerto | URL |
|----------|--------|-----|
| API Principal | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Neo4j Browser | 7474 | http://localhost:7474 |
| Neo4j Bolt | 7687 | bolt://localhost:7687 |
| Redis | 6379 | localhost:6379 |
| LightRAG | 8002 | http://localhost:8002 |

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Agrega nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Pull Request

---

## 📄 Licencia

[Especificar licencia]

---

## 🆘 Soporte

- **Issues**: GitHub Issues
- **Documentación**: Ver carpeta `/docs`
- **Troubleshooting**: `DEPLOYMENT_GPU.md` sección Troubleshooting

---

✅ **Sistema completo con integración S1+S2+S3, GPU optimizado y listo para deployment!** 🚀
