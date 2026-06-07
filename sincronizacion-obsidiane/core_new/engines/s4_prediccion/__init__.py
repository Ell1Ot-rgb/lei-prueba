"""
S4: Sistema de Predicción Tensorial
====================================

Módulo de predicción avanzada usando técnicas tensoriales:
- TensorFusionado: Combina tensores de S1/S2/S3
- RMN: Reservoir Memory Network (ESN mejorado)
- DMD: Dynamic Mode Decomposition (Koopman)
- HOSVD: Higher-Order SVD para modos temporales
- TensorAttention: Fusión multimodal
- CP/SPA: Patrones e incertidumbre
"""

from .tensor_fusionado import TensorFusionado, TensorHistorial
from .rmn import ReservoirMemoryNetwork
from .dmd import DMDPredictor, KoopmanObservable
from .hosvd import HOSVD, TensorModosTemporal
from .tensor_attention import TensorAttention
from .cp_decomposition import CPDecomposition
from .spa_predictor import SPAPredictor
from .motor_s4 import MotorS4, PrediccionS4
from .interfaz_ia_tensor import InterfazIATensor
from .storage_local import S4LocalStorage, S4StorageConfig
from .mapa_mental import MapaMental
from .percepcion_mental import PercepcionMental, ImagenMental
from .sistema_perceptual import SistemaPerceptualAvanzado

__all__ = [
    'TensorFusionado',
    'TensorHistorial',
    'ReservoirMemoryNetwork',
    'DMDPredictor',
    'KoopmanObservable',
    'HOSVD',
    'TensorModosTemporal',
    'TensorAttention',
    'CPDecomposition',
    'SPAPredictor',
    'MotorS4',
    'PrediccionS4',
    'InterfazIATensor',
    'S4LocalStorage',
    'S4StorageConfig',
    'MapaMental',
    'PercepcionMental',
    'ImagenMental',
    'SistemaPerceptualAvanzado',
]

__version__ = '1.0.0'

