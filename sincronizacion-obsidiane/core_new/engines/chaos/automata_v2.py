#!/usr/bin/env python3
"""
================================================================================
AUTÓMATA CELULAR v2.0 - MEJORAS AL BORDE DEL CAOS
================================================================================

Versión mejorada del autómata celular con 5 mejoras principales:

1. MAPEO HOLOGRÁFICO: Usa FFT + Otsu para binarización adaptativa
2. MULTI-REGLA ADAPTATIVA: Cambia entre reglas según estado dinámico
3. FEEDBACK LOOP CERRADO: Aplica ajustes automáticamente al sistema
4. AUTÓMATA 2D (GAME OF LIFE): Detección de gliders como conceptos
5. PERSISTENCIA: Guarda métricas y aprende patrones óptimos

Autor: Sistema Optimizado v2
================================================================================
"""

import numpy as np
import math
import time
import json
import os
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque
from pathlib import Path


# ==============================================================================
# PARTE 1: ENUMERACIONES Y ESTRUCTURAS
# ==============================================================================

class ClaseWolfram(Enum):
    """Clasificación de Wolfram para autómatas celulares."""
    CLASE_I = 1    # Orden: converge a homogéneo
    CLASE_II = 2   # Orden: estructuras periódicas
    CLASE_III = 3  # Caos: patrones aleatorios
    CLASE_IV = 4   # Borde del caos: estructuras complejas


class EstadoDinamico(Enum):
    """Estado dinámico del sistema."""
    MUY_ORDENADO = "muy_ordenado"
    ORDENADO = "ordenado"
    BORDE_CAOS = "borde_caos"
    CAOTICO = "caotico"
    MUY_CAOTICO = "muy_caotico"


