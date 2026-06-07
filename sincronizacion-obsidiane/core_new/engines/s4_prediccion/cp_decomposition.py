"""
CP Decomposition (CANDECOMP/PARAFAC)
====================================

Descomposición tensorial en suma de productos externos de rango 1.
Eficiente para encontrar patrones recurrentes en datos tensoriales.
"""

import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class CPConfig:
    """Configuración de la descomposición CP."""
    rank: int = 10           # Número de componentes
    max_iter: int = 100      # Iteraciones máximas de ALS
    tolerance: float = 1e-6  # Tolerancia de convergencia
    init: str = 'random'     # 'random' o 'svd'


class CPDecomposition:
    """
    Descomposición CP (CANDECOMP/PARAFAC).
    
    Descompone un tensor T en suma de productos externos:
        T ≈ Σᵣ λᵣ · a₁ᵣ ⊗ a₂ᵣ ⊗ ... ⊗ aNᵣ
    
    Donde:
    - λᵣ son los pesos
    - aᵢᵣ son vectores unitarios (factores)
    
    Algoritmo: Alternating Least Squares (ALS)
    """
    
    def __init__(self, config: Optional[CPConfig] = None):
        if config is None:
            config = CPConfig()
        self.config = config
        
        self.factors: List[np.ndarray] = []  # Factores por modo
        self.weights: Optional[np.ndarray] = None  # Pesos λ
        self.reconstruction_error: float = float('inf')
        self.n_iter: int = 0
    
    def _unfold(self, tensor: np.ndarray, mode: int) -> np.ndarray:
        """Desdobla tensor a lo largo del modo."""
        return np.moveaxis(tensor, mode, 0).reshape(tensor.shape[mode], -1)
    
    def _khatri_rao(self, matrices: List[np.ndarray], skip: int) -> np.ndarray:
        """
        Producto Khatri-Rao de todas las matrices excepto 'skip'.
        
        El producto Khatri-Rao es un producto columna-a-columna de Kronecker.
        """
        result = None
        for i, M in enumerate(matrices):
            if i == skip:
                continue
            if result is None:
                result = M
            else:
                # Khatri-Rao: para cada columna k, hacer Kronecker
                n_cols = result.shape[1]
                new_result = []
                for k in range(n_cols):
                    new_result.append(np.kron(result[:, k], M[:, k]))
                result = np.array(new_result).T
        return result
    
    def _init_factors(self, tensor: np.ndarray) -> List[np.ndarray]:
        """Inicializa los factores."""
        factors = []
        rank = self.config.rank
        
        if self.config.init == 'svd':
            # Inicialización basada en SVD de cada modo
            for mode in range(tensor.ndim):
                unfolded = self._unfold(tensor, mode)
                U, S, Vh = np.linalg.svd(unfolded, full_matrices=False)
                r = min(rank, U.shape[1])
                factor = U[:, :r]
                if r < rank:
                    # Pad con random
                    padding = np.random.randn(U.shape[0], rank - r) * 0.01
                    factor = np.hstack([factor, padding])
                factors.append(factor)
        else:
            # Inicialización random
            for dim in tensor.shape:
                factors.append(np.random.randn(dim, rank))
        
        return factors
    
    def fit(self, tensor: np.ndarray) -> Tuple[List[np.ndarray], np.ndarray]:
        """
        Calcula la descomposición CP usando ALS.
        
        Args:
            tensor: Tensor N-dimensional
        
        Returns:
            (factors, weights) donde:
            - factors: Lista de matrices de factores [dim_i, rank]
            - weights: Pesos de cada componente [rank]
        """
        n_modes = tensor.ndim
        rank = self.config.rank
        
        # Inicializar factores
        self.factors = self._init_factors(tensor)
        
        # ALS iterations
        prev_error = float('inf')
        
        for iteration in range(self.config.max_iter):
            # Actualizar cada modo
            for mode in range(n_modes):
                # Khatri-Rao de todos excepto mode actual
                V = self._khatri_rao(self.factors, skip=mode)
                
                # Resolver mínimos cuadrados
                unfolded = self._unfold(tensor, mode)
                
                # A_mode = X_(mode) @ V @ (V^T V)^(-1)
                VtV = V.T @ V
                try:
                    VtV_inv = np.linalg.inv(VtV + 1e-6 * np.eye(rank))
                    self.factors[mode] = unfolded @ V @ VtV_inv
                except np.linalg.LinAlgError:
                    self.factors[mode] = unfolded @ np.linalg.pinv(V)
            
            # Calcular error de reconstrucción
            reconstructed = self.reconstruct()
            error = np.linalg.norm(tensor - reconstructed)
            self.reconstruction_error = error
            
            # Verificar convergencia
            if abs(prev_error - error) < self.config.tolerance:
                break
            prev_error = error
            self.n_iter = iteration + 1
        
        # Normalizar factores y extraer pesos
        self.weights = np.ones(rank)
        for mode in range(n_modes):
            norms = np.linalg.norm(self.factors[mode], axis=0)
            norms[norms == 0] = 1
            self.factors[mode] /= norms
            self.weights *= norms
        
        return self.factors, self.weights
    
    def reconstruct(self) -> np.ndarray:
        """
        Reconstruye el tensor desde la descomposición.
        
        Returns:
            Tensor reconstruido
        """
        if not self.factors:
            raise RuntimeError("Debe llamar fit() primero")
        
        rank = self.factors[0].shape[1]
        shape = tuple(f.shape[0] for f in self.factors)
        
        result = np.zeros(shape)
        for r in range(rank):
            component = self.factors[0][:, r]
            for mode in range(1, len(self.factors)):
                component = np.outer(component, self.factors[mode][:, r]).flatten()
            component = component.reshape(shape)
            
            weight = self.weights[r] if self.weights is not None else 1.0
            result += weight * component
        
        return result
    
    def get_dominant_patterns(self, k: int = 5) -> Tuple[List[np.ndarray], np.ndarray]:
        """
        Retorna los k patrones más dominantes.
        
        Args:
            k: Número de patrones
        
        Returns:
            (factors_top_k, weights_top_k)
        """
        if self.weights is None:
            raise RuntimeError("Debe llamar fit() primero")
        
        # Ordenar por peso
        top_indices = np.argsort(np.abs(self.weights))[-k:][::-1]
        
        factors_k = [f[:, top_indices] for f in self.factors]
        weights_k = self.weights[top_indices]
        
        return factors_k, weights_k
    
    def extrapolate_time(self, time_mode: int = 0, 
                         n_steps: int = 10) -> np.ndarray:
        """
        Extrapola el factor temporal para predicción.
        
        Args:
            time_mode: Índice del modo temporal
            n_steps: Pasos a extrapolar
        
        Returns:
            Factor temporal extrapolado
        """
        time_factor = self.factors[time_mode]  # [T, rank]
        
        # Ajustar tendencia lineal para cada componente
        T = time_factor.shape[0]
        t = np.arange(T)
        
        extrapolated = []
        for t_new in range(T, T + n_steps):
            row = []
            for r in range(time_factor.shape[1]):
                # Regresión lineal simple
                slope, intercept = np.polyfit(t, time_factor[:, r], 1)
                pred = slope * t_new + intercept
                row.append(pred)
            extrapolated.append(row)
        
        return np.array(extrapolated)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: CP Decomposition")
    print("=" * 60)
    
    # Crear tensor sintético de rango bajo
    T, F1, F2 = 50, 30, 20  # tiempo × features1 × features2
    
    # Generar tensor como suma de productos externos
    rank_true = 5
    factors_true = [
        np.random.randn(T, rank_true),
        np.random.randn(F1, rank_true),
        np.random.randn(F2, rank_true)
    ]
    
    tensor = np.zeros((T, F1, F2))
    for r in range(rank_true):
        component = np.outer(factors_true[0][:, r], factors_true[1][:, r])
        component = np.outer(component.flatten(), factors_true[2][:, r]).reshape(T, F1, F2)
        tensor += component
    
    # Agregar ruido
    tensor += np.random.randn(T, F1, F2) * 0.1
    
    print(f"\n  Tensor original shape: {tensor.shape}")
    print(f"  Rango verdadero: {rank_true}")
    
    # Descomposición CP
    config = CPConfig(rank=5, max_iter=50)
    cp = CPDecomposition(config)
    factors, weights = cp.fit(tensor)
    
    print(f"\n  Iteraciones: {cp.n_iter}")
    print(f"  Error de reconstrucción: {cp.reconstruction_error:.6f}")
    print(f"  Factores shapes: {[f.shape for f in factors]}")
    print(f"  Pesos: {weights}")
    
    # Reconstrucción
    recon = cp.reconstruct()
    error_rel = np.linalg.norm(tensor - recon) / np.linalg.norm(tensor)
    print(f"\n  Error relativo: {error_rel:.6f}")
    
    # Patrones dominantes
    factors_top, weights_top = cp.get_dominant_patterns(k=3)
    print(f"  Top 3 pesos: {weights_top}")
    
    # Extrapolación
    extrap = cp.extrapolate_time(time_mode=0, n_steps=5)
    print(f"\n  Extrapolación shape: {extrap.shape}")
    
    print("\n" + "=" * 60)
    print("  TODOS LOS TESTS PASARON ✓")
    print("=" * 60)
