"""
ANALIZADOR DE CONVERGENCIA DEFINICIONAL
========================================
Detecta cuándo un concepto alcanza MÁXIMO RELACIONAL DEFINICIONAL
mediante convergencia a 99%+ certeza a través de 5 rutas independientes.

OPTIMIZADO PARA: AMD Dual-Core + 4GB RAM DDR3 @ 1334MHz
- RAM disponible: ~1.2GB de 4GB total
- Batch processing: SÍ (máx 10 conceptos)
- Lazy loading: SÍ
- Streaming: SÍ
- Memory efficient: CRÍTICO
- GC agresivo: Cada 3 batches
"""

import gc
import yaml
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# 1. CONFIGURACIÓN DE LOGGING LIGERO
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("MaximoRelacional")

# ============================================================
# 2. DATACLASSES PARA RESULTADOS
# ============================================================
@dataclass
class RutaDefinicional:
    """Una ruta de validación independiente"""
    nombre: str  # "Física", "Ergonómica", "Arquitectónica", "Lógica", "Ontológica"
    definicion: str
    embedding: np.ndarray
    certeza: float  # 0.0 a 1.0
    evidencias: List[str]

@dataclass
class ResultadoConvergencia:
    """Resultado del análisis de convergencia"""
    concepto: str
    rutas: List[RutaDefinicional]
    certeza_individual_promedio: float
    certeza_combinada: float  # Fórmula multiplicativa
    es_maximo_relacional: bool
    confianza_diagnostico: str  # "ALTO", "MEDIO", "BAJO"

