# 🚀 S4 ÓPTIMO: Investigación Avanzada de Tensores

## Resumen Ejecutivo

Esta investigación identifica las **mejores técnicas tensoriales** para maximizar el rendimiento de S4, aprovechando los tensores EXISTENTES del sistema y agregando nuevas capacidades.

---

## PARTE 1: TÉCNICAS PARA MEJORAR TENSORES EXISTENTES

### 1.1 ESN → Tensor Network Reservoir Computing (TNRC)

**Problema actual**: El ESN usa W_res[100×100] como matriz densa.
**Mejora**: Descomponer W_res en red de tensores.

```python
# ANTES (actual)
W_res = np.random.randn(100, 100)  # 10,000 parámetros

# DESPUÉS (TNRC - Tensor Network)
# Descomposición en factores de bajo rango
r = 10  # rango
W_res_A = np.random.randn(100, r)   # 1,000 parámetros  
W_res_B = np.random.randn(r, 100)   # 1,000 parámetros
W_res = W_res_A @ W_res_B           # O(100*r) en lugar de O(100²)
# Reducción: 80% menos parámetros, 90% más rápido
```

**Beneficio**: 2-3 órdenes de magnitud más rápido que ESN tradicional.

---

### 1.2 Embeddings[64] → HOSVD Temporal

**Problema actual**: Los embeddings son vectores independientes sin contexto temporal.
**Mejora**: Construir tensor 3D de historial y aplicar HOSVD.

```python
# Tensor de historial de embeddings
historial = np.zeros((T, 64, K))  # Tiempo × Features × Contextos

# HOSVD: Descomposición en modos
# T = G ×1 U_tiempo ×2 U_features ×3 U_contexto
core, (U_t, U_f, U_c) = hosvd(historial, ranks=[5, 32, 3])

# Beneficios:
# - Reduce T=100 pasos a 5 modos temporales principales
# - Reduce 64 features a 32 más informativas
# - Captura 3 patrones de contexto
```

**Beneficio**: Extrae patrones temporales latentes automáticamente.

---

### 1.3 Count-Min Sketch[5×2718] → Tensor Ring

**Problema actual**: El sketch es matriz fija.
**Mejora**: Representar como Tensor Ring para capturar correlaciones cruzadas.

```python
# Tensor Ring del sketch
# Permite capturar correlaciones entre diferentes hashes
# Más compacto para sketches muy grandes

from tensor_ring import TensorRing

sketch_tr = TensorRing(
    shape=(5, 2718),
    ranks=[2, 2]  # Anillo de bajo rango
)
# Compresión: 90%+ para sketches grandes
```

**Beneficio**: Captura correlaciones entre niveles del sketch.

---

### 1.4 Jacobiano[100×100] → Dynamic Mode Decomposition (DMD)

**Problema actual**: El Lyapunov usa solo la norma espectral del jacobiano.
**Mejora**: Aplicar DMD para extraer modos dinámicos.

```python
class DMDPredictor:
    """
    Dynamic Mode Decomposition para predicción.
    Conexión con operador de Koopman.
    """
    def __init__(self):
        self.modes = None
        self.eigenvalues = None
        self.amplitudes = None
    
    def fit(self, X: np.ndarray):
        """
        X: Matriz de snapshots [features × tiempo]
        """
        X1 = X[:, :-1]  # t = 0 a T-1
        X2 = X[:, 1:]   # t = 1 a T
        
        # SVD de X1
        U, S, Vh = np.linalg.svd(X1, full_matrices=False)
        r = min(20, len(S))  # Truncar
        U = U[:, :r]
        S = S[:r]
        Vh = Vh[:r, :]
        
        # Matriz DMD
        A_tilde = U.T @ X2 @ Vh.T @ np.diag(1/S)
        
        # Eigendescomposición
        self.eigenvalues, W = np.linalg.eig(A_tilde)
        self.modes = X2 @ Vh.T @ np.diag(1/S) @ W
        
        # Amplitudes iniciales
        self.amplitudes = np.linalg.pinv(self.modes) @ X[:, 0]
    
    def predict(self, horizonte: int) -> np.ndarray:
        """Predicción usando modos dinámicos."""
        preds = []
        for t in range(1, horizonte + 1):
            dynamics = self.eigenvalues ** t
            pred = self.modes @ (self.amplitudes * dynamics)
            preds.append(pred.real)
        return np.array(preds)
    
    def get_frequencies_and_growth(self):
        """Extrae frecuencias oscilatorias y tasas de crecimiento."""
        dt = 1.0
        omega = np.log(self.eigenvalues) / dt
        frequencies = omega.imag / (2 * np.pi)
        growth_rates = omega.real
        return frequencies, growth_rates
```

