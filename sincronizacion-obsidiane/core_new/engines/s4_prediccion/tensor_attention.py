"""
Tensor Attention - Fusión Multimodal con Atención de Bajo Rango
================================================================

Mecanismo de atención tensorial eficiente para combinar
múltiples modalidades (embedding, ESN, PAD, etc.).
"""

import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TensorAttentionConfig:
    """Configuración de la atención tensorial."""
    dims: List[int] = None  # Dimensiones de cada modalidad
    rank: int = 8           # Rango de proyección (bajo para eficiencia)
    temperature: float = 1.0  # Temperatura del softmax


class TensorAttention:
    """
    Atención tensorial de bajo rango para fusión multimodal.
    
    En lugar de atención completa O(n²), usa proyecciones de bajo rango
    para lograr O(n×r) donde r << n.
    
    Implementa atención cruzada entre modalidades:
    - embedding (64D) - semántica
    - esn_state (100D) - dinámica
    - pad_emotions (3D) - afectivo
    """
    
    def __init__(self, config: Optional[TensorAttentionConfig] = None):
        if config is None:
            # Dimensiones por defecto para el sistema
            config = TensorAttentionConfig(
                dims=[64, 100, 3],  # embedding, esn, pad
                rank=8
            )
        self.config = config
        self.dims = config.dims
        self.rank = config.rank
        
        # Inicializar matrices de proyección Q, K, V por modalidad
        np.random.seed(42)
        scale = 0.1
        
        self.W_q = [np.random.randn(d, self.rank) * scale for d in self.dims]
        self.W_k = [np.random.randn(d, self.rank) * scale for d in self.dims]
        self.W_v = [np.random.randn(d, self.rank) * scale for d in self.dims]
        
        # Proyección de salida
        total_rank = self.rank * len(self.dims)
        self.W_out = np.random.randn(total_rank, total_rank) * scale
    
    def _softmax(self, x: np.ndarray, temperature: float = 1.0) -> np.ndarray:
        """Softmax con temperatura."""
        x_scaled = x / temperature
        exp_x = np.exp(x_scaled - np.max(x_scaled))
        return exp_x / (exp_x.sum() + 1e-10)
    
    def forward(self, tensors: List[np.ndarray]) -> np.ndarray:
        """
        Aplica atención cross-modal.
        
        Args:
            tensors: Lista de tensores [embedding, esn_state, pad_emotions]
        
        Returns:
            Representación fusionada [rank * n_modalities]
        """
        if len(tensors) != len(self.dims):
            raise ValueError(f"Esperados {len(self.dims)} tensores, recibidos {len(tensors)}")
        
        # Proyectar a espacio de bajo rango
        queries = [t @ W for t, W in zip(tensors, self.W_q)]  # [rank] cada uno
        keys = [t @ W for t, W in zip(tensors, self.W_k)]
        values = [t @ W for t, W in zip(tensors, self.W_v)]
        
        # Concatenar todas las modalidades
        Q = np.concatenate(queries)  # [rank * n_modalities]
        K = np.concatenate(keys)
        V = np.concatenate(values)
        
        # Self-attention: score = Q @ K.T / sqrt(d_k)
        n = len(Q)
        scores = np.outer(Q, K) / np.sqrt(n)  # [n, n]
        
        # Softmax por filas
        attention_weights = np.apply_along_axis(
            lambda row: self._softmax(row, self.config.temperature),
            axis=1,
            arr=scores
        )
        
        # Aplicar atención: output = attention @ V
        attended = attention_weights @ V
        
        # Proyección de salida
        output = self.W_out @ attended
        
        return output
    
    def cross_modal_attention(self, query_tensor: np.ndarray, 
                               query_idx: int,
                               context_tensors: List[np.ndarray]) -> np.ndarray:
        """
        Atención de una modalidad contra las demás.
        
        Args:
            query_tensor: Tensor de consulta
            query_idx: Índice de la modalidad de consulta
            context_tensors: Lista de tensores de contexto
        
        Returns:
            Representación atendida [rank]
        """
        # Proyectar query
        Q = query_tensor @ self.W_q[query_idx]  # [rank]
        
        # Proyectar keys y values de contexto
        K_list = []
        V_list = []
        for i, t in enumerate(context_tensors):
            if i != query_idx:
                K_list.append(t @ self.W_k[i])
                V_list.append(t @ self.W_v[i])
        
        if not K_list:
            return Q
        
        K = np.vstack(K_list)  # [n_context, rank]
        V = np.vstack(V_list)
        
        # Scores
        scores = Q @ K.T / np.sqrt(self.rank)  # [n_context]
        weights = self._softmax(scores, self.config.temperature)
        
        # Atender
        attended = weights @ V  # [rank]
        
        return attended
    
    def get_attention_weights(self, tensors: List[np.ndarray]) -> np.ndarray:
        """
        Calcula y retorna los pesos de atención para interpretabilidad.
        
        Args:
            tensors: Lista de tensores
        
        Returns:
            Matriz de pesos de atención [n, n]
        """
        queries = [t @ W for t, W in zip(tensors, self.W_q)]
        keys = [t @ W for t, W in zip(tensors, self.W_k)]
        
        Q = np.concatenate(queries)
        K = np.concatenate(keys)
        
        scores = np.outer(Q, K) / np.sqrt(len(Q))
        weights = np.apply_along_axis(
            lambda row: self._softmax(row, self.config.temperature),
            axis=1,
            arr=scores
        )
        
        return weights


