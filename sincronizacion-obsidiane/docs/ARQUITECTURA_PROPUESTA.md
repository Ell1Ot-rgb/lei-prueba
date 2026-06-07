# 🏗️ Arquitectura Sistema Terminado - Diagrama Detallado

## 1. Vista General (Hexagonal/Onion)

```mermaid
graph TB
    subgraph EXTERNAL["🌐 MUNDO EXTERNO"]
        PC2["PC2 Neuromorfo<br/>(FPGA/TCP)"]
        REDIS["Redis<br/>(Mensajería)"]
        NEO4J["Neo4j<br/>(Grafos)"]
        N8N["n8n<br/>(Webhooks)"]
        LRAG["LightRAG<br/>(RAG)"]
    end
    
    subgraph ADAPTERS["📡 CAPA ADAPTADORES"]
        direction TB
        subgraph INBOUND["Entrada"]
            TCP_RX["tcp_neuromorphic.py"]
            REDIS_RX["redis_listener.py"]
            WH_RX["webhook_handler.py"]
        end
        subgraph OUTBOUND["Salida"]
            NEO4J_TX["neo4j_repository.py"]
            REDIS_TX["redis_publisher.py"]
            LRAG_TX["lightrag_client.py"]
        end
    end
    
    subgraph INTERFACES["🔌 CAPA INTERFACES"]
        PORTS["neural_ports.py<br/>(#1-#4)"]
        FACADE["system_facade.py"]
        HEALTH["health_monitor.py"]
    end
    
    subgraph CORE["🧠 NÚCLEO"]
        subgraph ENGINES["Motores"]
            S1["S1: Fenomenología"]
            S2["S2: Emergencia"]
            S3["S3: Lógica"]
        end
        subgraph CHAOS["Caos"]
            AUTO["Autómatas"]
            REG["Regulador"]
        end
        subgraph DOMAIN["Dominio"]
            ENT["Entidades"]
        end
    end
    
    PC2 <-->|neuro_result_t| TCP_RX
    REDIS <-->|Pub/Sub| REDIS_RX
    N8N -->|POST| WH_RX
    
    NEO4J_TX -->|Bolt| NEO4J
    REDIS_TX -->|Pub| REDIS
    LRAG_TX -->|HTTP| LRAG
    
    TCP_RX --> PORTS
    REDIS_RX --> FACADE
    WH_RX --> FACADE
    
    PORTS --> S1
    PORTS --> S2
    FACADE --> S1
    FACADE --> S2
    FACADE --> S3
    
    S1 <--> S2
    S2 <--> S3
    S2 --> AUTO
    AUTO --> REG
    
    S1 --> ENT
    S2 --> ENT
    S3 --> ENT
    
    FACADE --> NEO4J_TX
    FACADE --> REDIS_TX
    FACADE --> LRAG_TX
    
    HEALTH --> PORTS
    HEALTH --> AUTO
```

---

## 2. Flujo de Datos Detallado

```mermaid
sequenceDiagram
    participant EXT as 🌍 Entrada
    participant WH as Webhook
    participant S1 as S1 Fenomenología
    participant S2 as S2 Emergencia
    participant S3 as S3 Lógica
    participant AUTO as Autómata
    participant NEO as Neo4j
    
    EXT->>WH: POST /webhook/yo-estructural
    WH->>S1: procesar(texto)
    
    Note over S1: TokenizerLite<br/>EmbedderCompact<br/>ClasificadorYO
    
    S1->>S1: embed() → float32[64]
    S1-->>EXT: CONEXIÓN #1 (opcional)
    
    S1->>S2: grundzugs[]
    
    Note over S2: FCA MinHash<br/>GrafoConceptual<br/>Forman Curvature
    
    S2->>S2: emergir_conceptos()
    
    alt Novedad > 0.3
        S2->>S3: nuevo_concepto
        Note over S3: MotorAxiomas<br/>Punto Fijo
        S3->>S3: validar_coherencia()
        S3-->>S2: Axioma
    end
    
    S2->>AUTO: estado_sistema
    AUTO->>AUTO: evolucionar(50 pasos)
    AUTO-->>S2: métricas_borde_caos
    
    alt λ > 0.1
        AUTO-->>S2: ajustes{lr, decay, noise}
    end
    
    S2->>NEO: MERGE (:Concepto)
    S3->>NEO: MERGE (:Axioma)
    
    S2-->>WH: respuesta_json
    WH-->>EXT: 200 OK
```