**Beneficio**: Linealiza dinámica no lineal vía operador de Koopman.

---

## PARTE 2: NUEVOS TENSORES A AGREGAR

### 2.1 Tensor de Fusión Multimodal

Combinar TODOS los tensores existentes en uno solo:

```python
@dataclass
class TensorFusionado:
    """Tensor que fusiona todas las fuentes."""
    
    # Dimensiones: (batch, tiempo, features_totales)
    # features_totales = 64 + 100 + 3 + 10 + 5 = 182
    
    embedding: np.ndarray       # [64] - Semántica
    esn_state: np.ndarray       # [100] - Dinámica reservoir
    pad_emotions: np.ndarray    # [3] - Afecto
    grundzug_freq: np.ndarray   # [10] - Top-10 Grundzugs
    lyapunov_features: np.ndarray  # [5] - Métricas de caos
    
    def to_flat_tensor(self) -> np.ndarray:
        return np.concatenate([
            self.embedding,
            self.esn_state,
            self.pad_emotions,
            self.grundzug_freq,
            self.lyapunov_features
        ])  # [182]
    
    def to_tensor_3d(self, historial: List['TensorFusionado']) -> np.ndarray:
        """Construye tensor temporal."""
        return np.array([t.to_flat_tensor() for t in historial])
        # Shape: (T, 182)
```

### 2.2 Tensor de Atención Simplificado

```python
class TensorAttention:
    """
    Atención tensorial ligera para fusión cross-modal.
    Complejidad: O(n²) reducida a O(n*r) con bajo rango.
    """
    
    def __init__(self, dims: List[int], rank: int = 8):
        self.dims = dims  # [64, 100, 3] para emb, esn, pad
        self.rank = rank
        
        # Matrices de proyección de bajo rango
        self.W_q = [np.random.randn(d, rank) for d in dims]
        self.W_k = [np.random.randn(d, rank) for d in dims]
        self.W_v = [np.random.randn(d, rank) for d in dims]
    
    def attention(self, tensors: List[np.ndarray]) -> np.ndarray:
        """Atención cross-modal."""
        # Proyectar a espacio común de bajo rango
        queries = [t @ W for t, W in zip(tensors, self.W_q)]
        keys = [t @ W for t, W in zip(tensors, self.W_k)]
        values = [t @ W for t, W in zip(tensors, self.W_v)]
        
        # Concatenar
        Q = np.concatenate(queries)  # [rank * n_modalities]
        K = np.concatenate(keys)
        V = np.concatenate(values)
        
        # Atención (scaled dot-product)
        scores = Q @ K.T / np.sqrt(len(K))
        weights = self._softmax(scores)
        output = weights @ V
        
        return output
    
    def _softmax(self, x):
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()
```

### 2.3 Reservoir Memory Network (RMN)

Mejora del ESN con memoria de largo plazo:

```python
class ReservoirMemoryNetwork:
    """
    ESN mejorado con celda de memoria lineal.
    Octubre 2024 - ESANN.
    """
    
    def __init__(self, input_dim: int, reservoir_size: int = 100, 
                 memory_size: int = 50):
        # Reservoir no lineal (tradicional)
        self.W_in = np.random.randn(reservoir_size, input_dim) * 0.5
        self.W_res = np.random.randn(reservoir_size, reservoir_size) * 0.5
        self.state_res = np.zeros(reservoir_size)
        
        # Celda de memoria lineal (NUEVO)
        self.W_mem_in = np.random.randn(memory_size, input_dim) * 0.1
        self.W_mem = np.eye(memory_size) * 0.99  # Casi identidad → memoria larga
        self.state_mem = np.zeros(memory_size)
        
        # Salida combinada
        self.W_out = np.zeros((input_dim, reservoir_size + memory_size))
        
    def step(self, x: np.ndarray) -> np.ndarray:
        # Reservoir no lineal
        pre_res = self.W_in @ x + self.W_res @ self.state_res
        self.state_res = np.tanh(pre_res)
        
        # Memoria lineal (retiene información largo plazo)
        pre_mem = self.W_mem_in @ x + self.W_mem @ self.state_mem
        self.state_mem = pre_mem  # Lineal, no tanh
        
        # Concatenar estados
        combined = np.concatenate([self.state_res, self.state_mem])
        
        return combined
    
    def predict(self) -> np.ndarray:
        combined = np.concatenate([self.state_res, self.state_mem])
        return self.W_out @ combined
```

