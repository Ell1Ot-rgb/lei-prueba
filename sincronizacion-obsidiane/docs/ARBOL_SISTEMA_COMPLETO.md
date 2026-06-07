# 🌳 ÁRBOL COMPLETO DEL SISTEMA YO ESTRUCTURAL v3.0
## Ramificación con Ejecutables Marcados

```
YO estructural/
│
├── 📄 README.md                                    # Documentación principal
├── 📄 .env.example                                 # Template de configuración
├── 📄 .env                                         # Configuración (NO versionar)
├── 📄 requirements.txt                             # Dependencias Python base
├── 📄 requirements-gpu.txt                         # Dependencias GPU optimizadas
│
├── 🐳 Dockerfile.gpu                               # Docker multi-stage con CUDA
├── 🐳 docker-compose.gpu.yml                       # Stack completo (GPU + Neo4j + Redis)
│
├── 🔧 configuracion/
│   ├── config.yaml                                 # Config producción
│   ├── config_4gb.yaml                             # Config RAM limitada
│   └── config_dev.yaml                             # Config desarrollo
│
├── 📚 DOCUMENTACIÓN/
│   ├── DEPLOYMENT_GPU.md                           # ⭐ Guía deployment Docker
│   ├── VERIFICACION_INTEGRACION_S1_S2_S3.md       # ⭐ Verificación integración
│   ├── RESUMEN_IMPLEMENTACION_COMPLETA.md         # ⭐ Resumen completo
│   ├── PLAN_CLASIFICADOR_AVANZADO.md              # Plan clasificador 72D
│   ├── MEJORAS_APRENDIZAJE_INCREMENTAL.md         # Mejoras S2/S3
│   ├── FLUJO_DATOS_CAPA1.md                       # Datos desde Monje
│   ├── ACLARACION_PROCESAMIENTO_ARCHIVO.md        # Procesamiento único
│   ├── COMPARACION_CLASIFICADOR_PROCESADOR_TOKENIZADOR.md
│   ├── DESCRIPCION_TECNICA_COMPLETA_SISTEMA.md
│   ├── SIMULACION_PROCESAMIENTO_COMPLETO.md
│   ├── CALCULO_CONCEPTO_LLUVIA.md
│   ├── CONSULTA_CONCEPTO_LLUVIA_OUTPUT.md
│   ├── EXTENSION_MUNDOS_HIPOTETICOS.md
│   ├── IMPOSIBILIDAD_ROJO_ABSTRACTO.md
│   ├── EMERGENCIA_ROJO_RELACIONAL.md
│   ├── EMERGENCIA_ROJO_DESDE_ESTRUCTURA.md
│   └── EMERGENCIA_ENTROPIA_SIMULACION.md
│
├── 🧠 core/                                        # ⭐ NÚCLEO DEL SISTEMA
│   ├── __init__.py
│   ├── sistema_principal.py                       # ⭐ Sistema Principal (S1)
│   ├── orquestador_capa2.py                       # ⭐ Orquestador S1+S2+S3
│   └── database.py                                # Conexión Neo4j
│
├── 🎯 motor_yo/                                    # Motor YO Emergente
│   ├── __init__.py
│   ├── sistema_yo_emergente.py                    # Sistema YO principal
│   ├── gradient_system.py                         # Sistema de gradientes
│   └── tipos_yo.py                                # Tipos de YO
│
├── 🔬 emergencia_concepto/                         # ⭐ SISTEMA 2: EMERGENCIA
│   ├── __init__.py
│   ├── motor_emergencia.py                        # ⭐ Motor principal S2
│   ├── sistema_observado.py                       # Sistemas observados
│   ├── experimento.py                             # Experimentos
│   ├── patron_relacional.py                       # Detección de patrones
│   ├── concepto_emergente.py                      # Conceptos emergidos
│   └── 🚀 simulacion_entropia.py                  # ⭐ EJECUTABLE: Demo entropía
│
├── 🧮 logica_pura/                                 # ⭐ SISTEMA 3: LÓGICA PURA
│   ├── __init__.py
│   ├── motor_hipotetico.py                        # ⭐ Motor principal S3
│   ├── mundo_hipotetico.py                        # Mundos lógicos
│   ├── objeto_abstracto.py                        # Objetos abstractos
│   └── axioma.py                                  # Axiomas lógicos
│
├── 🔧 procesadores/                                # Procesadores Fenomenológicos
│   ├── __init__.py
│   ├── tokenizador_fenomenologico.py              # Tokenizador base (REMForge)
│   ├── tokenizador_fenomenologico_gpu.py          # ⭐ Tokenizador GPU optimizado
│   ├── clasificador_avanzado.py                   # ⭐ Clasificador ML 72D
│   ├── procesador_fenomenologico.py               # Procesador regex
│   ├── generador_rutas_fenomenologicas.py         # Generador rutas FCA
│   ├── gemini_integration.py                      # Integración Gemini
│   └── analizador_maximo_relacional_hibrido.py    # Analizador híbrido
│
├── 🤖 REm/                                         # REMForge (Tokenización)
│   ├── __init__.py
│   ├── remforge_ultra_formato_optimo.py           # REMForge Ultra
│   ├── remforge_lite.py                           # REMForge Lite
│   └── demo.py                                    # Demo REMForge
│
├── 🔗 integraciones/                               # Integraciones Externas
│   ├── __init__.py
│   ├── redis_connector.py                         # ⭐ Conector Redis (Monje)
│   ├── n8n_config.py                              # Integración n8n
│   ├── google_drive_connector.py                  # Google Drive
│   └── supabase_connector.py                      # Supabase
│
├── 📊 niveles/                                     # Niveles Fenomenológicos
│   ├── __init__.py
│   ├── preinstancia.py                            # Pre-instancia (nivel -4)
│   ├── instancia_existencia.py                    # Instancia (nivel 0)
│   └── vohexistencia.py                           # Vohexistencia (nivel +1)
│
├── 🌐 n8n_setup/                                   # Workflows n8n
│   ├── deploy-n8n-complete.ps1                    # 🚀 EJECUTABLE: Deploy n8n
│   ├── install-n8n-complete.ps1                   # 🚀 EJECUTABLE: Install n8n
│   ├── SETUP_GUIDE.md
│   └── workflows/
│       ├── workflow_1_monitor_archivos.json
│       ├── workflow_2_sync_neo4j.json
│       ├── workflow_3_text_processing.json
│       ├── workflow_4_google_drive_multimodal.json
│       └── workflow_5_generador_maximo_relacional.json
│
├── 🧪 scripts/                                     # ⭐ SCRIPTS EJECUTABLES
│   ├── 🚀 init_system.py                          # ⭐ EJECUTABLE: Inicializar sistema
│   ├── 🚀 test_kimi.py                            # ⭐ EJECUTABLE: Test Kimi API
│   ├── 🚀 test_llm_simple.py                      # ⭐ EJECUTABLE: Test LLM
│   ├── 🚀 test_sin_credenciales.py                # ⭐ EJECUTABLE: Test Neo4j sin auth
│   ├── 🚀 simular_monje.py                        # ⭐ EJECUTABLE: Simular Monje Gemelo
│   ├── 🚀 procesamiento_general.py                # ⭐ EJECUTABLE: Procesamiento general
│   ├── 🚀 analizador_local.py                     # ⭐ EJECUTABLE: Análisis local
│   ├── 🚀 analizador_sistema.py                   # ⭐ EJECUTABLE: Análisis sistema
│   ├── 🚀 n8n_connector.py                        # ⭐ EJECUTABLE: Conector n8n
│   ├── clasificador.py                            # Clasificador básico
│   └── README_N8N.md
│
├── 🧪 TESTS/                                       # ⭐ TESTS PRINCIPALES
│   ├── 🚀 test_integracion_s1_s2_s3.py            # ⭐ EJECUTABLE: Test integración completa
│   └── 🚀 demo_aprendizaje_incremental.py         # ⭐ EJECUTABLE: Demo S2+S3 incremental
│
├── 🎨 analizador_textos/                           # Analizadores de texto
│   ├── __init__.py
│   └── procesador_fenomenologico.py               # Procesador alternativo
│
├── 📦 api/                                         # APIs REST
│   ├── __init__.py
│   ├── api_sistema_yo.py                          # 🚀 API principal (FastAPI)
│   └── api_generador_maximo.py                    # API generador máximo
│
├── 📁 modelos/                                     # Modelos ML (persistidos)
│   ├── clasificador_avanzado.h5                   # Modelo clasificador
│   └── tokenizador_cache/                         # Cache de tokenizador
│
├── 📁 estado/                                      # Estados persistidos
│   ├── estado_emergencia.pkl                      # Estado S2
│   └── estado_logica_pura.pkl                     # Estado S3
│
├── 📁 logs/                                        # Logs del sistema
│   └── sistema_yo.log
│
├── 📁 cache/                                       # Cache Redis local
│
├── 📁 entrada_bruta/                               # Datos de entrada
│
└── 📁 procesado/                                   # Datos procesados
    └── yamls/

```

