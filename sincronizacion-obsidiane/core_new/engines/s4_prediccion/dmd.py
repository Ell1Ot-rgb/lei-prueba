"""
Dynamic Mode Decomposition (DMD) y Operador de Koopman
======================================================

Predicción basada en descomposición de modos dinámicos.
Aproxima el operador de Koopman para linealizar dinámicas no lineales.
"""

import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class DMDConfig:
    """Configuración del DMD."""
    rank: int = 20          # Rango de truncamiento SVD
    dt: float = 1.0         # Paso temporal
    observables_dim: int = 50  # Dimensión del espacio de observables


class DMDPredictor:
    """
    Dynamic Mode Decomposition para predicción de series temporales.
    
    Aproxima el operador de Koopman, que linealiza la dinámica no lineal
    en un espacio elevado de observables.
    
    Ecuación fundamental:
        x(t+1) = A @ x(t)
    
    Donde A se aproxima mediante SVD y eigendescomposición.
    """
    
    def __init__(self, config: Optional[DMDConfig] = None):
        if config is None:
            config = DMDConfig()
        self.config = config
        
        self.modes: Optional[np.ndarray] = None          # Modos DMD
        self.eigenvalues: Optional[np.ndarray] = None    # Eigenvalores
        self.amplitudes: Optional[np.ndarray] = None     # Amplitudes iniciales
        self.fitted = False
    
    def fit(self, X: np.ndarray):
        """
        Ajusta el modelo DMD a los datos.
        
        Args:
            X: Matriz de snapshots [features, tiempo]
               Cada columna es un snapshot en el tiempo
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        if X.shape[1] < 3:
            raise ValueError("Se necesitan al menos 3 snapshots")
        
        # Dividir en X1 (t) y X2 (t+1)
        X1 = X[:, :-1]  # t = 0 a T-1
        X2 = X[:, 1:]   # t = 1 a T
        
        # SVD de X1
        U, S, Vh = np.linalg.svd(X1, full_matrices=False)
        
        # Truncar al rango especificado
        r = min(self.config.rank, len(S))
        U = U[:, :r]
        S = S[:r]
        Vh = Vh[:r, :]
        
        # Matriz DMD reducida: Ã = U^T @ X2 @ V @ S^(-1)
        S_inv = np.diag(1.0 / S)
        A_tilde = U.T @ X2 @ Vh.T @ S_inv
        
        # Eigendescomposición de Ã
        eigenvalues, W = np.linalg.eig(A_tilde)
        
        # Modos DMD: Φ = X2 @ V @ S^(-1) @ W
        self.modes = X2 @ Vh.T @ S_inv @ W
        self.eigenvalues = eigenvalues
        
        # Amplitudes iniciales: b = pinv(Φ) @ x0
        self.amplitudes = np.linalg.pinv(self.modes) @ X[:, 0]
        
        self.fitted = True
    
    def predict(self, horizonte: int, 
                initial_state: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Predicción usando modos dinámicos.
        
        Args:
            horizonte: Número de pasos a predecir
            initial_state: Estado inicial (opcional, usa el del fit si no)
        
        Returns:
            Predicciones [horizonte, features]
        """
        if not self.fitted:
            raise RuntimeError("Debe llamar fit() primero")
        
        if initial_state is not None:
            amplitudes = np.linalg.pinv(self.modes) @ initial_state
        else:
            amplitudes = self.amplitudes
        
        predicciones = []
        for t in range(1, horizonte + 1):
            # x(t) = Φ @ diag(λ^t) @ b
            dynamics = self.eigenvalues ** t
            pred = self.modes @ (amplitudes * dynamics)
            predicciones.append(pred.real)
        
        return np.array(predicciones)
    
    def get_frequencies_and_growth(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extrae frecuencias oscilatorias y tasas de crecimiento.
        
        Returns:
            (frequencies, growth_rates)
            - frequencies: Frecuencias de oscilación (Hz si dt=1s)
            - growth_rates: >0 crecimiento, <0 decaimiento
        """
        if not self.fitted:
            raise RuntimeError("Debe llamar fit() primero")
        
        # ω = log(λ) / dt
        omega = np.log(self.eigenvalues + 1e-10) / self.config.dt
        
        frequencies = omega.imag / (2 * np.pi)
        growth_rates = omega.real
        
        return frequencies.real, growth_rates.real
    
    def get_dominant_modes(self, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Retorna los k modos más dominantes (mayor amplitud).
        
        Args:
            k: Número de modos a retornar
        
        Returns:
            (modes, eigenvalues) de los k más dominantes
        """
        if not self.fitted:
            raise RuntimeError("Debe llamar fit() primero")
        
        # Ordenar por magnitud de amplitud
        magnitudes = np.abs(self.amplitudes)
        top_indices = np.argsort(magnitudes)[-k:][::-1]
        
        return self.modes[:, top_indices], self.eigenvalues[top_indices]
    
    def reconstruct(self, t: int) -> np.ndarray:
        """
        Reconstruye el estado en el tiempo t.
        
        Args:
            t: Paso temporal
        
        Returns:
            Estado reconstruido
        """
        if not self.fitted:
            raise RuntimeError("Debe llamar fit() primero")
        
        dynamics = self.eigenvalues ** t
        return (self.modes @ (self.amplitudes * dynamics)).real


class KoopmanObservable:
    """
    Espacio de observables para el operador de Koopman.
    
    Eleva el estado a un espacio de mayor dimensión donde la dinámica
    se vuelve aproximadamente lineal.
    
    Observables incluidos:
    - Estado original
    - Polinomios de grado 2
    - Funciones radiales (RBF)
    """
    
    def __init__(self, state_dim: int, n_observables: int = 50, n_rbf: int = 20):
        self.state_dim = state_dim
        self.n_observables = n_observables
        self.n_rbf = n_rbf
        
        # Centros para RBF (generados aleatoriamente)
        np.random.seed(42)
        self.rbf_centers = np.random.randn(n_rbf, state_dim)
        self.rbf_sigma = 1.0
        
        # Calcular dimensión real de observables
        n_poly2 = state_dim * (state_dim + 1) // 2  # Polinomios grado 2
        self.actual_dim = min(n_observables, state_dim + n_poly2 + n_rbf)
    
    def lift(self, state: np.ndarray) -> np.ndarray:
        """
        Eleva el estado al espacio de observables.
        
        Args:
            state: Vector de estado [state_dim]
        
        Returns:
            Vector de observables [n_observables]
        """
        observables = []
        
        # 1. Estado original
        observables.extend(state.tolist())
        
        # 2. Polinomios de grado 2 (productos cruzados)
        for i in range(len(state)):
            for j in range(i, len(state)):
                observables.append(state[i] * state[j])
        
        # 3. Funciones radiales (RBF)
        for center in self.rbf_centers:
            dist_sq = np.sum((state - center) ** 2)
            rbf = np.exp(-dist_sq / (2 * self.rbf_sigma ** 2))
            observables.append(rbf)
        
        # Truncar/pad a n_observables
        observables = np.array(observables)
        if len(observables) > self.n_observables:
            observables = observables[:self.n_observables]
        elif len(observables) < self.n_observables:
            observables = np.pad(observables, (0, self.n_observables - len(observables)))
        
        return observables
    
    def lift_sequence(self, states: np.ndarray) -> np.ndarray:
        """
        Eleva una secuencia de estados.
        
        Args:
            states: [T, state_dim]
        
        Returns:
            [T, n_observables]
        """
        return np.array([self.lift(s) for s in states])


class ExtendedDMD:
    """
    Extended DMD que usa observables de Koopman.
    
    Combina KoopmanObservable con DMD para mejor aproximación
    de dinámicas no lineales.
    """
    
    def __init__(self, state_dim: int, 
                 n_observables: int = 50, 
                 rank: int = 20):
        self.observables = KoopmanObservable(state_dim, n_observables)
        self.dmd = DMDPredictor(DMDConfig(rank=rank))
        self.state_dim = state_dim
    
    def fit(self, X: np.ndarray):
        """
        Ajusta el EDMD.
        
        Args:
            X: Estados [T, state_dim]
        """
        # Elevar al espacio de observables
        X_lifted = self.observables.lift_sequence(X)
        
        # Aplicar DMD en el espacio elevado
        self.dmd.fit(X_lifted.T)  # DMD espera [features, tiempo]
    
    def predict(self, initial_state: np.ndarray, 
                horizonte: int) -> np.ndarray:
        """
        Predice en el espacio original.
        
        Args:
            initial_state: Estado inicial [state_dim]
            horizonte: Pasos a predecir
        
        Returns:
            Predicciones [horizonte, state_dim]
        """
        # Elevar estado inicial
        initial_lifted = self.observables.lift(initial_state)
        
        # Predecir en espacio elevado
        preds_lifted = self.dmd.predict(horizonte, initial_lifted)
        
        # Extraer las primeras state_dim componentes (estado original)
        return preds_lifted[:, :self.state_dim]


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: Dynamic Mode Decomposition")
    print("=" * 60)
    
    # Generar datos sintéticos (oscilador amortiguado)
    T = 100
    t = np.linspace(0, 10, T)
    X = np.vstack([
        np.exp(-0.1 * t) * np.cos(2 * t),
        np.exp(-0.1 * t) * np.sin(2 * t),
        0.5 * np.exp(-0.2 * t) * np.cos(3 * t)
    ])  # [3, T]
    
    print(f"\n  Datos shape: {X.shape}")
    
    # DMD
    dmd = DMDPredictor(DMDConfig(rank=3))
    dmd.fit(X)
    print(f"  ✓ DMD ajustado")
    print(f"  Modos shape: {dmd.modes.shape}")
    print(f"  Eigenvalores: {np.abs(dmd.eigenvalues)}")
    
    # Frecuencias
    freqs, growth = dmd.get_frequencies_and_growth()
    print(f"\n  Frecuencias: {freqs}")
    print(f"  Tasas de crecimiento: {growth}")
    
    # Predicción
    preds = dmd.predict(horizonte=20)
    print(f"\n  Predicciones shape: {preds.shape}")
    
    # Reconstrucción
    recon = dmd.reconstruct(50)
    error = np.linalg.norm(recon - X[:, 50])
    print(f"  Error reconstrucción t=50: {error:.6f}")
    
    # Test Koopman Observable
    print("\n" + "-" * 40)
    print("  TEST: Koopman Observable")
    
    obs = KoopmanObservable(state_dim=3, n_observables=30)
    state = np.array([1.0, 0.5, -0.3])
    lifted = obs.lift(state)
    print(f"  Estado original: {state.shape}")
    print(f"  Estado elevado: {lifted.shape}")
    
    # Test Extended DMD
    print("\n" + "-" * 40)
    print("  TEST: Extended DMD")
    
    edmd = ExtendedDMD(state_dim=3, n_observables=30, rank=10)
    edmd.fit(X.T)  # [T, features]
    preds_edmd = edmd.predict(X[:, 0], horizonte=10)
    print(f"  Predicciones EDMD shape: {preds_edmd.shape}")
    
    print("\n" + "=" * 60)
    print("  TODOS LOS TESTS PASARON ✓")
    print("=" * 60)
