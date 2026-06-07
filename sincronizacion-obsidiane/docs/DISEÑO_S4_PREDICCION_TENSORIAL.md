# 🔮 S4: Sistema de Predicción Tensorial
## Diseño para PC de Bajos Recursos (Sin GPU)

---

## 1. INVESTIGACIÓN: Tensores Físicos Fenomenológicos

### 1.1 Tensores en Meteorología

Los **tensores fenomenológicos** en meteorología son objetos matemáticos que describen propiedades físicas dependientes de dirección:

| Tensor | Orden | Aplicación |
|:-------|:-----:|:-----------|
| **Tensor de Esfuerzos** | 2 (3×3) | Fuerzas internas en la atmósfera |
| **Tensor de Deformación** | 2 (3×3) | Cambios en masa de aire |
| **Tensor de Reynolds** | 2 (3×3) | Turbulencia atmosférica |
| **Tensor de Difusión** | 2 (3×3) | Transferencia de calor/humedad |

### 1.2 Ecuaciones de Navier-Stokes (Base Física)

```
∂v/∂t + (v·∇)v = -∇p/ρ + ∇·τ + g

donde:
  v = vector velocidad del viento
  p = presión atmosférica
  ρ = densidad del aire
  τ = tensor de esfuerzos viscosos (3×3)
  g = gravedad
```

El **tensor de esfuerzos τ** es la clave para modelar:
- Viscosidad atmosférica
- Transferencia de momento
- Turbulencia

---

## 2. TÉCNICAS ÓPTIMAS PARA BAJOS RECURSOS

### 2.1 Comparativa de Métodos

| Método | RAM | CPU | Precisión | Complejidad |
|:-------|:---:|:---:|:---------:|:-----------:|
| **SPA (Mainz)** | ~500MB | Baja | ★★★★★ | O(n) |
| **CP Decomposition** | ~200MB | Baja | ★★★★ | O(r³) |
| **Tensor Train** | ~300MB | Media | ★★★★★ | O(nr²) |
| **Tucker** | ~1GB | Alta | ★★★★ | O(n^d) |
| **ESN Tensorial** | ~100MB | Baja | ★★★★ | O(n²) |
| TensorFlow/PyTorch | 2GB+ | GPU | ★★★★★ | Alta |

### 2.2 Técnica Recomendada: **Híbrido SPA + ESN + CP**

```
┌─────────────────────────────────────────────────────────────┐
│                 S4: PREDICTOR TENSORIAL                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ENTRADA                                                   │
│   ───────                                                   │
│   Tensor T ∈ ℝ^(n×m×k)  (ej: ubicación × variable × tiempo)│
│                                                             │
│   FASE 1: DESCOMPOSICIÓN CP                                 │
│   ─────────────────────────                                 │
│   T ≈ Σᵣ aᵣ ⊗ bᵣ ⊗ cᵣ  (r factores de rango 1)           │
│   Complejidad: O(r × (n+m+k))                               │
│   RAM: ~50-200 MB                                           │
│                                                             │
│   FASE 2: ESN COMPACTO                                      │
│   ───────────────────────                                   │
│   Reservoir de 100-500 neuronas                             │
│   Memoria fading para series temporales                     │
│   Solo entrenar capa de salida (regresión lineal)           │
│   RAM: ~10-50 MB                                            │
│                                                             │
│   FASE 3: SPA (PATRONES DISCRETOS)                          │
│   ────────────────────────────────                          │
│   Identificar K patrones dominantes (K << n)                │
│   Transiciones Markovianas entre patrones                   │
│   Error esperado: 0.75°C (superficie)                       │
│   RAM: ~50-100 MB                                           │
│                                                             │
│   SALIDA                                                    │
│   ──────                                                    │
│   Predicción T̂(t+Δt) + Incertidumbre σ                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. ARQUITECTURA S4 PROPUESTA

### 3.1 Estructura de Clases

```python
# core/engines/s4_prediccion/
├── __init__.py
├── tensor_fenomenologico.py    # Representación de datos
├── descomposicion_cp.py        # CP/Tucker decomposition
├── esn_tensorial.py            # Echo State Network
├── spa_predictor.py            # Scalable Probabilistic Approx
├── motor_prediccion.py         # Orquestador S4
└── metricas.py                 # Error, incertidumbre
```

### 3.2 Flujo de Datos

```
                    ┌──────────────────┐
                    │   Datos Brutos   │
                    │ (Meteorológicos) │
                    └────────┬─────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   TensorFenomenologico       │
              │   shape: (loc, var, tiempo)  │
              │   ej: (100, 5, 24)           │
              └──────────────┬───────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ DecompCP    │   │ ESNTensor   │   │ SPA         │
    │ Factores    │   │ Reservoir   │   │ Patrones    │
    │ r=10-50     │   │ N=100-500   │   │ K=20-100    │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │     MotorPrediccionS4        │
              │  - Fusión de predicciones    │
              │  - Cuantificación de error   │
              │  - Integración con S1/S2/S3  │
              └──────────────────────────────┘