---

## 🚀 EJECUTABLES PRINCIPALES

### 1. **Inicialización y Setup**

```bash
# Inicializar sistema completo
python scripts/init_system.py

# Deploy n8n workflows
powershell n8n_setup/deploy-n8n-complete.ps1

# Instalar n8n
powershell n8n_setup/install-n8n-complete.ps1
```

### 2. **Tests y Verificación**

```bash
# Test integración S1+S2+S3
python test_integracion_s1_s2_s3.py

# Demo aprendizaje incremental
python demo_aprendizaje_incremental.py

# Test APIs
python scripts/test_kimi.py
python scripts/test_llm_simple.py
python scripts/test_sin_credenciales.py
```

### 3. **Simulaciones y Demos**

```bash
# Simular Monje Gemelo (Capa 1)
python scripts/simular_monje.py

# Demo emergencia de entropía
python emergencia_concepto/simulacion_entropia.py
```

### 4. **Procesamiento**

```bash
# Procesamiento general
python scripts/procesamiento_general.py

# Análisis local
python scripts/analizador_local.py

# Análisis sistema completo
python scripts/analizador_sistema.py
```

### 5. **APIs y Servicios**

```bash
# API principal (FastAPI)
uvicorn api.api_sistema_yo:app --host 0.0.0.0 --port 8000

# Conector n8n
python scripts/n8n_connector.py
```

