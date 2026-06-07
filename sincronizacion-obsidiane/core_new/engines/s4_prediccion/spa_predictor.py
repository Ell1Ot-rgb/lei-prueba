"""
SPA Predictor - Scalable Probabilistic Approximation
=====================================================

Predicción basada en patrones discretos con cuantificación de incertidumbre.
Inspirado en el algoritmo SPA de la Universidad de Mainz.
"""

import numpy as np
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class SPAConfig:
    """Configuración del predictor SPA."""
    n_patrones: int = 50        # Número de patrones discretos
    min_transiciones: int = 5   # Mínimo de transiciones para matriz estable
    suavizado: float = 0.01     # Suavizado de Laplace


class SPAPredictor:
    """
    Scalable Probabilistic Approximation para predicción.
    
    Basado en el trabajo de Metzner et al. (Universidad de Mainz):
    - Discretiza el espacio de estados en K patrones
    - Construye matriz de transición Markoviana
    - Proporciona predicciones con incertidumbre
    
    Ventajas:
    - Muy eficiente (O(n) complejidad)
    - Cuantifica incertidumbre naturalmente
    - Funciona bien en PCs de bajos recursos
    """
    
    def __init__(self, config: Optional[SPAConfig] = None):
        if config is None:
            config = SPAConfig()
        self.config = config
        
        self.centroides: Optional[np.ndarray] = None      # [K, features]
        self.matriz_transicion: Optional[np.ndarray] = None  # [K, K]
        self.conteo_patrones: Optional[np.ndarray] = None    # [K]
        self.fitted = False
    
    def _minibatch_kmeans(self, X: np.ndarray, 
                          n_clusters: int,
                          batch_size: int = 100,
                          max_iter: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Mini-batch K-means implementado sin sklearn.
        
        Args:
            X: Datos [n_samples, features]
            n_clusters: Número de clusters
            batch_size: Tamaño del mini-batch
            max_iter: Iteraciones máximas
        
        Returns:
            (centroides, etiquetas)
        """
        n_samples, n_features = X.shape
        
        # Inicialización: seleccionar centroides aleatorios de los datos
        indices = np.random.choice(n_samples, size=min(n_clusters, n_samples), replace=False)
        centroides = X[indices].copy()
        
        # Si hay menos muestras que clusters, pad con random
        if len(centroides) < n_clusters:
            padding = np.random.randn(n_clusters - len(centroides), n_features)
            centroides = np.vstack([centroides, padding])
        
        counts = np.ones(n_clusters)
        
        for iteration in range(max_iter):
            # Seleccionar mini-batch
            batch_indices = np.random.choice(n_samples, size=min(batch_size, n_samples), replace=False)
            batch = X[batch_indices]
            
            # Asignar a cluster más cercano
            distances = np.linalg.norm(batch[:, np.newaxis] - centroides, axis=2)
            asignaciones = np.argmin(distances, axis=1)
            
            # Actualizar centroides
            for k in range(n_clusters):
                mask = asignaciones == k
                if mask.any():
                    counts[k] += mask.sum()
                    eta = 1.0 / counts[k]
                    centroides[k] = (1 - eta) * centroides[k] + eta * batch[mask].mean(axis=0)
        
        # Etiquetas finales
        distances = np.linalg.norm(X[:, np.newaxis] - centroides, axis=2)
        etiquetas = np.argmin(distances, axis=1)
        
        return centroides, etiquetas
    
    def fit(self, serie_temporal: np.ndarray):
        """
        Ajusta el modelo SPA.
        
        Args:
            serie_temporal: Datos [T, features]
        """
        n_samples = len(serie_temporal)
        n_patrones = min(self.config.n_patrones, n_samples // 2)
        
        if n_patrones < 2:
            raise ValueError("Se necesitan más datos para ajustar SPA")
        
        # 1. Clustering para encontrar patrones
        self.centroides, etiquetas = self._minibatch_kmeans(
            serie_temporal, n_patrones
        )
        
        # 2. Construir matriz de transición
        self.matriz_transicion = np.zeros((n_patrones, n_patrones))
        self.conteo_patrones = np.zeros(n_patrones)
        
        for i in range(len(etiquetas) - 1):
            from_state = etiquetas[i]
            to_state = etiquetas[i + 1]
            self.matriz_transicion[from_state, to_state] += 1
            self.conteo_patrones[from_state] += 1
        
        # 3. Suavizado de Laplace
        self.matriz_transicion += self.config.suavizado
        
        # 4. Normalizar a probabilidades
        sumas = self.matriz_transicion.sum(axis=1, keepdims=True)
        sumas[sumas == 0] = 1
        self.matriz_transicion /= sumas
        
        self.fitted = True
    
    def _encontrar_patron_cercano(self, estado: np.ndarray) -> Tuple[int, float]:
        """
        Encuentra el patrón más cercano al estado dado.
        
        Returns:
            (indice_patron, distancia)
        """
        distancias = np.linalg.norm(self.centroides - estado, axis=1)
        idx = np.argmin(distancias)
        return idx, distancias[idx]
    
    def predict(self, estado_actual: np.ndarray, 
                horizonte: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predicción con cuantificación de incertidumbre.
        
        Args:
            estado_actual: Estado actual [features]
            horizonte: Pasos a predecir
        
        Returns:
            (predicciones, incertidumbres)
            - predicciones: [horizonte, features]
            - incertidumbres: [horizonte] (entropía de la distribución)
        """
        if not self.fitted:
            raise RuntimeError("Debe llamar fit() primero")
        
        # Encontrar patrón actual
        patron_actual, _ = self._encontrar_patron_cercano(estado_actual)
        
        # Distribución de probabilidad sobre patrones
        prob = np.zeros(len(self.centroides))
        prob[patron_actual] = 1.0
        
        predicciones = []
        incertidumbres = []
        
        for _ in range(horizonte):
            # Transición Markoviana
            prob = prob @ self.matriz_transicion
            
            # Predicción: media ponderada de centroides
            pred = self.centroides.T @ prob  # [features]
            predicciones.append(pred)
            
            # Incertidumbre: entropía de Shannon
            entropia = -np.sum(prob * np.log(prob + 1e-10))
            incertidumbres.append(entropia)
        
        return np.array(predicciones), np.array(incertidumbres)
    
    def predict_distribution(self, estado_actual: np.ndarray, 
                             horizonte: int) -> List[np.ndarray]:
        """
        Retorna la distribución completa sobre patrones en cada paso.
        
        Args:
            estado_actual: Estado actual [features]
            horizonte: Pasos a predecir
        
        Returns:
            Lista de distribuciones [horizonte]
        """
        if not self.fitted:
            raise RuntimeError("Debe llamar fit() primero")
        
        patron_actual, _ = self._encontrar_patron_cercano(estado_actual)
        prob = np.zeros(len(self.centroides))
        prob[patron_actual] = 1.0
        
        distribuciones = []
        for _ in range(horizonte):
            prob = prob @ self.matriz_transicion
            distribuciones.append(prob.copy())
        
        return distribuciones
    
    def get_pattern_statistics(self) -> Dict[str, np.ndarray]:
        """
        Retorna estadísticas sobre los patrones.
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.fitted:
            raise RuntimeError("Debe llamar fit() primero")
        
        # Distribución estacionaria
        # Encontrar eigenvector izquierdo con eigenvalor 1
        eigenvalues, eigenvectors = np.linalg.eig(self.matriz_transicion.T)
        idx = np.argmin(np.abs(eigenvalues - 1))
        estacionaria = np.real(eigenvectors[:, idx])
        estacionaria = estacionaria / estacionaria.sum()
        
        return {
            'centroides': self.centroides,
            'conteo_patrones': self.conteo_patrones,
            'distribucion_estacionaria': estacionaria,
            'entropia_transicion': -np.sum(
                self.matriz_transicion * np.log(self.matriz_transicion + 1e-10),
                axis=1
            )
        }
    
    def get_most_likely_sequence(self, estado_actual: np.ndarray, 
                                  horizonte: int) -> List[int]:
        """
        Retorna la secuencia de patrones más probable (Viterbi simplificado).
        
        Args:
            estado_actual: Estado actual [features]
            horizonte: Pasos a predecir
        
        Returns:
            Secuencia de índices de patrones
        """
        if not self.fitted:
            raise RuntimeError("Debe llamar fit() primero")
        
        patron_actual, _ = self._encontrar_patron_cercano(estado_actual)
        secuencia = [patron_actual]
        
        for _ in range(horizonte):
            # Transición más probable desde el estado actual
            siguiente = np.argmax(self.matriz_transicion[secuencia[-1]])
            secuencia.append(siguiente)
        
        return secuencia[1:]  # Excluir el inicial


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: SPA Predictor")
    print("=" * 60)
    
    # Generar datos sintéticos (patrones cíclicos + ruido)
    T = 500
    t = np.linspace(0, 10 * np.pi, T)
    
    # 3 patrones distintos
    pattern1 = np.column_stack([np.sin(t), np.cos(t)])
    pattern2 = np.column_stack([np.sin(2*t), np.cos(2*t)])
    pattern3 = np.column_stack([np.sin(0.5*t), np.cos(0.5*t)])
    
    # Alternar entre patrones
    data = np.zeros((T, 2))
    for i in range(T):
        if i % 3 == 0:
            data[i] = pattern1[i]
        elif i % 3 == 1:
            data[i] = pattern2[i]
        else:
            data[i] = pattern3[i]
    data += np.random.randn(T, 2) * 0.1
    
    print(f"\n  Datos shape: {data.shape}")
    
    # Ajustar SPA
    config = SPAConfig(n_patrones=20)
    spa = SPAPredictor(config)
    spa.fit(data)
    
    print(f"  Centroides shape: {spa.centroides.shape}")
    print(f"  ✓ SPA ajustado")
    
    # Predicción
    estado = data[-1]
    predicciones, incertidumbres = spa.predict(estado, horizonte=10)
    
    print(f"\n  Predicciones shape: {predicciones.shape}")
    print(f"  Incertidumbres: {incertidumbres}")
    
    # Distribución
    distribs = spa.predict_distribution(estado, horizonte=5)
    print(f"  Distribuciones: {len(distribs)} pasos")
    
    # Estadísticas
    stats = spa.get_pattern_statistics()
    print(f"\n  Distribución estacionaria (top 5): {stats['distribucion_estacionaria'][:5]}")
    
    # Secuencia más probable
    secuencia = spa.get_most_likely_sequence(estado, horizonte=5)
    print(f"  Secuencia más probable: {secuencia}")
    
    print("\n" + "=" * 60)
    print("  TODOS LOS TESTS PASARON ✓")
    print("=" * 60)
