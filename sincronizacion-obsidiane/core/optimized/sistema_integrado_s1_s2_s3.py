"""
Sistema Integrado S1 + S2 + S3 - Versión Optimizada
====================================================

Integración de los 3 sistemas de Capa 2:
- S1: Sistema Principal (YO Estructural) - Procesamiento fenomenológico
- S2: Emergencia de Conceptos - Aprendizaje incremental desde Grundzugs
- S3: Lógica Pura - Mundos posibles y razonamiento hipotético

OPTIMIZADO para hardware restringido mientras preserva funcionalidad esencial.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict
import sys
import os

# Importar componentes optimizados base
sys.path.insert(0, os.path.dirname(__file__))
from components import (
    TokenizerLite, EmbedderCompact, ClassifierYO,
    MDCEManager, GrundzugTracker, EmotionEngine
)
from health_manager import HealthManager


class EchoStateNetwork:
    """
    Predictor Temporal (ESN) - Reservoir Computing Ligero
    Memoria: ~50 KB
    
    CONEXIÓN #3: Implementación del componente faltante.
    """
    def __init__(self, input_dim=64, reservoir_size=100, spectral_radius=0.9):
        # Inicialización del reservorio (pesos fijos aleatorios)
        self.W_in = np.random.uniform(-0.5, 0.5, (reservoir_size, input_dim))
        self.W_res = np.random.uniform(-0.5, 0.5, (reservoir_size, reservoir_size))
        
        # Ajuste de radio espectral
        try:
            eigenvalues = np.linalg.eigvals(self.W_res)
            max_eig = max(abs(eigenvalues))
            if max_eig > 0:
                self.W_res *= spectral_radius / max_eig
        except:
            pass # Fallback si falla convergencia
            
        # Pesos de salida (entrenables)
        self.W_out = np.zeros((input_dim, reservoir_size))
        
        # Estado interno
        self.state = np.zeros(reservoir_size)
        self.alpha = 0.3 # Leaking rate
        
    def predict(self, input_vector):
        """Realiza predicción y actualiza estado."""
        # Update reservoir state
        pre_activation = np.dot(self.W_in, input_vector) + np.dot(self.W_res, self.state)
        self.state = (1 - self.alpha) * self.state + self.alpha * np.tanh(pre_activation)
        
        # Predict (readout)
        return np.dot(self.W_out, self.state)
        
    def train(self, target_vector, learning_rate=0.01):
        """Aprendizaje online (LMS)."""
        prediction = np.dot(self.W_out, self.state)
        error = target_vector - prediction
        # Regla de aprendizaje simple: W_out += lr * error * state.T
        self.W_out += learning_rate * np.outer(error, self.state)


class S2EmergenciaConceptosOptimizado:
    """
    Sistema 2: Emergencia de Conceptos (OPTIMIZADO)
    
    Aprende patrones desde Grundzugs detectados por S1.
    Memoria: ~50 KB (vs ~10 MB original)
    """
    
    def __init__(self, max_conceptos: int = 100):
        self.max_conceptos = max_conceptos
        
        # Conceptos emergidos: {nombre: {certeza, observaciones, estabilidad}}
        self.conceptos = {}
        
        # Historial de certezas para detectar convergencia
        self.historico_certezas = defaultdict(list)
        
        # Contador de iteraciones
        self.iteracion = 0
        self.convergencia_alcanzada = False
    
    def procesar_grundzugs(self, grundzugs: List[int], 
                           grundzug_tracker: GrundzugTracker) -> Dict[str, Any]:
        """
        Extrae conceptos desde Grundzugs estables.
        
        Args:
            grundzugs: Lista de IDs de features
            grundzug_tracker: Tracker de Grundzugs de S1
        
        Returns:
            Resultado del ciclo de emergencia
        """
        self.iteracion += 1
        conceptos_nuevos = []
        
        # Detectar Grundzugs estables (patrones recurrentes)
        for gid in set(grundzugs):
            if grundzug_tracker.is_grundzug(gid):
                # Crear/refinar concepto
                nombre = f"concepto_{gid}"
                
                # Calcular certeza basada en frecuencia
                freq_total = grundzug_tracker.estimate(gid)
                freq_window = grundzug_tracker.estimate_window(gid)
                
                certeza = min(1.0, (freq_total + freq_window) / 
                            (grundzug_tracker.total_count + len(grundzug_tracker.window_queue)))
                
                if nombre not in self.conceptos:
                    self.conceptos[nombre] = {
                        'certeza': certeza,
                        'observaciones': 1,
                        'estabilidad': 0.5,
                        'gid': gid
                    }
                    conceptos_nuevos.append(nombre)
                else:
                    # Refinar concepto existente
                    concepto = self.conceptos[nombre]
                    concepto['observaciones'] += 1
                    
                    # Actualizar certeza con promedio móvil exponencial
                    alpha = 0.3
                    concepto['certeza'] = alpha * certeza + (1 - alpha) * concepto['certeza']
                
                # Actualizar historial
                self.historico_certezas[nombre].append(self.conceptos[nombre]['certeza'])
                
                # Calcular estabilidad
                if len(self.historico_certezas[nombre]) >= 3:
                    ultimas = self.historico_certezas[nombre][-3:]
                    varianza = np.var(ultimas)
                    self.conceptos[nombre]['estabilidad'] = max(0.0, 1.0 - varianza * 10)
        
        # Verificar convergencia global
        self._verificar_convergencia()
        
        # Limpieza: eliminar conceptos débiles si excedemos límite
        if len(self.conceptos) > self.max_conceptos:
            self._limpiar_conceptos_debiles()
        
        return {
            'conceptos_totales': len(self.conceptos),
            'conceptos_nuevos': len(conceptos_nuevos),
            'patron_certeza': np.mean([c['certeza'] for c in self.conceptos.values()]) if self.conceptos else 0.0,
            'convergencia': self.convergencia_alcanzada,
            'conceptos': list(self.conceptos.keys())
        }
    
    def _verificar_convergencia(self):
        """Detecta si los conceptos han convergido."""
        if len(self.conceptos) < 3:
            return
        
        # Convergencia = al menos 3 conceptos con certeza > 0.9 y estabilidad > 0.9
        conceptos_estables = [
            c for c in self.conceptos.values()
            if c['certeza'] > 0.9 and c['estabilidad'] > 0.9
        ]
        
        if len(conceptos_estables) >= 3:
            self.convergencia_alcanzada = True
    
    def _limpiar_conceptos_debiles(self):
        """Elimina conceptos con menor certeza para liberar memoria."""
        # Ordenar por certeza
        conceptos_ordenados = sorted(
            self.conceptos.items(),
            key=lambda x: x[1]['certeza'],
            reverse=True
        )
        
        # Mantener solo los top max_conceptos
        self.conceptos = dict(conceptos_ordenados[:self.max_conceptos])

    def inyectar_concepto_externo(self, nombre: str, certeza: float):
        """
        CONEXIÓN #2: Permite al Tejido Neuronal inyectar conceptos directamente.
        """
        if nombre not in self.conceptos:
            self.conceptos[nombre] = {
                'certeza': certeza,
                'observaciones': 1,
                'estabilidad': 0.5,
                'gid': -1 # Indicador de origen externo (Tejido)
            }
        else:
            # Reforzar existente con input neuronal
            self.conceptos[nombre]['certeza'] = max(self.conceptos[nombre]['certeza'], certeza)
            self.conceptos[nombre]['observaciones'] += 1


class S3LogicaPuraOptimizado:
    """
    Sistema 3: Lógica Pura (OPTIMIZADO)
    
    Valida axiomas lógicos sobre Grundzugs y conceptos emergidos.
    Memoria: ~20 KB (vs ~5 MB original)
    """
    
    def __init__(self, max_axiomas: int = 50):
        self.max_axiomas = max_axiomas
        
        # Axiomas aprendidos: {id: {sujeto, predicado, objeto, certeza}}
        self.axiomas = {}
        self.axioma_counter = 0
        
        # Objetos del mundo (conceptos validados lógicamente)
        self.objetos_mundo = set()
    
    def procesar_conceptos(self, conceptos_s2: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Valida conceptos de S2 y genera axiomas lógicos.
        
        Args:
            conceptos_s2: Conceptos emergidos por S2
        
        Returns:
            Resultado del procesamiento lógico
        """
        axiomas_nuevos = 0
        
        for nombre, info in conceptos_s2.items():
            certeza = info['certeza']
            
            # Solo procesar conceptos con certeza alta
            if certeza > 0.7:
                # Agregar al mundo
                self.objetos_mundo.add(nombre)
                
                # Generar axioma de existencia
                axioma_id = f"ax_{self.axioma_counter}"
                self.axioma_counter += 1
                
                self.axiomas[axioma_id] = {
                    'sujeto': nombre,
                    'predicado': 'existente',
                    'objeto': 'mundo',
                    'certeza': certeza,
                    'tipo': 'existencia'
                }
                axiomas_nuevos += 1
                
                # Generar axioma de estabilidad si es estable
                if info.get('estabilidad', 0) > 0.8:
                    axioma_id = f"ax_{self.axioma_counter}"
                    self.axioma_counter += 1
                    
                    self.axiomas[axioma_id] = {
                        'sujeto': nombre,
                        'predicado': 'estable',
                        'objeto': 'tiempo',
                        'certeza': info['estabilidad'],
                        'tipo': 'estabilidad'
                    }
                    axiomas_nuevos += 1
        
        # Limpieza de axiomas débiles
        if len(self.axiomas) > self.max_axiomas:
            self._limpiar_axiomas_debiles()
        
        return {
            'objetos_totales': len(self.objetos_mundo),
            'axiomas_totales': len(self.axiomas),
            'axiomas_nuevos_aprendidos': axiomas_nuevos,
            'validacion': {
                'consistencia': self._calcular_consistencia(),
                'completitud': len(self.objetos_mundo) / max(1, len(conceptos_s2))
            }
        }
    
    def _calcular_consistencia(self) -> float:
        """Calcula consistencia interna de axiomas."""
        if not self.axiomas:
            return 1.0
        
        # Consistencia = promedio de certezas
        certezas = [ax['certeza'] for ax in self.axiomas.values()]
        return np.mean(certezas)
    
    def _limpiar_axiomas_debiles(self):
        """Elimina axiomas con menor certeza."""
        axiomas_ordenados = sorted(
            self.axiomas.items(),
            key=lambda x: x[1]['certeza'],
            reverse=True
        )
        self.axiomas = dict(axiomas_ordenados[:self.max_axiomas])


