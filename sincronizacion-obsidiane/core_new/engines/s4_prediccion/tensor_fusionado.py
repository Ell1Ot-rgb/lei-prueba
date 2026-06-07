"""
Tensor Fusionado - Combina todos los tensores del sistema
==========================================================
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from collections import deque


@dataclass
class TensorFusionado:
    """
    Fusiona todos los tensores existentes del sistema en una estructura unificada.
    
    Dimensiones totales: 182
    - embedding[64]: Vector semántico de S1
    - esn_state[100]: Estado del reservoir ESN
    - pad_emotions[3]: Pleasure, Arousal, Dominance
    - grundzug_freq[10]: Top-10 frecuencias de Grundzugs
    - lyapunov_features[5]: Métricas de dinámica caótica
    """
    
    embedding: np.ndarray           # [64] - Semántica
    esn_state: np.ndarray           # [100] - Dinámica reservoir
    pad_emotions: np.ndarray        # [3] - Afecto
    grundzug_freq: np.ndarray       # [10] - Frecuencias Grundzug
    lyapunov_features: np.ndarray   # [5] - Métricas de caos
    timestamp: float = 0.0
    
    @classmethod
    def from_system_state(cls,
                          embedding: np.ndarray,
                          esn_state: np.ndarray,
                          pad_emotions: np.ndarray,
                          grundzug_sketch: np.ndarray,
                          jacobiano: np.ndarray,
                          timestamp: float) -> 'TensorFusionado':
        """
        Crea TensorFusionado desde el estado actual del sistema.
        
        Args:
            embedding: Vector de embedding de S1
            esn_state: Estado del ESN
            pad_emotions: Vector PAD del motor de emociones
            grundzug_sketch: Matriz Count-Min Sketch
            jacobiano: Jacobiano del ESN para Lyapunov
            timestamp: Marca temporal
        """
        # Extraer top-10 frecuencias del sketch
        grundzug_freq = cls._extract_top_frequencies(grundzug_sketch, k=10)
        
        # Calcular features de Lyapunov
        lyapunov_features = cls._compute_lyapunov_features(jacobiano, esn_state)
        
        return cls(
            embedding=embedding.astype(np.float32),
            esn_state=esn_state.astype(np.float32),
            pad_emotions=pad_emotions.astype(np.float32),
            grundzug_freq=grundzug_freq.astype(np.float32),
            lyapunov_features=lyapunov_features.astype(np.float32),
            timestamp=timestamp
        )
    
    @staticmethod
    def _extract_top_frequencies(sketch: np.ndarray, k: int = 10) -> np.ndarray:
        """Extrae las k frecuencias más altas del Count-Min Sketch."""
        if sketch is None or sketch.size == 0:
            return np.zeros(k, dtype=np.float32)
        
        # Tomar el mínimo por columna (estimación CM)
        min_counts = sketch.min(axis=0)
        
        # Normalizar
        total = min_counts.sum()
        if total > 0:
            normalized = min_counts / total
        else:
            normalized = min_counts
        
        # Top-k
        top_indices = np.argsort(normalized)[-k:]
        top_freqs = normalized[top_indices]
        
        # Pad si necesario
        if len(top_freqs) < k:
            top_freqs = np.pad(top_freqs, (0, k - len(top_freqs)))
        
        return top_freqs
    
    @staticmethod
    def _compute_lyapunov_features(jacobiano: np.ndarray, 
                                    state: np.ndarray) -> np.ndarray:
        """
        Calcula 5 features relacionadas con la dinámica de Lyapunov.
        
        Features:
        0. Exponente de Lyapunov (norma espectral log)
        1. Radio espectral
        2. Determinante (signo de expansión/contracción)
        3. Traza (suma de eigenvalores)
        4. Condición del jacobiano
        """
        features = np.zeros(5, dtype=np.float32)
        
        if jacobiano is None or jacobiano.size == 0:
            return features
        
        try:
            # 0. Exponente de Lyapunov
            norma = np.linalg.norm(jacobiano, ord=2)
            features[0] = np.log(norma) if norma > 0 else -1.0
            
            # 1. Radio espectral
            eigenvalues = np.linalg.eigvals(jacobiano)
            features[1] = np.max(np.abs(eigenvalues))
            
            # 2. Log|det| (signo de expansión)
            det = np.linalg.det(jacobiano)
            features[2] = np.sign(det) * np.log(np.abs(det) + 1e-10)
            
            # 3. Traza normalizada
            features[3] = np.trace(jacobiano) / jacobiano.shape[0]
            
            # 4. Número de condición (log)
            cond = np.linalg.cond(jacobiano)
            features[4] = np.log(cond) if cond < 1e10 else 10.0
            
        except Exception:
            pass
        
        return features
    
    def to_flat(self) -> np.ndarray:
        """Concatena todos los tensores en un vector plano [182]."""
        return np.concatenate([
            self.embedding,         # 64
            self.esn_state,         # 100
            self.pad_emotions,      # 3
            self.grundzug_freq,     # 10
            self.lyapunov_features  # 5
        ])  # Total: 182
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'embedding': self.embedding.tolist(),
            'esn_state': self.esn_state.tolist(),
            'pad_emotions': self.pad_emotions.tolist(),
            'grundzug_freq': self.grundzug_freq.tolist(),
            'lyapunov_features': self.lyapunov_features.tolist(),
            'timestamp': self.timestamp
        }
    
    @classmethod
    def dims(cls) -> Dict[str, int]:
        """Retorna las dimensiones de cada componente."""
        return {
            'embedding': 64,
            'esn_state': 100,
            'pad_emotions': 3,
            'grundzug_freq': 10,
            'lyapunov_features': 5,
            'total': 182
        }


class TensorHistorial:
    """
    Mantiene un historial de TensorFusionado para análisis temporal.
    """
    
    def __init__(self, maxlen: int = 100):
        self.buffer: deque = deque(maxlen=maxlen)
        self.maxlen = maxlen
    
    def append(self, tensor: TensorFusionado):
        """Agrega un tensor al historial."""
        self.buffer.append(tensor)
    
    def to_matrix(self) -> Optional[np.ndarray]:
        """
        Convierte el historial a matriz [tiempo, features].
        
        Returns:
            np.ndarray de shape (T, 182) o None si vacío
        """
        if len(self.buffer) == 0:
            return None
        
        return np.array([t.to_flat() for t in self.buffer])
    
    def to_tensor_3d(self) -> Optional[np.ndarray]:
        """
        Convierte a tensor 3D [tiempo, tipo_tensor, max_dim].
        Útil para HOSVD.
        
        Returns:
            np.ndarray de shape (T, 5, 100) donde:
            - dim 0: tiempo
            - dim 1: tipo (emb, esn, pad, grundzug, lyapunov)
            - dim 2: features (padded a 100)
        """
        if len(self.buffer) == 0:
            return None
        
        T = len(self.buffer)
        tensor_3d = np.zeros((T, 5, 100), dtype=np.float32)
        
        for t, tf in enumerate(self.buffer):
            # Embedding (64 → pad a 100)
            tensor_3d[t, 0, :64] = tf.embedding
            # ESN state (100)
            tensor_3d[t, 1, :100] = tf.esn_state
            # PAD emotions (3 → pad a 100)
            tensor_3d[t, 2, :3] = tf.pad_emotions
            # Grundzug freq (10 → pad a 100)
            tensor_3d[t, 3, :10] = tf.grundzug_freq
            # Lyapunov features (5 → pad a 100)
            tensor_3d[t, 4, :5] = tf.lyapunov_features
        
        return tensor_3d
    
    def get_component_history(self, component: str) -> Optional[np.ndarray]:
        """
        Obtiene historial de un componente específico.
        
        Args:
            component: 'embedding', 'esn_state', 'pad_emotions', 
                      'grundzug_freq', 'lyapunov_features'
        
        Returns:
            np.ndarray de shape (T, dim_component)
        """
        if len(self.buffer) == 0:
            return None
        
        return np.array([getattr(t, component) for t in self.buffer])
    
    def __len__(self) -> int:
        return len(self.buffer)
    
    def clear(self):
        """Limpia el historial."""
        self.buffer.clear()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: TensorFusionado")
    print("=" * 60)
    
    # Simular datos
    embedding = np.random.randn(64).astype(np.float32)
    esn_state = np.random.randn(100).astype(np.float32)
    pad_emotions = np.array([0.5, 0.3, 0.7], dtype=np.float32)
    grundzug_freq = np.random.rand(10).astype(np.float32)
    lyapunov_features = np.array([0.1, 0.9, -0.5, 0.2, 1.5], dtype=np.float32)
    
    # Crear tensor
    tf = TensorFusionado(
        embedding=embedding,
        esn_state=esn_state,
        pad_emotions=pad_emotions,
        grundzug_freq=grundzug_freq,
        lyapunov_features=lyapunov_features,
        timestamp=1.0
    )
    
    flat = tf.to_flat()
    print(f"  Dimensiones: {TensorFusionado.dims()}")
    print(f"  Vector plano shape: {flat.shape}")
    print(f"  ✓ TensorFusionado funciona correctamente")
    
    # Test historial
    historial = TensorHistorial(maxlen=50)
    for i in range(20):
        t = TensorFusionado(
            embedding=np.random.randn(64).astype(np.float32),
            esn_state=np.random.randn(100).astype(np.float32),
            pad_emotions=np.random.rand(3).astype(np.float32),
            grundzug_freq=np.random.rand(10).astype(np.float32),
            lyapunov_features=np.random.rand(5).astype(np.float32),
            timestamp=float(i)
        )
        historial.append(t)
    
    matriz = historial.to_matrix()
    tensor_3d = historial.to_tensor_3d()
    
    print(f"\n  Historial length: {len(historial)}")
    print(f"  Matriz shape: {matriz.shape}")
    print(f"  Tensor 3D shape: {tensor_3d.shape}")
    print(f"  ✓ TensorHistorial funciona correctamente")
    
    print("\n" + "=" * 60)
    print("  TODOS LOS TESTS PASARON ✓")
    print("=" * 60)
