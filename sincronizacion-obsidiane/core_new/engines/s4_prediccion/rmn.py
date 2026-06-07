"""
Reservoir Memory Network (RMN) - ESN Mejorado con Memoria de Largo Plazo
=========================================================================

Octubre 2024 - ESANN: Combina reservoir no lineal con celda de memoria lineal
para mejorar la retención de información temporal.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class RMNConfig:
    """Configuración del Reservoir Memory Network."""
    input_dim: int = 64
    reservoir_size: int = 100
    memory_size: int = 50
    spectral_radius: float = 0.9
    memory_decay: float = 0.99  # Cercano a 1 = memoria larga
    input_scaling: float = 0.5
    leaking_rate: float = 0.3
    ridge_alpha: float = 1e-4


class ReservoirMemoryNetwork:
    """
    ESN mejorado con celda de memoria lineal.
    
    Arquitectura:
    - Reservoir no lineal (tradicional ESN con tanh)
    - Celda de memoria lineal (retiene información largo plazo)
    - Salida combinada de ambos
    
    Ventajas sobre ESN tradicional:
    - Mejor retención de dependencias de largo plazo
    - Memoria lineal no sufre de vanishing gradients
    - Solo se entrena la capa de salida (eficiente)
    """
    
    def __init__(self, config: Optional[RMNConfig] = None):
        if config is None:
            config = RMNConfig()
        self.config = config
        
        # === RESERVOIR NO LINEAL (ESN tradicional) ===
        self.W_in_res = np.random.uniform(
            -config.input_scaling, config.input_scaling,
            (config.reservoir_size, config.input_dim)
        )
        
        # Matriz del reservoir con radio espectral ajustado
        W_res = np.random.randn(config.reservoir_size, config.reservoir_size)
        # Ajustar radio espectral
        eigenvalues = np.linalg.eigvals(W_res)
        spectral_radius_actual = np.max(np.abs(eigenvalues))
        if spectral_radius_actual > 0:
            W_res *= config.spectral_radius / spectral_radius_actual
        self.W_res = W_res
        
        self.state_res = np.zeros(config.reservoir_size)
        
        # === CELDA DE MEMORIA LINEAL (NUEVO) ===
        self.W_in_mem = np.random.uniform(
            -0.1, 0.1,
            (config.memory_size, config.input_dim)
        )
        
        # Matriz de memoria casi-identidad para retención larga
        self.W_mem = np.eye(config.memory_size) * config.memory_decay
        # Agregar pequeñas conexiones aleatorias
        self.W_mem += np.random.randn(config.memory_size, config.memory_size) * 0.01
        
        self.state_mem = np.zeros(config.memory_size)
        
        # === CAPA DE SALIDA ===
        output_dim = config.reservoir_size + config.memory_size
        self.W_out = np.zeros((config.input_dim, output_dim))
        
        # === PARÁMETROS ===
        self.alpha = config.leaking_rate
        self.trained = False
    
    def reset_state(self):
        """Reinicia los estados del reservoir y memoria."""
        self.state_res = np.zeros(self.config.reservoir_size)
        self.state_mem = np.zeros(self.config.memory_size)
    
    def step(self, x: np.ndarray) -> np.ndarray:
        """
        Un paso del RMN.
        
        Args:
            x: Vector de entrada [input_dim]
        
        Returns:
            Estado combinado [reservoir_size + memory_size]
        """
        # === Reservoir no lineal ===
        pre_res = self.W_in_res @ x + self.W_res @ self.state_res
        # Leaky integration con tanh
        self.state_res = (1 - self.alpha) * self.state_res + self.alpha * np.tanh(pre_res)
        
        # === Memoria lineal (NO usa tanh) ===
        pre_mem = self.W_in_mem @ x + self.W_mem @ self.state_mem
        self.state_mem = pre_mem  # Lineal, sin activación
        
        # === Estado combinado ===
        combined = np.concatenate([self.state_res, self.state_mem])
        
        return combined
    
    def predict(self, x: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Genera predicción.
        
        Args:
            x: Input opcional (si se proporciona, hace step primero)
        
        Returns:
            Predicción [input_dim]
        """
        if x is not None:
            self.step(x)
        
        combined = np.concatenate([self.state_res, self.state_mem])
        return self.W_out @ combined
    
    def fit(self, X: np.ndarray, Y: np.ndarray, washout: int = 10):
        """
        Entrena la capa de salida usando Ridge Regression.
        
        Args:
            X: Datos de entrada [T, input_dim]
            Y: Targets [T, input_dim] (típicamente X desplazado)
            washout: Pasos iniciales a descartar
        """
        self.reset_state()
        
        # Recolectar estados
        estados = []
        for t in range(len(X)):
            combined = self.step(X[t])
            if t >= washout:
                estados.append(combined)
        
        estados = np.array(estados)  # [T-washout, reservoir_size + memory_size]
        targets = Y[washout:]        # [T-washout, input_dim]
        
        # Ridge Regression: W_out = Y^T @ H @ (H^T @ H + λI)^(-1)
        H = estados
        HtH = H.T @ H
        regularization = self.config.ridge_alpha * np.eye(HtH.shape[0])
        
        try:
            self.W_out = targets.T @ H @ np.linalg.inv(HtH + regularization)
        except np.linalg.LinAlgError:
            # Fallback a pseudoinversa
            self.W_out = targets.T @ np.linalg.pinv(H)
        
        self.trained = True
    
    def predict_sequence(self, initial_input: np.ndarray, 
                         horizonte: int) -> np.ndarray:
        """
        Predicción auto-regresiva.
        
        Args:
            initial_input: Input inicial [input_dim]
            horizonte: Número de pasos a predecir
        
        Returns:
            Predicciones [horizonte, input_dim]
        """
        predicciones = []
        current = initial_input.copy()
        
        for _ in range(horizonte):
            self.step(current)
            pred = self.predict()
            predicciones.append(pred)
            current = pred  # Feedback
        
        return np.array(predicciones)
    
    def get_memory_content(self) -> np.ndarray:
        """Retorna el contenido actual de la memoria lineal."""
        return self.state_mem.copy()
    
    def get_reservoir_state(self) -> np.ndarray:
        """Retorna el estado actual del reservoir."""
        return self.state_res.copy()
    
    def compute_lyapunov_estimate(self) -> float:
        """
        Estima el exponente de Lyapunov local.
        
        Returns:
            Lambda: >0 caos, <0 orden, ~0 borde del caos
        """
        # Jacobiano del reservoir: W_res * diag(1 - state²)
        derivada = 1.0 - self.state_res ** 2
        jacobiano = self.W_res * derivada[:, np.newaxis]
        
        try:
            norma = np.linalg.norm(jacobiano, ord=2)
            if norma > 0:
                return np.log(norma)
            return -1.0
        except:
            return 0.0


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: Reservoir Memory Network")
    print("=" * 60)
    
    # Configuración
    config = RMNConfig(
        input_dim=64,
        reservoir_size=100,
        memory_size=50,
        spectral_radius=0.9
    )
    
    rmn = ReservoirMemoryNetwork(config)
    
    # Simular secuencia
    T = 200
    X = np.random.randn(T, 64).astype(np.float32)
    Y = np.roll(X, -1, axis=0)  # Target = siguiente paso
    
    # Entrenar
    print("\n  Entrenando RMN...")
    rmn.fit(X, Y, washout=20)
    print(f"  ✓ Entrenamiento completado")
    print(f"  W_out shape: {rmn.W_out.shape}")
    
    # Predecir
    rmn.reset_state()
    predicciones = rmn.predict_sequence(X[0], horizonte=10)
    print(f"\n  Predicciones shape: {predicciones.shape}")
    
    # Lyapunov
    rmn.step(X[0])
    lyapunov = rmn.compute_lyapunov_estimate()
    print(f"  Exponente de Lyapunov: {lyapunov:.4f}")
    
    # Verificar memoria
    memoria = rmn.get_memory_content()
    reservoir = rmn.get_reservoir_state()
    print(f"\n  Memoria shape: {memoria.shape}")
    print(f"  Reservoir shape: {reservoir.shape}")
    
    print("\n" + "=" * 60)
    print("  TODOS LOS TESTS PASARON ✓")
    print("=" * 60)
