# 📊 Análisis de Bases de Datos e Interacción IA-Tensores

## Resumen Ejecutivo

Este documento analiza:
1. **Bases de datos externas** del sistema
2. **Bases de datos locales** de la PC
3. **Conexión n8n** para automatización
4. **Investigación: IA interactuando directamente con tensores**

---

## PARTE 1: BASES DE DATOS EXTERNAS

### 1.1 Neo4j (Grafo)

**Ubicación**: `procesadores/extensiones_neo4j_lightrag.py`

```python
class ExtensionNeo4j:
    def __init__(self, bolt_url: str, usuario: str, password: str):
        """
        Conexión: bolt://192.168.1.37:7687
        Usuario: neo4j
        Password: fenomenologia2024
        """
```

| Aspecto | Detalle |
|:--------|:--------|
| **Protocolo** | Bolt (Neo4j nativo) |
| **Puerto** | 7687 |
| **Ubicación** | PC2 (192.168.1.37) |
| **Despliegue** | Docker |
| **Uso** | Persistencia de grafos conceptuales |

**Operaciones soportadas**:
- `guardar_ruta()`: Nodos Concepto → DefinicionRuta
- `obtener_maximos_relacionales()`: Consulta máximos
- `calcular_comunidades_maximos()`: GDS Louvain
- `analizar_convergencia_temporal()`: Historial

**Schema Cypher**:
```cypher
(:Concepto {nombre: "SOPORTE"})
  ├─ [:RUTA_FISICA] → (:DefinicionRuta {texto: "..."})
  ├─ [:RUTA_ERGONOMICA] → (:DefinicionRuta {texto: "..."})
  └─ [:ES_MAXIMO] → (:MaximoRelacional {certeza: 0.99})
```

---

### 1.2 LightRAG (Semántica)

**Ubicación**: `procesadores/extensiones_neo4j_lightrag.py`

```python
class ExtensionLightRAG:
    def __init__(self, api_url: str = "http://192.168.1.37:8000"):
```

| Aspecto | Detalle |
|:--------|:--------|
| **Protocolo** | HTTP REST |
| **Puerto** | 8000 |
| **Ubicación** | PC2 (192.168.1.37) |
| **Despliegue** | Docker |
| **Uso** | Refinamiento semántico |

**Endpoints**:
- `GET /health` - Health check
- `POST /refinar` - Refinar definición
- `POST /validar_convergencia` - Validar rutas

**Payload ejemplo**:
```json
{
  "texto": "SOPORTE es material que sostiene",
  "contexto": "Perspectiva física",
  "nivel_refinamiento": "profundo"
}
```

---

### 1.3 Redis (Cache + Pub/Sub)

**Ubicación**: `integraciones/redis_connector.py`

```python
class RedisMonjeConnector:
    def __init__(self, host: str = "localhost", port: int = 6379):
```

| Aspecto | Detalle |
|:--------|:--------|
| **Protocolo** | Redis nativo |
| **Puerto** | 6379 |
| **Ubicación** | Configurable (localhost o remoto) |
| **Uso** | Comunicación Capa 1 ↔ Capa 2 |

**Canales Pub/Sub**:
- `monje/fenomenologia/*` - Eventos de Capa 1 (Monje Gemelo)
- `dasein/feedback` - Feedback a Capa 1

**Estructura VectorFisico**:
```python
@dataclass
class VectorFisico:
    tiempo: int           # Ciclos de CPU
    instrucciones: int    # Instrucciones ejecutadas
    energia: int          # Microjoules
    entropia: int         # Entropía del hash
    concepto: str         # TÉCNICO, POÉTICO, NUMÉRICO, CAOS
    confianza: float      # 0.0 - 1.0
    hash_id: str          # Hash del evento
    timestamp: float      # Epoch
```

---

## PARTE 2: BASE DE DATOS LOCAL

### 2.1 Sin SQLite Nativo

El sistema actual **NO usa SQLite** directamente en el código principal. Las búsquedas por `sqlite` no encontraron resultados.

### 2.2 Almacenamiento Local Actual

