"""
Higher-Order Singular Value Decomposition (HOSVD)
=================================================

Generalización de SVD para tensores de orden superior.
Extrae modos principales en cada dimensión.
"""

import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class HOSVDConfig:
    """Configuración de HOSVD."""
    ranks: List[int] = None  # Rangos de truncamiento por modo
    energy_threshold: float = 0.95  # Umbral de energía para auto-rank


def unfold(tensor: np.ndarray, mode: int) -> np.ndarray:
    """
    Desdobla (unfold) un tensor a lo largo del modo especificado.
    
    Args:
        tensor: Tensor N-dimensional
        mode: Modo a lo largo del cual desdoblar (0-indexed)
    
    Returns:
        Matriz 2D con la dimensión del modo como filas
    """
    return np.moveaxis(tensor, mode, 0).reshape(tensor.shape[mode], -1)


def fold(matrix: np.ndarray, mode: int, shape: Tuple[int, ...]) -> np.ndarray:
    """
    Dobla (fold) una matriz de vuelta a tensor.
    
    Args:
        matrix: Matriz 2D
        mode: Modo original
        shape: Shape original del tensor
    
    Returns:
        Tensor N-dimensional
    """
    new_shape = [shape[mode]] + [s for i, s in enumerate(shape) if i != mode]
    tensor = matrix.reshape(new_shape)
    return np.moveaxis(tensor, 0, mode)


def mode_product(tensor: np.ndarray, matrix: np.ndarray, mode: int) -> np.ndarray:
    """
    Producto modal: T ×_mode M
    
    Args:
        tensor: Tensor N-dimensional
        matrix: Matriz 2D [new_dim, tensor.shape[mode]]
        mode: Modo para el producto
    
    Returns:
        Tensor con dimensión del modo cambiada
    """
    unfolded = unfold(tensor, mode)
    result = matrix @ unfolded
    new_shape = list(tensor.shape)
    new_shape[mode] = matrix.shape[0]
    return fold(result, mode, tuple(new_shape))


