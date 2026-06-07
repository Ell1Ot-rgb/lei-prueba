"""
GENERADOR DE RUTAS FENOMENOLÓGICAS
===================================
Genera automáticamente 5 rutas de definición para cualquier concepto
y detecta convergencia a máximo relacional definicional.

VERSIÓN: 1.0 - Python Puro (4GB RAM optimizado)
- Entrada: Concepto (string)
- Proceso: Generar 5 rutas + calcular convergencia
- Salida: Máximo relacional con certeza >= 99%

OPTIMIZACIONES 4GB:
- Lazy loading de modelos
- Batch processing
- Memory-aware garbage collection
"""

import gc
import yaml
import logging
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import numpy as np
from sentence_transformers import SentenceTransformer
import psutil
import time
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# 1. CONFIGURACIÓN DE LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("GeneradorRutas")

# ============================================================
# 2. DATACLASSES
# ============================================================
@dataclass
class RutaFenomenologica:
    """Una ruta de definición para un concepto"""
    nombre: str  # "Física", "Ergonómica", etc.
    definicion: str
    embedding: Optional[np.ndarray] = None
    similitud_promedio: float = 0.0
    confianza: float = 0.0

@dataclass
class ResultadoGeneracion:
    """Resultado de la generación de rutas"""
    concepto: str
    rutas: List[RutaFenomenologica]
    certeza_individual_promedio: float
    certeza_combinada: float
    es_maximo_relacional: bool
    confianza_diagnostico: str  # "ALTO", "MEDIO", "BAJO"
    tiempo_procesamiento_ms: float