---

## 3. Estructura de Carpetas Propuesta

```
sistema_terminado/
│
├── 📁 core/                          # SIN DEPENDENCIAS EXTERNAS
│   │
│   ├── 📁 domain/                    # Entidades del dominio
│   │   ├── __init__.py
│   │   ├── concepto.py               # Concepto, ConceptoEmergente
│   │   ├── axioma.py                 # Axioma, Proposición
│   │   ├── grundzug.py               # Grundzug, TipoYO
│   │   ├── instancia.py              # Instancia, InstanciaAbstracta
│   │   └── configuracion.py          # ConfiguracionSistema
│   │
│   ├── 📁 engines/                   # Motores de procesamiento
│   │   │
│   │   ├── 📁 s1_fenomenologia/      # CAPA EMPÍRICA
│   │   │   ├── __init__.py
│   │   │   ├── tokenizer.py          # TokenizerLite
│   │   │   ├── embedder.py           # EmbedderCompact
│   │   │   ├── clasificador.py       # ClasificadorYO (SGD)
│   │   │   ├── grundzug_tracker.py   # Count-Min Sketch
│   │   │   ├── emotion_engine.py     # PAD Model
│   │   │   └── esn.py                # EchoStateNetwork
│   │   │
│   │   ├── 📁 s2_emergencia/         # CAPA EMERGENCIA
│   │   │   ├── __init__.py
│   │   │   ├── motor_emergencia.py   # Orquestador S2
│   │   │   ├── fca_processor.py      # FCA + MinHash + LSH
│   │   │   ├── grafo_conceptual.py   # Grafos + Curvatura
│   │   │   ├── mdce_manager.py       # Memory-Driven CE
│   │   │   └── apoptosis.py          # Muerte celular
│   │   │
│   │   └── 📁 s3_logica/             # CAPA LÓGICA
│   │       ├── __init__.py
│   │       ├── motor_axiomas.py      # Forward Chaining
│   │       ├── mundo_hipotetico.py   # Universo cerrado
│   │       └── logica_pura.py        # S3LogicaPura
│   │
│   └── 📁 chaos/                     # BORDE DEL CAOS
│       ├── __init__.py
│       ├── automata_1d.py            # Regla 110 + Langton
│       ├── automata_2d.py            # Game of Life + Gliders
│       ├── regulador.py              # Feedback cerrado
│       └── metricas.py               # Lyapunov, Entropía
│
├── 📁 adapters/                      # CONEXIONES EXTERNAS
│   │
│   ├── 📁 inbound/                   # Entrada al sistema
│   │   ├── __init__.py
│   │   ├── tcp_neuromorphic.py       # NeuralReceiver (PC2)
│   │   ├── redis_listener.py         # RedisMonjeConnector
│   │   └── webhook_handler.py        # HTTP entrada
│   │
│   └── 📁 outbound/                  # Salida del sistema
│       ├── __init__.py
│       ├── neo4j_repository.py       # Persistencia grafos
│       ├── redis_publisher.py        # Pub eventos
│       ├── lightrag_client.py        # RAG API
│       └── n8n_integrator.py         # Webhook salida
│
├── 📁 interfaces/                    # CONTRATOS PÚBLICOS
│   ├── __init__.py
│   ├── neural_ports.py               # Conexiones #1-#4
│   ├── system_facade.py              # Orquestador maestro
│   └── health_monitor.py             # HealthManager
│
├── 📁 config/
│   ├── settings.py                   # Pydantic Settings
│   ├── logging_config.py
│   └── .env.example
│
├── 📁 tests/
│   ├── test_s1.py
│   ├── test_s2.py
│   ├── test_s3.py
│   └── test_integration.py
│
├── 📁 docs/
│   ├── CATALOGO_CONEXIONES.md
│   ├── ARQUITECTURA.md
│   └── API.md
│
├── main.py                           # Punto de entrada
├── requirements.txt
└── README.md
```