class SistemaIntegradoS1S2S3:
    """
    Orquestador optimizado de los 3 sistemas de Capa 2.
    
    Memoria total: ~800 KB (S1) + ~50 KB (S2) + ~20 KB (S3) ≈ 870 KB
    """
    
    def __init__(self, vocab_path: str = None, embed_path: str = None):
        # ============================================
        # S1: SISTEMA PRINCIPAL (Base optimizada)
        # ============================================
        self.tokenizer = TokenizerLite(vocab_path)
        self.embedder = EmbedderCompact()
        if embed_path:
            self.embedder.load_quantized(embed_path)
        
        self.classifier = ClassifierYO()
        self.mdce = MDCEManager()
        self.grundzug_tracker = GrundzugTracker()
        self.health = HealthManager()
        self.emotion = EmotionEngine()
        
        # ============================================
        # S2: EMERGENCIA DE CONCEPTOS
        # ============================================
        self.s2_emergencia = S2EmergenciaConceptosOptimizado()
        
        # ============================================
        # S3: LÓGICA PURA
        # ============================================
        self.s3_logica = S3LogicaPuraOptimizado()
        
        # ============================================
        # CAPA DE CONTROL: PREDICTOR TEMPORAL
        # ============================================
        self.predictor_esn = EchoStateNetwork(input_dim=64, reservoir_size=100)
        
        # Estadísticas globales
        self.iteracion_global = 0
        self.estadisticas = {
            's1_eventos': 0,
            's2_conceptos': 0,
            's3_axiomas': 0,
            'convergencias': 0
        }
    
    def procesar_evento_completo(self, texto: str, source: str = "default") -> Dict[str, Any]:
        """
        Procesar evento a través de los 3 sistemas.
        
        Flujo:
        texto → S1 (fenomenología) → Grundzugs → 
        S2 (emergencia) → Conceptos → 
        S3 (lógica) → Axiomas
        
        Args:
            texto: Texto de entrada
            source: Fuente del evento
        
        Returns:
            Resultado consolidado de S1, S2, S3
        """
        self.iteracion_global += 1
        
        # =============================================
        # PASO 1: S1 - PROCESAMIENTO FENOMENOLÓGICO
        # =============================================
        
        # Rate limiting
        if not self.health.check_rate_limit(source):
            return {"status": "rate_limited", "source": source}
        
        # Tokenización
        tokens = self.tokenizer.encode(texto)
        
        # Embedding
        embedding = self.embedder.embed(tokens)
        
        # Clasificación YO
        yo_type = self.classifier.predict(embedding)
        yo_probs = self.classifier.predict_proba(embedding)
        
        # Registrar instancia
        instance_id = self.mdce.add_instance(yo_type)
        
        # Actualizar Grundzugs (patrones estables)
        grundzugs_detectados = []
        for token in tokens:
            self.grundzug_tracker.update(token)
            if self.grundzug_tracker.is_grundzug(token):
                grundzugs_detectados.append(token)
        
        # Actualizar emociones
        self.emotion.update(embedding)
        
        # Apoptosis periódica
        if self.iteracion_global % 100 == 0:
            self.health.run_apoptosis()
            
        # =============================================
        # CONEXIÓN #3: PREDICTOR ESN
        # =============================================
        # Entrenar con el embedding actual (predicción one-step ahead)
        # En realidad, entrenamos para predecir el ACTUAL basándonos en el estado anterior,
        # o predecimos el SIGUIENTE. Aquí haremos entrenamiento online simple.
        prediccion_esn = self.predictor_esn.predict(embedding)
        self.predictor_esn.train(embedding) # Entrenar para reconstruir/predecir
        
        self.estadisticas['s1_eventos'] += 1
        
        resultado_s1 = {
            'instance_id': instance_id,
            'yo_type': ClassifierYO.CLASSES[yo_type],
            'yo_confidence': float(yo_probs[yo_type]),
            'grundzugs_detectados': len(grundzugs_detectados),
            'grundzug_ids': grundzugs_detectados,
            'emotion_state': self.emotion.get_valence(),
            'embedding_vector': embedding.tolist(), # CONEXIÓN #1: Exponer embedding
            'esn_prediccion': prediccion_esn.tolist() # Resultado ESN
        }
        
        # =============================================
        # PASO 2: S2 - EMERGENCIA DE CONCEPTOS
        # =============================================
        
        resultado_s2 = self.s2_emergencia.procesar_grundzugs(
            grundzugs_detectados,
            self.grundzug_tracker
        )
        
        self.estadisticas['s2_conceptos'] = resultado_s2['conceptos_totales']
        if resultado_s2['convergencia']:
            self.estadisticas['convergencias'] += 1
        
        # =============================================
        # PASO 3: S3 - LÓGICA PURA
        # =============================================
        
        resultado_s3 = self.s3_logica.procesar_conceptos(
            self.s2_emergencia.conceptos
        )
        
        self.estadisticas['s3_axiomas'] = resultado_s3['axiomas_totales']
        
        # =============================================
        # RESULTADO CONSOLIDADO
        # =============================================
        
        return {
            'status': 'ok',
            'iteracion_global': self.iteracion_global,
            
            # S1: Fenomenología
            's1_resultado': resultado_s1,
            
            # S2: Conceptos emergidos
            's2_resultado': resultado_s2,
            
            # S3: Axiomas lógicos
            's3_resultado': resultado_s3,
            
            # Validación cruzada
            'validacion_cruzada': self._validar_s2_vs_s3(resultado_s2, resultado_s3),
            
            # Estadísticas globales
            'estadisticas': self.estadisticas
        }
    
    def _validar_s2_vs_s3(self, resultado_s2: Dict, resultado_s3: Dict) -> Dict:
        """Valida consistencia entre S2 y S3."""
        conceptos_count = resultado_s2['conceptos_totales']
        axiomas_count = resultado_s3['axiomas_totales']
        
        if conceptos_count == 0:
            consistencia = 1.0
        else:
            # Heurística: ratio axiomas/conceptos debería estar cerca de 1-2
            ratio = axiomas_count / conceptos_count
            consistencia = 1.0 - min(1.0, abs(1.5 - ratio) / 1.5)
        
        return {
            'consistencia': consistencia,
            'conceptos_s2': conceptos_count,
            'axiomas_s3': axiomas_count,
            'validacion_exitosa': consistencia > 0.7,
            'convergencia_s2': resultado_s2['convergencia'],
            'completitud_s3': resultado_s3['validacion']['completitud']
        }
    
    def get_estado_completo(self) -> Dict[str, Any]:
        """Obtiene estado de los 3 sistemas."""
        return {
            'iteracion_global': self.iteracion_global,
            'estadisticas': self.estadisticas,
            
            's1_estado': {
                'eventos_procesados': self.estadisticas['s1_eventos'],
                'instancias_mdce': self.mdce.instance_count,
                'grundzugs_totales': self.grundzug_tracker.total_count,
                'emotion_state': self.emotion.get_valence()
            },
            
            's2_estado': {
                'conceptos_totales': len(self.s2_emergencia.conceptos),
                'iteracion': self.s2_emergencia.iteracion,
                'convergencia': self.s2_emergencia.convergencia_alcanzada
            },
            
            's3_estado': {
                'objetos_mundo': len(self.s3_logica.objetos_mundo),
                'axiomas_totales': len(self.s3_logica.axiomas),
                'consistencia': self.s3_logica._calcular_consistencia()
            }
        }