---

## PARTE 3: ARQUITECTURA S4 OPTIMIZADA

### 3.1 Pipeline Completo

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        S4: ARQUITECTURA ÓPTIMA                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ENTRADA (Tensores Existentes)                                               │
│  ─────────────────────────────                                               │
│  embedding[64] ──┬                                                           │
│  esn.state[100] ─┼──→ TensorFusionado[182]                                  │
│  pad[3] ─────────┤                                                           │
│  grundzugs[10] ──┤                                                           │
│  lyapunov[5] ────┘                                                           │
│                                                                              │
│  FASE 1: MEJORA DE TENSORES EXISTENTES                                      │
│  ─────────────────────────────────────                                       │
│                                                                              │
│  ESN mejorado con:                                                           │
│  ├── Tensor Network W_res (80% menos params)                                │
│  └── Reservoir Memory Network (memoria largo plazo)                         │
│                                                                              │
│  Historial de embeddings:                                                    │
│  └── HOSVD → 5 modos temporales + 32 features principales                   │
│                                                                              │
│  FASE 2: FUSIÓN MULTIMODAL                                                  │
│  ─────────────────────────                                                   │
│                                                                              │
│  TensorAttention:                                                            │
│  ├── Cross-modal entre embedding, esn_state, pad                            │
│  └── Bajo rango (r=8) para eficiencia                                       │
│                                                                              │
│  FASE 3: PREDICCIÓN                                                         │
│  ───────────────────                                                         │
│                                                                              │
│  DMD (Dynamic Mode Decomposition):                                           │
│  ├── Extrae modos dinámicos principales                                     │
│  ├── Aproxima operador de Koopman                                            │
│  └── Predicción multi-horizonte                                              │
│                                                                              │
│  CP Decomposition:                                                           │
│  ├── Tensor temporal T[tiempo, features]                                    │
│  └── Factores para patrones recurrentes                                     │
│                                                                              │
│  FASE 4: CUANTIFICACIÓN DE INCERTIDUMBRE                                    │
│  ───────────────────────────────────────                                     │
│                                                                              │
│  SPA (Scalable Probabilistic Approximation):                                │
│  ├── K patrones discretos                                                    │
│  ├── Matriz de transición Markoviana                                        │
│  └── Distribución de probabilidad sobre predicciones                        │
│                                                                              │
│  SALIDA                                                                      │
│  ──────                                                                      │
│  ├── prediccion[horizonte, features]                                        │
│  ├── incertidumbre[horizonte]                                               │
│  ├── modos_dinamicos[] (interpretabilidad)                                  │
│  └── frecuencias_koopman[] (análisis espectral)                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Estructura de Archivos

```
core_new/engines/s4_prediccion/
├── __init__.py
├── tensor_fusionado.py       # Fusión de tensores existentes
├── tnrc.py                   # Tensor Network Reservoir Computing
├── rmn.py                    # Reservoir Memory Network
├── hosvd.py                  # Higher-Order SVD
├── dmd.py                    # Dynamic Mode Decomposition
├── tensor_attention.py       # Atención multimodal
├── cp_decomposition.py       # CANDECOMP/PARAFAC
├── spa_predictor.py          # Probabilistic Approximation
└── motor_s4.py               # Orquestador
```

---

## PARTE 4: NUEVOS TENSORES RECOMENDADOS

### 4.1 Tensor de Koopman Observable

```python
class KoopmanObservable:
    """
    Observables para operador de Koopman.
    Linealiza dinámica no lineal.
    """
    def __init__(self, state_dim: int, n_observables: int = 50):
        self.state_dim = state_dim
        self.n_obs = n_observables
        
    def lift(self, state: np.ndarray) -> np.ndarray:
        """Eleva el estado al espacio de observables."""
        observables = [state]  # Estado original
        
        # Polinomios de grado 2
        for i in range(len(state)):
            for j in range(i, len(state)):
                observables.append([state[i] * state[j]])
        
        # Funciones radiales
        centers = np.random.randn(20, len(state))
        for c in centers:
            rbf = np.exp(-np.linalg.norm(state - c)**2)
            observables.append([rbf])
        
        return np.concatenate(observables)[:self.n_obs]
```

### 4.2 Tensor de Gradiente Temporal

