"""
Motor S4 - Orquestador del Sistema de Predicción Tensorial
==========================================================

Integra todos los componentes de S4 en un pipeline unificado.
Conecta con S1/S2/S3 existentes para formar el sistema completo.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import time
from collections import deque

# Imports del módulo S4 (soporta ejecución como módulo y standalone)
try:
    from .tensor_fusionado import TensorFusionado, TensorHistorial
    from .rmn import ReservoirMemoryNetwork, RMNConfig
    from .dmd import DMDPredictor, DMDConfig, ExtendedDMD, KoopmanObservable
    from .hosvd import HOSVD, TensorModosTemporal
    from .tensor_attention import TensorAttention, TensorAttentionConfig
    from .cp_decomposition import CPDecomposition, CPConfig
    from .spa_predictor import SPAPredictor, SPAConfig
except ImportError:
    from tensor_fusionado import TensorFusionado, TensorHistorial
    from rmn import ReservoirMemoryNetwork, RMNConfig
    from dmd import DMDPredictor, DMDConfig, ExtendedDMD, KoopmanObservable
    from hosvd import HOSVD, TensorModosTemporal
    from tensor_attention import TensorAttention, TensorAttentionConfig
    from cp_decomposition import CPDecomposition, CPConfig
    from spa_predictor import SPAPredictor, SPAConfig


@dataclass
class S4Config:
    """Configuración del Motor S4."""
    # Historial
    historial_size: int = 100
    
    # RMN
    rmn_reservoir_size: int = 100
    rmn_memory_size: int = 50
    
    # DMD
    dmd_rank: int = 20
    
    # HOSVD
    hosvd_modos_tiempo: int = 5
    hosvd_modos_features: int = 32
    
    # Attention
    attention_rank: int = 8
    
    # CP
    cp_rank: int = 10
    
    # SPA
    spa_patrones: int = 50
    
    # Predicción
    horizonte_default: int = 10
    min_historial_para_entrenar: int = 30


@dataclass
class PrediccionS4:
    """Resultado de una predicción S4."""
    prediccion: np.ndarray          # [horizonte, features]
    incertidumbre: np.ndarray       # [horizonte]
    modos_dmd: Optional[np.ndarray] = None  # Modos dinámicos principales
    frecuencias: Optional[np.ndarray] = None  # Frecuencias de Koopman
    lyapunov: float = 0.0           # Exponente de Lyapunov
    patrones_spa: Optional[List[int]] = None  # Secuencia de patrones
    timestamp: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'prediccion': self.prediccion.tolist(),
            'incertidumbre': self.incertidumbre.tolist(),
            'lyapunov': self.lyapunov,
            'patrones_spa': self.patrones_spa,
            'timestamp': self.timestamp
        }


class MotorS4:
    """
    Motor de Predicción Tensorial S4.
    
    Pipeline:
    1. Recibe estado del sistema (embedding, ESN, PAD, etc.)
    2. Fusiona en TensorFusionado
    3. Actualiza historial
    4. Aplica componentes de predicción:
       - RMN: Predicción temporal con memoria
       - DMD: Modos dinámicos de Koopman
       - CP: Patrones recurrentes
       - SPA: Distribución probabilística
    5. Fusiona predicciones con TensorAttention
    6. Retorna predicción con incertidumbre
    
    Conexiones con S1/S2/S3:
    - S1 → embedding, grundzug_sketch
    - S2 → conceptos emergentes
    - S3 → axiomas y lógica
    """
    
    def __init__(self, config: Optional[S4Config] = None):
        if config is None:
            config = S4Config()
        self.config = config
        
        # Historial
        self.historial = TensorHistorial(maxlen=config.historial_size)
        
        # Componentes
        self.rmn = ReservoirMemoryNetwork(RMNConfig(
            input_dim=182,  # TensorFusionado total
            reservoir_size=config.rmn_reservoir_size,
            memory_size=config.rmn_memory_size
        ))
        
        self.dmd = DMDPredictor(DMDConfig(rank=config.dmd_rank))
        
        self.hosvd_temporal = TensorModosTemporal(
            n_modos_tiempo=config.hosvd_modos_tiempo,
            n_modos_features=config.hosvd_modos_features
        )
        
        self.attention = TensorAttention(TensorAttentionConfig(
            dims=[64, 100, 3],  # embedding, esn, pad
            rank=config.attention_rank
        ))
        
        self.cp = CPDecomposition(CPConfig(rank=config.cp_rank))
        
        self.spa = SPAPredictor(SPAConfig(n_patrones=config.spa_patrones))
        
        # Estado
        self.entrenado = False
        self.ultima_prediccion: Optional[PrediccionS4] = None
        self.metricas: Dict[str, float] = {}
    
    def actualizar(self, 
                   embedding: np.ndarray,
                   esn_state: np.ndarray,
                   pad_emotions: np.ndarray,
                   grundzug_sketch: Optional[np.ndarray] = None,
                   jacobiano: Optional[np.ndarray] = None,
                   timestamp: Optional[float] = None) -> TensorFusionado:
        """
        Actualiza el estado de S4 con nuevos datos.
        
        Args:
            embedding: Vector de embedding de S1 [64]
            esn_state: Estado del ESN [100]
            pad_emotions: Vector PAD [3]
            grundzug_sketch: Matriz Count-Min Sketch (opcional)
            jacobiano: Jacobiano del ESN (opcional)
            timestamp: Marca temporal (opcional)
        
        Returns:
            TensorFusionado creado
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Crear TensorFusionado
        tensor = TensorFusionado.from_system_state(
            embedding=embedding,
            esn_state=esn_state,
            pad_emotions=pad_emotions,
            grundzug_sketch=grundzug_sketch if grundzug_sketch is not None else np.array([]),
            jacobiano=jacobiano if jacobiano is not None else np.array([]),
            timestamp=timestamp
        )
        
        # Agregar al historial
        self.historial.append(tensor)
        
        # Actualizar RMN
        self.rmn.step(tensor.to_flat())
        
        # Verificar si podemos entrenar
        if len(self.historial) >= self.config.min_historial_para_entrenar:
            if not self.entrenado:
                self._entrenar_componentes()
        
        return tensor
    
    def _entrenar_componentes(self):
        """Entrena los componentes con el historial actual."""
        historial_matriz = self.historial.to_matrix()
        if historial_matriz is None:
            return
        
        try:
            # Entrenar RMN
            X = historial_matriz[:-1]
            Y = historial_matriz[1:]
            self.rmn.fit(X, Y, washout=10)
            
            # Entrenar DMD
            self.dmd.fit(historial_matriz.T)
            
            # Entrenar SPA
            self.spa.fit(historial_matriz)
            
            self.entrenado = True
            
        except Exception as e:
            print(f"[S4] Error entrenando: {e}")
    
    def predecir(self, horizonte: Optional[int] = None) -> PrediccionS4:
        """
        Genera predicción usando todos los componentes.
        
        Args:
            horizonte: Pasos a predecir (usa default si None)
        
        Returns:
            PrediccionS4 con predicción e incertidumbre
        """
        if horizonte is None:
            horizonte = self.config.horizonte_default
        
        if len(self.historial) == 0:
            # Sin datos, retornar predicción vacía
            return PrediccionS4(
                prediccion=np.zeros((horizonte, 182)),
                incertidumbre=np.ones(horizonte),
                timestamp=time.time()
            )
        
        # Estado actual
        estado_actual = self.historial.buffer[-1].to_flat()
        timestamp = time.time()
        
        predicciones = []
        incertidumbres = []
        modos_dmd = None
        frecuencias = None
        patrones_spa = None
        lyapunov = 0.0
        
        # --- RMN ---
        try:
            pred_rmn = self.rmn.predict_sequence(estado_actual, horizonte)
            predicciones.append(pred_rmn)
            lyapunov = self.rmn.compute_lyapunov_estimate()
        except Exception:
            pred_rmn = np.zeros((horizonte, 182))
            predicciones.append(pred_rmn)
        
        # --- DMD ---
        if self.dmd.fitted:
            try:
                pred_dmd = self.dmd.predict(horizonte, estado_actual)
                predicciones.append(pred_dmd)
                
                modos_dmd, _ = self.dmd.get_dominant_modes(k=5)
                frecuencias, _ = self.dmd.get_frequencies_and_growth()
            except Exception:
                pass
        
        # --- SPA ---
        if self.spa.fitted:
            try:
                pred_spa, incert_spa = self.spa.predict(estado_actual, horizonte)
                predicciones.append(pred_spa)
                incertidumbres.append(incert_spa)
                
                patrones_spa = self.spa.get_most_likely_sequence(estado_actual, horizonte)
            except Exception:
                pass
        
        # --- Fusionar predicciones ---
        if len(predicciones) > 1:
            # Promedio ponderado (pesos iguales por ahora)
            prediccion_final = np.mean(np.stack(predicciones), axis=0)
        elif len(predicciones) == 1:
            prediccion_final = predicciones[0]
        else:
            prediccion_final = np.zeros((horizonte, 182))
        
        # --- Fusionar incertidumbres ---
        if len(incertidumbres) > 0:
            incertidumbre_final = np.mean(np.stack(incertidumbres), axis=0)
        else:
            # Incertidumbre basada en varianza de predicciones
            if len(predicciones) > 1:
                stacked = np.stack(predicciones)
                incertidumbre_final = np.mean(np.std(stacked, axis=0), axis=1)
            else:
                incertidumbre_final = np.ones(horizonte) * 0.5
        
        # Crear resultado
        resultado = PrediccionS4(
            prediccion=prediccion_final,
            incertidumbre=incertidumbre_final,
            modos_dmd=modos_dmd,
            frecuencias=frecuencias[:5] if frecuencias is not None else None,
            lyapunov=lyapunov,
            patrones_spa=patrones_spa,
            timestamp=timestamp
        )
        
        self.ultima_prediccion = resultado
        return resultado
    
    def analizar_dinamica(self) -> Dict[str, Any]:
        """
        Analiza la dinámica del sistema usando HOSVD y CP.
        
        Returns:
            Diccionario con análisis
        """
        if len(self.historial) < 10:
            return {'error': 'Historial insuficiente'}
        
        historial_matriz = self.historial.to_matrix()
        
        resultado = {}
        
        # HOSVD para modos temporales
        try:
            modos_t, modos_f = self.hosvd_temporal.fit_transform(historial_matriz)
            resultado['modos_temporales'] = modos_t
            resultado['modos_features'] = modos_f
            resultado['compresion'] = self.hosvd_temporal.get_compressed_representation()
        except Exception as e:
            resultado['hosvd_error'] = str(e)
        
        # CP para patrones recurrentes
        try:
            # Crear tensor 3D para CP
            T = len(self.historial)
            tensor_3d = self.historial.to_tensor_3d()
            if tensor_3d is not None:
                self.cp.fit(tensor_3d)
                factors_top, weights_top = self.cp.get_dominant_patterns(k=5)
                resultado['patrones_dominantes'] = {
                    'weights': weights_top.tolist(),
                    'n_iter': self.cp.n_iter,
                    'error': self.cp.reconstruction_error
                }
        except Exception as e:
            resultado['cp_error'] = str(e)
        
        # Lyapunov
        resultado['lyapunov'] = self.rmn.compute_lyapunov_estimate()
        
        # Clasificación de régimen dinámico
        if resultado['lyapunov'] > 0.1:
            resultado['regimen'] = 'CAOTICO'
        elif resultado['lyapunov'] < -0.1:
            resultado['regimen'] = 'ORDENADO'
        else:
            resultado['regimen'] = 'BORDE_DEL_CAOS'
        
        return resultado
    
    def aplicar_attention(self, 
                          embedding: np.ndarray,
                          esn_state: np.ndarray,
                          pad_emotions: np.ndarray) -> np.ndarray:
        """
        Aplica atención tensorial para fusión multimodal.
        
        Args:
            embedding: Vector de embedding [64]
            esn_state: Estado ESN [100]
            pad_emotions: Vector PAD [3]
        
        Returns:
            Representación fusionada
        """
        return self.attention.forward([embedding, esn_state, pad_emotions])
    
    def get_estado(self) -> Dict[str, Any]:
        """Retorna el estado actual del motor S4."""
        return {
            'historial_size': len(self.historial),
            'entrenado': self.entrenado,
            'lyapunov': self.rmn.compute_lyapunov_estimate(),
            'memoria_rmn': self.rmn.get_memory_content().tolist() if self.rmn else None,
            'dmd_fitted': self.dmd.fitted if self.dmd else False,
            'spa_fitted': self.spa.fitted if self.spa else False,
        }
    
    def reset(self):
        """Reinicia el motor S4."""
        self.historial.clear()
        self.rmn.reset_state()
        self.entrenado = False
        self.ultima_prediccion = None


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  TEST: Motor S4 - Sistema de Predicción Tensorial")
    print("=" * 70)
    
    # Crear motor
    config = S4Config(
        historial_size=100,
        rmn_reservoir_size=50,
        rmn_memory_size=25,
        min_historial_para_entrenar=20
    )
    motor = MotorS4(config)
    print(f"\n  Motor S4 inicializado")
    print(f"  Configuración: historial={config.historial_size}, RMN={config.rmn_reservoir_size}")
    
    # Simular actualizaciones
    print("\n  Simulando 50 actualizaciones...")
    for i in range(50):
        embedding = np.random.randn(64).astype(np.float32)
        esn_state = np.random.randn(100).astype(np.float32)
        pad_emotions = np.random.rand(3).astype(np.float32)
        
        motor.actualizar(
            embedding=embedding,
            esn_state=esn_state,
            pad_emotions=pad_emotions
        )
    
    estado = motor.get_estado()
    print(f"\n  Estado del motor:")
    print(f"    - Historial: {estado['historial_size']}")
    print(f"    - Entrenado: {estado['entrenado']}")
    print(f"    - Lyapunov: {estado['lyapunov']:.4f}")
    
    # Predicción
    print("\n  Generando predicción...")
    pred = motor.predecir(horizonte=10)
    
    print(f"\n  Predicción:")
    print(f"    - Shape: {pred.prediccion.shape}")
    print(f"    - Incertidumbre media: {pred.incertidumbre.mean():.4f}")
    print(f"    - Lyapunov: {pred.lyapunov:.4f}")
    print(f"    - Patrones SPA: {pred.patrones_spa}")
    
    # Análisis de dinámica
    print("\n  Analizando dinámica...")
    analisis = motor.analizar_dinamica()
    print(f"    - Régimen: {analisis.get('regimen', 'N/A')}")
    print(f"    - Lyapunov: {analisis.get('lyapunov', 0):.4f}")
    
    # Attention
    print("\n  Probando TensorAttention...")
    fusion = motor.aplicar_attention(
        np.random.randn(64),
        np.random.randn(100),
        np.random.randn(3)
    )
    print(f"    - Fusión shape: {fusion.shape}")
    
    print("\n" + "=" * 70)
    print("  MOTOR S4 OPERATIVO ✓")
    print("=" * 70)