---

## 4. Mapa de Conexiones por Capa

```mermaid
graph LR
    subgraph CAPA1["📊 CAPA 1: Física"]
        MONJE["Monje Gemelo<br/>(Binarios)"]
    end
    
    subgraph CAPA2["🧠 CAPA 2: Cognitiva"]
        subgraph S1["S1"]
            TOK["Tokenizer"]
            EMB["Embedder"]
            CLS["Clasificador"]
            ESN["ESN"]
        end
        subgraph S2["S2"]
            FCA["FCA"]
            GRAF["Grafo"]
            APOP["Apoptosis"]
        end
        subgraph S3["S3"]
            AXI["Axiomas"]
            MUN["Mundos"]
        end
    end
    
    subgraph CAPA3["🔮 CAPA 3: Neuromorfa"]
        PC2["FPGA/Neural"]
    end
    
    MONJE -->|Redis: vectores_capa1| S1
    
    TOK --> EMB
    EMB -->|#1| PC2
    CLS --> S2
    ESN -->|#3| PC2
    
    S1 -->|Grundzugs| S2
    S2 -->|Conceptos| S3
    S3 -->|Axiomas| S2
    
    PC2 -->|#2: inyectar| S2
    PC2 -->|neuro_result| S2
    
    FCA --> GRAF
    GRAF --> APOP
    
    S2 -.->|feedback| PC2
```

---

## 5. Conexiones Numeradas

| # | Nombre | Origen | Destino | Formato | Archivo |
|:--|:-------|:-------|:--------|:--------|:--------|
| **#1** | Embedding Out | S1.Embedder | Externo/PC2 | `float32[64]` | `embedder.py` |
| **#2** | Concept Inject | Externo/PC2 | S2.Motor | `(str, float)` | `motor_emergencia.py` |
| **#3** | Temporal Pred | S1.ESN | Externo/PC2 | `float32[64]` | `esn.py` |
| **#4** | Axioma Bridge | S2 | S3 | `Axioma` | `logica_pura.py` |
| **R1** | Redis In | Capa1 | S1 | JSON | `redis_listener.py` |
| **R2** | Redis Out | S2 | Capa1 | JSON | `redis_publisher.py` |
| **N1** | Neo4j Write | S2/S3 | DB | Cypher | `neo4j_repository.py` |
| **T1** | TCP Neuro | PC2 | S2 | `neuro_result_t` | `tcp_neuromorphic.py` |
| **W1** | Webhook In | n8n | Facade | HTTP POST | `webhook_handler.py` |
| **L1** | LightRAG | Facade | API | HTTP | `lightrag_client.py` |

---

## 6. Dependencias entre Módulos

```mermaid
graph TD
    subgraph "Sin Dependencias Externas"
        DOM[domain/]
        S1E[engines/s1/]
        S2E[engines/s2/]
        S3E[engines/s3/]
        CHAOS[chaos/]
    end
    
    subgraph "Con Dependencias"
        INBOUND[adapters/inbound/]
        OUTBOUND[adapters/outbound/]
        IFACE[interfaces/]
    end
    
    DOM --> S1E
    DOM --> S2E
    DOM --> S3E
    
    S1E --> S2E
    S2E --> S3E
    S2E --> CHAOS
    
    S1E --> IFACE
    S2E --> IFACE
    S3E --> IFACE
    CHAOS --> IFACE
    
    INBOUND --> IFACE
    IFACE --> OUTBOUND
    
    style DOM fill:#90EE90
    style S1E fill:#90EE90
    style S2E fill:#90EE90
    style S3E fill:#90EE90
    style CHAOS fill:#90EE90
    style INBOUND fill:#FFB6C1
    style OUTBOUND fill:#FFB6C1
    style IFACE fill:#87CEEB
```

**Verde** = Core puro (testeable sin mocks)  
**Rosa** = Adapters (requieren mocks)  
**Azul** = Interfaces (puente)
