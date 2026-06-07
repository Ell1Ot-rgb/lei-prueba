# 🌳 ÁRBOL DE FLUJO RAMIFICADO - SISTEMA YO ESTRUCTURAL v3.0
## Diagrama Detallado de Ejecución y Flujo de Datos

---

## 📊 FLUJO PRINCIPAL DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INICIO DEL SISTEMA                               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  🚀 docker-compose.gpu.yml up -d          │
        │  (Levanta stack completo)                 │
        └───────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │   Neo4j     │ │   Redis     │ │  LightRAG   │
        │   :7687     │ │   :6379     │ │   :8002     │
        └─────────────┘ └─────────────┘ └─────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  🚀 Aplicación Principal                  │
        │  core/sistema_principal.py                │
        │  (Inicializa S1 + S2 + S3)                │
        └───────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │  Sistema 1  │ │  Sistema 2  │ │  Sistema 3  │
        │  Principal  │ │  Emergencia │ │  Lógica     │
        └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🔄 FLUJO DETALLADO POR CAPAS

### CAPA 1: MONJE GEMELO (Simulación Hardware)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CAPA 1: MONJE GEMELO                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  🚀 scripts/simular_monje.py              │
        │  (Simula hardware en Renode)              │
        │                                           │
        │  INPUT:                                   │
        │  └─ Archivo binario (cualquier formato)  │
        │                                           │
        │  PROCESA:                                 │
        │  ├─ Lee bytes completos                  │
        │  ├─ Calcula hash Blake3                  │
        │  ├─ Mide energía (µJ)                    │
        │  ├─ Mide entropía Shannon                │
        │  ├─ Cuenta ciclos CPU                    │
        │  └─ Cuenta instrucciones                 │
        │                                           │
        │  OUTPUT:                                  │
        │  └─ Vector Físico (JSON)                 │
        └───────────────────────────────────────────┘
                                │
                                ▼
                    {
                      "hash": "a7f3e2d9c1b4a8f3...",
                      "energia_uj": 3420,
                      "entropia": 2847563921,
                      "ciclos": 1250000,
                      "instrucciones": 45823,
                      "timestamp": "2025-11-25T23:40:00Z"
                    }
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  Redis Pub/Sub                            │
        │  Canal: monje/fenomenologia/*             │
        │                                           │
        │  integraciones/redis_connector.py         │
        │  └─ Publica evento                        │
        └───────────────────────────────────────────┘
                                │
                                ▼
                        [Pasa a Capa 2]
```

---

### CAPA 2: YO ESTRUCTURAL (Procesamiento Fenomenológico)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA 2: YO ESTRUCTURAL                           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  🚀 core/orquestador_capa2.py             │
        │  (Coordina S1 + S2 + S3)                  │
        │                                           │
        │  INPUT:                                   │
        │  └─ Vector Físico desde Redis             │
        │                                           │
        │  SUSCRIBE:                                │
        │  └─ redis.subscribe("monje/fenomenologia/*")│
        └───────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │  SISTEMA 1  │ │  SISTEMA 2  │ │  SISTEMA 3  │
        └─────────────┘ └─────────────┘ └─────────────┘
```

#### SISTEMA 1: PRINCIPAL

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SISTEMA 1: PRINCIPAL                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  core/sistema_principal.py                │
        │  (Sistema YO Estructural)                 │
        │                                           │
        │  INPUT:                                   │
        │  └─ Vector Físico                         │
        │                                           │
        │  COMPONENTES ACTIVOS:                     │
        │  ├─ Motor YO                              │
        │  ├─ Sistema de Gradientes                 │
        │  ├─ Procesadores                          │
        │  ├─ Sistema Emergencia (S2)               │
        │  └─ Sistema Lógica (S3)                   │
        └───────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │ Clasificador│ │ Tokenizador │ │  Procesador │
        │   Avanzado  │ │     GPU     │ │Fenomenológico│
        └─────────────┘ └─────────────┘ └─────────────┘
```

##### 1.1 CLASIFICADOR AVANZADO

```
        ┌───────────────────────────────────────────┐
        │  procesadores/clasificador_avanzado.py    │
        │  (Predice desde métricas físicas)         │
        │                                           │
        │  INPUT:                                   │
        │  └─ Vector Físico (hash, E, S, T, I)      │
        │                                           │
        │  PROCESA:                                 │
        │  ├─ Extrae 72 features:                  │
        │  │  ├─ 16D: Hash spectral (FFT 2D)       │
        │  │  ├─ 8D: Estadísticas hash             │
        │  │  ├─ 4D: Complejidad Kolmogorov        │
        │  │  ├─ 10D: Features espectrales         │
        │  │  ├─ 6D: Ratios (E/T, I/T, etc.)       │
        │  │  └─ 28D: Derivadas y combinaciones    │
        │  │                                        │
        │  ├─ Red Neuronal:                        │
        │  │  └─ 72 → 128 → 64 → Attention → 32 → N│
        │  │                                        │
        │  └─ Softmax → Probabilidades             │
        │                                           │
        │  OUTPUT:                                  │
        │  └─ Predicción {                          │
        │       "clase": "melancolía",              │
        │       "certeza": 0.72,                    │
        │       "probabilidades": {                 │
        │         "melancolía": 0.72,               │
        │         "alegría": 0.15,                  │
        │         "neutro": 0.08,                   │
        │         ...                               │
        │       }                                   │
        │     }                                     │
        └───────────────────────────────────────────┘
                                │
                                ▼
                    [Guarda en Neo4j]
```

##### 1.2 TOKENIZADOR GPU

```
        ┌───────────────────────────────────────────┐
        │  procesadores/tokenizador_fenomenologico_gpu.py│
        │  (Análisis fenomenológico profundo)       │
        │                                           │
        │  INPUT:                                   │
        │  └─ Texto original (si disponible)        │
        │     └─ Busca por hash en BD               │
        │                                           │
        │  PROCESA (GPU):                           │
        │  ├─ REMForge Ultra/Lite                   │
        │  ├─ Batch processing (8 textos paralelo)  │
        │  ├─ Cache Redis (TTL 24h)                 │
        │  └─ Mixed Precision (AMP)                 │
        │                                           │
        │  ANALIZA:                                 │
        │  ├─ Noetic Layer:                         │
        │  │  ├─ Modo intencional                   │
        │  │  ├─ Directedness                       │
        │  │  └─ Ego involvement                    │
        │  │                                        │
        │  ├─ Sensorial Layer:                      │
        │  │  ├─ Modalidad dominante                │
        │  │  ├─ Valencia afectiva                  │
        │  │  └─ Arousal                            │
        │  │                                        │
        │  ├─ Phenomenal Core:                      │
        │  │  ├─ Qualia signature                   │
        │  │  ├─ Invariantes                        │
        │  │  └─ Eidetic reductions                 │
        │  │                                        │
        │  └─ Semantic Contamination:               │
        │     ├─ Interferencia                      │
        │     └─ Lexical anchors                    │
        │                                           │
        │  OUTPUT:                                  │
        │  └─ PhenomenalREM-Ultra JSON Schema       │
        └───────────────────────────────────────────┘
                                │
                                ▼
                    {
                      "header": {...},
                      "noetic_layer": {
                        "intentional_mode": "perception",
                        "directedness": "objeto rojo",
                        "ego_involvement": 0.85
                      },
                      "sensorial_layer": {
                        "modality_distribution": {
                          "visual": 0.72,
                          "auditory": 0.28
                        },
                        "affective_valence": 0.62,
                        "affective_arousal": 0.45
                      },
                      "phenomenal_core": {
                        "qualia_signature": {
                          "qualia_type": "visual_chromatic",
                          "intensity_profile": [0.92, ...],
                          "saturation": 0.78
                        }
                      },
                      "semantic_contamination": {
                        "contamination_strength": 0.42,
                        "lexical_anchors": [...]
                      }
                    }
                                │
                                ▼
                        [Genera Grundzugs]
```

##### 1.3 GENERACIÓN DE GRUNDZUGS

```
        ┌───────────────────────────────────────────┐
        │  Motor YO + Procesadores                  │
        │  (Sintetiza información)                  │
        │                                           │
        │  INPUT:                                   │
        │  ├─ Predicción Clasificador               │
        │  ├─ Análisis Tokenizador                  │
        │  └─ Vector Físico original                │
        │                                           │
        │  GENERA:                                  │
        │  └─ Grundzugs (Conceptos Formales)        │
        │                                           │
        │  OUTPUT:                                  │
        │  └─ [                                     │
        │       {                                   │
        │         "nombre": "concepto_melancolico_visual",│
        │         "certeza": 0.87,                  │
        │         "nivel": 1,                       │
        │         "instancias_count": 1,            │
        │         "qualia_dominante": "visual",     │
        │         "valencia_afectiva": 0.25,        │
        │         "origen_hash": "a7f3e2d9...",     │
        │         "timestamp": "2025-11-25T..."     │
        │       },                                  │
        │       ...                                 │
        │     ]                                     │
        └───────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │   Neo4j     │ │  Sistema 2  │ │  Sistema 3  │
        │  (Persiste) │ │ (Emergencia)│ │  (Lógica)   │
        └─────────────┘ └─────────────┘ └─────────────┘
```

#### SISTEMA 2: EMERGENCIA DE CONCEPTOS

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SISTEMA 2: EMERGENCIA DE CONCEPTOS               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  emergencia_concepto/motor_emergencia.py  │
        │  (Aprendizaje incremental)                │
        │                                           │
        │  INPUT:                                   │
        │  └─ Grundzugs desde S1                    │
        │                                           │
        │  PROCESA:                                 │
        │  ├─ ciclo_incremental(grundzugs)          │
        │  │  ├─ Ingesta desde S1                   │
        │  │  ├─ Ejecuta experimentos               │
        │  │  ├─ Detecta patrones (DBSCAN)          │
        │  │  ├─ Emerge/refina conceptos            │
        │  │  └─ Verifica convergencia              │
        │  │                                        │
        │  ├─ Estado persistente:                   │
        │  │  └─ estado_emergencia.pkl              │
        │  │                                        │
        │  └─ Convergencia:                         │
        │     └─ Certeza > 0.90 (3+ iteraciones)    │
        │                                           │
        │  OUTPUT:                                  │
        │  └─ {                                     │
        │       "patron_certeza": 0.92,             │
        │       "convergencia": true,               │
        │       "conceptos": [                      │
        │         {                                 │
        │           "nombre": "concepto_emergido_1",│
        │           "certeza": 0.94,                │
        │           "leyes_descubiertas": [...],    │
        │           "predicciones": [...]           │
        │         }                                 │
        │       ],                                  │
        │       "iteracion": 15                     │
        │     }                                     │
        └───────────────────────────────────────────┘
                                │
                                ▼
                    [Guarda estado + Neo4j]
```

##### 2.1 DEMO EMERGENCIA

```
        ┌───────────────────────────────────────────┐
        │  🚀 emergencia_concepto/simulacion_entropia.py│
        │  (Demo: Emergencia de "Entropía")         │
        │                                           │
        │  FLUJO:                                   │
        │  ├─ Crea 5 sistemas observados            │
        │  ├─ Ejecuta 4 experimentos:               │
        │  │  ├─ Predictibilidad                    │
        │  │  ├─ Reversibilidad                     │
        │  │  ├─ Diversidad                         │
        │  │  └─ Tendencia temporal                 │
        │  │                                        │
        │  ├─ Detecta patrones con FCA              │
        │  ├─ Emerge concepto "entropía"            │
        │  └─ Descubre Segunda Ley                  │
        │                                           │
        │  OUTPUT:                                  │
        │  └─ Concepto emergido con certeza 0.89    │
        └───────────────────────────────────────────┘
```

#### SISTEMA 3: LÓGICA PURA

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SISTEMA 3: LÓGICA PURA                         │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  logica_pura/motor_hipotetico.py          │
        │  (Mundos hipotéticos + Axiomas)           │
        │                                           │
        │  INPUT:                                   │
        │  ├─ Grundzugs desde S1                    │
        │  └─ Observaciones empíricas               │
        │                                           │
        │  PROCESA:                                 │
        │  ├─ ciclo_incremental(mundo, grundzugs, obs)│
        │  │  ├─ Expande mundo desde grundzugs      │
        │  │  ├─ Aprende axiomas desde observaciones│
        │  │  ├─ Infiere relaciones                 │
        │  │  └─ Valida con S1                      │
        │  │                                        │
        │  ├─ Estado persistente:                   │
        │  │  └─ estado_logica_pura.pkl             │
        │  │                                        │
        │  └─ Validación cruzada:                   │
        │     └─ Compara lógico vs empírico         │
        │                                           │
        │  OUTPUT:                                  │
        │  └─ {                                     │
        │       "objetos_totales": 47,              │
        │       "axiomas_totales": 23,              │
        │       "axiomas_nuevos_aprendidos": 3,     │
        │       "validacion": {                     │
        │         "certeza": 0.88,                  │
        │         "inconsistencias": []             │
        │       }                                   │
        │     }                                     │
        └───────────────────────────────────────────┘
                                │
                                ▼
                    [Guarda estado + Neo4j]
```

---

### VALIDACIÓN CRUZADA S2 ↔ S3

```
        ┌───────────────────────────────────────────┐
        │  core/orquestador_capa2.py                │
        │  _validar_s2_vs_s3()                      │
        │                                           │
        │  COMPARA:                                 │
        │  ├─ Conceptos emergidos (S2)              │
        │  └─ Axiomas lógicos (S3)                  │
        │                                           │
        │  CALCULA:                                 │
        │  └─ Consistencia = axiomas / conceptos    │
        │                                           │
        │  OUTPUT:                                  │
        │  └─ {                                     │
        │       "consistencia": 0.87,               │
        │       "conceptos_s2": 15,                 │
        │       "axiomas_s3": 23,                   │
        │       "validacion_exitosa": true          │
        │     }                                     │
        └───────────────────────────────────────────┘
```

---

## 💾 PERSISTENCIA DE DATOS

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PERSISTENCIA                                │
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │   Neo4j     │ │    Redis    │ │   Pickle    │
        │   :7687     │ │    :6379    │ │   Files     │
        └─────────────┘ └─────────────┘ └─────────────┘
                │               │               │
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │ Grundzugs   │ │ Cache REM   │ │ Estado S2   │
        │ Conceptos   │ │ Pub/Sub     │ │ Estado S3   │
        │ Instancias  │ │ Eventos     │ │             │
        │ Relaciones  │ │             │ │             │
        └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🧪 TESTING Y VERIFICACIÓN

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TESTING Y VERIFICACIÓN                           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  🚀 test_integracion_s1_s2_s3.py          │
        │  (Test completo de integración)           │
        │                                           │
        │  VERIFICA:                                │
        │  ├─ [1/5] Imports correctos               │
        │  ├─ [2/5] Sistema inicializa              │
        │  ├─ [3/5] S2 disponible + ciclo_incremental│
        │  ├─ [4/5] S3 disponible + ciclo_incremental│
        │  └─ [5/5] Test funcional con datos        │
        │                                           │
        │  OUTPUT:                                  │
        │  └─ ✅ INTEGRACIÓN VERIFICADA             │
        └───────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  🚀 demo_aprendizaje_incremental.py       │
        │  (Demo S2 + S3 con 4 oleadas)             │
        │                                           │
        │  FLUJO:                                   │
        │  ├─ Oleada 1: 3 Grundzugs iniciales       │
        │  ├─ Oleada 2: +2 Grundzugs (refina)       │
        │  ├─ Oleada 3: +3 Grundzugs (expande)      │
        │  └─ Oleada 4: +2 Grundzugs (converge)     │
        │                                           │
        │  MUESTRA:                                 │
        │  ├─ Evolución de certeza S2               │
        │  ├─ Crecimiento de axiomas S3             │
        │  └─ Convergencia progresiva               │
        └───────────────────────────────────────────┘
```

---

## 🌐 APIs Y SERVICIOS

```
┌─────────────────────────────────────────────────────────────────────┐
│                         APIs REST                                   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  🚀 api/api_sistema_yo.py                 │
        │  uvicorn api.api_sistema_yo:app           │
        │  (FastAPI - Puerto 8000)                  │
        │                                           │
        │  ENDPOINTS:                               │
        │  ├─ GET  /health                          │
        │  ├─ POST /procesar                        │
        │  ├─ POST /clasificar                      │
        │  ├─ POST /tokenizar                       │
        │  ├─ GET  /grundzugs                       │
        │  ├─ GET  /conceptos                       │
        │  └─ GET  /mundos                          │
        │                                           │
        │  DOCS:                                    │
        │  └─ http://localhost:8000/docs            │
        └───────────────────────────────────────────┘
```

---

## 📊 RESUMEN DE FLUJO COMPLETO

```
ARCHIVO ORIGINAL
        │
        ▼
[Monje Gemelo] → Vector Físico → Redis
        │
        ▼
[Orquestador Capa 2]
        │
        ├─→ [S1: Principal]
        │   ├─→ Clasificador → Predicción
        │   ├─→ Tokenizador → Análisis fenomenológico
        │   └─→ Genera Grundzugs
        │
        ├─→ [S2: Emergencia]
        │   └─→ ciclo_incremental() → Conceptos emergidos
        │
        └─→ [S3: Lógica]
            └─→ ciclo_incremental() → Axiomas + Mundos
        │
        ▼
[Validación Cruzada S2 ↔ S3]
        │
        ▼
[Persistencia: Neo4j + Redis + Pickle]
        │
        ▼
CONOCIMIENTO CONSOLIDADO
```

---

✅ **Árbol de flujo ramificado completo con todos los ejecutables y su interconexión!** 🌳
