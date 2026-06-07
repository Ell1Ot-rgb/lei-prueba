# 🔌 CATÁLOGO COMPLETO DE CONEXIONES
## Sistema Terminado - Análisis Exhaustivo

---

## 📊 RESUMEN

| Categoría | Conexiones | Estado |
|:----------|:----------:|:------:|
| Neural Internas (#1-#4) | 4 | ✅ Implementadas |
| Neuromorfo Externo (TCP) | 3 | 📋 Diseñadas |
| Inter-Sistema (S1↔S2↔S3) | 8 | ✅/📋 Parcial |
| Servicios Externos | 6 | ✅ Implementadas |
| **TOTAL** | **21** | - |

---

## 🧠 CATEGORÍA 1: Interfaces Neuronales Internas

**Archivo**: `core/optimized/sistema_vivo_v100_completo.py`
**Documentación**: `core/optimized/DETALLE_SISTEMA_ORIGINAL_V100.md` (L115-123)

| ID | Nombre | Dirección | Formato | Ubicación | Estado |
|:---|:-------|:----------|:--------|:----------|:------:|
| **#1** | Embedding Output | S1 → Ext | `float32[64]` | `EmbedderCompact.embed()` L155 | ✅ |
| **#2** | Concept Injection | Ext → S2 | `(str, float)` | `MotorEmergencia.inyectar_concepto()` L371-384 | ✅ |
| **#3** | Temporal Prediction | ESN → Ext | `float32[64]` | `EchoStateNetwork.predict_train()` L500 | ✅ |
| **#4** | Complex Interaction | S2 ↔ S3 | `Axioma` | `S3LogicaPura.procesar_conceptos()` L445 | ✅ |

### Detalles

**CONEXIÓN #1**: Vector semántico de 64 dimensiones que representa el estado actual del procesamiento.
```python
# sistema_vivo_v100_completo.py L155
def embed(self, tokens: List[int]) -> np.ndarray:
    # Retorna float32[64] - Estado semántico actual
```

**CONEXIÓN #2**: Permite inyección externa de conceptos al motor de emergencia.
```python
# sistema_vivo_v100_completo.py L371-384
def inyectar_concepto(self, nombre: str, certeza: float = 1.0) -> int:
    """CONEXIÓN #2: Permite al Tejido Neuronal inyectar conceptos."""
```

**CONEXIÓN #3**: Predicción temporal del futuro estado + Exponente de Lyapunov.
```python
# sistema_vivo_v100_completo.py L508-527
def calcular_lyapunov(self) -> float:
    """Exponente de Lyapunov: λ>0 caos, λ≈0 borde, λ<0 orden"""
```

**CONEXIÓN #4**: Generación de axiomas de equivalencia/implicación entre conceptos.
```python
# sistema_vivo_v100_completo.py L445
def procesar_conceptos(self, conceptos, timestamp) -> Dict:
    # Genera axiomas relacionales entre conceptos
```

---

## 🌐 CATEGORÍA 2: Conexiones Neuromórficas Externas (Dual-PC)

**Documentación**: 
- `core/optimized/CONEXIONES_NEUROMORFICAS_EXTERNAS.md`
- `core/optimized/DISEÑO_RECEPTOR_OPTIMO.md`

### Arquitectura Física

```
PC1 (Organismo Vivo) ←──TCP/LAN──→ PC2 (Neuromorfo/FPGA)
```

| ID | Nombre | Dirección | Protocolo | Formato | Estado |
|:---|:-------|:----------|:----------|:--------|:------:|
| **E1** | Vector 256D | PC1→PC2 | TCP Socket | `neuro_input_packet_t` (261 bytes) | 📋 Diseño |
| **E2** | Respuesta Neural | PC2→PC1 | TCP Socket | `neuro_result_t` (20 bytes) | 📋 Diseño |
| **E3** | Feedback STDP | PC1→PC2 | TCP Socket | `float` (4 bytes) | 📋 Diseño |

### Estructuras de Datos (C)

```c
// E1: PC1 → PC2 (Entrada)
typedef struct {
    uint8_t vector[256];  // Mapa semántico-emocional
    uint32_t timestamp;   // Sincronización
    uint8_t mode;         // 0=Inferencia, 1=Aprendizaje
} neuro_input_packet_t;  // 261 bytes

// E2: PC2 → PC1 (Salida)
typedef struct {
    uint32_t patron_id;   // ID del atractor reconocido
    float similitud;      // Confianza (0.0-1.0)
    float novedad;        // Sorpresa (0.0-1.0)
    float energia;        // Activación del reservoir
    uint8_t categoria_pad; // Feedback emocional
} neuro_result_t;  // 20 bytes
```

### Mapa del Vector 256D

| Bytes | Fuente | Contenido |
|:------|:-------|:----------|
| 000-063 | EmbedderCompact | Embedding semántico 64D |
| 064-071 | GrundzugTracker | Rasgos fundamentales |
| 072-074 | EmotionEngine | PAD (Pleasure, Arousal, Dominance) |
| 075-127 | Fenomenología | Patrones detectados |
| 128-255 | vector256_compute | Hash/features C |

### Implementación Receptor (Python)

**Archivo**: `core/optimized/DISEÑO_RECEPTOR_OPTIMO.md` L48-138

```python
class NeuralReceiver:
    def _escuchar_intuicion(self):
        data = self.socket.recv(20)  # neuro_result_t
        patron_id, sim, nov, energia = struct.unpack('Ifff', data)
        
    def enviar_feedback(self, reward: float):
        packet = struct.pack('f', reward)
        self.socket.send(packet)
```

---

## 🔗 CATEGORÍA 3: Conexiones Inter-Sistema (S1↔S2↔S3)

**Documentación**: `docs/ARBOL_COMPLETO_SISTEMA.md` L572-590

### Diagrama de Flujo

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  SISTEMA 1  │◄──────►│  SISTEMA 2  │◄──────►│  SISTEMA 3  │
│  (Empírico) │        │ (Emergencia)│        │(Lóg. Pura)  │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘
```

| ID | Nombre | De → A | Función | Archivo |
|:---|:-------|:-------|:--------|:--------|
| **I1** | Grundzug→S2 | S1→S2 | Envía conceptos empíricos | `motor_emergencia.py` L45 |
| **I2** | ConceptoE→Grundzug | S2→S1 | Retorna concepto meta | `concepto_emergente.py` |
| **I3** | Grundzug→S3 | S1→S3 | Crea mundo desde conceptos | `mundo_hipotetico.py` L295 |
| **I4** | Instancia→S1 | S3→S1 | Fusiona con instancias | `instancia_abstracta.py` |
| **I5** | Patrón→Axiomas | S2→S3 | Convierte patrones a lógica | `patron_relacional.py` L214 |
| **I6** | Mundo→Sistemas | S3→S2 | Crea sistemas observables | `motor_hipotetico.py` L278 |
| **I7** | Apoptosis | S2 int | Muerte celular de conceptos | `sistema_vivo_v100_completo.py` L386 |
| **I8** | Curvatura Grafo | S2 int | Detección de puentes/clusters | `GrafoConceptual` L323 |

### Canales Redis

```python
# redis_connector.py L95-103
CANALES = [
    "monje/fenomenologia/*",    # Capa1 → Capa2
    "vectores_capa1",           # Vectores físicos
    "conceptos_emergentes",     # S2 → todos
    "instancias_abstractas",    # S3 → todos
    "dasein/feedback"           # Retorno a Capa1
]
```

---

## 🔧 CATEGORÍA 4: Conexiones Servicios Externos

### 4.1 Redis (Mensajería)

**Archivo**: `integraciones/redis_connector.py`

| Conexión | Puerto | Función |
|:---------|:-------|:--------|
| RedisMonjeConnector | 6379 | Pub/Sub con Capa 1 |
| Cache Redis | 6379 | Cache de embeddings |

```python
class RedisMonjeConnector:
    def conectar(self) -> bool:
        self.redis_client = redis.Redis(host, port, db)
    
    def escuchar_eventos(self) -> Generator:
        for mensaje in self.pubsub.listen():
            yield TraductorFenomenologico.traducir(mensaje)
```

### 4.2 Neo4j (Grafo de Conocimiento)

**Archivo**: `procesadores/extensiones_neo4j_lightrag.py` L45

| Conexión | Puerto | Protocolo |
|:---------|:-------|:----------|
| Neo4j Bolt | 7687 | Bolt |
| Neo4j HTTP | 7474 | REST |

**Schema de Nodos**:
- `:Ereignis`, `:Instancia`, `:Grundzug` (S1)
- `:ConceptoEmergente`, `:SistemaObservado` (S2)
- `:InstanciaAbstracta`, `:MundoHipotetico` (S3)

### 4.3 n8n (Webhooks)

**Archivo**: `integraciones/n8n_config.py`

| Endpoint | Método | Función |
|:---------|:-------|:--------|
| `/webhook/fenomenologia` | POST | Entrada principal |
| `/webhook/yo-estructural-v2` | POST | Procesamiento completo |
| `/webhook/yo-estructural-completo` | POST | Con Neo4j + Gemini |

```python
class N8nIntegrator:
    def enviar_datos_webhook(self, datos, origen="api"):
        requests.post(self.n8n_webhook_url, json=payload)
```

### 4.4 LightRAG (RAG API)

**Archivo**: `procesadores/extensiones_neo4j_lightrag.py` L270

| Endpoint | Puerto | Función |
|:---------|:-------|:--------|
| LightRAG API | 8000 | Búsqueda semántica |

### 4.5 Gemini (LLM)

| Endpoint | Función |
|:---------|:--------|
| `generativelanguage.googleapis.com/v1beta/...` | Generación de texto |

---

## 📋 ESTADO DE IMPLEMENTACIÓN

| Conexión | Archivo Código | Archivo Doc | Estado |
|:---------|:---------------|:------------|:------:|
| #1 Embedding | ✅ sistema_vivo | ✅ DETALLE | ✅ |
| #2 Injection | ✅ sistema_vivo | ✅ DETALLE | ✅ |
| #3 Lyapunov | ✅ sistema_vivo | ✅ DETALLE | ✅ |
| #4 Axiomas | ✅ sistema_vivo | ✅ DETALLE | ✅ |
| E1 Vector256 | ❌ | ✅ CONEXIONES | 📋 |
| E2 neuro_result | ❌ | ✅ DISEÑO | 📋 |
| E3 Feedback | ❌ | ✅ DISEÑO | 📋 |
| Redis Monje | ✅ redis_connector | - | ✅ |
| n8n Webhook | ✅ n8n_config | - | ✅ |
| Neo4j Bolt | ✅ extensiones | - | ✅ |

**Leyenda**: ✅ Implementado | 📋 Diseñado (no implementado) | ❌ No existe