| Tipo | Formato | Uso |
|:-----|:--------|:----|
| **Cache en memoria** | Dict/deque | TensorHistorial, GrundzugTracker |
| **Embeddings** | NumPy arrays | Persistencia opcional .npy |
| **Configuración** | YAML | `config_4gb_optimizado.yaml` |
| **Logs** | Python logging | Consola + archivo |

### 2.3 Recomendación: SQLite Local

Para optimizar S4, recomiendo agregar SQLite local:

```python
# Propuesta: almacenamiento local ligero
class S4LocalStorage:
    """
    SQLite para persistencia local de S4.
    
    TABLAS:
    - tensores: Historial de TensorFusionado
    - predicciones: Cache de predicciones
    - patrones_spa: Patrones detectados
    """
    
    def __init__(self, db_path: str = "s4_local.db"):
        self.conn = sqlite3.connect(db_path)
        self._crear_tablas()
    
    def guardar_tensor(self, tensor: TensorFusionado):
        """Guarda tensor fusionado."""
        self.conn.execute("""
            INSERT INTO tensores (
                timestamp, embedding, esn_state, pad, grundzug, lyapunov
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tensor.timestamp,
            tensor.embedding.tobytes(),
            tensor.esn_state.tobytes(),
            tensor.pad_emotions.tobytes(),
            tensor.grundzug_freq.tobytes(),
            tensor.lyapunov_features.tobytes()
        ))
        self.conn.commit()
```

---

## PARTE 3: CONEXIÓN n8n

### 3.1 Integrador n8n

**Ubicación**: `integraciones/n8n_config.py`

```python
class N8nIntegrator:
    def __init__(self):
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 
            'http://localhost:5678/webhook/fenomenologia')
        self.n8n_api_key = os.getenv('N8N_API_KEY', '')
        self.n8n_base_url = os.getenv('N8N_BASE_URL', 
            'http://localhost:5678')
```

| Aspecto | Detalle |
|:--------|:--------|
| **Protocolo** | HTTP REST |
| **Puerto** | 5678 |
| **Autenticación** | X-N8N-API-KEY header |
| **Ubicación** | Local o Render |

### 3.2 Métodos Disponibles

| Método | Endpoint | Uso |
|:-------|:---------|:----|
| `enviar_datos_webhook` | POST /webhook/fenomenologia | Trigger workflow |
| `obtener_workflows` | GET /api/v1/workflows | Listar workflows |
| `activar_workflow` | POST /api/v1/workflows/{id}/activate | Activar |
| `ejecutar_workflow` | POST /api/v1/workflows/{id}/execute | Ejecutar |

### 3.3 Payload de Integración

```python
payload = {
    "datos": datos,              # Datos procesados
    "origen": "YO_estructural",  # Identificador
    "timestamp": datetime.now().isoformat(),
    "sistema": "YO_estructural"
}
```

### 3.4 Variables de Entorno

```env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/fenomenologia
N8N_API_KEY=tu_api_key
N8N_BASE_URL=http://localhost:5678
```

---

## PARTE 4: IA INTERACTUANDO DIRECTAMENTE CON TENSORES

### 4.1 Estado del Arte

La investigación muestra varias aproximaciones para que una IA interactúe directamente con tensores:

#### A. Inferencia desde Cero (C/CUDA)

| Proyecto | Descripción |
|:---------|:------------|
| **llama.cpp** | LLM en C++ puro, CUDA kernels personalizados |
| **llm.c** | GPT-2/3 en C/CUDA puro (Andrej Karpathy) |
| **Fast LLM Inference** | Optimización manual de operaciones tensoriales |

**Cómo funciona**:
```cpp
// Acceso directo a tensor
float* Q = query_tensor.data;
float* K = key_tensor.data;
float* V = value_tensor.data;

// Operación de atención manual
for (int i = 0; i < seq_len; i++) {
    for (int j = 0; j < head_dim; j++) {
        // Manipulación directa de memoria
        output[i][j] = softmax(Q[i] @ K.T)[j] * V[j];
    }
}
```

#### B. Tensor Networks para LLMs