# ============================================================
# 3. GENERADOR PRINCIPAL
# ============================================================
class GeneradorRutasFenomenologicas:
    """
    Generador de rutas fenomenológicas.
    
    ESTRATEGIA:
    1. Recibe un concepto (ej: "SOPORTE")
    2. Genera 5 rutas automáticamente usando templates
    3. Crea embeddings de cada ruta
    4. Calcula convergencia
    5. Determina si es máximo relacional
    
    RUTAS DISPONIBLES:
    - Física: Desde propiedades materiales
    - Ergonómica: Desde interacción humana
    - Arquitectónica: Desde estructura/función
    - Lógica: Desde relaciones conceptuales
    - Ontológica: Desde esencia/naturaleza
    """
    
    RUTAS_TEMPLATES = {
        "Física": (
            "Desde una perspectiva física, {concepto} se refiere a "
            "las propiedades materiales, fuerzas y estructuras que lo componen. "
            "Es observable, medible y sigue leyes de la naturaleza."
        ),
        "Ergonómica": (
            "Desde una perspectiva ergonómica, {concepto} se define por "
            "cómo interactúa con el usuario o agente. "
            "Su valor está en la adaptación, comodidad y eficiencia de uso."
        ),
        "Arquitectónica": (
            "Desde una perspectiva arquitectónica, {concepto} es un elemento "
            "dentro de un sistema mayor. Su función es transferir, soportar o conectar. "
            "Su esencia está en su rol estructural."
        ),
        "Lógica": (
            "Desde una perspectiva lógica, {concepto} es un concepto que "
            "establece relaciones causales y de justificación. "
            "Su definición emerge de las proposiciones que lo sustentan."
        ),
        "Ontológica": (
            "Desde una perspectiva ontológica, {concepto} representa una entidad "
            "cuya existencia es fundamental. "
            "Su naturaleza esencial trasciende contextos específicos."
        )
    }
    
    def __init__(self, config_path: str = "./config_4gb_optimizado.yaml"):
        """Inicializar generador con configuración 4GB"""
        
        # Cargar configuración
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"[INIT] Configuración no encontrada: {config_path}, usando defaults")
            self.config = self._get_config_default()
        
        logger.info("[INIT] Generador de Rutas Fenomenológicas inicializado")
        logger.info(f"[INIT] Configuración: 4GB RAM, batch_size={self.config.get('clustering', {}).get('batch_size', 100)}")
        
        # Variables de control
        self._modelo_embedding = None  # Lazy load
        self.cache_embeddings = {}
        self.batch_counter = 0
        self.cache_rutas = {}  # Cache de rutas generadas
        
        # Verificar RAM
        mem = psutil.virtual_memory()
        self.ram_disponible_gb = mem.available / (1024**3)
        logger.info(f"[INIT] RAM disponible: {self.ram_disponible_gb:.2f}GB de {mem.total/(1024**3):.1f}GB")
    
    def _get_config_default(self) -> Dict:
        """Retorna configuración por defecto si no existe archivo"""
        return {
            'nlp': {
                'embedding_model': 'paraphrase-MiniLM-L3-v2',
                'embedding_cache_size': 200,
                'batch_size': 16
            },
            'clustering': {
                'batch_size': 100,
            },
            'optimization': {
                'max_memory_mb': 1024,
                'max_workers': 1,
                'gc_interval': 3
            },
            'maximo_relacional': {
                'target_certainty': 0.99,
                'min_routes_convergence': 5
            }
        }
    
    def _obtener_modelo_embedding(self):
        """Lazy loading del modelo de embeddings"""
        if self._modelo_embedding is None:
            logger.info("[LAZY_LOAD] Cargando modelo de embeddings...")
            modelo_name = self.config['nlp']['embedding_model']
            self._modelo_embedding = SentenceTransformer(modelo_name)
            logger.info(f"[LAZY_LOAD] ✓ Modelo cargado: {modelo_name} (60MB)")
        
        return self._modelo_embedding
    
    def _generar_rutas_para_concepto(self, concepto: str) -> Dict[str, str]:
        """
        Genera 5 rutas de definición para un concepto usando templates.
        
        ENTRADA: concepto (string, ej: "SOPORTE")
        SALIDA: dict con 5 rutas, cada una con 2-3 oraciones
        """
        # Verificar cache
        if concepto in self.cache_rutas:
            logger.debug(f"[RUTAS] Cache hit para: {concepto}")
            return self.cache_rutas[concepto]
        
        logger.debug(f"[RUTAS] Generando 5 rutas para: {concepto}")
        
        rutas = {}
        for nombre_ruta, template in self.RUTAS_TEMPLATES.items():
            # Reemplazar {concepto} en el template
            definicion = template.format(concepto=concepto)
            rutas[nombre_ruta] = definicion
            logger.debug(f"  ├─ {nombre_ruta}: {definicion[:60]}...")
        
        # Guardar en cache
        if len(self.cache_rutas) < self.config['nlp']['embedding_cache_size']:
            self.cache_rutas[concepto] = rutas
        
        return rutas
    
    def _generar_embedding_ruta(self, definicion: str) -> np.ndarray:
        """
        Generar embedding para una ruta de definición.
        
        OPTIMIZACIÓN:
        - Cachea embeddings
        - Carga modelo lazy
        """
        # Verificar cache
        if definicion in self.cache_embeddings:
            return self.cache_embeddings[definicion]
        
        modelo = self._obtener_modelo_embedding()
        embedding = modelo.encode(definicion, convert_to_numpy=True)
        
        # Guardar en cache si hay espacio
        if len(self.cache_embeddings) < self.config['nlp']['embedding_cache_size']:
            self.cache_embeddings[definicion] = embedding
        
        return embedding
    
    def _calcular_similitud_coseno(self, 
                                  embedding1: np.ndarray, 
                                  embedding2: np.ndarray) -> float:
        """
        Calcular similitud coseno entre dos embeddings.
        
        RANGO: [0, 1] donde 1 es idéntico
        """
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        # Normalizar de [-1, 1] a [0, 1]
        normalized = (similarity + 1) / 2
        
        return float(normalized)
    
    def _combinar_certezas(self, certezas: List[float]) -> Tuple[float, float]:
        """
        Combinar 5 certezas individuales a certeza final.
        
        FÓRMULA MULTIPLICATIVA:
        P(definición_correcta) = 1 - ∏(1 - certeza_i)
        
        Para 5 certezas de 0.91:
        P = 1 - (0.09)^5 = 0.9999941
        """
        if not certezas:
            return 0.0, 0.0
        
        # Promedio individual
        promedio = np.mean(certezas)
        
        # Combinada (multiplicativa)
        product = np.prod([1 - c for c in certezas])
        combinada = 1 - product
        
        return float(promedio), float(combinada)
    
    def _limpiar_memoria(self, fuerza: bool = False):
        """
        Ejecutar garbage collection si es necesario.
        
        OPTIMIZACIÓN 4GB: GC cada 3 batches o forzado
        """
        self.batch_counter += 1
        
        intervalo = self.config['optimization']['gc_interval']
        if self.batch_counter >= intervalo or fuerza:
            gc.collect()
            self.batch_counter = 0
            logger.debug("[GC] Garbage collection ejecutado")
            
            # Advertencia si RAM baja
            mem = psutil.virtual_memory()
            if mem.percent > 80:
                logger.warning(f"[GC] ⚠ RAM crítica: {mem.percent:.1f}% usado")
    
    def _verificar_ram_disponible(self) -> bool:
        """Verificar que hay suficiente RAM disponible"""
        mem = psutil.virtual_memory()
        disponible_gb = mem.available / (1024**3)
        
        if disponible_gb < 0.5:  # Menos de 500MB
            logger.warning(f"[RAM] ⚠ RAM baja: {disponible_gb:.2f}GB disponibles")
            return False
        
        return True
    
    def generar_rutas(self, concepto: str) -> ResultadoGeneracion:
        """
        Generar 5 rutas para un concepto y detectar máximo relacional.
        
        PROCESO:
        1. Generar 5 rutas usando templates
        2. Crear embeddings para cada ruta
        3. Calcular similitudes respecto a promedio
        4. Combinar certezas
        5. Determinar si es máximo relacional
        
        ENTRADA:
        - concepto: string (ej: "SOPORTE")
        
        SALIDA:
        - ResultadoGeneracion con:
          * 5 rutas
          * Certeza combinada
          * ¿Es máximo relacional?
        """
        inicio = time.time()
        
        logger.info(f"[GENERAR] Procesando concepto: {concepto}")
        
        # Verificar RAM
        if not self._verificar_ram_disponible():
            logger.warning("[GENERAR] RAM insuficiente, limpiando caché...")
            self.cache_embeddings = {}
            self._limpiar_memoria(fuerza=True)
        
        # 1. Generar rutas
        logger.debug("[GENERAR] Paso 1: Generando 5 rutas...")
        rutas_textos = self._generar_rutas_para_concepto(concepto)
        
        # 2. Generar embeddings
        logger.debug("[GENERAR] Paso 2: Generando embeddings...")
        modelo = self._obtener_modelo_embedding()
        
        embeddings_dict = {}
        definiciones_lista = list(rutas_textos.values())
        
        # Batch encoding para eficiencia
        embeddings_array = modelo.encode(
            definiciones_lista,
            batch_size=16,
            convert_to_numpy=True
        )
        
        for (nombre, definicion), embedding in zip(rutas_textos.items(), embeddings_array):
            embeddings_dict[nombre] = embedding
        
        # 3. Calcular embedding de referencia (promedio)
        embedding_referencia = np.mean(embeddings_array, axis=0)
        
        # 4. Calcular similitudes para cada ruta
        logger.debug("[GENERAR] Paso 3: Calculando similitudes...")
        rutas_resultados = []
        certezas = []
        
        for nombre, definicion in rutas_textos.items():
            embedding = embeddings_dict[nombre]
            
            # Similitud con referencia
            similitud = self._calcular_similitud_coseno(embedding, embedding_referencia)
            certezas.append(similitud)
            
            ruta = RutaFenomenologica(
                nombre=nombre,
                definicion=definicion,
                embedding=embedding,
                similitud_promedio=similitud,
                confianza=similitud
            )
            rutas_resultados.append(ruta)
            
            logger.debug(f"  ├─ {nombre}: similitud={similitud:.4f}")
        
        # 5. Combinar certezas
        logger.debug("[GENERAR] Paso 4: Combinando certezas...")
        cert_promedio, cert_combinada = self._combinar_certezas(certezas)
        
        # 6. Determinar confianza del diagnóstico
        target_certainty = self.config['maximo_relacional']['target_certainty']
        
        if cert_combinada >= target_certainty:
            confianza_diagnostico = "ALTO"
            es_maximo = True
        elif cert_combinada >= 0.95:
            confianza_diagnostico = "MEDIO"
            es_maximo = False
        else:
            confianza_diagnostico = "BAJO"
            es_maximo = False
        
        # 7. Limpiar memoria
        self._limpiar_memoria()
        
        # Tiempo de procesamiento
        tiempo_ms = (time.time() - inicio) * 1000
        
        # Crear resultado
        resultado = ResultadoGeneracion(
            concepto=concepto,
            rutas=rutas_resultados,
            certeza_individual_promedio=cert_promedio,
            certeza_combinada=cert_combinada,
            es_maximo_relacional=es_maximo,
            confianza_diagnostico=confianza_diagnostico,
            tiempo_procesamiento_ms=tiempo_ms
        )
        
        # Log final
        if es_maximo:
            logger.info(f"[GENERAR] ✓ MÁXIMO RELACIONAL detectado: {concepto}")
            logger.info(f"[GENERAR]   Certeza: {cert_combinada:.4f} ({cert_combinada*100:.2f}%)")
        else:
            logger.info(f"[GENERAR] ✗ No es máximo relacional: {concepto}")
            logger.info(f"[GENERAR]   Certeza: {cert_combinada:.4f} ({cert_combinada*100:.2f}%)")
        
        return resultado
    
    def generar_rutas_batch(self, 
                           conceptos: List[str],
                           batch_size: int = 10) -> List[ResultadoGeneracion]:
        """
        Procesar múltiples conceptos en lotes.
        
        OPTIMIZACIÓN 4GB:
        - Procesa 10 conceptos a la vez
        - Limpia memoria entre lotes
        - Reporta progreso
        """
        logger.info(f"[BATCH] Procesando {len(conceptos)} conceptos en lotes de {batch_size}")
        
        resultados = []
        
        for i in range(0, len(conceptos), batch_size):
            lote = conceptos[i:i+batch_size]
            logger.info(f"[BATCH] Lote {i//batch_size + 1}: {len(lote)} conceptos")
            
            for concepto in lote:
                try:
                    resultado = self.generar_rutas(concepto)
                    resultados.append(resultado)
                except Exception as e:
                    logger.error(f"[BATCH] Error procesando '{concepto}': {e}")
                    continue
            
            # Limpiar memoria entre lotes
            self._limpiar_memoria(fuerza=True)
        
        logger.info(f"[BATCH] ✓ Procesados {len(resultados)} conceptos")
        
        maximos_encontrados = sum(1 for r in resultados if r.es_maximo_relacional)
        logger.info(f"[BATCH] Máximos relacionales encontrados: {maximos_encontrados}")
        
        return resultados
    
    def guardar_resultado(self, 
                         resultado: ResultadoGeneracion,
                         ruta_salida: str = "./resultados_rutas/"):
        """
        Guardar resultado en YAML y JSON.
        
        FORMATO:
        - YAML: Legible para humanos
        - JSON: Para integración con otros sistemas
        """
        import os
        os.makedirs(ruta_salida, exist_ok=True)
        
        # Serializar resultado (sin embeddings numpy)
        resultado_dict = {
            'concepto': resultado.concepto,
            'certeza_individual_promedio': float(resultado.certeza_individual_promedio),
            'certeza_combinada': float(resultado.certeza_combinada),
            'es_maximo_relacional': resultado.es_maximo_relacional,
            'confianza_diagnostico': resultado.confianza_diagnostico,
            'tiempo_procesamiento_ms': resultado.tiempo_procesamiento_ms,
            'rutas': [
                {
                    'nombre': r.nombre,
                    'definicion': r.definicion,
                    'similitud_promedio': float(r.similitud_promedio),
                    'confianza': float(r.confianza)
                }
                for r in resultado.rutas
            ]
        }
        
        # Guardar YAML
        ruta_yaml = os.path.join(ruta_salida, f"{resultado.concepto.lower()}_rutas.yaml")
        with open(ruta_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(resultado_dict, f, default_flow_style=False, allow_unicode=True)
        
        logger.debug(f"[SAVE] YAML guardado: {ruta_yaml}")
        
        # Guardar JSON
        ruta_json = os.path.join(ruta_salida, f"{resultado.concepto.lower()}_rutas.json")
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(resultado_dict, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"[SAVE] JSON guardado: {ruta_json}")
    
    def generar_reporte(self, resultados: List[ResultadoGeneracion]) -> str:
        """
        Generar reporte consolidado de generación de rutas.
        
        INCLUYE:
        - Total conceptos procesados
        - Máximos relacionales detectados
        - Certeza promedio
        - Tiempo total
        """
        total = len(resultados)
        maximos = sum(1 for r in resultados if r.es_maximo_relacional)
        tiempo_total = sum(r.tiempo_procesamiento_ms for r in resultados)
        certeza_promedio = np.mean([r.certeza_combinada for r in resultados])
        
        reporte = f"""
╔════════════════════════════════════════════════════════════════╗
║         REPORTE GENERACIÓN DE RUTAS FENOMENOLÓGICAS           ║
╚════════════════════════════════════════════════════════════════╝

📊 RESUMEN GENERAL:
  • Conceptos procesados: {total}
  • Máximos relacionales: {maximos} ({100*maximos/total:.1f}%)
  • Certeza promedio: {certeza_promedio:.4f} ({100*certeza_promedio:.2f}%)
  • Tiempo total: {tiempo_total:.0f}ms ({tiempo_total/1000:.2f}s)

⚙️ RENDIMIENTO:
  • Tiempo promedio/concepto: {tiempo_total/total:.0f}ms
  • Throughput: {total/(tiempo_total/1000):.1f} conceptos/segundo

🎯 MÁXIMOS ENCONTRADOS:
"""
        
        for resultado in resultados:
            if resultado.es_maximo_relacional:
                reporte += f"  ✓ {resultado.concepto} (certeza: {resultado.certeza_combinada:.4f})\n"
        
        reporte += """
════════════════════════════════════════════════════════════════════
"""
        
        return reporte


# ============================================================
# 4. EJEMPLO DE USO
# ============================================================
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("DEMOSTRACIÓN: GENERADOR DE RUTAS FENOMENOLÓGICAS")
    logger.info("=" * 70)
    
    # Inicializar generador
    gen = GeneradorRutasFenomenologicas()
    
    # Ejemplo 1: Un concepto
    logger.info("\n[DEMO] Procesando concepto individual: SOPORTE")
    resultado = gen.generar_rutas("SOPORTE")
    
    print(f"\n{'='*70}")
    print(f"CONCEPTO: {resultado.concepto}")
    print(f"{'='*70}")
    print(f"Certeza individual promedio: {resultado.certeza_individual_promedio:.4f}")
    print(f"Certeza combinada: {resultado.certeza_combinada:.4f}")
    print(f"¿Máximo relacional?: {resultado.es_maximo_relacional}")
    print(f"Confianza: {resultado.confianza_diagnostico}")
    print(f"Tiempo: {resultado.tiempo_procesamiento_ms:.1f}ms")
    
    print(f"\n{'─'*70}")
    print("RUTAS GENERADAS:")
    print(f"{'─'*70}")
    for i, ruta in enumerate(resultado.rutas, 1):
        print(f"\n{i}. {ruta.nombre}")
        print(f"   Definición: {ruta.definicion[:80]}...")
        print(f"   Confianza: {ruta.confianza:.4f}")
    
    # Guardar resultado
    gen.guardar_resultado(resultado)
    
    # Ejemplo 2: Batch de conceptos
    logger.info("\n[DEMO] Procesando batch de conceptos")
    conceptos = ["TIEMPO", "ESPACIO", "CONSCIENCIA", "EMERGENCIA", "IDENTIDAD"]
    resultados = gen.generar_rutas_batch(conceptos, batch_size=3)
    
    # Reporte
    print(gen.generar_reporte(resultados))
    
    logger.info("\n[DEMO] ✓ Demostración completada")