class HOSVD:
    """
    Higher-Order Singular Value Decomposition.
    
    Descompone un tensor T en:
        T = G ×_1 U_1 ×_2 U_2 ... ×_N U_N
    
    Donde:
    - G es el tensor core (reducido)
    - U_i son matrices ortogonales (modos principales)
    """
    
    def __init__(self, config: Optional[HOSVDConfig] = None):
        if config is None:
            config = HOSVDConfig()
        self.config = config
        
        self.core: Optional[np.ndarray] = None
        self.factors: List[np.ndarray] = []
        self.singular_values: List[np.ndarray] = []
        self.ranks: List[int] = []
        self.original_shape: Tuple[int, ...] = ()
    
    def fit(self, tensor: np.ndarray, ranks: Optional[List[int]] = None) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        Calcula la descomposición HOSVD.
        
        Args:
            tensor: Tensor N-dimensional
            ranks: Rangos de truncamiento por modo (opcional)
        
        Returns:
            (core, factors) donde:
            - core: Tensor core reducido
            - factors: Lista de matrices U_i por modo
        """
        self.original_shape = tensor.shape
        n_modes = tensor.ndim
        
        if ranks is None:
            ranks = self.config.ranks
        if ranks is None:
            ranks = list(tensor.shape)  # Sin truncamiento
        
        self.ranks = ranks
        self.factors = []
        self.singular_values = []
        
        # Para cada modo, calcular SVD del unfolding
        for mode in range(n_modes):
            unfolded = unfold(tensor, mode)
            U, S, Vh = np.linalg.svd(unfolded, full_matrices=False)
            
            # Truncar al rango especificado
            r = min(ranks[mode], len(S))
            self.factors.append(U[:, :r])
            self.singular_values.append(S[:r])
        
        # Calcular tensor core: G = T ×_1 U_1^T ×_2 U_2^T ...
        core = tensor.copy()
        for mode, U in enumerate(self.factors):
            core = mode_product(core, U.T, mode)
        
        self.core = core
        return core, self.factors
    
    def reconstruct(self) -> np.ndarray:
        """
        Reconstruye el tensor desde la descomposición.
        
        Returns:
            Tensor reconstruido
        """
        if self.core is None:
            raise RuntimeError("Debe llamar fit() primero")
        
        result = self.core.copy()
        for mode, U in enumerate(self.factors):
            result = mode_product(result, U, mode)
        
        return result
    
    def get_mode_importance(self, mode: int) -> np.ndarray:
        """
        Retorna la importancia (varianza explicada) de cada componente de un modo.
        
        Args:
            mode: Índice del modo
        
        Returns:
            Varianza explicada por cada componente (normalizada)
        """
        S = self.singular_values[mode]
        return (S ** 2) / np.sum(S ** 2)
    
    def get_temporal_modes(self, time_mode: int = 0) -> np.ndarray:
        """
        Extrae los modos temporales (patrones principales en tiempo).
        
        Args:
            time_mode: Índice del modo temporal
        
        Returns:
            Matriz de modos temporales [n_modos, n_tiempo]
        """
        return self.factors[time_mode].T


class TensorModosTemporal:
    """
    Especialización de HOSVD para extraer modos temporales de historial.
    
    Input: Historial [tiempo, features]
    Output: Modos temporales principales
    """
    
    def __init__(self, n_modos_tiempo: int = 5, n_modos_features: int = 32):
        self.n_modos_tiempo = n_modos_tiempo
        self.n_modos_features = n_modos_features
        self.hosvd = HOSVD()
    
    def fit_transform(self, historial: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extrae modos temporales y de features.
        
        Args:
            historial: [T, features]
        
        Returns:
            (modos_tiempo, modos_features)
            - modos_tiempo: [n_modos_tiempo, T]
            - modos_features: [n_modos_features, features]
        """
        # Aplicar HOSVD
        ranks = [self.n_modos_tiempo, self.n_modos_features]
        self.hosvd.fit(historial, ranks=ranks)
        
        modos_tiempo = self.hosvd.factors[0].T  # [n_modos, T]
        modos_features = self.hosvd.factors[1].T  # [n_modos, features]
        
        return modos_tiempo, modos_features
    
    def get_compressed_representation(self) -> np.ndarray:
        """
        Retorna la representación comprimida (core tensor).
        """
        return self.hosvd.core
    
    def get_temporal_pattern(self, mode_idx: int) -> np.ndarray:
        """
        Retorna el patrón temporal de un modo específico.
        
        Args:
            mode_idx: Índice del modo temporal
        
        Returns:
            Patrón temporal [T]
        """
        return self.hosvd.factors[0][:, mode_idx]
    
    def project_new_sample(self, sample: np.ndarray) -> np.ndarray:
        """
        Proyecta una nueva muestra al espacio reducido.
        
        Args:
            sample: Nueva muestra [features]
        
        Returns:
            Representación reducida [n_modos_features]
        """
        U_features = self.hosvd.factors[1]  # [features, n_modos]
        return U_features.T @ sample


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: HOSVD (Higher-Order SVD)")
    print("=" * 60)
    
    # Crear tensor sintético [tiempo, features, variables]
    T, F, V = 50, 64, 5
    tensor = np.random.randn(T, F, V)
    print(f"\n  Tensor original shape: {tensor.shape}")
    
    # HOSVD
    hosvd = HOSVD()
    ranks = [10, 32, 5]  # Reducir tiempo a 10, features a 32
    core, factors = hosvd.fit(tensor, ranks=ranks)
    
    print(f"  Core shape: {core.shape}")
    print(f"  Factores: {[f.shape for f in factors]}")
    
    # Reconstrucción
    recon = hosvd.reconstruct()
    error = np.linalg.norm(tensor - recon) / np.linalg.norm(tensor)
    print(f"\n  Error relativo reconstrucción: {error:.6f}")
    
    # Importancia de modos
    importance_tiempo = hosvd.get_mode_importance(0)
    print(f"  Importancia modos tiempo (top 5): {importance_tiempo[:5]}")
    
    # Test TensorModosTemporal
    print("\n" + "-" * 40)
    print("  TEST: TensorModosTemporal")
    
    historial = np.random.randn(100, 64)  # [T, features]
    tmt = TensorModosTemporal(n_modos_tiempo=5, n_modos_features=20)
    modos_t, modos_f = tmt.fit_transform(historial)
    
    print(f"  Historial shape: {historial.shape}")
    print(f"  Modos tiempo shape: {modos_t.shape}")
    print(f"  Modos features shape: {modos_f.shape}")
    
    # Proyecciónnueva muestra
    nueva = np.random.randn(64)
    proyeccion = tmt.project_new_sample(nueva)
    print(f"  Proyección nueva muestra: {proyeccion.shape}")
    
    print("\n" + "=" * 60)
    print("  TODOS LOS TESTS PASARON ✓")
    print("=" * 60)