# ============================================================
# 3. ANALIZADOR PRINCIPAL - OPTIMIZADO PARA MEMORIA
# ============================================================
class AnalizadorConvergenciaOptimizado:
    """
    Analiza convergencia de 5 rutas hacia definición única.
    
    OPTIMIZACIONES APLICADAS:
    - Carga lazy del modelo embedding
    - Procesa por lotes
    - Limpia memoria frecuentemente
    - Usa embeddings pequeños (384 dims)
    """
    
    def __init__(self, config_path: str = "./config_4gb_optimizado.yaml"):
        """Inicializar con configuración optimizada para 4GB RAM"""
        
        # Cargar config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info("[INIT] Cargando analizador para 4GB RAM...")
        logger.info(f"[INIT] RAM disponible: ~1.2GB de 4GB total")
        
        # Variables de control
        self._modelo_embedding = None  # Lazy load
        self.cache_embeddings = {}
        self.batch_counter = 0
        
        # Verificar memoria disponible
        import psutil
        mem = psutil.virtual_memory()
        if mem.available < 1.5 * 1024**3:  # <1.5GB disponible
            logger.warning(f"[INIT] ⚠ Memoria baja: {mem.available/(1024**3):.2f}GB disponibles")
        
        logger.info("[INIT] ✓ Analizador listo")
    
    def _obtener_modelo_embedding(self):
        """
        Lazy loading del modelo embedding.
        Solo se carga cuando se necesita.
        """
        if self._modelo_embedding is None:
            logger.info("[LAZY_LOAD] Cargando modelo embedding...")
            modelo_name = self.config['nlp']['embedding_model']
            self._modelo_embedding = SentenceTransformer(modelo_name)
            logger.info(f"[LAZY_LOAD] ✓ Modelo cargado: {modelo_name}")
        
        return self._modelo_embedding
    
    def _generar_embedding(self, texto: str) -> np.ndarray:
        """
        Generar embedding con caché.
        
        OPTIMIZACIÓN:
        - Cachea embeddings para evitar recálculos
        - Usa batch encoding
        """
        if texto in self.cache_embeddings:
            return self.cache_embeddings[texto]
        
        modelo = self._obtener_modelo_embedding()
        embedding = modelo.encode(texto, convert_to_numpy=True)
        
        # Cachear si no superamos límite
        if len(self.cache_embeddings) < self.config['nlp']['embedding_cache_size']:
            self.cache_embeddings[texto] = embedding
        
        return embedding
    
    def _calcular_certeza_ruta(self, 
                               ruta: RutaDefinicional,
                               embedding_referencia: np.ndarray) -> float:
        """
        Calcular certeza de una ruta comparando embeddings.
        
        FÓRMULA: similarity coseno normalizada a rango [0, 1]
        """
        embedding_ruta = ruta.embedding
        
        # Similitud coseno
        similarity = np.dot(embedding_ruta, embedding_referencia) / (
            np.linalg.norm(embedding_ruta) * np.linalg.norm(embedding_referencia) + 1e-8
        )
        
        # Normalizar a [0, 1]
        certeza = (similarity + 1) / 2
        
        return float(certeza)
    
    def _combinar_certezas(self, certezas: List[float]) -> Tuple[float, float]:
        """
        Combinar 5 certezas individuales a certeza final.
        
        FÓRMULA MULTIPLICATIVA (usada en sesión anterior):
        P(definición_correcta) = 1 - ∏(1 - certeza_i)
        
        Para 5 certezas de 0.91:
        P = 1 - (1-0.91)^5 = 1 - 0.09^5 = 1 - 0.0000059 = 0.9999941
        """
        if not certezas:
            return 0.0, 0.0
        
        # Promedio individual
        promedio = np.mean(certezas)
        
        # Combinada (fórmula multiplicativa)
        product = np.prod([1 - c for c in certezas])
        combinada = 1 - product
        
        return promedio, combinada
    
    def _limpiar_memoria(self, fuerza: bool = False):
        """
        Limpiar memoria si es necesario.
        
        OPTIMIZACIÓN: Ejecuta garbage collection estratégicamente
        """
        self.batch_counter += 1
        
        intervalo = self.config['optimization']['gc_interval']
        if self.batch_counter >= intervalo or fuerza:
            gc.collect()
            self.batch_counter = 0
            logger.debug("[GC] Memoria limpiada")
    
    def analizar_concepto(self, 
                         concepto: str,
                         rutas_definiciones: Dict[str, str]) -> ResultadoConvergencia:
        """
        Analizar si concepto alcanza máximo relacional definicional.
        
        ENTRADA:
        - concepto: "SOPORTE"
        - rutas_definiciones: {
            "Física": "Material que sostiene algo",
            "Ergonómica": "Superficie que distribuye fuerzas...",
            ...
          }
        
        SALIDA:
        - ResultadoConvergencia con certeza combinada y diagnóstico
        """
        logger.info(f"[ANÁLISIS] Analizando concepto: {concepto}")
        
        # Validar entrada
        if len(rutas_definiciones) != 5:
            logger.warning(f"[ANÁLISIS] ⚠ Se esperan 5 rutas, se recibieron {len(rutas_definiciones)}")
        
        # Embedding de referencia (definición promedio)
        definiciones_lista = list(rutas_definiciones.values())
        modelo = self._obtener_modelo_embedding()
        
        embeddings_batch = modelo.encode(
            definiciones_lista,
            batch_size=32,
            convert_to_numpy=True
        )
        
        # Promedio de embeddings como referencia
        embedding_referencia = np.mean(embeddings_batch, axis=0)
        
        # Procesar cada ruta
        rutas = []
        certezas = []
        
        for nombre, definicion in rutas_definiciones.items():
            embedding = self._generar_embedding(definicion)
            
            # Calcular certeza para esta ruta
            certeza = self._calcular_certeza_ruta(
                RutaDefinicional(nombre, definicion, embedding, 0.0, []),
                embedding_referencia
            )
            
            certezas.append(certeza)
            
            ruta = RutaDefinicional(
                nombre=nombre,
                definicion=definicion,
                embedding=embedding,
                certeza=certeza,
                evidencias=[f"Similitud con referencia: {certeza:.4f}"]
            )
            rutas.append(ruta)
            
            logger.debug(f"  → {nombre}: {certeza:.4f}")
        
        # Combinar certezas
        cert_promedio, cert_combinada = self._combinar_certezas(certezas)
        
        # Diagnóstico
        es_maximo = cert_combinada >= self.config['maximo_relacional']['target_certainty']
        
        if es_maximo:
            confianza = "ALTO" if cert_combinada >= 0.999 else "MEDIO"
        else:
            confianza = "BAJO"
        
        resultado = ResultadoConvergencia(
            concepto=concepto,
            rutas=rutas,
            certeza_individual_promedio=cert_promedio,
            certeza_combinada=cert_combinada,
            es_maximo_relacional=es_maximo,
            confianza_diagnostico=confianza
        )
        
        logger.info(f"[RESULTADO] {concepto}")
        logger.info(f"  ├─ Certeza individual: {cert_promedio:.4f}")
        logger.info(f"  ├─ Certeza combinada:  {cert_combinada:.6f}")
        logger.info(f"  ├─ Es máximo relacional: {'✓ SÍ' if es_maximo else '✗ NO'}")
        logger.info(f"  └─ Confianza: {confianza}")
        
        # Limpiar memoria
        self._limpiar_memoria()
        
        return resultado
    
    def procesar_lote_conceptos(self,
                                conceptos_rutas: Dict[str, Dict[str, str]],
                                batch_size: int = 10) -> List[ResultadoConvergencia]:
        """
        Procesar múltiples conceptos en lotes (OPTIMIZACIÓN CRÍTICA para 4GB RAM).
        
        ENTRADA:
        - conceptos_rutas: {
            "SOPORTE": {"Física": "...", "Ergonómica": "...", ...},
            "ESTRUCTURA": {...},
            ...
          }
        
        PROCESAMIENTO POR LOTES MUY PEQUEÑOS:
        - Procesa batch_size conceptos
        - Libera memoria después de cada lote
        - Permite procesamiento de 500+ conceptos en 4GB (NO 1000+)
        """
        logger.info(f"[LOTE] Procesando {len(conceptos_rutas)} conceptos en lotes de {batch_size}...")
        logger.info(f"[LOTE] ⚠ Modo 4GB RAM: batch_size pequeño recomendado (<= 10)")
        
        resultados = []
        conceptos_items = list(conceptos_rutas.items())
        
        for i in range(0, len(conceptos_items), batch_size):
            lote = conceptos_items[i:i+batch_size]
            logger.info(f"[LOTE] Procesando concepto {i+1}/{len(conceptos_items)}")
            
            # Verificar memoria ANTES de cada lote
            import psutil
            mem = psutil.virtual_memory()
            if mem.percent > 80:  # >80% usado
                logger.warning(f"[LOTE] ⚠ RAM alta: {mem.percent:.1f}% - Forzando GC...")
                self._limpiar_memoria(fuerza=True)
            
            for concepto, rutas in lote:
                resultado = self.analizar_concepto(concepto, rutas)
                resultados.append(resultado)
            
            # Limpiar después del lote (SIEMPRE en 4GB)
            self._limpiar_memoria(fuerza=True)
            
            # Pausa pequeña para permitir liberación
            import time
            time.sleep(0.1)
        
        return resultados


