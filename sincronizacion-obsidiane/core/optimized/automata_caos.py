"""
MÓDULO: AUTÓMATA CELULAR AL BORDE DEL CAOS
==========================================

Implementa un autómata celular 1D que puede integrarse con el sistema
para proporcionar dinámica adicional al borde del caos. 

Inspirado en Regla 110 y teoría de Langton. 
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from collections import deque


class ClaseWolfram(Enum):
    """Clasificación de Wolfram para autómatas celulares."""
    CLASE_I = 1    # Orden: converge a homogéneo
    CLASE_II = 2   # Orden: estructuras periódicas
    CLASE_III = 3  # Caos: patrones aleatorios
    CLASE_IV = 4   # Borde del caos: estructuras complejas


@dataclass
class MetricasBordeCaos:
    """Métricas para determinar si el sistema está al borde del caos."""
    entropia: float              # Entropía de Shannon
    entropia_normalizada: float  # Entropía / Entropía máxima
    parametro_lambda: float      # Parámetro de Langton
    densidad: float              # Proporción de celdas activas
    complejidad: float           # Medida de complejidad estructural
    lyapunov_estimado: float     # Exponente de Lyapunov aproximado
    clase_estimada: ClaseWolfram # Clasificación estimada


class AutomataCelular1D:
    """
    Autómata celular 1D con análisis de borde del caos. 
    
    Fundamento Matemático:
    
    1.  PARÁMETRO DE LANGTON (λ):
       λ = (K^N - n_q) / K^N
       donde n_q = transiciones al estado quiescente
       
    2.  ENTROPÍA DE BLOQUE:
       H_b = -Σ p(bloque) log₂ p(bloque)
       Mide complejidad de patrones de tamaño b
       
    3.EXPONENTE DE LYAPUNOV:
       λ_L = lim (1/t) Σ log |δx_t / δx_0|
       λ_L < 0: orden, λ_L ≈ 0: borde, λ_L > 0: caos
    """
    
    # Reglas conocidas al borde del caos
    REGLAS_BORDE_CAOS = [110, 124, 137, 193, 54, 62, 126]
    
    def __init__(self, tamano: int = 256, regla: int = 110):
        """
        Args:
            tamano: Número de celdas
            regla: Número de regla Wolfram (0-255)
        """
        self.tamano = tamano
        self.regla = regla
        
        # Decodificar regla a tabla de transición
        self.tabla_transicion = self._decodificar_regla(regla)
        
        # Estado actual
        self.estado = np.zeros(tamano, dtype=np.uint8)
        
        # Historial para análisis
        self.historial: deque = deque(maxlen=1000)
        
        # Calcular parámetro λ
        self.lambda_param = self._calcular_lambda()
    
    def _decodificar_regla(self, regla: int) -> Dict[Tuple[int,int,int], int]:
        """
        Decodificar número de regla Wolfram a tabla de transición.
        
        La regla R se interpreta como:
        - Bit 0: resultado para vecindad (0,0,0)
        - Bit 1: resultado para vecindad (0,0,1)
        - ... 
        - Bit 7: resultado para vecindad (1,1,1)
        """
        tabla = {}
        for i in range(8):
            # Configuración de vecindad (izq, centro, der)
            vecindad = ((i >> 2) & 1, (i >> 1) & 1, i & 1)
            # Resultado según la regla
            resultado = (regla >> i) & 1
            tabla[vecindad] = resultado
        return tabla
    
    def _calcular_lambda(self) -> float:
        """
        Calcular parámetro de Langton. 
        
        λ = (transiciones a estado 1) / (total transiciones)
        """
        transiciones_activas = sum(self.tabla_transicion.values())
        return transiciones_activas / 8.0
    
    def inicializar_aleatorio(self, densidad: float = 0.5):
        """Inicializar con estado aleatorio."""
        self.estado = (np.random.random(self.tamano) < densidad).astype(np.uint8)
        self.historial.clear()
        self.historial.append(self.estado.copy())
    
    def inicializar_semilla(self, posicion: int = None):
        """Inicializar con una sola celda activa (semilla)."""
        self.estado = np.zeros(self.tamano, dtype=np.uint8)
        if posicion is None:
            posicion = self.tamano // 2
        self.estado[posicion] = 1
        self.historial.clear()
        self.historial.append(self.estado.copy())
    
    def paso(self) -> np.ndarray:
        """
        Ejecutar un paso del autómata.
        
        Aplica la regla a cada celda basándose en su vecindad. 
        """
        nuevo_estado = np.zeros_like(self.estado)
        
        for i in range(self.tamano):
            # Obtener vecindad con condiciones de frontera periódicas
            izq = self.estado[(i - 1) % self.tamano]
            centro = self.estado[i]
            der = self.estado[(i + 1) % self.tamano]
            
            # Aplicar regla
            nuevo_estado[i] = self.tabla_transicion[(izq, centro, der)]
        
        self.estado = nuevo_estado
        self.historial.append(self.estado.copy())
        
        return self.estado
    
    def evolucionar(self, pasos: int) -> np.ndarray:
        """
        Evolucionar el autómata por varios pasos.
        
        Returns:
            Matriz de tamaño (pasos+1, tamano) con la evolución
        """
        evolucion = [self.estado.copy()]
        for _ in range(pasos):
            self.paso()
            evolucion.append(self.estado.copy())
        return np.array(evolucion)
    
    def calcular_entropia(self, tamano_bloque: int = 3) -> float:
        """
        Calcular entropía de bloques del estado actual.
        
        H = -Σ p(bloque) log₂ p(bloque)
        """
        if self.tamano < tamano_bloque:
            return 0.0
        
        # Contar bloques
        conteos = {}
        for i in range(self.tamano - tamano_bloque + 1):
            bloque = tuple(self.estado[i:i + tamano_bloque])
            conteos[bloque] = conteos.get(bloque, 0) + 1
        
        # Calcular probabilidades y entropía
        total = sum(conteos.values())
        entropia = 0.0
        for count in conteos.values():
            p = count / total
            if p > 0:
                entropia -= p * np.log2(p)
        
        return entropia
    
    def estimar_lyapunov(self, pasos: int = 100) -> float:
        """
        Estimar exponente de Lyapunov por perturbación.
        
        Mide sensibilidad a condiciones iniciales. 
        λ > 0: caótico, λ ≈ 0: borde, λ < 0: ordenado
        """
        # Guardar estado actual
        estado_original = self.estado.copy()
        
        # Crear estado perturbado (cambiar 1 bit)
        estado_perturbado = estado_original.copy()
        pos_perturb = np.random.randint(0, self.tamano)
        estado_perturbado[pos_perturb] = 1 - estado_perturbado[pos_perturb]
        
        # Evolucionar ambos
        divergencias = []
        
        self.estado = estado_original.copy()
        original_evol = self.evolucionar(pasos)
        
        self.estado = estado_perturbado
        perturbado_evol = self.evolucionar(pasos)
        
        # Calcular divergencia en cada paso
        for t in range(1, pasos + 1):
            diff = np.sum(original_evol[t] != perturbado_evol[t])
            if diff > 0:
                divergencias.append(np.log(diff))
        
        # Restaurar estado
        self.estado = estado_original
        
        # Estimar Lyapunov como pendiente
        if len(divergencias) < 2:
            return 0.0
        
        return np.mean(np.diff(divergencias))
    
    def calcular_densidad(self) -> float:
        """Calcular densidad de celdas activas."""
        return np.mean(self.estado)
    
    def calcular_complejidad(self) -> float:
        """
        Calcular complejidad estructural.
        
        Usa la complejidad de Lempel-Ziv como proxy.
        Máxima en el borde del caos.
        """
        # Convertir a string
        s = ''.join(map(str, self.estado))
        
        # Complejidad de Lempel-Ziv normalizada
        n = len(s)
        if n == 0:
            return 0.0
        
        # Contar número de palabras distintas
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
        
        # Normalizar por complejidad máxima teórica
        c = len(palabras)
        c_max = n / np.log2(n) if n > 1 else 1
        
        return c / c_max if c_max > 0 else 0.0
    
    def clasificar_dinamica(self) -> ClaseWolfram:
        """
        Clasificar la dinámica del autómata según Wolfram.
        
        Basado en entropía, densidad y complejidad.
        """
        entropia = self.calcular_entropia()
        densidad = self.calcular_densidad()
        complejidad = self.calcular_complejidad()
        lyapunov = self.estimar_lyapunov(pasos=50)
        
        entropia_max = np.log2(2**3)  # Para bloques de 3
        entropia_norm = entropia / entropia_max if entropia_max > 0 else 0
        
        # Heurísticas de clasificación
        if entropia_norm < 0.1 or densidad < 0.05 or densidad > 0.95:
            return ClaseWolfram.CLASE_I
        elif lyapunov < -0.5 and complejidad < 0.3:
            return ClaseWolfram.CLASE_II
        elif lyapunov > 0.5 and entropia_norm > 0.9:
            return ClaseWolfram.CLASE_III
        else:
            return ClaseWolfram.CLASE_IV  # Borde del caos
    
    def obtener_metricas(self) -> MetricasBordeCaos:
        """Obtener todas las métricas de borde del caos."""
        entropia = self.calcular_entropia()
        entropia_max = np.log2(2**3)
        
        return MetricasBordeCaos(
            entropia=entropia,
            entropia_normalizada=entropia / entropia_max if entropia_max > 0 else 0,
            parametro_lambda=self.lambda_param,
            densidad=self.calcular_densidad(),
            complejidad=self.calcular_complejidad(),
            lyapunov_estimado=self.estimar_lyapunov(pasos=50),
            clase_estimada=self.clasificar_dinamica()
        )


class ReguladorBordeCaos:
    """
    Regulador que mantiene al sistema en el borde del caos.
    
    Usa métricas del autómata celular para ajustar parámetros
    del sistema principal.
    
    Fundamento:
    Sistemas al borde del caos tienen máxima capacidad de:
    - Procesamiento de información
    - Memoria
    - Adaptabilidad
    """
    
    def __init__(self, 
                 objetivo_lambda: float = 0.5,
                 objetivo_entropia: float = 0.5,
                 tolerancia: float = 0.1):
        """
        Args:
            objetivo_lambda: Valor objetivo del parámetro λ (0.5 = borde)
            objetivo_entropia: Entropía normalizada objetivo
            tolerancia: Tolerancia para considerar "en el borde"
        """
        self.objetivo_lambda = objetivo_lambda
        self.objetivo_entropia = objetivo_entropia
        self.tolerancia = tolerancia
        
        # Historial de métricas
        self.historial_metricas: List[MetricasBordeCaos] = []
    
    def evaluar_distancia_borde(self, metricas: MetricasBordeCaos) -> float:
        """
        Calcular distancia al borde del caos ideal.
        
        Distancia = 0 significa exactamente en el borde.
        """
        dist_lambda = abs(metricas.parametro_lambda - self.objetivo_lambda)
        dist_entropia = abs(metricas.entropia_normalizada - self.objetivo_entropia)
        
        # Penalizar exponente de Lyapunov lejos de 0
        dist_lyapunov = abs(metricas.lyapunov_estimado)
        
        # Complejidad debería ser alta en el borde
        dist_complejidad = max(0, 0.5 - metricas.complejidad)
        
        return (dist_lambda + dist_entropia + dist_lyapunov + dist_complejidad) / 4
    
    def esta_en_borde(self, metricas: MetricasBordeCaos) -> bool:
        """Verificar si el sistema está en el borde del caos."""
        return self.evaluar_distancia_borde(metricas) < self.tolerancia
    
    def sugerir_ajuste(self, metricas: MetricasBordeCaos) -> Dict[str, float]:
        """
        Sugerir ajustes de parámetros para acercarse al borde.
        
        Returns:
            Diccionario con direcciones de ajuste para cada parámetro
        """
        ajustes = {}
        
        # Si λ muy bajo → aumentar actividad
        if metricas.parametro_lambda < self.objetivo_lambda - self.tolerancia:
            ajustes['learning_rate'] = 1.1  # Multiplicador
            ajustes['emotion_decay'] = 0.95  # Menos decay = más memoria
            ajustes['grundzug_threshold'] = 0.9  # Menor umbral = más patrones
        
        # Si λ muy alto → reducir actividad
        elif metricas.parametro_lambda > self.objetivo_lambda + self.tolerancia:
            ajustes['learning_rate'] = 0.9
            ajustes['emotion_decay'] = 1.05
            ajustes['grundzug_threshold'] = 1.1
        
        # Si entropía muy baja → más variabilidad
        if metricas.entropia_normalizada < self.objetivo_entropia - self.tolerancia:
            ajustes['noise_injection'] = 1.2
        
        # Si entropía muy alta → más estructura
        elif metricas.entropia_normalizada > self.objetivo_entropia + self.tolerancia:
            ajustes['regularization'] = 1.1
        
        # Si Lyapunov positivo → estabilizar
        if metricas.lyapunov_estimado > 0.1:
            ajustes['stability_factor'] = 1.1
        
        return ajustes
    
    def registrar(self, metricas: MetricasBordeCaos):
        """Registrar métricas para análisis histórico."""
        self.historial_metricas.append(metricas)
    
    def tendencia(self) -> str:
        """Analizar tendencia del sistema."""
        if len(self.historial_metricas) < 5:
            return "insuficiente_datos"
        
        lambdas = [m.parametro_lambda for m in self.historial_metricas[-10:]]
        tendencia = np.mean(np.diff(lambdas))
        
        if tendencia > 0.05:
            return "hacia_caos"
        elif tendencia < -0.05:
            return "hacia_orden"
        else:
            return "estable"


class IntegradorSistemaBordeCaos:
    """
    Integra el autómata celular con el sistema principal
    para mantenerlo operando al borde del caos.
    """
    
    def __init__(self, tamano_automata: int = 128):
        # Autómata celular como "sensor" de dinámica
        self.automata = AutomataCelular1D(tamano=tamano_automata, regla=110)
        
        # Regulador
        self.regulador = ReguladorBordeCaos()
        
        # Mapeo de estado del sistema a estado del autómata
        self.factor_mapeo = tamano_automata
    
    def mapear_estado_sistema(self, 
                               embedding: np.ndarray,
                               emotion: np.ndarray,
                               entropia: float) -> np.ndarray:
        """
        Mapear estado del sistema a estado del autómata. 
        
        Idea: Usar características del sistema para inicializar
        el autómata y observar su dinámica.
        """
        # Combinar características
        features = np.concatenate([
            embedding[:32] if len(embedding) >= 32 else embedding,
            emotion,
            [entropia]
        ])
        
        # Normalizar a [0, 1]
        features_norm = (features - features.min()) / (features.max() - features.min() + 1e-8)
        
        # Expandir/contraer a tamaño del autómata
        if len(features_norm) < self.factor_mapeo:
            estado = np.interp(
                np.linspace(0, 1, self.factor_mapeo),
                np.linspace(0, 1, len(features_norm)),
                features_norm
            )
        else:
            estado = features_norm[:self.factor_mapeo]
        
        # Binarizar
        umbral = np.median(estado)
        return (estado > umbral).astype(np.uint8)
    
    def evaluar_dinamica(self, 
                         embedding: np.ndarray,
                         emotion: np.ndarray,
                         entropia: float,
                         pasos_simulacion: int = 50) -> MetricasBordeCaos:
        """
        Evaluar dinámica del sistema usando el autómata. 
        
        1.Mapear estado del sistema al autómata
        2.Evolucionar el autómata
        3.Medir métricas de borde del caos
        4.Retornar métricas
        """
        # Mapear
        estado_inicial = self.mapear_estado_sistema(embedding, emotion, entropia)
        self.automata.estado = estado_inicial
        self.automata.historial.clear()
        self.automata.historial.append(estado_inicial.copy())
        
        # Evolucionar
        self.automata.evolucionar(pasos_simulacion)
        
        # Obtener métricas
        metricas = self.automata.obtener_metricas()
        
        # Registrar
        self.regulador.registrar(metricas)
        
        return metricas
    
    def obtener_ajustes(self, metricas: MetricasBordeCaos) -> Dict[str, float]:
        """Obtener ajustes sugeridos para mantener borde del caos."""
        return self.regulador.sugerir_ajuste(metricas)
    
    def esta_en_borde(self, metricas: MetricasBordeCaos) -> bool:
        """Verificar si el sistema está en el borde del caos."""
        return self.regulador.esta_en_borde(metricas)


# ==============================================================================
# DEMOSTRACIÓN Y VISUALIZACIÓN
# ==============================================================================

def demo_automata_borde_caos():
    """Demostración del autómata celular y análisis de borde del caos."""
    
    print("=" * 70)
    print("  DEMOSTRACIÓN: AUTÓMATA CELULAR AL BORDE DEL CAOS")
    print("=" * 70)
    
    # Probar diferentes reglas
    reglas_test = [
        (0, "Clase I - Todo muere"),
        (8, "Clase II - Periódico simple"),
        (30, "Clase III - Caótico"),
        (110, "Clase IV - BORDE DEL CAOS"),
        (90, "Clase II - Patrón fractal"),
    ]
    
    print("\n ANÁLISIS DE DIFERENTES REGLAS:")
    print("-" * 70)
    
    for regla, descripcion in reglas_test:
        automata = AutomataCelular1D(tamano=128, regla=regla)
        automata.inicializar_semilla()
        automata.evolucionar(100)
        
        metricas = automata.obtener_metricas()
        
        print(f"\n Regla {regla}: {descripcion}")
        print(f"   λ (Langton):        {metricas.parametro_lambda:.3f}")
        print(f"   Entropía norm:      {metricas.entropia_normalizada:.3f}")
        print(f"   Densidad:           {metricas.densidad:.3f}")
        print(f"   Complejidad:        {metricas.complejidad:.3f}")
        print(f"   Lyapunov (est):     {metricas.lyapunov_estimado:.3f}")
        print(f"   Clase:              {metricas.clase_estimada.name}")
    
    # Visualizar evolución de Regla 110
    print("\n" + "=" * 70)
    print("  EVOLUCIÓN DE REGLA 110 (BORDE DEL CAOS)")
    print("=" * 70)
    
    automata = AutomataCelular1D(tamano=60, regla=110)
    automata.inicializar_semilla()
    evolucion = automata.evolucionar(30)
    
    print("\n  (█ = 1, ░ = 0)")
    print()
    for t, fila in enumerate(evolucion):
        linea = ''.join('█' if c else '░' for c in fila)
        print(f"  t={t:2d} │{linea}│")
    
    # Demostrar regulador
    print("\n" + "=" * 70)
    print("  REGULADOR DE BORDE DEL CAOS")
    print("=" * 70)
    
    integrador = IntegradorSistemaBordeCaos(tamano_automata=64)
    
    # Simular diferentes estados del sistema
    estados_test = [
        (np.zeros(64), np.zeros(3), 0.1, "Sistema muy ordenado"),
        (np.random.randn(64), np.random.randn(3), 0.9, "Sistema caótico"),
        (np.sin(np.linspace(0, 4*np.pi, 64)), np.array([0.3, -0.2, 0.1]), 0.5, "Sistema estructurado"),
    ]
    
    print("\n EVALUACIÓN DE DIFERENTES ESTADOS:")
    print("-" * 70)
    
    for embedding, emotion, entropia, descripcion in estados_test:
        metricas = integrador.evaluar_dinamica(embedding, emotion, entropia)
        en_borde = integrador.esta_en_borde(metricas)
        ajustes = integrador.obtener_ajustes(metricas)
        
        print(f"\n {descripcion}:")
        print(f"   ¿En borde del caos? {'SÍ ✓' if en_borde else 'NO ✗'}")
        print(f"   Distancia al borde: {integrador.regulador.evaluar_distancia_borde(metricas):.3f}")
        if ajustes:
            print(f"   Ajustes sugeridos:  {ajustes}")
    
    print("\n" + "=" * 70)
    print("  FIN DE DEMOSTRACIÓN")
    print("=" * 70)


if __name__ == "__main__":
    demo_automata_borde_caos()
