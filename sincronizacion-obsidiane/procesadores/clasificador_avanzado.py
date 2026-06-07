"""
Clasificador Avanzado Auto-Calibrado
=====================================

Clasificador ML que aprende patrones emocionales/conceptuales
desde métricas físicas puras (hash, energía, entropía, ciclos).

NO depende de semántica para predicciones iniciales.
Se auto-calibra con feedback del TokenizadorFenomenológico.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import logging
from typing import Dict, List, Any, Optional, Tuple
import zlib
import lzma
import bz2
from dataclasses import dataclass

logger = logging.getLogger("ClasificadorAvanzado")


@dataclass
class PrediccionClasificador:
    """Resultado de una clasificación."""
    clases_probabilidades: Dict[str, float]
    clase_predicha: str
    certeza: float
    vector_entrada: np.ndarray


class ExtractorFeatures72D:
    """
    Extrae vector de 72 dimensiones desde vector físico de Capa  1.
    
    Componentes:
    -----------
    - 4D: Métricas básicas normalizadas
    - 6D: Ratios entre métricas
    - 4D: Transformaciones logarítmicas
    - 16D: Embedding espectral del hash
    - 8D: Estadísticas del hash
    - 4D: Complejidad Kolmogorov
    - 10D: Features espectrales FFT
    - 20D: Features derivadas y productos cruzados
    """
    
    def extraer(self, vector_fisico: Dict) -> np.ndarray:
        """
        Extrae features 72D desde vector físico.
        
        Args:
            vector_fisico: Dict con {energia, entropia, tiempo, instrucciones, hash}
        
        Returns:
            np.ndarray de 72 dimensiones
        """
        features = []
        
        # Métricas base
        E = vector_fisico.get('energia', 0)
        S = vector_fisico.get('entropia', 0)
        T = vector_fisico.get('tiempo', 0)
        I = vector_fisico.get('instrucciones', 0)
        hash_str = vector_fisico.get('hash', '0' * 64)
        
        # ===== 1. FEATURES BÁSICAS (4D) =====
        features.extend([
            E / 10000.0,        # Energía norm [0-1]
            S / 4e9,            # Entropía norm [0-1]
            T / 1e7,            # Tiempo norm [0-1]
            I / 1e6             # Instrucciones norm [0-1]
        ])
        
        # ===== 2. RATIOS (6D) =====
        features.extend([
            E / (T + 1),        # Potencia
            I / (T + 1),        # IPC
            S / (E + 1),        # Entropía/energía
            E / (I + 1),        # Energía/instrucción
            S / (I + 1),        # Entropía/instrucción
            T / (I + 1)         # Ciclos/instrucción
        ])
        
        # ===== 3. LOGARÍTMICOS (4D) =====
        features.extend([
            np.log1p(E),
            np.log1p(S),
            np.log1p(T),
            np.log1p(I)
        ])
        
        # ===== 4. HASH EMBEDDING ESPECTRAL (16D) =====
        hash_emb = self._hash_to_embedding(hash_str)
        features.extend(hash_emb)
        
        # ===== 5. ESTADÍSTICAS DEL HASH (8D) =====
        hash_stats = self._hash_stats(hash_str)
        features.extend(hash_stats)
        
        # ===== 6. COMPLEJIDAD KOLMOGOROV (4D) =====
        kolmogorov = self._complejidad_kolmogorov(hash_str)
        features.extend(kolmogorov)
        
        # ===== 7. FEATURES ESPECTRALES (10D) =====
        spectral = self._features_espectrales(hash_str)
        features.extend(spectral)
        
        # ===== 8. FEATURES DERIVADAS (20D) =====
        derivadas = self._features_derivadas(E, S, T, I)
        features.extend(derivadas)
        
        # Asegurar 72 dimensiones exactas
        features_array = np.array(features[:72], dtype=np.float32)
        
        # Manejar NaN/Inf
        features_array = np.nan_to_num(features_array, nan=0.0, posinf=1.0, neginf=0.0)
        
        return features_array
    
    def _hash_to_embedding(self, hash_str: str) -> List[float]:
        """Embedding espectral del hash (16D)."""
        try:
            hash_bytes = bytes.fromhex(hash_str[:32])
            matrix = np.frombuffer(hash_bytes, dtype=np.uint8).reshape(4, 4)
            
            # FFT 2D
            fft = np.fft.fft2(matrix)
            magnitudes = np.abs(fft.flatten())
            
            # Top 16 coeficientes normalizados
            embedding = magnitudes[:16] / (np.max(magnitudes) + 1e-8)
            
            return embedding.tolist()
        except:
            return [0.0] * 16
    
    def _hash_stats(self, hash_str: str) -> List[float]:
        """Estadísticas del hash (8D)."""
        try:
            hash_bytes = np.array(list(bytes.fromhex(hash_str[:32])), dtype=np.float32)
            
            return [
                np.mean(hash_bytes) / 255.0,
                np.std(hash_bytes) / 255.0,
                np.median(hash_bytes) / 255.0,
                np.min(hash_bytes) / 255.0,
                np.max(hash_bytes) / 255.0,
                np.percentile(hash_bytes, 25) / 255.0,
                np.percentile(hash_bytes, 75) / 255.0,
                len(set(hash_bytes)) / 256.0  # Diversidad
            ]
        except:
            return [0.0] * 8
    
    def _complejidad_kolmogorov(self, hash_str: str) -> List[float]:
        """Complejidad Kolmogorov aproximada (4D)."""
        try:
            hash_bytes = bytes.fromhex(hash_str[:32])
            len_original = len(hash_bytes)
            
            return [
                len(zlib.compress(hash_bytes)) / len_original,
                len(lzma.compress(hash_bytes)) / len_original,
                len(bz2.compress(hash_bytes)) / len_original,
                np.corrcoef(
                    np.array(list(hash_bytes[:-1])),
                    np.array(list(hash_bytes[1:]))
                )[0, 1]
            ]
        except:
            return [0.5, 0.5, 0.5, 0.0]
    
    def _features_espectrales(self, hash_str: str) -> List[float]:
        """Features espectrales FFT (10D)."""
        try:
            hash_bytes = np.array(list(bytes.fromhex(hash_str[:32])), dtype=np.float32)
            
            spectrum = np.fft.fft(hash_bytes)
            magnitudes = np.abs(spectrum)[:10]
            
            return (magnitudes / (np.max(magnitudes) + 1e-8)).tolist()
        except:
            return [0.0] * 10
    
    def _features_derivadas(self, E, S, T, I) -> List[float]:
        """Features derivadas y productos cruzados (20D)."""
        features = []
        
        # Productos cruzados normalizados
        features.extend([
            (E * S) / 1e13,
            (E * T) / 1e10,
            (S * T) / 1e16,
            (I * E) / 1e9,
            (I * S) / 1e13,
            (I * T) / 1e10
        ])
        
        # Potencias
        features.extend([
            np.sqrt(E) / 100,
            np.sqrt(S) / 1e5,
            np.sqrt(T) / 1e4,
            np.sqrt(I) / 1e3
        ])
        
        # Inversos (evitar división por cero)
        features.extend([
            1.0 / (E + 1),
            1.0 / (S + 1e6),
            1.0 / (T + 1e3),
            1.0 / (I + 1e2)
        ])
        
        # Combinaciones trigonométricas (para capturar periodicidad)
        features.extend([
            np.sin(E / 1000),
            np.cos(S / 1e9),
            np.sin(T / 1e6),
            np.cos(I / 1e5),
            np.tanh(E / 5000),
            np.tanh(S / 2e9)
        ])
        
        return features[:20]


class ClasificadorAvanzado:
    """
    Clasificador neuronal profundo que predice conceptos/emociones
    desde vector físico 72D.
    """
    
    def __init__(self, num_clases: int = 20, modelo_path: Optional[str] = None):
        """
        Inicializa clasificador.
        
        Args:
            num_clases: Número de clases de salida
            modelo_path: Ruta al modelo pre-entrenado (.h5)
        """
        self.num_clases = num_clases
        self.extractor = ExtractorFeatures72D()
        
        # Nombres de clases (ejemplo - personalizar según necesidad)
        self.nombres_clases = [
            'melancolía', 'alegría', 'serenidad', 'angustia',
            'neutro', 'técnico', 'poético', 'narrativo',
            'visual', 'auditivo', 'haptico', 'olfativo',
            'abstracto', 'concreto', 'reflexivo', 'perceptivo',
            'memoria', 'imaginación', 'anticipación', 'presente'
        ][:num_clases]
        
        # Cargar o crear modelo
        if modelo_path and os.path.exists(modelo_path):
            logger.info(f"Cargando modelo desde {modelo_path}")
            self.modelo = keras.models.load_model(modelo_path)
        else:
            logger.info("Creando nuevo modelo")
            self.modelo = self._crear_modelo()
        
        logger.info(f"✅ Clasificador inicializado ({num_clases} clases)")
    
    def _crear_modelo(self) -> keras.Model:
        """
        Crea arquitectura de red neuronal profunda.
        
        Arquitectura:
        ------------
        Input (72) → Dense(128) → BN → Dropout(0.3)
                  → Dense(64) → BN → Dropout(0.2)
                  → MultiHeadAttention
                  → Dense(32) → Dropout(0.1)
                  → Output(num_clases)
        """
        inputs = keras.Input(shape=(72,), name='vector_fisico')
        
        # Capa 1: Expansión
        x = keras.layers.Dense(128, activation='relu', name='dense_1')(inputs)
        x = keras.layers.BatchNormalization(name='bn_1')(x)
        x = keras.layers.Dropout(0.3, name='dropout_1')(x)
        
        # Capa 2: Abstracción
        x = keras.layers.Dense(64, activation='relu', name='dense_2')(x)
        x = keras.layers.BatchNormalization(name='bn_2')(x)
        x = keras.layers.Dropout(0.2, name='dropout_2')(x)
        
        # Capa 3: Self-Attention (aprende importancia de features)
        # Reshape para attention: (batch, seq_len, dim) = (batch, 1, 64)
        x_reshaped = keras.layers.Reshape((1, 64))(x)
        attention = keras.layers.MultiHeadAttention(
            num_heads=4,
            key_dim=16,
            name='attention'
        )(x_reshaped, x_reshaped)
        attention_flat = keras.layers.Flatten()(attention)
        x = keras.layers.Add(name='attention_add')([x, attention_flat])
        
        # Capa 4: Compresión
        x = keras.layers.Dense(32, activation='relu', name='dense_3')(x)
        x = keras.layers.Dropout(0.1, name='dropout_3')(x)
        
        # Output
        outputs = keras.layers.Dense(
            self.num_clases,
            activation='softmax',
            name='output'
        )(x)
        
        modelo = keras.Model(inputs=inputs, outputs=outputs, name='clasificador_avanzado')
        
        # Compilar
        modelo.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
        )
        
        return modelo
    
    def predecir(self, vector_fisico: Dict) -> PrediccionClasificador:
        """
        Predice clase desde vector físico.
        
        Args:
            vector_fisico: Dict con energia, entropia, tiempo, instrucciones, hash
        
        Returns:
            PrediccionClasificador con probabilidades y clase predicha
        """
        # Extraer features 72D
        features = self.extractor.extraer(vector_fisico)
        features_batch = np.expand_dims(features, axis=0)
        
        # Predicción
        probabilidades = self.modelo.predict(features_batch, verbose=0)[0]
        
        # Clase con mayor probabilidad
        idx_predicho = np.argmax(probabilidades)
        clase_predicha = self.nombres_clases[idx_predicho]
        certeza = float(probabilidades[idx_predicho])
        
        # Dict de probabilidades
        probs_dict = {
            self.nombres_clases[i]: float(probabilidades[i])
            for i in range(len(self.nombres_clases))
        }
        
        return PrediccionClasificador(
            clases_probabilidades=probs_dict,
            clase_predicha=clase_predicha,
            certeza=certeza,
            vector_entrada=features
        )
    
    def entrenar_incremental(
        self,
        vector_fisico: Dict,
        clase_verdadera: str,
        learning_rate: float = 0.0001
    ):
        """
        Entrenamient incremental con un solo ejemplo (online learning).
        
        Args:
            vector_fisico: Vector físico de entrada
            clase_verdadera: Clase correcta (para supervisión)
            learning_rate: Tasa de aprendizaje
        """
        # Extraer features
        features = self.extractor.extraer(vector_fisico)
        X = np.expand_dims(features, axis=0)
        
        # One-hot encoding de la clase
        try:
            idx_clase = self.nombres_clases.index(clase_verdadera)
        except ValueError:
            logger.warning(f"Clase desconocida: {clase_verdadera}")
            return
        
        y = np.zeros((1, self.num_clases))
        y[0, idx_clase] = 1.0
        
        # Ajustar learning rate
        keras.backend.set_value(self.modelo.optimizer.learning_rate, learning_rate)
        
        # Entrenar con un solo batch
        loss = self.modelo.train_on_batch(X, y)
        
        logger.debug(f"Entrenamiento incremental: loss={loss:.4f}")
    
    def guardar_modelo(self, path: str):
        """Guarda modelo en disco."""
        self.modelo.save(path)
        logger.info(f"💾 Modelo guardado en {path}")
    
    def obtener_info(self) -> Dict:
        """Información del clasificador."""
        return {
            'num_clases': self.num_clases,
            'nombres_clases': self.nombres_clases,
            'arquitectura': self.modelo.summary(),
            'parametros_totales': self.modelo.count_params()
        }


# =============================================
# EJEMPLO DE USO
# =============================================

if __name__ == "__main__":
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    # Crear clasificador
    clf = ClasificadorAvanzado(num_clases=20)
    
    # Ejemplo de vector físico
    vector_test = {
        'energia': 3420,
        'entropia': 2847563921,
        'tiempo': 1250000,
        'instrucciones': 45823,
        'hash': 'a7f3e2d9c1b4a8f3e2c5d7b9a4f6e8c2'
    }
    
    # Predicción
    prediccion = clf.predecir(vector_test)
    
    print(f"\n✅ Predicción:")
    print(f"  Clase: {prediccion.clase_predicha}")
    print(f"  Certeza: {prediccion.certeza:.2%}")
    print(f"\n  Top 3 clases:")
    sorted_probs = sorted(
        prediccion.clases_probabilidades.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    for clase, prob in sorted_probs:
        print(f"    - {clase}: {prob:.2%}")
    
    # Guardar modelo
    clf.guardar_modelo("modelos/clasificador_avanzado.h5")
