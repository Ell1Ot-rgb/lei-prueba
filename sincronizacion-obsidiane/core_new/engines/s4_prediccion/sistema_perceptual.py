"""
Sistema Perceptual Avanzado con Visualización - OPTIMIZADO + WOLFRAM
======================================================================

Optimizaciones aplicadas:
- Vectorización de padding y loops
- Pre-cálculo de strings fijos
- Remoción de matrices no usadas
- Cache de operaciones repetidas

Módulos Wolfram añadidos:
- CausalGraph: Rastreo de causalidad entre percepciones
- Class4Metrics: Métricas de borde del caos (Lyapunov, complejidad)
"""

import numpy as np
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque
import colorsys


# =============================================================================
# WOLFRAM-INSPIRED: CAUSAL GRAPH (Optimizado)
# =============================================================================

class CausalGraph:
    """
    Rastreo de causalidad entre percepciones - inspirado en Wolfram Physics.
    OPTIMIZADO: Usa arrays numpy pre-allocados, sin diccionarios anidados.
    """
    
    __slots__ = ['_max_nodes', '_edges', '_node_data', '_n_nodes', 
                 '_parent_idx', '_child_counts']
    
    def __init__(self, max_nodes: int = 1000):
        self._max_nodes = max_nodes
        self._n_nodes = 0
        
        # Pre-allocar arrays (evitar resize dinámico)
        self._edges = np.zeros((max_nodes, 4), dtype=np.int32)  # [from, to, type, weight]
        self._node_data = np.zeros((max_nodes, 4), dtype=np.float64)  # [timestamp, surprise, phi, coherence]
        self._parent_idx = np.full(max_nodes, -1, dtype=np.int32)  # Padre de cada nodo
        self._child_counts = np.zeros(max_nodes, dtype=np.int32)
    
    def add_node(self, surprise: float, phi: float, coherence: float, 
                 parent_id: int = -1) -> int:
        """Añade nodo causal - O(1)."""
        if self._n_nodes >= self._max_nodes:
            # Circular buffer: sobrescribir más antiguo
            node_id = self._n_nodes % self._max_nodes
        else:
            node_id = self._n_nodes
        
        self._node_data[node_id] = [self._n_nodes, surprise, phi, coherence]
        self._parent_idx[node_id] = parent_id
        
        if parent_id >= 0 and parent_id < self._max_nodes:
            self._child_counts[parent_id] += 1
        
        self._n_nodes += 1
        return node_id
    
    def get_causal_chain(self, node_id: int, max_depth: int = 10) -> np.ndarray:
        """Obtiene cadena causal hacia atrás - O(depth)."""
        chain = np.zeros(max_depth, dtype=np.int32)
        current = node_id
        depth = 0
        
        while current >= 0 and depth < max_depth:
            chain[depth] = current
            current = self._parent_idx[current]
            depth += 1
        
        return chain[:depth]
    
    def compute_causal_density(self, window: int = 50) -> float:
        """Densidad causal reciente - O(1)."""
        if self._n_nodes < 2:
            return 0.0
        
        start = max(0, self._n_nodes - window)
        end = min(self._n_nodes, self._max_nodes)
        
        # Contar conexiones en ventana
        connected = np.sum(self._parent_idx[start:end] >= 0)
        return float(connected / window)
    
    def find_event_horizon(self, current_id: int, threshold: float = 0.1) -> int:
        """Encuentra 'event horizon' = punto donde causalidad se pierde."""
        chain = self.get_causal_chain(current_id, 100)
        
        if len(chain) < 2:
            return -1
        
        # Buscar donde surprise cambia drásticamente
        for i in range(1, len(chain)):
            if chain[i] < 0:
                return int(chain[i-1])
            
            delta = abs(self._node_data[chain[i], 1] - self._node_data[chain[i-1], 1])
            if delta > threshold:
                return int(chain[i])
        
        return int(chain[-1])


# =============================================================================
# WOLFRAM-INSPIRED: CLASS 4 METRICS (Optimizado)
# =============================================================================