@dataclass
class MetricasBordeCaosV2:
    """Métricas extendidas para el borde del caos v2."""
    # Métricas básicas
    entropia: float
    entropia_normalizada: float
    parametro_lambda: float
    densidad: float
    complejidad_lz: float
    lyapunov_estimado: float
    clase_estimada: ClaseWolfram
    
    # Métricas nuevas v2
    fase_fft_dominante: float = 0.0
    coherencia_espacial: float = 0.0
    gliders_detectados: int = 0
    estabilidad_temporal: float = 0.0
    estado_dinamico: EstadoDinamico = EstadoDinamico.BORDE_CAOS
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario para serialización."""
        d = asdict(self)
        d['clase_estimada'] = self.clase_estimada.name
        d['estado_dinamico'] = self.estado_dinamico.value
        return d


@dataclass
class AjustesSistema:
    """Ajustes sugeridos/aplicados al sistema principal."""
    learning_rate_factor: float = 1.0
    emotion_decay_factor: float = 1.0
    grundzug_threshold_factor: float = 1.0
    noise_injection: float = 0.0
    regularization: float = 0.0
    stability_factor: float = 1.0
    regla_sugerida: int = 110
    aplicado: bool = False
    timestamp: float = field(default_factory=time.time)


# ==============================================================================
# PARTE 2: AUTÓMATA CELULAR 1D MEJORADO
# ==============================================================================

class AutomataCelular1DV2:
    """
    Autómata Celular 1D mejorado con:
    - Multi-regla adaptativa
    - Mapeo holográfico (FFT + Otsu)
    - Métricas extendidas
    """
    
    # Reglas por clase de Wolfram
    REGLAS_CLASE_IV = [110, 124, 137, 193]  # Borde del caos
    REGLAS_CLASE_III = [30, 45, 73, 105]     # Caóticas (perturbación)
    REGLAS_CLASE_II = [4, 50, 108, 218]      # Periódicas (estabilización)
    
    def __init__(self, tamano: int = 256, regla: int = 110):
        self.tamano = tamano
        self.regla = regla
        self.tabla_transicion = self._decodificar_regla(regla)
        self.estado = np.zeros(tamano, dtype=np.uint8)
        self.historial: deque = deque(maxlen=1000)
        self.lambda_param = self._calcular_lambda()
        
        # Historial de reglas usadas (para aprendizaje)
        self.historial_reglas: List[Tuple[int, float]] = []  # (regla, distancia_borde)
    
    def _decodificar_regla(self, regla: int) -> Dict[Tuple[int,int,int], int]:
        """Decodificar número de regla Wolfram a tabla de transición."""
        tabla = {}
        for i in range(8):
            vecindad = ((i >> 2) & 1, (i >> 1) & 1, i & 1)
            resultado = (regla >> i) & 1
            tabla[vecindad] = resultado
        return tabla
    
    def _calcular_lambda(self) -> float:
        """Calcular parámetro de Langton."""
        transiciones_activas = sum(self.tabla_transicion.values())
        return transiciones_activas / 8.0
    
    def cambiar_regla(self, nueva_regla: int):
        """Cambiar la regla del autómata dinámicamente."""
        self.regla = nueva_regla
        self.tabla_transicion = self._decodificar_regla(nueva_regla)
        self.lambda_param = self._calcular_lambda()
    
    def seleccionar_regla_adaptativa(self, estado_dinamico: EstadoDinamico) -> int:
        """
        MEJORA #2: Seleccionar regla según estado dinámico.
        
        - Si muy ordenado → regla caótica (clase III) para perturbar
        - Si muy caótico → regla periódica (clase II) para estabilizar
        - Si borde → mantener clase IV
        """
        if estado_dinamico in [EstadoDinamico.MUY_ORDENADO, EstadoDinamico.ORDENADO]:
            # Necesita perturbación
            return np.random.choice(self.REGLAS_CLASE_III)
        elif estado_dinamico in [EstadoDinamico.CAOTICO, EstadoDinamico.MUY_CAOTICO]:
            # Necesita estabilización
            return np.random.choice(self.REGLAS_CLASE_II)
        else:
            # Mantener borde del caos
            return np.random.choice(self.REGLAS_CLASE_IV)
    
    def mapear_estado_holografico(self, 
                                   embedding: np.ndarray,
                                   emotion: np.ndarray,
                                   conceptos_activos: List[int] = None) -> np.ndarray:
        """
        MEJORA #1: Mapeo Holográfico con FFT y binarización Otsu.
        
        Usa TODAS las dimensiones del embedding + emoción + conceptos.
        """
        # 1. FFT del embedding para capturar estructura frecuencial
        if len(embedding) >= 2:
            fft = np.fft.fft(embedding)
            fase = np.angle(fft)
            magnitud = np.abs(fft)
        else:
            fase = np.array([0.0])
            magnitud = np.array([1.0])
        
        # 2. Modular fase con emoción (PAD)
        if len(emotion) >= 3:
            modulacion = emotion[0] * 0.3 + emotion[1] * 0.5 + emotion[2] * 0.2
        else:
            modulacion = 0.0
        
        fase_modulada = fase + modulacion * np.pi
        
        # 3. Incorporar información de conceptos activos
        if conceptos_activos:
            for concepto_id in conceptos_activos[:10]:  # Max 10 conceptos
                idx = concepto_id % len(fase_modulada)
                fase_modulada[idx] += 0.1 * np.pi
        
        # 4. Combinar en señal de mapeo
        senal = magnitud * np.cos(fase_modulada)
        
        # 5. Expandir/contraer al tamaño del autómata
        if len(senal) != self.tamano:
            senal = np.interp(
                np.linspace(0, 1, self.tamano),
                np.linspace(0, 1, len(senal)),
                senal
            )
        
        # 6. Binarización adaptativa (Otsu simplificado)
        umbral = self._otsu_threshold(senal)
        
        return (senal > umbral).astype(np.uint8)
    
    def _otsu_threshold(self, data: np.ndarray) -> float:
        """
        Calcular umbral óptimo de Otsu para binarización.
        Maximiza la varianza entre clases.
        """
        # Normalizar datos a [0, 1]
        data_norm = (data - data.min()) / (data.max() - data.min() + 1e-8)
        
        # Probar diferentes umbrales
        mejor_umbral = 0.5
        mejor_varianza = 0
        
        for t in np.linspace(0.1, 0.9, 17):
            # Clase 0: datos <= t
            # Clase 1: datos > t
            w0 = np.sum(data_norm <= t) / len(data_norm)
            w1 = 1 - w0
            
            if w0 == 0 or w1 == 0:
                continue
            
            mu0 = data_norm[data_norm <= t].mean() if w0 > 0 else 0
            mu1 = data_norm[data_norm > t].mean() if w1 > 0 else 0
            
            # Varianza entre clases
            varianza = w0 * w1 * (mu0 - mu1) ** 2
            
            if varianza > mejor_varianza:
                mejor_varianza = varianza
                mejor_umbral = t
        
        return data.min() + mejor_umbral * (data.max() - data.min())
    
    def paso(self) -> np.ndarray:
        """Ejecutar un paso del autómata."""
        nuevo_estado = np.zeros_like(self.estado)
        
        for i in range(self.tamano):
            izq = self.estado[(i - 1) % self.tamano]
            centro = self.estado[i]
            der = self.estado[(i + 1) % self.tamano]
            nuevo_estado[i] = self.tabla_transicion[(izq, centro, der)]
        
        self.estado = nuevo_estado
        self.historial.append(self.estado.copy())
        
        return self.estado
    
    def evolucionar(self, pasos: int) -> np.ndarray:
        """Evolucionar el autómata por varios pasos."""
        evolucion = [self.estado.copy()]
        for _ in range(pasos):
            self.paso()
            evolucion.append(self.estado.copy())
        return np.array(evolucion)
    
    def calcular_entropia(self, tamano_bloque: int = 3) -> float:
        """Calcular entropía de bloques."""
        if self.tamano < tamano_bloque:
            return 0.0
        
        conteos = {}
        for i in range(self.tamano - tamano_bloque + 1):
            bloque = tuple(self.estado[i:i + tamano_bloque])
            conteos[bloque] = conteos.get(bloque, 0) + 1
        
        total = sum(conteos.values())
        entropia = 0.0
        for count in conteos.values():
            p = count / total
            if p > 0:
                entropia -= p * np.log2(p)
        
        return entropia
    
    def calcular_complejidad_lz(self) -> float:
        """Calcular complejidad de Lempel-Ziv."""
        s = ''.join(map(str, self.estado))
        n = len(s)
        if n == 0:
            return 0.0
        
        palabras = set()
        i = 0
        while i < n:
            for j in range(i + 1, n + 1):
                if s[i:j] not in palabras:
                    palabras.add(s[i:j])
                    i = j
                    break
            else:
                break
        
        c = len(palabras)
        c_max = n / np.log2(n) if n > 1 else 1
        return c / c_max if c_max > 0 else 0.0
    
    def estimar_lyapunov(self, pasos: int = 100) -> float:
        """Estimar exponente de Lyapunov."""
        estado_original = self.estado.copy()
        estado_perturbado = estado_original.copy()
        pos = np.random.randint(0, self.tamano)
        estado_perturbado[pos] = 1 - estado_perturbado[pos]
        
        divergencias = []
        
        self.estado = estado_original.copy()
        orig_evol = self.evolucionar(pasos)
        
        self.estado = estado_perturbado
        pert_evol = self.evolucionar(pasos)
        
        for t in range(1, min(len(orig_evol), len(pert_evol))):
            diff = np.sum(orig_evol[t] != pert_evol[t])
            if diff > 0:
                divergencias.append(np.log(diff))
        
        self.estado = estado_original
        
        if len(divergencias) < 2:
            return 0.0
        return np.mean(np.diff(divergencias))
    
    def calcular_coherencia_espacial(self) -> float:
        """Calcular coherencia espacial (autocorrelación)."""
        if len(self.estado) < 2:
            return 0.0
        
        estado_float = self.estado.astype(float)
        media = estado_float.mean()
        estado_centrado = estado_float - media
        
        # Autocorrelación normalizada
        autocorr = np.correlate(estado_centrado, estado_centrado, mode='full')
        autocorr = autocorr[len(autocorr)//2:]  # Solo lado positivo
        
        if autocorr[0] == 0:
            return 0.0
        
        return autocorr[1] / autocorr[0] if len(autocorr) > 1 else 0.0
    
    def calcular_fase_fft_dominante(self) -> float:
        """Calcular fase de la frecuencia dominante."""
        if len(self.estado) < 2:
            return 0.0
        
        fft = np.fft.fft(self.estado.astype(float))
        magnitudes = np.abs(fft[1:len(fft)//2])  # Excluir DC
        
        if len(magnitudes) == 0:
            return 0.0
        
        idx_max = np.argmax(magnitudes) + 1
        fase = np.angle(fft[idx_max])
        
        return fase
    
    def clasificar_estado_dinamico(self, lyapunov: float, entropia_norm: float) -> EstadoDinamico:
        """Clasificar el estado dinámico actual."""
        if lyapunov < -0.5 and entropia_norm < 0.2:
            return EstadoDinamico.MUY_ORDENADO
        elif lyapunov < -0.1 and entropia_norm < 0.4:
            return EstadoDinamico.ORDENADO
        elif lyapunov > 0.5 and entropia_norm > 0.8:
            return EstadoDinamico.MUY_CAOTICO
        elif lyapunov > 0.1 and entropia_norm > 0.6:
            return EstadoDinamico.CAOTICO
        else:
            return EstadoDinamico.BORDE_CAOS
    
    def obtener_metricas_v2(self) -> MetricasBordeCaosV2:
        """Obtener métricas extendidas v2."""
        entropia = self.calcular_entropia()
        entropia_max = np.log2(2**3)
        entropia_norm = entropia / entropia_max if entropia_max > 0 else 0
        
        lyapunov = self.estimar_lyapunov(pasos=50)
        complejidad = self.calcular_complejidad_lz()
        coherencia = self.calcular_coherencia_espacial()
        fase_fft = self.calcular_fase_fft_dominante()
        
        # Clasificar
        if entropia_norm < 0.1:
            clase = ClaseWolfram.CLASE_I
        elif lyapunov < -0.3:
            clase = ClaseWolfram.CLASE_II
        elif lyapunov > 0.3:
            clase = ClaseWolfram.CLASE_III
        else:
            clase = ClaseWolfram.CLASE_IV
        
        estado_din = self.clasificar_estado_dinamico(lyapunov, entropia_norm)
        
        return MetricasBordeCaosV2(
            entropia=entropia,
            entropia_normalizada=entropia_norm,
            parametro_lambda=self.lambda_param,
            densidad=np.mean(self.estado),
            complejidad_lz=complejidad,
            lyapunov_estimado=lyapunov,
            clase_estimada=clase,
            fase_fft_dominante=fase_fft,
            coherencia_espacial=coherencia,
            estado_dinamico=estado_din
        )


# ==============================================================================
# PARTE 3: AUTÓMATA 2D (GAME OF LIFE) PARA GLIDERS
# ==============================================================================

class AutomataGameOfLife:
    """
    MEJORA #4: Autómata 2D (Game of Life) para detección de Gliders.
    
    Los Gliders representan conceptos estables que "viajan" por el espacio
    conceptual, análogos a ideas persistentes.
    """
    
    # Patrones conocidos de Gliders
    GLIDER_PATTERNS = [
        np.array([[0,1,0], [0,0,1], [1,1,1]]),  # Glider estándar
        np.array([[1,1,0], [0,1,1], [0,1,0]]),  # Glider rotado
    ]
    
    def __init__(self, filas: int = 32, columnas: int = 32):
        self.filas = filas
        self.columnas = columnas
        self.grilla = np.zeros((filas, columnas), dtype=np.uint8)
        self.historial: List[np.ndarray] = []
    
    def inicializar_desde_1d(self, estado_1d: np.ndarray):
        """Convertir estado 1D a grilla 2D."""
        # Reshape o tile para llenar la grilla
        total = self.filas * self.columnas
        if len(estado_1d) < total:
            estado_extendido = np.tile(estado_1d, (total // len(estado_1d) + 1))[:total]
        else:
            estado_extendido = estado_1d[:total]
        
        self.grilla = estado_extendido.reshape((self.filas, self.columnas))
        self.historial = [self.grilla.copy()]
    
    def paso(self) -> np.ndarray:
        """Ejecutar un paso de Game of Life."""
        nueva_grilla = np.zeros_like(self.grilla)
        
        for i in range(self.filas):
            for j in range(self.columnas):
                # Contar vecinos vivos (8 vecinos)
                vecinos = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni = (i + di) % self.filas
                        nj = (j + dj) % self.columnas
                        vecinos += self.grilla[ni, nj]
                
                # Reglas de Conway
                if self.grilla[i, j] == 1:
                    # Celda viva: sobrevive con 2 o 3 vecinos
                    if vecinos in [2, 3]:
                        nueva_grilla[i, j] = 1
                else:
                    # Celda muerta: nace con exactamente 3 vecinos
                    if vecinos == 3:
                        nueva_grilla[i, j] = 1
        
        self.grilla = nueva_grilla
        self.historial.append(self.grilla.copy())
        return self.grilla
    
    def evolucionar(self, pasos: int) -> List[np.ndarray]:
        """Evolucionar por varios pasos."""
        resultado = [self.grilla.copy()]
        for _ in range(pasos):
            self.paso()
            resultado.append(self.grilla.copy())
        return resultado
    
    def detectar_gliders(self) -> int:
        """
        Detectar gliders en la grilla actual.
        Retorna el número de gliders encontrados.
        """
        gliders = 0
        
        for patron in self.GLIDER_PATTERNS:
            h, w = patron.shape
            for i in range(self.filas - h + 1):
                for j in range(self.columnas - w + 1):
                    subgrilla = self.grilla[i:i+h, j:j+w]
                    if np.array_equal(subgrilla, patron):
                        gliders += 1
        
        return gliders
    
    def calcular_actividad(self) -> float:
        """Calcular nivel de actividad (densidad)."""
        return np.mean(self.grilla)


# ==============================================================================
# PARTE 4: REGULADOR CON FEEDBACK CERRADO
# ==============================================================================

class ReguladorBordeCaosV2:
    """
    MEJORA #3: Regulador con Feedback Loop Cerrado.
    
    No solo sugiere ajustes, sino que puede aplicarlos automáticamente
    al sistema principal con intensidad configurable.
    """
    
    def __init__(self,
                 objetivo_lambda: float = 0.5,
                 objetivo_entropia: float = 0.5,
                 tolerancia: float = 0.1,
                 intensidad_ajuste: float = 0.1,
                 intervalo_aplicacion: int = 10):
        """
        Args:
            objetivo_lambda: Valor objetivo del parámetro λ
            objetivo_entropia: Entropía normalizada objetivo
            tolerancia: Tolerancia para "en el borde"
            intensidad_ajuste: Qué tan agresivos son los ajustes (0-1)
            intervalo_aplicacion: Cada cuántos ciclos aplicar ajustes
        """
        self.objetivo_lambda = objetivo_lambda
        self.objetivo_entropia = objetivo_entropia
        self.tolerancia = tolerancia
        self.intensidad_ajuste = intensidad_ajuste
        self.intervalo_aplicacion = intervalo_aplicacion
        
        self.historial_metricas: List[MetricasBordeCaosV2] = []
        self.historial_ajustes: List[AjustesSistema] = []
        self.ciclos_desde_ajuste = 0
        
        # Parámetros actuales del sistema (para feedback cerrado)
        self.params_sistema = {
            'learning_rate': 0.1,
            'emotion_decay': 0.9,
            'grundzug_threshold': 0.01
        }
    
    def evaluar_distancia_borde(self, metricas: MetricasBordeCaosV2) -> float:
        """Calcular distancia al borde del caos ideal."""
        dist_lambda = abs(metricas.parametro_lambda - self.objetivo_lambda)
        dist_entropia = abs(metricas.entropia_normalizada - self.objetivo_entropia)
        dist_lyapunov = abs(metricas.lyapunov_estimado)
        dist_complejidad = max(0, 0.5 - metricas.complejidad_lz)
        
        return (dist_lambda + dist_entropia + dist_lyapunov + dist_complejidad) / 4
    
    def esta_en_borde(self, metricas: MetricasBordeCaosV2) -> bool:
        """Verificar si está en el borde del caos."""
        return metricas.estado_dinamico == EstadoDinamico.BORDE_CAOS
    
    def calcular_ajustes(self, metricas: MetricasBordeCaosV2) -> AjustesSistema:
        """Calcular ajustes necesarios."""
        ajuste = AjustesSistema()
        
        # Ajustar según estado dinámico
        if metricas.estado_dinamico == EstadoDinamico.MUY_ORDENADO:
            ajuste.learning_rate_factor = 1.0 + 0.2 * self.intensidad_ajuste
            ajuste.emotion_decay_factor = 1.0 - 0.1 * self.intensidad_ajuste
            ajuste.noise_injection = 0.1 * self.intensidad_ajuste
            ajuste.regla_sugerida = 30  # Regla caótica
            
        elif metricas.estado_dinamico == EstadoDinamico.ORDENADO:
            ajuste.learning_rate_factor = 1.0 + 0.1 * self.intensidad_ajuste
            ajuste.noise_injection = 0.05 * self.intensidad_ajuste
            ajuste.regla_sugerida = 45
            
        elif metricas.estado_dinamico == EstadoDinamico.CAOTICO:
            ajuste.learning_rate_factor = 1.0 - 0.1 * self.intensidad_ajuste
            ajuste.stability_factor = 1.0 + 0.1 * self.intensidad_ajuste
            ajuste.regularization = 0.1 * self.intensidad_ajuste
            ajuste.regla_sugerida = 108
            
        elif metricas.estado_dinamico == EstadoDinamico.MUY_CAOTICO:
            ajuste.learning_rate_factor = 1.0 - 0.2 * self.intensidad_ajuste
            ajuste.stability_factor = 1.0 + 0.2 * self.intensidad_ajuste
            ajuste.regularization = 0.2 * self.intensidad_ajuste
            ajuste.regla_sugerida = 4  # Regla muy ordenada
            
        else:  # BORDE_CAOS
            ajuste.regla_sugerida = 110
        
        return ajuste
    
    def aplicar_ajustes(self, ajuste: AjustesSistema) -> Dict[str, float]:
        """
        MEJORA #3: Aplicar ajustes al sistema (feedback cerrado).
        
        Returns:
            Nuevos valores de parámetros
        """
        self.params_sistema['learning_rate'] *= ajuste.learning_rate_factor
        self.params_sistema['emotion_decay'] *= ajuste.emotion_decay_factor
        self.params_sistema['grundzug_threshold'] *= ajuste.grundzug_threshold_factor
        
        # Clampar valores
        self.params_sistema['learning_rate'] = np.clip(
            self.params_sistema['learning_rate'], 0.001, 1.0
        )
        self.params_sistema['emotion_decay'] = np.clip(
            self.params_sistema['emotion_decay'], 0.5, 0.99
        )
        self.params_sistema['grundzug_threshold'] = np.clip(
            self.params_sistema['grundzug_threshold'], 0.001, 0.1
        )
        
        ajuste.aplicado = True
        self.historial_ajustes.append(ajuste)
        self.ciclos_desde_ajuste = 0
        
        return self.params_sistema.copy()
    
    def ciclo(self, metricas: MetricasBordeCaosV2) -> Tuple[AjustesSistema, bool]:
        """
        Ejecutar un ciclo del regulador.
        
        Returns:
            (ajustes, fue_aplicado)
        """
        self.historial_metricas.append(metricas)
        self.ciclos_desde_ajuste += 1
        
        ajuste = self.calcular_ajustes(metricas)
        
        # Decidir si aplicar
        debe_aplicar = (
            self.ciclos_desde_ajuste >= self.intervalo_aplicacion and
            not self.esta_en_borde(metricas)
        )
        
        if debe_aplicar:
            self.aplicar_ajustes(ajuste)
            return ajuste, True
        
        return ajuste, False
    
    def obtener_parametros_actuales(self) -> Dict[str, float]:
        """Obtener parámetros actuales del sistema."""
        return self.params_sistema.copy()


# ==============================================================================
# PARTE 5: PERSISTENCIA Y APRENDIZAJE
# ==============================================================================

class PersistenciaBordeCaos:
    """
    MEJORA #5: Persistencia de métricas y aprendizaje.
    
    Guarda historial de métricas y ajustes exitosos para
    aprender qué combinaciones funcionan mejor.
    """
    
    def __init__(self, ruta_archivo: str = "metricas_borde_caos.json"):
        self.ruta_archivo = ruta_archivo
        self.datos = {
            'metricas': [],
            'ajustes_exitosos': [],
            'mejores_reglas': {},
            'version': '2.0'
        }
        self.cargar()
    
    def cargar(self):
        """Cargar datos desde archivo."""
        try:
            if os.path.exists(self.ruta_archivo):
                with open(self.ruta_archivo, 'r') as f:
                    self.datos = json.load(f)
        except Exception as e:
            print(f"Aviso: No se pudo cargar {self.ruta_archivo}: {e}")
    
    def guardar(self):
        """Guardar datos a archivo."""
        try:
            with open(self.ruta_archivo, 'w') as f:
                json.dump(self.datos, f, indent=2, default=str)
        except Exception as e:
            print(f"Error guardando {self.ruta_archivo}: {e}")
    
    def registrar_metricas(self, metricas: MetricasBordeCaosV2):
        """Registrar métricas."""
        self.datos['metricas'].append(metricas.to_dict())
        
        # Limitar tamaño del historial
        if len(self.datos['metricas']) > 10000:
            self.datos['metricas'] = self.datos['metricas'][-5000:]
    
    def registrar_ajuste_exitoso(self, 
                                  regla: int, 
                                  estado_antes: EstadoDinamico,
                                  estado_despues: EstadoDinamico):
        """Registrar un ajuste que llevó a mejor estado."""
        if estado_despues == EstadoDinamico.BORDE_CAOS:
            clave = estado_antes.value
            if clave not in self.datos['mejores_reglas']:
                self.datos['mejores_reglas'][clave] = {}
            
            regla_str = str(regla)
            if regla_str not in self.datos['mejores_reglas'][clave]:
                self.datos['mejores_reglas'][clave][regla_str] = 0
            
            self.datos['mejores_reglas'][clave][regla_str] += 1
    
    def obtener_mejor_regla(self, estado_actual: EstadoDinamico) -> Optional[int]:
        """Obtener la mejor regla aprendida para un estado dado."""
        clave = estado_actual.value
        if clave in self.datos['mejores_reglas']:
            reglas = self.datos['mejores_reglas'][clave]
            if reglas:
                mejor = max(reglas.items(), key=lambda x: x[1])
                return int(mejor[0])
        return None


# ==============================================================================
# PARTE 6: INTEGRADOR COMPLETO V2
# ==============================================================================

class IntegradorSistemaBordeCaosV2:
    """
    Integrador completo v2 que combina todas las mejoras:
    - Autómata 1D con mapeo holográfico
    - Autómata 2D para gliders
    - Regulador con feedback cerrado
    - Persistencia y aprendizaje
    """
    
    def __init__(self, 
                 tamano_automata: int = 128,
                 intensidad_ajuste: float = 0.1,
                 ruta_persistencia: str = None):
        """
        Args:
            tamano_automata: Tamaño del autómata 1D
            intensidad_ajuste: Intensidad de ajustes automáticos
            ruta_persistencia: Ruta para guardar métricas (None = sin persistencia)
        """
        # Autómata 1D mejorado
        self.automata_1d = AutomataCelular1DV2(tamano=tamano_automata, regla=110)
        
        # Autómata 2D para gliders
        lado_2d = int(np.sqrt(tamano_automata))
        self.automata_2d = AutomataGameOfLife(filas=lado_2d, columnas=lado_2d)
        
        # Regulador con feedback cerrado
        self.regulador = ReguladorBordeCaosV2(
            intensidad_ajuste=intensidad_ajuste,
            intervalo_aplicacion=10
        )
        
        # Persistencia (opcional)
        self.persistencia = None
        if ruta_persistencia:
            self.persistencia = PersistenciaBordeCaos(ruta_persistencia)
        
        # Estado anterior para detectar transiciones
        self.estado_anterior: Optional[EstadoDinamico] = None
    
    def evaluar_dinamica_completa(self,
                                   embedding: np.ndarray,
                                   emotion: np.ndarray,
                                   entropia_sistema: float,
                                   conceptos_activos: List[int] = None,
                                   pasos_simulacion: int = 50) -> MetricasBordeCaosV2:
        """
        Evaluación completa de dinámica.
        
        1. Mapeo holográfico
        2. Evolución 1D y 2D
        3. Detección de gliders
        4. Métricas completas
        """
        # 1. Mapeo holográfico al autómata 1D
        estado_1d = self.automata_1d.mapear_estado_holografico(
            embedding, emotion, conceptos_activos
        )
        self.automata_1d.estado = estado_1d
        self.automata_1d.historial.clear()
        self.automata_1d.historial.append(estado_1d.copy())
        
        # 2. Evolucionar 1D
        self.automata_1d.evolucionar(pasos_simulacion)
        
        # 3. Inicializar y evolucionar 2D
        self.automata_2d.inicializar_desde_1d(self.automata_1d.estado)
        self.automata_2d.evolucionar(pasos_simulacion // 2)
        
        # 4. Obtener métricas
        metricas = self.automata_1d.obtener_metricas_v2()
        metricas.gliders_detectados = self.automata_2d.detectar_gliders()
        
        # 5. Calcular estabilidad temporal
        if len(self.automata_1d.historial) >= 10:
            ultimos = list(self.automata_1d.historial)[-10:]
            cambios = sum(
                np.sum(ultimos[i] != ultimos[i-1]) 
                for i in range(1, len(ultimos))
            )
            metricas.estabilidad_temporal = 1.0 - min(1.0, cambios / (10 * self.automata_1d.tamano))
        
        # 6. Registrar en persistencia
        if self.persistencia:
            self.persistencia.registrar_metricas(metricas)
        
        return metricas
    
    def ciclo_regulacion(self, metricas: MetricasBordeCaosV2) -> Tuple[AjustesSistema, Dict[str, float]]:
        """
        Ejecutar ciclo de regulación con feedback cerrado.
        
        Returns:
            (ajustes, nuevos_parametros)
        """
        ajuste, aplicado = self.regulador.ciclo(metricas)
        
        # Adaptar regla del autómata si cambió estado
        if self.estado_anterior != metricas.estado_dinamico:
            # Buscar regla aprendida
            regla_aprendida = None
            if self.persistencia:
                regla_aprendida = self.persistencia.obtener_mejor_regla(metricas.estado_dinamico)
            
            if regla_aprendida:
                nueva_regla = regla_aprendida
            else:
                nueva_regla = self.automata_1d.seleccionar_regla_adaptativa(metricas.estado_dinamico)
            
            self.automata_1d.cambiar_regla(nueva_regla)
            ajuste.regla_sugerida = nueva_regla
            
            # Registrar transición en persistencia
            if self.persistencia and self.estado_anterior:
                self.persistencia.registrar_ajuste_exitoso(
                    nueva_regla,
                    self.estado_anterior,
                    metricas.estado_dinamico
                )
        
        self.estado_anterior = metricas.estado_dinamico
        
        return ajuste, self.regulador.obtener_parametros_actuales()
    
    def guardar_estado(self):
        """Guardar persistencia."""
        if self.persistencia:
            self.persistencia.guardar()


# ==============================================================================
# PARTE 7: DEMOSTRACIÓN
# ==============================================================================

def demo_automata_v2():
    """Demostración del Autómata Celular v2 con todas las mejoras."""
    print("=" * 70)
    print("  AUTÓMATA CELULAR v2.0 - BORDE DEL CAOS MEJORADO")
    print("=" * 70)
    
    # Crear integrador
    integrador = IntegradorSistemaBordeCaosV2(
        tamano_automata=128,
        intensidad_ajuste=0.15
    )
    
    print("\n[1] Probando Mapeo Holográfico (MEJORA #1)")
    print("-" * 50)
    
    # Simular diferentes estados del sistema
    estados_test = [
        ("Sistema ordenado", np.zeros(64), np.array([0.1, 0.1, 0.1]), 0.1),
        ("Sistema estructurado", np.sin(np.linspace(0, 4*np.pi, 64)), np.array([0.3, -0.2, 0.1]), 0.5),
        ("Sistema caótico", np.random.randn(64), np.array([0.9, 0.8, 0.7]), 0.9),
    ]
    
    for nombre, emb, emo, ent in estados_test:
        metricas = integrador.evaluar_dinamica_completa(emb, emo, ent)
        print(f"\n  {nombre}:")
        print(f"    Estado: {metricas.estado_dinamico.value}")
        print(f"    λ Langton: {metricas.parametro_lambda:.3f}")
        print(f"    Entropía norm: {metricas.entropia_normalizada:.3f}")
        print(f"    Lyapunov: {metricas.lyapunov_estimado:.3f}")
        print(f"    Fase FFT: {metricas.fase_fft_dominante:.3f}")
        print(f"    Gliders (2D): {metricas.gliders_detectados}")
    
    print("\n\n[2] Probando Multi-Regla Adaptativa (MEJORA #2)")
    print("-" * 50)
    
    for estado in EstadoDinamico:
        regla = integrador.automata_1d.seleccionar_regla_adaptativa(estado)
        print(f"    {estado.value:15} → Regla {regla}")
    
    print("\n\n[3] Probando Feedback Loop Cerrado (MEJORA #3)")
    print("-" * 50)
    
    print(f"    Parámetros iniciales: {integrador.regulador.obtener_parametros_actuales()}")
    
    # Simular varios ciclos
    for i in range(3):
        emb = np.random.randn(64) * (0.5 + i * 0.3)
        emo = np.array([0.5, 0.5, 0.5])
        metricas = integrador.evaluar_dinamica_completa(emb, emo, 0.5)
        ajuste, params = integrador.ciclo_regulacion(metricas)
        print(f"\n    Ciclo {i+1}:")
        print(f"      Estado: {metricas.estado_dinamico.value}")
        print(f"      Ajuste aplicado: {ajuste.aplicado}")
        print(f"      Parámetros: lr={params['learning_rate']:.4f}, decay={params['emotion_decay']:.3f}")
    
    print("\n\n[4] Autómata 2D y Detección de Gliders (MEJORA #4)")
    print("-" * 50)
    
    # Insertar un glider manualmente
    integrador.automata_2d.grilla = np.zeros((11, 11), dtype=np.uint8)
    integrador.automata_2d.grilla[1:4, 1:4] = [[0,1,0], [0,0,1], [1,1,1]]
    
    print("\n    Grilla inicial con glider insertado:")
    for fila in integrador.automata_2d.grilla:
        print("    " + ''.join('█' if c else '░' for c in fila))
    
    gliders = integrador.automata_2d.detectar_gliders()
    print(f"\n    Gliders detectados: {gliders}")
    
    print("\n    Evolución (5 pasos):")
    for t in range(5):
        integrador.automata_2d.paso()
        gliders = integrador.automata_2d.detectar_gliders()
        actividad = integrador.automata_2d.calcular_actividad()
        print(f"    t={t+1}: Gliders={gliders}, Actividad={actividad:.3f}")
    
    print("\n\n[5] Persistencia (MEJORA #5)")
    print("-" * 50)
    print("    La persistencia guarda métricas y ajustes exitosos")
    print("    para aprender qué reglas funcionan mejor para cada estado.")
    print("    (Deshabilitada en esta demo, requiere ruta de archivo)")
    
    print("\n" + "=" * 70)
    print("  FIN DE DEMOSTRACIÓN v2.0")
    print("=" * 70)


if __name__ == "__main__":
    demo_automata_v2()