def main():
    """Demo del sistema integrado S1+S2+S3."""
    print("=" * 70)
    print("SISTEMA INTEGRADO S1 + S2 + S3 - OPTIMIZADO")
    print("=" * 70)
    
    sistema = SistemaIntegradoS1S2S3()
    
    # Eventos de prueba que generan Grundzugs
    eventos = [
        "El ser humano reflexiona sobre su existencia",
        "La herramienta está disponible para uso",
        "El ser reflexiona profundamente",
        "La existencia humana implica consciencia",
        "El ser es consciente de sí mismo",
        "La reflexión profunda caracteriza al humano"
    ]
    
    print("\nProcesando eventos...\n")
    
    for i, evento in enumerate(eventos, 1):
        resultado = sistema.procesar_evento_completo(evento)
        
        print(f"[Evento {i}] {evento[:50]}...")
        print(f"  S1: Tipo={resultado['s1_resultado']['yo_type']}, "
              f"Grundzugs={resultado['s1_resultado']['grundzugs_detectados']}")
        print(f"  S2: Conceptos={resultado['s2_resultado']['conceptos_totales']}, "
              f"Certeza={resultado['s2_resultado']['patron_certeza']:.2f}")
        print(f"  S3: Axiomas={resultado['s3_resultado']['axiomas_totales']}, "
              f"Objetos={resultado['s3_resultado']['objetos_totales']}")
        print(f"  Validación: Consistencia={resultado['validacion_cruzada']['consistencia']:.2f}")
        print()
    
    # Estado final
    print("=" * 70)
    print("ESTADO FINAL DE LOS 3 SISTEMAS")
    print("=" * 70)
    
    estado = sistema.get_estado_completo()
    print(f"\nIteración global: {estado['iteracion_global']}")
    print(f"\nS1 (Fenomenología):")
    print(f"  - Eventos: {estado['s1_estado']['eventos_procesados']}")
    print(f"  - Instancias: {estado['s1_estado']['instancias_mdce']}")
    print(f"  - Grundzugs totales: {estado['s1_estado']['grundzugs_totales']}")
    
    print(f"\nS2 (Emergencia):")
    print(f"  - Conceptos: {estado['s2_estado']['conceptos_totales']}")
    print(f"  - Convergencia: {'SÍ' if estado['s2_estado']['convergencia'] else 'NO'}")
    
    print(f"\nS3 (Lógica):")
    print(f"  - Objetos mundo: {estado['s3_estado']['objetos_mundo']}")
    print(f"  - Axiomas: {estado['s3_estado']['axiomas_totales']}")
    print(f"  - Consistencia: {estado['s3_estado']['consistencia']:.2f}")


if __name__ == "__main__":
    main()