| Técnica | Aplicación |
|:--------|:-----------|
| **Tensor Network Compression** | Comprimir LLMs hasta 250× |
| **Tensor Train (TT)** | Descomponer pesos de atención |
| **Tensor Ring (TR)** | Representación compacta de KV-cache |

**Ejemplo TensorLLM**:
```python
# Comprimir atención multi-cabeza
W_attention = TensorNetwork(
    shape=(n_heads, d_model, d_model),
    rank=10  # Bajo rango para eficiencia
)

# La IA accede a los tensores comprimidos directamente
output = W_attention.contract_with(input_tensor)
```

#### C. Knowledge Editing

| Método | Descripción |
|:-------|:------------|
| **ROME** | Rank-One Model Editing |
| **MEMIT** | Mass-Editing Memory |
| **In-Context Editing** | Modificación en tiempo de inferencia |

**Modificación directa de tensores**:
```python
# Localizar neurona responsable de conocimiento
neuron_idx = locate_knowledge_neuron(model, "Paris is capital of France")

# Modificar tensor de pesos directamente
model.layers[layer_idx].mlp.weights[neuron_idx] = new_value
```

### 4.2 Propuesta: Interfaz IA-Tensor para S4

```python
class InterfazIATensor:
    """
    Permite a una IA (LLM) interactuar directamente con los tensores de S4.
    
    CAPACIDADES:
    1. Leer estado tensorial actual
    2. Modificar tensores en tiempo real
    3. Consultar predicciones
    4. Ajustar hiperparámetros
    """
    
    def __init__(self, motor_s4: MotorS4):
        self.motor = motor_s4
    
    # ===== LECTURA =====
    
    def leer_estado_tensor(self) -> Dict[str, np.ndarray]:
        """
        Retorna el estado tensorial actual para que la IA lo analice.
        """
        if len(self.motor.historial) == 0:
            return {}
        
        ultimo = self.motor.historial.buffer[-1]
        return {
            "embedding": ultimo.embedding,
            "esn_state": ultimo.esn_state,
            "pad_emotions": ultimo.pad_emotions,
            "grundzug_freq": ultimo.grundzug_freq,
            "lyapunov": ultimo.lyapunov_features,
            "flat": ultimo.to_flat()
        }
    
    def leer_modos_dinamicos(self) -> Dict[str, Any]:
        """
        La IA puede analizar los modos de Koopman.
        """
        if not self.motor.dmd.fitted:
            return {}
        
        modes, eigenvalues = self.motor.dmd.get_dominant_modes(k=5)
        freqs, growth = self.motor.dmd.get_frequencies_and_growth()
        
        return {
            "modes": modes.tolist(),
            "eigenvalues": eigenvalues.tolist(),
            "frequencies": freqs[:5].tolist(),
            "growth_rates": growth[:5].tolist(),
            "interpretation": self._interpretar_modos(freqs, growth)
        }
    
    def _interpretar_modos(self, freqs, growth) -> str:
        """Genera interpretación textual para la IA."""
        dominant_freq = np.abs(freqs[0])
        dominant_growth = growth[0]
        
        if dominant_growth > 0.1:
            return f"Sistema en expansión (λ={dominant_growth:.3f}), periodo={1/max(dominant_freq,0.01):.1f}s"
        elif dominant_growth < -0.1:
            return f"Sistema en contracción (λ={dominant_growth:.3f})"
        else:
            return f"Sistema estable, oscilación a {dominant_freq:.3f} Hz"
    
    # ===== ESCRITURA =====
    
    def modificar_pad_emotions(self, pleasure: float, arousal: float, dominance: float):
        """
        La IA puede modificar directamente el estado emocional.
        """
        if len(self.motor.historial) > 0:
            ultimo = self.motor.historial.buffer[-1]
            ultimo.pad_emotions = np.array([pleasure, arousal, dominance], dtype=np.float32)
    
    def inyectar_patron(self, patron: np.ndarray):
        """
        La IA puede inyectar un patrón directamente al ESN.
        """
        if patron.shape[0] == 182:
            # Actualizar con patrón sintético
            self.motor.rmn.step(patron)
    
    def ajustar_memoria_rmn(self, decay: float):
        """
        La IA puede ajustar el decay de la memoria a largo plazo.
        """
        self.motor.rmn.config.memory_decay = np.clip(decay, 0.9, 0.999)
        # Reconstruir matriz de memoria
        self.motor.rmn.W_mem = np.eye(self.motor.rmn.config.memory_size) * decay
    
    # ===== PREDICCIÓN =====
    
    def pedir_prediccion_textual(self, horizonte: int = 5) -> str:
        """
        Genera predicción en formato textual para la IA.
        """
        pred = self.motor.predecir(horizonte)
        
        texto = f"""
PREDICCIÓN S4 (horizonte={horizonte})
=====================================
Lyapunov: {pred.lyapunov:.4f} ({self._clasificar_regimen(pred.lyapunov)})
Incertidumbre media: {pred.incertidumbre.mean():.4f}

Patrones SPA: {pred.patrones_spa}

Tendencias:
- Embedding: {'↑' if pred.prediccion[-1, :64].mean() > pred.prediccion[0, :64].mean() else '↓'}
- ESN: {'↑' if pred.prediccion[-1, 64:164].mean() > pred.prediccion[0, 64:164].mean() else '↓'}
- PAD: P={pred.prediccion[-1, 164]:.2f}, A={pred.prediccion[-1, 165]:.2f}, D={pred.prediccion[-1, 166]:.2f}
"""
        return texto.strip()
    
    def _clasificar_regimen(self, lyapunov: float) -> str:
        if lyapunov > 0.1:
            return "CAÓTICO"
        elif lyapunov < -0.1:
            return "ORDENADO"
        else:
            return "BORDE DEL CAOS"
    
    # ===== HERRAMIENTAS PARA LLM =====
    
    def get_tools_for_llm(self) -> List[Dict]:
        """
        Retorna definiciones de herramientas para un LLM (function calling).
        """
        return [
            {
                "name": "leer_estado_tensor",
                "description": "Lee el estado tensorial actual del sistema S4",
                "parameters": {}
            },
            {
                "name": "leer_modos_dinamicos",
                "description": "Analiza los modos de Koopman/DMD del sistema",
                "parameters": {}
            },
            {
                "name": "modificar_pad_emotions",
                "description": "Modifica el estado emocional PAD",
                "parameters": {
                    "pleasure": "float, -1.0 a 1.0",
                    "arousal": "float, -1.0 a 1.0",
                    "dominance": "float, -1.0 a 1.0"
                }
            },
            {
                "name": "ajustar_memoria_rmn",
                "description": "Ajusta el decay de memoria del RMN",
                "parameters": {
                    "decay": "float, 0.9 a 0.999"
                }
            },
            {
                "name": "pedir_prediccion_textual",
                "description": "Genera predicción en formato textual",
                "parameters": {
                    "horizonte": "int, pasos a predecir"
                }
            }
        ]
```