# ============================================================
# 4. FUNCIONES AUXILIARES
# ============================================================
def generar_reporte(resultados: List[ResultadoConvergencia]) -> str:
    """Generar reporte textual de resultados"""
    
    maximo_count = sum(1 for r in resultados if r.es_maximo_relacional)
    
    reporte = f"""
╔════════════════════════════════════════════════════════════╗
║        REPORTE DE MÁXIMO RELACIONAL DEFINICIONAL          ║
╚════════════════════════════════════════════════════════════╝

RESUMEN:
  • Conceptos analizados:        {len(resultados)}
  • Máximos relacionales (99%+): {maximo_count}
  • Porcentaje:                  {100*maximo_count/len(resultados):.1f}%

CONCEPTOS CON MÁXIMO RELACIONAL:
"""
    for r in resultados:
        if r.es_maximo_relacional:
            reporte += f"""
  ✓ {r.concepto}
    ├─ Certeza combinada: {r.certeza_combinada:.6f}
    ├─ Confianza: {r.confianza_diagnostico}
    └─ Rutas convergentes: {len(r.rutas)}
"""
    
    return reporte


# ============================================================
# 5. EJEMPLO DE USO
# ============================================================
if __name__ == "__main__":
    # Inicializar con config para 4GB RAM
    analizador = AnalizadorConvergenciaOptimizado(
        config_path="./config_4gb_optimizado.yaml"
    )
    
    # Ejemplo: analizar concepto SOPORTE
    rutas_soporte = {
        "Física": "Material que sostiene peso y distribuye fuerzas hacia abajo",
        "Ergonómica": "Superficie que acomoda la forma del cuerpo humano",
        "Arquitectónica": "Elemento estructural que transfiere cargas al suelo",
        "Lógica": "Entidad que fundamenta la existencia de otra",
        "Ontológica": "Razón de ser fundamental en la estructura del ser"
    }
    
    resultado = analizador.analizar_concepto("SOPORTE", rutas_soporte)
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                    RESULTADO FINAL                        ║
║              (Optimizado para 4GB RAM)                    ║
╚════════════════════════════════════════════════════════════╝

Concepto: {resultado.concepto}
Certeza combinada: {resultado.certeza_combinada:.6f}
¿Es máximo relacional?: {'✓ SÍ' if resultado.es_maximo_relacional else '✗ NO'}
Confianza: {resultado.confianza_diagnostico}

RUTAS INDIVIDUALES:
""")
    
    for ruta in resultado.rutas:
        print(f"  {ruta.nombre}: {ruta.certeza:.4f}")