```

---

## 4. IMPLEMENTACIÓN: Componentes Clave

### 4.1 Tensor Fenomenológico

```python
@dataclass
class TensorFenomenologico:
    """Tensor físico con metadatos fenomenológicos."""
    
    datos: np.ndarray           # Shape: (loc, var, tiempo)
    variables: List[str]        # ['temperatura', 'presion', 'humedad', ...]
    ubicaciones: List[Tuple]    # [(lat, lon), ...]
    timestamps: List[datetime]
    
    # Metadatos físicos
    unidades: Dict[str, str]    # {'temperatura': 'K', 'presion': 'Pa'}
    tensor_esfuerzos: Optional[np.ndarray] = None  # 3×3 por ubicación
    
    def to_cp_format(self) -> Tuple[np.ndarray, ...]:
        """Prepara para descomposición CP."""
        pass
    
    def calcular_gradientes(self) -> np.ndarray:
        """Gradientes espaciales/temporales."""
        pass
```

### 4.2 Descomposición CP (Lightweight)

```python
class DescomposicionCP:
    """
    CANDECOMP/PARAFAC sin dependencias pesadas.
    Solo NumPy + scipy.
    """
    
    def __init__(self, rango: int = 20, max_iter: int = 100):
        self.rango = rango
        self.max_iter = max_iter
        self.factores = None
    
    def fit(self, tensor: np.ndarray) -> Tuple[np.ndarray, ...]:
        """
        Alternating Least Squares (ALS).
        Complejidad: O(rango × Π dim_i × iter)
        """
        # Inicialización aleatoria
        factores = [np.random.randn(dim, self.rango) 
                   for dim in tensor.shape]
        
        for _ in range(self.max_iter):
            for modo in range(tensor.ndim):
                # Actualizar factor del modo actual
                factores[modo] = self._actualizar_modo(
                    tensor, factores, modo
                )
        
        self.factores = factores
        return tuple(factores)
    
    def predict_next(self, horizonte: int = 1) -> np.ndarray:
        """Extrapola el factor temporal."""
        pass
```

### 4.3 ESN Compacto

```python
class ESNTensorial:
    """
    Echo State Network optimizado para tensores.
    Sin PyTorch - Solo NumPy.
    """
    
    def __init__(self, 
                 input_dim: int,
                 reservoir_size: int = 200,
                 spectral_radius: float = 0.9,
                 sparsity: float = 0.9):
        self.reservoir_size = reservoir_size
        self.spectral_radius = spectral_radius
        
        # Matriz reservoir sparse (90% ceros)
        self.W = self._crear_reservoir_sparse(sparsity)
        self.W_in = np.random.randn(reservoir_size, input_dim) * 0.1
        self.W_out = None  # Solo esto se entrena
        
        self.estado = np.zeros(reservoir_size)
    
    def _crear_reservoir_sparse(self, sparsity: float) -> np.ndarray:
        """Reservoir con sparsity para eficiencia."""
        W = np.random.randn(self.reservoir_size, self.reservoir_size)
        mask = np.random.random(W.shape) > sparsity
        W *= mask
        
        # Escalar a spectral radius
        eigenvalues = np.abs(np.linalg.eigvals(W))
        W *= self.spectral_radius / np.max(eigenvalues)
        return W
    
    def step(self, x: np.ndarray) -> np.ndarray:
        """Un paso del reservoir."""
        self.estado = np.tanh(
            self.W @ self.estado + self.W_in @ x
        )
        return self.estado
    
    def fit(self, X: np.ndarray, Y: np.ndarray):
        """Entrena solo la capa de salida (Ridge Regression)."""
        estados = []
        for x in X:
            estados.append(self.step(x))
        
        estados = np.array(estados)
        # Ridge regression: W_out = Y @ estados.T @ inv(estados @ estados.T + λI)
        lambda_reg = 1e-4
        self.W_out = Y.T @ estados @ np.linalg.inv(
            estados.T @ estados + lambda_reg * np.eye(self.reservoir_size)
        )
    
    def predict(self, horizonte: int) -> np.ndarray:
        """Predicción auto-regresiva."""
        predicciones = []
        for _ in range(horizonte):
            pred = self.W_out @ self.estado
            predicciones.append(pred)
            self.step(pred)  # Feedback
        return np.array(predicciones)