class Class4Metrics:
    """
    Métricas para detectar dinámicas Clase 4 (borde del caos).
    OPTIMIZADO: Cálculos vectorizados, historial circular.
    
    Clase 4 = ni muy ordenado ni muy caótico = donde emerge consciencia.
    """
    
    __slots__ = ['_history', '_max_history', '_lyapunov_cache', 
                 '_complexity_cache', '_edge_of_chaos_range']
    
    def __init__(self, max_history: int = 100):
        self._max_history = max_history
        self._history = np.zeros((max_history, 3), dtype=np.float64)  # [energy, entropy, surprise]
        self._lyapunov_cache = 0.0
        self._complexity_cache = 0.0
        self._edge_of_chaos_range = (0.3, 0.7)  # Rango óptimo para Clase 4
    
    def update(self, energy: float, entropy: float, surprise: float) -> Dict[str, float]:
        """Actualiza historial y calcula métricas - O(1) amortizado."""
        # Shift circular
        self._history = np.roll(self._history, -1, axis=0)
        self._history[-1] = [energy, entropy, surprise]
        
        # Calcular métricas
        lyapunov = self._compute_lyapunov()
        complexity = self._compute_complexity()
        is_class4 = self._check_class4(lyapunov, complexity)
        
        return {
            'lyapunov': lyapunov,
            'complexity': complexity,
            'is_class4': is_class4,
            'chaos_score': self._chaos_score(lyapunov)
        }
    
    def _compute_lyapunov(self) -> float:
        """Exponente de Lyapunov aproximado - mide sensibilidad."""
        if np.all(self._history == 0):
            return 0.0
        
        # Diferencias consecutivas (vectorizado)
        diffs = np.diff(self._history[:, 0])  # Usar energy
        
        if len(diffs) < 2:
            return 0.0
        
        # Lyapunov ≈ promedio de log(|diff|)
        nonzero = np.abs(diffs[diffs != 0])
        if len(nonzero) == 0:
            return -1.0  # Sistema estable
        
        self._lyapunov_cache = float(np.mean(np.log(nonzero + 1e-10)))
        return self._lyapunov_cache
    
    def _compute_complexity(self) -> float:
        """Complejidad aproximada (entropía de patrones)."""
        entropy_col = self._history[:, 1]
        
        if np.std(entropy_col) < 1e-10:
            return 0.0
        
        # Normalizar y calcular entropía de distribución
        normalized = (entropy_col - entropy_col.min()) / (entropy_col.max() - entropy_col.min() + 1e-10)
        bins = 10
        hist, _ = np.histogram(normalized, bins=bins, density=True)
        hist = hist[hist > 0]
        
        if len(hist) == 0:
            return 0.0
        
        self._complexity_cache = float(-np.sum(hist * np.log2(hist + 1e-10)) / np.log2(bins))
        return self._complexity_cache
    
    def _check_class4(self, lyapunov: float, complexity: float) -> bool:
        """Verifica si estamos en Clase 4 (borde del caos)."""
        # Clase 4: Lyapunov cerca de 0 (ni positivo ni muy negativo)
        # y complejidad moderada-alta
        lyap_ok = -0.5 < lyapunov < 0.5
        comp_ok = self._edge_of_chaos_range[0] < complexity < self._edge_of_chaos_range[1]
        return lyap_ok and comp_ok
    
    def _chaos_score(self, lyapunov: float) -> float:
        """Score 0-1 de qué tan caótico es el sistema."""
        # Mapear lyapunov a 0-1
        # -inf → 0 (muy estable), 0 → 0.5 (borde), +inf → 1 (caótico)
        return float(1.0 / (1.0 + np.exp(-lyapunov)))



# =============================================================================
# UTILIDADES OPTIMIZADAS
# =============================================================================