### 4.3 Diagrama de Interacción

```
┌─────────────────────────────────────────────────────────────────────┐
│                     INTERFAZ IA-TENSOR                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     LECTURA      ┌──────────────────────┐         │
│  │             │ ───────────────→ │                      │         │
│  │  LLM/IA     │                  │     MOTOR S4         │         │
│  │  (Gemini,   │ ←─────────────── │                      │         │
│  │   GPT, etc) │     ESCRITURA    │  ┌────────────────┐  │         │
│  │             │                  │  │ TensorFusionado│  │         │
│  └─────────────┘                  │  │ RMN            │  │         │
│        │                          │  │ DMD            │  │         │
│        │                          │  │ SPA            │  │         │
│        ▼                          │  └────────────────┘  │         │
│  ┌─────────────┐                  └──────────────────────┘         │
│  │  Function   │                                                    │
│  │  Calling    │                                                    │
│  │  Tools      │                                                    │
│  └─────────────┘                                                    │
│                                                                     │
│  OPERACIONES DISPONIBLES:                                           │
│  ├── leer_estado_tensor()     → Dict[str, np.ndarray]              │
│  ├── leer_modos_dinamicos()   → Dict[eigenvalues, frequencies]     │
│  ├── modificar_pad_emotions() → Escritura directa                  │
│  ├── inyectar_patron()        → RMN step con patrón sintético      │
│  ├── ajustar_memoria_rmn()    → Modificar decay de memoria         │
│  └── pedir_prediccion()       → Texto interpretable                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.4 Casos de Uso IA-Tensor

| Caso | Descripción | Implementación |
|:-----|:------------|:---------------|
| **Diagnóstico** | IA analiza estado caótico | `leer_modos_dinamicos()` |
| **Ajuste emocional** | IA modifica PAD | `modificar_pad_emotions()` |
| **Optimización** | IA ajusta hyperparámetros | `ajustar_memoria_rmn()` |
| **Predicción** | IA solicita forecast | `pedir_prediccion_textual()` |
| **Inyección** | IA inyecta patrones | `inyectar_patron()` |

---

## PARTE 5: DIAGRAMA COMPLETO DE CONEXIONES

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ARQUITECTURA DE DATOS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐                                                            │
│  │   CAPA 1    │ ──── Redis Pub/Sub ────┐                                   │
│  │   (Monje)   │     monje/fenomenologia/ │                                 │
│  └─────────────┘                        │                                   │
│                                         ▼                                   │
│                            ┌─────────────────────┐                          │
│                            │    SISTEMA YO v100  │                          │
│                            │                     │                          │
│  ┌─────────────┐           │  ┌─────────────┐   │           ┌─────────────┐│
│  │    n8n      │ ◄────────►│  │    S1-S4    │   │◄─────────►│   Neo4j     ││
│  │  Webhooks   │  HTTP     │  │   Engines   │   │   Bolt    │   (Grafo)   ││
│  │  :5678      │           │  └─────────────┘   │           │   :7687     ││
│  └─────────────┘           │                     │           └─────────────┘│
│                            │  ┌─────────────┐   │                          │
│                            │  │   Motor S4   │   │           ┌─────────────┐│
│  ┌─────────────┐           │  │  ┌───────┐  │   │◄─────────►│  LightRAG   ││
│  │   Redis     │ ◄────────►│  │  │Tensor │  │   │   HTTP    │  (Semántica)││
│  │   Cache     │   PubSub  │  │  │Fusion │  │   │           │   :8000     ││
│  │   :6379     │           │  │  └───────┘  │   │           └─────────────┘│
│  └─────────────┘           │  └─────────────┘   │                          │
│                            │                     │                          │
│                            │  ┌─────────────┐   │                          │
│                            │  │ Interfaz IA │   │ ◄──── LLM (Gemini/GPT)   │
│                            │  │  (Nueva)    │   │       Function Calling   │
│                            │  └─────────────┘   │                          │
│                            └─────────────────────┘                          │
│                                                                             │
│  LEYENDA:                                                                   │
│  ─────── Conexión existente                                                 │
│  - - - - Conexión propuesta                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PARTE 6: RESUMEN DE CONEXIONES

| Base de Datos | Tipo | Puerto | Protocolo | Estado |
|:--------------|:-----|:------:|:----------|:------:|
| **Neo4j** | Grafo | 7687 | Bolt | ✅ Implementado |
| **LightRAG** | API | 8000 | HTTP | ✅ Implementado |
| **Redis** | Cache/PubSub | 6379 | Redis | ✅ Implementado |
| **n8n** | Workflows | 5678 | HTTP | ✅ Implementado |
| **SQLite** | Local | - | Archivo | ❌ Por implementar |

---

## CONCLUSIÓN

1. **Bases de datos externas**: El sistema usa Neo4j (grafo), LightRAG (semántica), y Redis (cache/pubsub) en PC2.

2. **Base de datos local**: No hay SQLite actualmente. Recomiendo agregarlo para persistir historial S4.

3. **n8n**: Integración completa vía webhooks para automatización de workflows.

4. **IA + Tensores**: Propuesta de `InterfazIATensor` que permite a un LLM:
   - Leer estado tensorial
   - Modificar tensores en tiempo real
   - Analizar modos de Koopman
   - Ajustar hiperparámetros
   - Generar predicciones textuales