```python
class GradientTemporalTensor:
    """
    Captura derivadas temporales del estado.
    Mejora predicción dinámica.
    """
    def __init__(self, buffer_size: int = 5):
        self.buffer = deque(maxlen=buffer_size)
        
    def update(self, state: np.ndarray):
        self.buffer.append(state)
        
    def get_gradient_tensor(self) -> np.ndarray:
        """
        Retorna tensor con:
        - Estado actual
        - Primera derivada (velocidad)
        - Segunda derivada (aceleración)
        """
        if len(self.buffer) < 3:
            return None
            
        states = np.array(self.buffer)
        
        # Derivadas por diferencias finitas
        velocity = np.diff(states, axis=0)[-1]
        acceleration = np.diff(states, n=2, axis=0)[-1]
        
        return np.concatenate([
            states[-1],      # Estado actual
            velocity,        # Primera derivada
            acceleration     # Segunda derivada
        ])
```

### 4.3 Tensor de Fase Espacial (del Autómata)

```python
class PhaseSpaceTensor:
    """
    Transforma el autómata 2D en tensor de características de fase.
    """
    def __init__(self, automata_shape: Tuple[int, int]):
        self.shape = automata_shape
        
    def extract_features(self, grilla: np.ndarray) -> np.ndarray:
        """Extrae características del espacio de fase."""
        features = []
        
        # 1. Densidad global
        features.append(grilla.mean())
        
        # 2. Entropía local (bloques 4x4)
        block_entropies = []
        for i in range(0, grilla.shape[0]-3, 4):
            for j in range(0, grilla.shape[1]-3, 4):
                block = grilla[i:i+4, j:j+4]
                p = block.mean()
                if 0 < p < 1:
                    entropy = -p*np.log(p) - (1-p)*np.log(1-p)
                else:
                    entropy = 0
                block_entropies.append(entropy)
        features.extend(block_entropies[:10])  # Top 10
        
        # 3. FFT 2D (frecuencias espaciales)
        fft = np.fft.fft2(grilla)
        magnitudes = np.abs(fft)
        features.extend(magnitudes.flatten()[:20])  # Top 20 frecuencias
        
        # 4. Detección de gliders (patrones móviles)
        glider_count = self._count_gliders(grilla)
        features.append(glider_count)
        
        return np.array(features)
    
    def _count_gliders(self, grilla: np.ndarray) -> int:
        """Cuenta patrones de glider del Game of Life."""
        glider_pattern = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ])
        from scipy import signal
        correlation = signal.correlate2d(grilla, glider_pattern, mode='valid')
        return int((correlation == 5).sum())
```

---

## PARTE 5: COMPARATIVA Y SELECCIÓN

### 5.1 Tabla de Técnicas

| Técnica | Mejora | Complejidad | RAM | Implementar |
|:--------|:-------|:-----------:|:---:|:-----------:|
| **TNRC** (Tensor Network RC) | ESN 2-3× más rápido | O(nr) | ~20MB | ✅ Sí |
| **HOSVD** | Extrae modos temporales | O(n³) | ~50MB | ✅ Sí |
| **Tensor Ring** | 90% compresión | O(nr²) | ~10MB | ❌ Opcional |
| **DMD** (Koopman) | Linealiza no-lineal | O(r³) | ~30MB | ✅ Sí |
| **RMN** | Memoria largo plazo | O(n²) | ~30MB | ✅ Sí |
| **Tensor Attention** | Fusión multimodal | O(n×r) | ~20MB | ✅ Sí |
| **CP Decomposition** | Patrones recurrentes | O(r³) | ~20MB | ✅ Sí |
| **SPA** | Incertidumbre | O(K²) | ~30MB | ✅ Sí |

### 5.2 Recursos Totales Estimados

| Componente | RAM | CPU/pred |
|:-----------|:---:|:--------:|
| Tensores existentes (S1-S3) | ~50MB | - |
| TNRC mejorado | +20MB | 10ms |
| RMN | +30MB | 5ms |
| HOSVD | +50MB | 50ms |
| DMD | +30MB | 20ms |
| Tensor Attention | +20MB | 10ms |
| CP + SPA | +50MB | 30ms |
| **TOTAL S4** | **~250MB** | **~125ms** |

---

## PARTE 6: IMPLEMENTACIÓN PRIORITARIA

### Orden de implementación recomendado:

1. **TensorFusionado** - Combinar tensores existentes (1 día)
2. **RMN** - Mejorar ESN con memoria (1 día)
3. **DMD** - Predicción con Koopman (2 días)
4. **HOSVD** - Modos temporales (1 día)
5. **TensorAttention** - Fusión multimodal (1 día)
6. **CP + SPA** - Patrones e incertidumbre (2 días)
7. **MotorS4** - Orquestador final (1 día)

**Total estimado: 9 días de desarrollo**