### 6. **Docker**

```bash
# Levantar stack completo
docker-compose -f docker-compose.gpu.yml up -d

# Ver logs
docker-compose -f docker-compose.gpu.yml logs -f

# Detener
docker-compose -f docker-compose.gpu.yml down
```

---

## 📊 FLUJO DE EJECUCIÓN TÍPICO

```
1. Setup inicial:
   docker-compose -f docker-compose.gpu.yml up -d
   
2. Verificar integración:
   python test_integracion_s1_s2_s3.py
   
3. Simular Monje (Capa 1):
   python scripts/simular_monje.py
   
4. Procesar con sistema completo:
   python scripts/procesamiento_general.py
   
5. Ver resultados en Neo4j:
   http://localhost:7474
```

---

## 🎯 PUNTOS DE ENTRADA PRINCIPALES

| Ejecutable | Propósito | Uso |
|------------|-----------|-----|
| `core/sistema_principal.py` | Sistema completo S1 | `from core.sistema_principal import SistemaYoEstructural` |
| `core/orquestador_capa2.py` | Orquestador S1+S2+S3 | `from core.orquestador_capa2 import OrquestadorCapa2` |
| `test_integracion_s1_s2_s3.py` | Test completo | `python test_integracion_s1_s2_s3.py` |
| `scripts/simular_monje.py` | Simular Capa 1 | `python scripts/simular_monje.py` |
| `api/api_sistema_yo.py` | API REST | `uvicorn api.api_sistema_yo:app` |

---

✅ **Árbol completo del sistema con todos los ejecutables identificados!** 🌳