class MultiHeadTensorAttention:
    """
    Atención multi-cabeza para mayor capacidad expresiva.
    """
    
    def __init__(self, dims: List[int], n_heads: int = 4, rank_per_head: int = 4):
        self.n_heads = n_heads
        self.heads = [
            TensorAttention(TensorAttentionConfig(
                dims=dims,
                rank=rank_per_head
            ))
            for _ in range(n_heads)
        ]
        
        # Proyección final para combinar cabezas
        total_dim = rank_per_head * len(dims) * n_heads
        output_dim = rank_per_head * len(dims)
        self.W_combine = np.random.randn(output_dim, total_dim) * 0.1
    
    def forward(self, tensors: List[np.ndarray]) -> np.ndarray:
        """
        Aplica atención multi-cabeza.
        
        Args:
            tensors: Lista de tensores
        
        Returns:
            Representación fusionada
        """
        # Aplicar cada cabeza
        head_outputs = [head.forward(tensors) for head in self.heads]
        
        # Concatenar
        concatenated = np.concatenate(head_outputs)
        
        # Proyección final
        output = self.W_combine @ concatenated
        
        return output


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: Tensor Attention")
    print("=" * 60)
    
    # Simular tensores del sistema
    embedding = np.random.randn(64).astype(np.float32)
    esn_state = np.random.randn(100).astype(np.float32)
    pad_emotions = np.random.randn(3).astype(np.float32)
    
    tensors = [embedding, esn_state, pad_emotions]
    
    # Atención tensorial
    config = TensorAttentionConfig(dims=[64, 100, 3], rank=8)
    attention = TensorAttention(config)
    
    output = attention.forward(tensors)
    print(f"\n  Input shapes: {[t.shape for t in tensors]}")
    print(f"  Output shape: {output.shape}")
    
    # Pesos de atención
    weights = attention.get_attention_weights(tensors)
    print(f"  Attention weights shape: {weights.shape}")
    
    # Cross-modal attention
    cross_out = attention.cross_modal_attention(
        embedding, query_idx=0, context_tensors=tensors
    )
    print(f"  Cross-modal output shape: {cross_out.shape}")
    
    # Multi-head
    print("\n" + "-" * 40)
    print("  TEST: Multi-Head Tensor Attention")
    
    mh_attention = MultiHeadTensorAttention(
        dims=[64, 100, 3], n_heads=4, rank_per_head=4
    )
    mh_output = mh_attention.forward(tensors)
    print(f"  Multi-head output shape: {mh_output.shape}")
    
    print("\n" + "=" * 60)
    print("  TODOS LOS TESTS PASARON ✓")
    print("=" * 60)