def _normalize_dim(arr: np.ndarray, target: int = 64) -> np.ndarray:
    """Normaliza array a dimensión objetivo - vectorizado."""
    if len(arr) >= target:
        return arr[:target]
    out = np.zeros(target, dtype=np.float64)
    out[:len(arr)] = arr
    return out


# =============================================================================
# 1. GAMMA OSCILLATOR (Feature Binding) - OPTIMIZADO
# =============================================================================

class GammaOscillator:
    """
    Sincroniza features usando oscilaciones gamma (30-80 Hz).
    OPTIMIZADO: Pre-cálculo de constantes.
    """
    
    def __init__(self, frequency: float = 40.0):
        self.freq = frequency
        self.fase = 0.0
        self.time = 0.0
        self._two_pi_freq = 2 * np.pi * frequency  # Pre-calculado
        self._dim = 64
        self._zero_array = np.zeros(self._dim)
    
    def tick(self, dt: float = 0.001):
        """Avanza el oscilador."""
        self.time += dt
        self.fase = (self._two_pi_freq * self.time) % (2 * np.pi)
    
    def compute_coherence(self, features: List[np.ndarray]) -> float:
        """Calcula coherencia entre features - OPTIMIZADO."""
        n = len(features)
        if n < 2:
            return 1.0
        
        # Vectorizado: calcular todas las fases de una vez
        exp_fase = np.exp(1j * self.fase)
        phases = np.array([np.angle(np.sum(f * exp_fase)) for f in features])
        
        # Coherencia usando std
        return float(np.exp(-np.std(phases)))
    
    def bind(self, features: Dict[str, np.ndarray]) -> np.ndarray:
        """Une features - OPTIMIZADO."""
        if not features:
            return self._zero_array.copy()
        
        # Vectorizado: normalizar y sumar
        normalized = np.array([_normalize_dim(f, self._dim) for f in features.values()])
        combined = normalized.mean(axis=0)
        
        # Aplicar coherencia
        coherence = self.compute_coherence(list(features.values()))
        return combined * coherence


# =============================================================================
# 2. CROSS-MODAL ATTENTION (Fusión) - OPTIMIZADO
# =============================================================================