```

### 4.4 SPA Simplificado

```python
class SPAPredictor:
    """
    Scalable Probabilistic Approximation simplificado.
    Basado en: Metzner et al., Mainz University
    """
    
    def __init__(self, n_patrones: int = 50):
        self.n_patrones = n_patrones
        self.centroides = None
        self.matriz_transicion = None
    
    def fit(self, serie_temporal: np.ndarray):
        """
        1. Discretizar en K patrones (clustering)
        2. Calcular matriz de transición Markoviana
        """
        from sklearn.cluster import MiniBatchKMeans
        
        # Clustering eficiente
        kmeans = MiniBatchKMeans(
            n_clusters=self.n_patrones,
            batch_size=1000
        )
        etiquetas = kmeans.fit_predict(serie_temporal)
        self.centroides = kmeans.cluster_centers_
        
        # Matriz de transición
        self.matriz_transicion = np.zeros(
            (self.n_patrones, self.n_patrones)
        )
        for i in range(len(etiquetas) - 1):
            self.matriz_transicion[etiquetas[i], etiquetas[i+1]] += 1
        
        # Normalizar a probabilidades
        sumas = self.matriz_transicion.sum(axis=1, keepdims=True)
        sumas[sumas == 0] = 1
        self.matriz_transicion /= sumas
    
    def predict(self, estado_actual: np.ndarray, 
                horizonte: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predicción + incertidumbre.
        Returns: (predicciones, desviaciones_std)
        """
        # Encontrar patrón más cercano
        distancias = np.linalg.norm(
            self.centroides - estado_actual, axis=1
        )
        patron_actual = np.argmin(distancias)
        
        predicciones = []
        incertidumbres = []
        prob = np.zeros(self.n_patrones)
        prob[patron_actual] = 1.0
        
        for _ in range(horizonte):
            prob = prob @ self.matriz_transicion
            pred = self.centroides.T @ prob
            predicciones.append(pred)
            
            # Incertidumbre como entropía de la distribución
            entropia = -np.sum(prob * np.log(prob + 1e-10))
            incertidumbres.append(entropia)
        
        return np.array(predicciones), np.array(incertidumbres)
```

---

## 5. INTEGRACIÓN CON S1/S2/S3

### 5.1 Conexiones Inter-Sistema

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     S1       │     │     S2       │     │     S3       │     │     S4       │
│ Fenomenología│ ──→ │  Emergencia  │ ──→ │   Lógica     │ ──→ │  Predicción  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       │ Grundzugs          │ Conceptos          │ Axiomas            │ Predicciones
       │ sensoriales        │ emergidos          │ validados          │ tensoriales
       ▼                    ▼                    ▼                    ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │                        GRAFO DE CONOCIMIENTO                          │
   │                             (Neo4j)                                   │
   └────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Flujo S1 → S4

```python
def flujo_fenomenologico_a_tensor(grundzugs: List[Grundzug]) -> TensorFenomenologico:
    """
    Convierte Grundzugs (S1) en tensor para S4.
    """
    # Agrupar por tipo y tiempo
    matriz = np.zeros((n_ubicaciones, n_variables, n_tiempos))
    
    for g in grundzugs:
        loc_idx = obtener_indice_ubicacion(g.origen)
        var_idx = obtener_indice_variable(g.tipo)
        t_idx = obtener_indice_tiempo(g.timestamp)
        
        matriz[loc_idx, var_idx, t_idx] = g.valor
    
    return TensorFenomenologico(
        datos=matriz,
        variables=[...],
        ubicaciones=[...],
        timestamps=[...]
    )
```

---

## 6. REQUISITOS DE RECURSOS

### 6.1 Estimación de Uso

| Componente | RAM | CPU (1 pred) | Entrenamiento |
|:-----------|:---:|:------------:|:-------------:|
| TensorFenomenologico | ~10 MB | - | - |
| DescomposicionCP | ~50 MB | 100 ms | 5 seg |
| ESNTensorial (200) | ~20 MB | 1 ms | 2 seg |
| SPAPredictor (50) | ~30 MB | 10 ms | 10 seg |
| **TOTAL S4** | **~110 MB** | **~112 ms** | **~17 seg** |

### 6.2 Dependencias

```txt
# requirements-s4.txt (Solo CPU)
numpy>=1.21.0
scipy>=1.7.0
scikit-learn>=1.0.0  # Solo para MiniBatchKMeans
```

---

## 7. PRÓXIMOS PASOS

1. [ ] Implementar `tensor_fenomenologico.py`
2. [ ] Implementar `descomposicion_cp.py`
3. [ ] Implementar `esn_tensorial.py`
4. [ ] Implementar `spa_predictor.py`
5. [ ] Implementar `motor_prediccion.py` (orquestador)
6. [ ] Crear tests con datos sintéticos
7. [ ] Integrar con S1/S2/S3
8. [ ] Probar con datos meteorológicos reales

---

## 8. REFERENCIAS

1. **SPA Algorithm**: Metzner et al., Johannes Gutenberg University Mainz
2. **Tensor Train**: Oseledets (2011), "Tensor-Train Decomposition"
3. **CP Decomposition**: Kolda & Bader (2009), "Tensor Decompositions"
4. **ESN**: Jaeger (2001), "Echo State Networks"
5. **Tensor de Esfuerzos**: Navier-Stokes equations in meteorology