class CrossModalAttention:
    """
    Atención cruzada - OPTIMIZADO con operaciones matriciales.
    """
    
    def __init__(self, dim: int = 64):
        self.dim = dim
        self._sqrt_dim = np.sqrt(dim)  # Pre-calculado
        
        # Matrices de proyección
        self.W_q = np.random.randn(dim, dim).astype(np.float64) * 0.1
        self.W_k = np.random.randn(dim, dim).astype(np.float64) * 0.1
        self.W_v = np.random.randn(dim, dim).astype(np.float64) * 0.1
        
        self._zero_array = np.zeros(dim)
    
    def fuse(self, modalidades: Dict[str, np.ndarray]) -> Tuple[np.ndarray, Dict[str, float]]:
        """Fusiona modalidades - OPTIMIZADO."""
        if not modalidades:
            return self._zero_array.copy(), {}
        
        names = list(modalidades.keys())
        n = len(names)
        
        # Vectorizado: crear matriz de embeddings
        X = np.zeros((n, self.dim), dtype=np.float64)
        for i, name in enumerate(names):
            X[i] = _normalize_dim(modalidades[name], self.dim)
        
        # Proyecciones matriciales (optimizado)
        Q = X @ self.W_q
        K = X @ self.W_k
        V = X @ self.W_v
        
        # Attention scores
        scores = (Q @ K.T) / self._sqrt_dim
        weights = self._softmax(scores.mean(axis=0))
        
        # Fusión vectorizada
        fused = weights @ V
        
        # Diccionario de pesos
        attention_weights = {names[i]: float(weights[i]) for i in range(n)}
        
        return fused, attention_weights
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax numéricamente estable."""
        exp_x = np.exp(x - x.max())
        return exp_x / exp_x.sum()


# =============================================================================
# 3. HIERARCHICAL PREDICTOR (Predictive Coding) - OPTIMIZADO
# =============================================================================

class HierarchicalPredictor:
    """
    Modelo generativo jerárquico - OPTIMIZADO.
    Removidas matrices W_up/W_down no usadas.
    """
    
    def __init__(self, dims: List[int] = [64, 32, 16]):
        self.dims = dims
        self.n_levels = len(dims)
        
        # Estado de cada nivel (pre-allocated)
        self.mu = [np.zeros(d, dtype=np.float64) for d in dims]
        self.sigma = [np.ones(d, dtype=np.float64) for d in dims]
        self.error = [np.zeros(d, dtype=np.float64) for d in dims]
        
        # Pre-calcular ratios entre niveles
        self._block_sizes = []
        for i in range(1, len(dims)):
            self._block_sizes.append(dims[i-1] // dims[i])
        
        # Historial (deque es eficiente para append/pop)
        self.surprise_history = deque(maxlen=50)
        self._avg_surprise = 0.0
    
    def predict_and_update(self, observation: np.ndarray) -> Dict:
        """Ciclo de predicción - OPTIMIZADO."""
        # Normalizar observación
        obs = _normalize_dim(observation, self.dims[0])
        
        total_surprise = 0.0
        level_errors = []
        
        for i in range(self.n_levels):
            if i == 0:
                target = obs
            else:
                # OPTIMIZADO: reshape + mean vectorizado
                prev = self.mu[i-1]
                bs = self._block_sizes[i-1]
                if bs > 0:
                    # Reshape and mean por bloques
                    target = prev[:bs * self.dims[i]].reshape(-1, bs).mean(axis=1)
                else:
                    target = prev[:self.dims[i]]
            
            # Error de predicción
            self.error[i] = target - self.mu[i]
            err_sq = self.error[i] ** 2
            level_errors.append(float(err_sq.mean()))
            
            # Actualizar predicción (precision-weighted)
            precision = 1.0 / (self.sigma[i] + 1e-6)
            self.mu[i] += 0.1 * precision * self.error[i]
            
            total_surprise += err_sq.sum()
        
        # Free energy
        complexity = sum(s.sum() for s in self.sigma)
        free_energy = total_surprise + 0.01 * complexity
        
        # Actualizar historial y promedio
        self.surprise_history.append(total_surprise)
        self._avg_surprise = np.mean(self.surprise_history) if self.surprise_history else 0
        
        return {
            'predictions': [m.copy() for m in self.mu],
            'errors': level_errors,
            'surprise': float(total_surprise),
            'free_energy': float(free_energy),
            'is_surprising': total_surprise > self._avg_surprise * 1.5 if self._avg_surprise > 0 else False
        }


# =============================================================================
# 4. GLOBAL WORKSPACE (Consciencia) - OPTIMIZADO
# =============================================================================

@dataclass(slots=True)  # slots para menor uso de memoria
class Coalition:
    contenido: np.ndarray
    saliencia: float
    origen: str
    timestamp: float


class GlobalWorkspace:
    """Global Workspace - OPTIMIZADO con slots y menos copias."""
    
    __slots__ = ['capacity', 'coalitions', 'conscious_content', 'broadcast_count']
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.coalitions: List[Coalition] = []
        self.conscious_content: Optional[Coalition] = None
        self.broadcast_count = 0
    
    def add_coalition(self, contenido: np.ndarray, saliencia: float, origen: str):
        """Añade coalición - sin time.time() costoso."""
        self.coalitions.append(Coalition(
            contenido=contenido,
            saliencia=saliencia,
            origen=origen,
            timestamp=self.broadcast_count  # Usar contador en vez de time.time()
        ))
    
    def compete_and_broadcast(self) -> Optional[Dict]:
        """Winner-take-all - OPTIMIZADO."""
        if not self.coalitions:
            return None
        
        # Encontrar máximo directamente (más rápido que sort completo)
        winner = max(self.coalitions, key=lambda c: c.saliencia)
        self.conscious_content = winner
        self.broadcast_count += 1
        
        # Mantener solo capacity elementos
        if len(self.coalitions) > self.capacity:
            self.coalitions = sorted(self.coalitions, 
                                     key=lambda c: c.saliencia, 
                                     reverse=True)[:self.capacity]
        
        return {
            'contenido': winner.contenido,
            'origen': winner.origen,
            'saliencia': winner.saliencia,
            'broadcast_id': self.broadcast_count
        }


# =============================================================================
# 5. PHI CALCULATOR - OPTIMIZADO
# =============================================================================

class PhiCalculator:
    """Calcula Φ - OPTIMIZADO con cache de bins."""
    
    __slots__ = ['_bins']
    
    def __init__(self):
        self._bins = 20
    
    def calculate(self, states: List[np.ndarray]) -> float:
        """Calcula Φ aproximado - OPTIMIZADO."""
        if not states or len(states) < 2:
            return 0.0
        
        # Concatenar una sola vez
        all_states = np.concatenate([s.ravel() for s in states])
        H_total = self._entropy(all_states)
        
        # Suma de entropías individuales
        H_parts = sum(self._entropy(s.ravel()) for s in states)
        
        # Phi normalizado
        phi = max(0, H_parts - H_total) / (len(states) + 1e-6)
        
        return float(phi)
    
    def _entropy(self, x: np.ndarray) -> float:
        """Entropía de Shannon - OPTIMIZADO."""
        if len(x) == 0:
            return 0.0
        
        bins = min(self._bins, len(x))
        hist, _ = np.histogram(x, bins=bins, density=True)
        hist = hist[hist > 0]
        
        return float(-np.sum(hist * np.log2(hist + 1e-10))) if len(hist) > 0 else 0.0


# =============================================================================
# 6. VISUALIZADOR GRÁFICO - OPTIMIZADO
# =============================================================================

class VisualizadorPerceptual:
    """Genera visualizaciones - OPTIMIZADO con strings pre-calculados."""
    
    def __init__(self, width: int = 40, height: int = 20):
        self.width = width
        self.height = height
        
        # Pre-calcular strings constantes
        self._header = "╔" + "═" * (width - 2) + "╗"
        self._footer = "╚" + "═" * (width - 2) + "╝"
        self._separator_double = "╠" + "═" * (width - 2) + "╣"
        self._separator_single = "╠" + "─" * (width - 2) + "╣"
        self._title = "║" + " PERCEPCIÓN ACTUAL ".center(width - 2) + "║"
        self._attention_label = "║" + " ATENCIÓN: ".ljust(width - 2) + "║"
        
        # Caracteres para matriz visual
        self._chars = " ·∘○◎●◉"
        self._n_chars = len(self._chars)
        
        # Seed fijo para reproducibilidad en visualización
        self._rng = np.random.RandomState(42)
    
    def generar_mapa_calor(self, 
                           coherence: float,
                           attention: Dict[str, float],
                           surprise: float,
                           phi: float) -> str:
        """Genera mapa de calor ASCII - OPTIMIZADO."""
        lines = [
            self._header,
            self._title,
            self._separator_double,
            self._barra("Coherencia", coherence),
            self._barra("Sorpresa", surprise),
            self._barra("Φ (integr.)", phi),
            self._separator_single,
            self._attention_label,
        ]
        
        # Atención (máximo 3)
        for name, weight in list(attention.items())[:3]:
            lines.append(self._barra(f"  {name[:8]}", weight))
        
        lines.append(self._separator_single)
        
        # Mapa visual
        lines.extend(self._generar_matriz_visual(coherence, surprise, phi))
        
        lines.append(self._footer)
        
        return "\n".join(lines)
    
    def _barra(self, label: str, value: float, max_len: int = 15) -> str:
        """Genera barra de progreso - OPTIMIZADO."""
        label_str = label[:10].ljust(10)
        filled = int(value * max_len)
        bar = "█" * filled + "░" * (max_len - filled)
        content = f" {label_str} {bar} {value*100:5.1f}%"
        return "║" + content.ljust(self.width - 2) + "║"
    
    def _generar_matriz_visual(self, coherence: float, 
                                surprise: float, phi: float) -> List[str]:
        """Genera matriz visual - OPTIMIZADO con vectorización."""
        # Crear grid vectorizado
        rows, cols = 5, 20
        
        # Base coherence (uniforme)
        grid = np.full((rows, cols), coherence * 0.3)
        
        # Sorpresa: usar patrón fijo en vez de random cada vez
        self._rng.seed(42)  # Reset seed para consistencia
        grid += surprise * self._rng.random((rows, cols)) * 0.4
        
        # Phi: patrón radial desde centro
        y, x = np.ogrid[:rows, :cols]
        dist = np.abs(x - cols//2) / (cols//2) + np.abs(y - rows//2) / (rows//2)
        grid += phi * (1 - dist/2) * 0.3
        
        # Clamp y convertir a índices
        grid = np.clip(grid, 0, 1)
        indices = (grid * (self._n_chars - 1)).astype(int)
        
        # Convertir a strings
        lines = []
        for row in indices:
            line = "".join(self._chars[i] for i in row)
            lines.append("║" + line.center(self.width - 2) + "║")
        
        return lines


# =============================================================================
# 7. SISTEMA INTEGRADO - OPTIMIZADO
# =============================================================================

@dataclass(slots=True)
class PercepcionResult:
    """Resultado de una percepción - con slots para eficiencia + Wolfram metrics."""
    timestamp: float
    consciente: bool
    coherence: float
    surprise: float
    free_energy: float
    phi: float
    attention_weights: Dict[str, float]
    es_sorprendente: bool
    integracion: str
    mapa_visual: str
    descripcion: str
    # Wolfram metrics
    lyapunov: float = 0.0
    complexity: float = 0.0
    is_class4: bool = False
    chaos_score: float = 0.5
    causal_density: float = 0.0


class SistemaPerceptualAvanzado:
    """Sistema perceptual completo - OPTIMIZADO + WOLFRAM."""
    
    __slots__ = ['gamma', 'attention', 'predictor', 'workspace', 
                 'phi_calc', 'visualizer', 'tick_count', 'last_result',
                 'causal_graph', 'class4_metrics', '_last_node_id']
    
    def __init__(self):
        self.gamma = GammaOscillator(40.0)
        self.attention = CrossModalAttention(64)
        self.predictor = HierarchicalPredictor([64, 32, 16])
        self.workspace = GlobalWorkspace(7)
        self.phi_calc = PhiCalculator()
        self.visualizer = VisualizadorPerceptual()
        
        # Wolfram modules
        self.causal_graph = CausalGraph(1000)
        self.class4_metrics = Class4Metrics(100)
        self._last_node_id = -1
        
        self.tick_count = 0
        self.last_result: Optional[PercepcionResult] = None
    
    def percibir(self, dendritas: Dict[str, np.ndarray]) -> PercepcionResult:
        """Procesa inputs - OPTIMIZADO + WOLFRAM."""
        self.tick_count += 1
        self.gamma.tick()
        
        # 1. Gamma Binding
        coherence = self.gamma.compute_coherence(list(dendritas.values()))
        
        # 2. Cross-Modal Attention
        fused, attention_weights = self.attention.fuse(dendritas)
        
        # 3. Hierarchical Prediction
        pred = self.predictor.predict_and_update(fused)
        
        # 4. Global Workspace
        saliencia = 1.0 / (1.0 + pred['surprise'])
        self.workspace.add_coalition(fused, saliencia, "fusion")
        broadcast = self.workspace.compete_and_broadcast()
        
        # 5. Phi
        phi = self.phi_calc.calculate(pred['predictions'])
        
        # 6. WOLFRAM: Class 4 Metrics
        energy = float(np.mean(np.abs(fused)))
        entropy = float(np.std(fused))
        wolfram = self.class4_metrics.update(energy, entropy, pred['surprise'])
        
        # 7. WOLFRAM: Causal Graph
        node_id = self.causal_graph.add_node(
            surprise=pred['surprise'],
            phi=phi,
            coherence=coherence,
            parent_id=self._last_node_id
        )
        self._last_node_id = node_id
        causal_density = self.causal_graph.compute_causal_density()
        
        # 8. Integración
        integracion = "alta" if phi > 0.5 else ("media" if phi > 0.2 else "baja")
        
        # 9. Visualización
        mapa_visual = self.visualizer.generar_mapa_calor(
            coherence=coherence,
            attention=attention_weights,
            surprise=min(1.0, pred['surprise'] / 10),
            phi=min(1.0, phi)
        )
        
        # 10. Descripción (incluye Clase 4)
        descripcion = self._generar_descripcion(
            coherence, pred['is_surprising'], phi, broadcast, wolfram['is_class4']
        )
        
        result = PercepcionResult(
            timestamp=self.tick_count,
            consciente=broadcast is not None,
            coherence=coherence,
            surprise=pred['surprise'],
            free_energy=pred['free_energy'],
            phi=phi,
            attention_weights=attention_weights,
            es_sorprendente=pred['is_surprising'],
            integracion=integracion,
            mapa_visual=mapa_visual,
            descripcion=descripcion,
            # Wolfram metrics
            lyapunov=wolfram['lyapunov'],
            complexity=wolfram['complexity'],
            is_class4=wolfram['is_class4'],
            chaos_score=wolfram['chaos_score'],
            causal_density=causal_density
        )
        
        self.last_result = result
        return result
    
    def _generar_descripcion(self, coherence: float, is_surprising: bool, 
                             phi: float, broadcast, is_class4: bool = False) -> str:
        """Genera descripción - OPTIMIZADO + WOLFRAM."""
        parts = ["[CONSCIENTE]"] if broadcast else []
        parts.append("¡SORPRESA!" if is_surprising else "predecible")
        parts.append("integrado" if phi > 0.5 else "fragmentado")
        if coherence > 0.7:
            parts.append("coherente")
        if is_class4:
            parts.append("CLASE-4")  # Borde del caos
        return " | ".join(parts)
    
    def ver(self) -> str:
        """Retorna visualización actual."""
        return self.last_result.mapa_visual if self.last_result else "Sin percepción."


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    import time as t
    
    print("=" * 50)
    print("  SISTEMA PERCEPTUAL OPTIMIZADO - TEST")
    print("=" * 50)
    
    sistema = SistemaPerceptualAvanzado()
    
    # Benchmark
    dendritas_test = {
        "energia": np.random.randn(32),
        "entropia": np.random.randn(32) * 0.5,
        "concepto": np.random.randn(32),
    }
    
    # Warmup
    for _ in range(10):
        sistema.percibir(dendritas_test)
    
    # Medir tiempo
    start = t.perf_counter()
    N = 100
    for _ in range(N):
        sistema.percibir(dendritas_test)
    elapsed = t.perf_counter() - start
    
    print(f"\n⏱️  BENCHMARK:")
    print(f"   {N} percepciones en {elapsed*1000:.2f} ms")
    print(f"   Promedio: {elapsed/N*1000:.3f} ms por percepción")
    print(f"   Tasa: {N/elapsed:.1f} percepciones/segundo")
    
    # Mostrar una percepción
    print(f"\n{'─' * 50}")
    print("  ÚLTIMA PERCEPCIÓN:")
    print(f"{'─' * 50}")
    
    resultado = sistema.percibir(dendritas_test)
    print(resultado.mapa_visual)
    print(f"\n  Estado: {resultado.descripcion}")
    print(f"  Coherencia: {resultado.coherence:.3f}")
    print(f"  Sorpresa: {resultado.surprise:.3f}")
    print(f"  Phi (Φ): {resultado.phi:.3f}")
    
    print("\n" + "=" * 50)
    print("  SISTEMA OPTIMIZADO ✓")
    print("=" * 50)
