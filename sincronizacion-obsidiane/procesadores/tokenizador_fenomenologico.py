"""
Tokenizador Fenomenológico - Wrapper de REMForge
=================================================

Proporciona una interfaz unificada para la tokenización fenomenológica,
integrando REMForge Ultra/Lite en el sistema YO Estructural.

Autor: Sistema YO Estructural v3.0
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import psutil

# Agregar directorio REm al path si no está
rem_path = Path(__file__).parent.parent / "REm"
if str(rem_path) not in sys.path:
    sys.path.insert(0, str(rem_path))

try:
    from REm.remforge_ultra_formato_optimo import REMForgeUltraFormatoOptimo
    from REm.remforge_lite import REMForgeLite
    REMFORGE_AVAILABLE = True
except ImportError as e:
    REMFORGE_AVAILABLE = False
    logging.warning(f"REMForge no disponible: {e}")

logger = logging.getLogger("TokenizadorFenomenologico")


class TokenizadorFenomenologico:
    """
    Interfaz unificada para REMForge (tokenización fenomenológica)
    
    Selecciona automáticamente entre REMForge Ultra (completo) y Lite (ligero)
    basado en recursos disponibles del sistema.
    
    Funcionalidades:
    - Tokenización con análisis de interferencia fenomenológica
    - Extracción de invariantes noéticas
    - Análisis de qualia lingüística
    - Separación afecto semántico vs fenomenológico
    - Generación de PhenomenalREM-Ultra JSON Schema
    
    Ejemplo:
        >>> tokenizador = TokenizadorFenomenologico()
        >>> resultado = tokenizador.forge_text_ultra(
        ...     "Veo un objeto rojo en la mesa.",
        ...     context={"autor": "usuario1"}
        ... )
        >>> print(resultado['phenomenal_core']['qualia_signature'])
    """
    
    def __init__(self, device: str = "auto", modo: str = "auto", precision: str = "float16"):
        """
        Inicializa el tokenizador fenomenológico
        
        Args:
            device: 'cpu' | 'cuda' | 'mps' | 'auto'
                Dispositivo para cómputo. 'auto' detecta automáticamente.
            modo: 'ultra' | 'lite' | 'auto'
                Modo de operación. 'auto' selecciona según RAM disponible.
            precision: 'float16' | 'float32'
                Precisión de cálculos (solo para Ultra)
        """
        if not REMFORGE_AVAILABLE:
            raise ImportError(
                "REMForge no está disponible. "
                "Verifique que los archivos REm/remforge_*.py existan."
            )
        
        self.device = device
        self.modo = modo
        self.precision = precision
        self.forge = None
        
        self._inicializar_forge()
        
        logger.info(f"✅ TokenizadorFenomenologico inicializado - Modo: {self.modo}, Device: {self.device}")
    
    def _inicializar_forge(self):
        """Inicializa REMForge según el modo y recursos disponibles"""
        # Determinar modo automáticamente si es necesario
        if self.modo == "auto":
            self.modo = self._detectar_modo_optimo()
        
        # Inicializar según modo
        if self.modo == "ultra":
            try:
                self.forge = REMForgeUltraFormatoOptimo(
                    device=self.device,
                    precision=self.precision
                )
                logger.info("✅ REMForge Ultra inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Error inicializando Ultra: {e}. Fallback a Lite")
                self.modo = "lite"
                self._inicializar_lite()
        else:
            self._inicializar_lite()
    
    def _inicializar_lite(self):
        """Inicializa REMForge Lite (fallback)"""
        try:
            self.forge = REMForgeLite(device="cpu")
            logger.info("✅ REMForge Lite inicializado")
        except Exception as e:
            logger.error(f"❌ Error crítico inicializando Lite: {e}")
            raise RuntimeError("No se pudo inicializar ninguna versión de REMForge")
    
    def _detectar_modo_optimo(self) -> str:
        """
        Detecta el modo óptimo según recursos del sistema
        
        Returns:
            'ultra' si RAM > 6GB, 'lite' en caso contrario
        """
        try:
            ram_disponible_gb = psutil.virtual_memory().available / (1024**3)
            
            if ram_disponible_gb > 6:
                logger.info(f"RAM disponible: {ram_disponible_gb:.1f}GB - Usando Ultra")
                return "ultra"
            else:
                logger.info(f"RAM disponible: {ram_disponible_gb:.1f}GB - Usando Lite")
                return "lite"
        except Exception as e:
            logger.warning(f"Error detectando RAM: {e}. Default a Lite")
            return "lite"
    
    def forge_text_ultra(
        self, 
        texto: str, 
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Tokeniza texto con análisis fenomenológico completo
        
        Args:
            texto: Texto experiencial a analizar (narrativa, diario, descripción)
            context: Contexto opcional con claves:
                - situational_context: str
                - temporal_context: str
                - author_id: str
        
        Returns:
            Dict con PhenomenalREM-Ultra JSON Schema:
            
            {
                "header": {
                    "rem_id": str,
                    "forge_version": str,
                    "creation_timestamp": str (ISO),
                    "modality_origin": str,
                    "temporal_scope": {...},
                    "quality_metrics": {
                        "completeness_score": float,
                        "contamination_detected": bool,
                        "phenomenal_resolution": float (bits/token)
                    }
                },
                "experiential_stream": {
                    "narrative_raw": str,
                    "narrative_enriched": str,
                    "clause_boundaries": List[Dict],
                    "temporal_markers": List[str]
                },
                "noetic_layer": {
                    "intentional_mode": str (perception|memory|imagination|reflection),
                    "directedness": str,
                    "temporal_phase": str,
                    "ego_involvement": float (0-1),
                    "horizon_type": str,
                    "act_intensity": float
                },
                "sensorial_layer": {
                    "modality_distribution": Dict[str, float],
                    "spatial_horizon": str,
                    "spatial_coordinates": {...},
                    "affective_valence": float,
                    "affective_arousal": float,
                    "sensorial_resolution": {...}
                },
                "semantic_contamination": {
                    "contamination_strength": float (0-1),
                    "source": str,
                    "lexical_anchors": List[Dict],
                    "semantic_traces": List[Dict],
                    "invariance_under_semantic_permutation": Dict
                },
                "phenomenal_core": {
                    "invariant_features": {...},
                    "qualia_signature": {
                        "qualia_type": str,
                        "intensity_profile": List[float],
                        "discrimination_threshold": float,
                        "phenomenal_saturation": float
                    },
                    "eidetic_reductions": {...}
                },
                "multiscale_representation": {
                    "coarse_scale": {...},
                    "medium_scale": {...},
                    "fine_scale": {...}
                },
                "visualization_layer": {
                    "experience_map": {...},
                    "contamination_heatmap": {...},
                    "temporal_flow": {...}
                }
            }
        
        Raises:
            ValueError: Si el texto está vacío
            RuntimeError: Si hay error en el procesamiento
        
        Ejemplo:
            >>> texto = "Percibo un sonido agudo que vibra en el espacio cercano."
            >>> resultado = tokenizador.forge_text_ultra(texto)
            >>> print(f"Modo intencional: {resultado['noetic_layer']['intentional_mode']}")
            >>> print(f"Qualia dominante: {resultado['phenomenal_core']['qualia_signature']['qualia_type']}")
        """
        if not texto or not texto.strip():
            raise ValueError("El texto no puede estar vacío")
        
        if context is None:
            context = {}
        
        try:
            # Llamar al método principal de REMForge
            rem_output = self.forge.forge_text_ultra(texto, context)
            
            # Agregar metadata de integración
            rem_output["integration_metadata"] = {
                "tokenizer_mode": self.modo,
                "device_used": self.device,
                "sistema_yo_version": "3.0",
                "processing_timestamp": rem_output['header']['creation_timestamp']
            }
            
            logger.debug(f"Tokenización exitosa: {len(texto)} chars → {rem_output['header']['rem_id']}")
            
            return rem_output
        
        except Exception as e:
            logger.error(f"❌ Error en tokenización fenomenológica: {e}")
            raise RuntimeError(f"Error procesando texto: {str(e)}")
    
    def extraer_invariantes_noeticas(self, texto: str) -> Dict[str, Any]:
        """
        Extrae solo invariantes noéticas (pipeline rápido sin análisis completo)
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Dict con:
            - dominant_mode: str (modo intencional dominante)
            - directedness: str (dirección de la intencionalidad)
            - invariant_vectors: List[List[float]] (vectores de invariantes)
            - shifts: List[Dict] (cambios intencionales)
            - transitions: List[Dict] (transiciones de fase)
            - temporal_vectors: List[List[float]] (retención-protensión)
        """
        if hasattr(self.forge, '_extract_noetic_invariants'):
            try:
                clauses = self.forge._analyze_clausal_structure(texto)
                invariantes = self.forge._extract_noetic_invariants(clauses)
                
                logger.debug(f"Invariantes noéticas extraídas - Modo: {invariantes.get('dominant_mode')}")
                return invariantes
            except Exception as e:
                logger.warning(f"Error extrayendo invariantes: {e}")
                return {}
        else:
            logger.warning("Método _extract_noetic_invariants no disponible en esta versión")
            return {}
    
    def calcular_interferencia_tokens(self, texto: str) -> Dict[str, Any]:
        """
        Calcula interferencia fenomenológica de tokens
        
        La interferencia mide cuánto "contamina" la semántica conceptual
        la pureza del contenido fenomenológico directo.
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Dict con:
            - anchors: List[str] (tokens de anclaje)
            - embeddings: List[List[float]] (vectores de embeddings)
            - interference_scores: List[float] (0=puro, 1=contaminado)
            - promedio_interferencia: float
            - tokens_puros: List[str] (interferencia < 0.3)
            - tokens_contaminados: List[str] (interferencia > 0.7)
        """
        if hasattr(self.forge, '_extract_anchors_with_interference'):
            try:
                anchors, embeddings, interference_scores = self.forge._extract_anchors_with_interference(texto)
                
                # Clasificar tokens por nivel de interferencia
                tokens_puros = [a for a, i in zip(anchors, interference_scores) if i < 0.3]
                tokens_contaminados = [a for a, i in zip(anchors, interference_scores) if i > 0.7]
                
                promedio = sum(interference_scores) / len(interference_scores) if interference_scores else 0.0
                
                logger.debug(
                    f"Interferencia calculada: {len(anchors)} tokens, "
                    f"promedio={promedio:.2f}, puros={len(tokens_puros)}, contaminados={len(tokens_contaminados)}"
                )
                
                return {
                    "anchors": anchors,
                    "embeddings": [emb.tolist() if hasattr(emb, 'tolist') else emb for emb in embeddings],
                    "interference_scores": interference_scores,
                    "promedio_interferencia": promedio,
                    "tokens_puros": tokens_puros,
                    "tokens_contaminados": tokens_contaminados,
                    "nivel_pureza": "ALTO" if promedio < 0.3 else "MEDIO" if promedio < 0.7 else "BAJO"
                }
            except Exception as e:
                logger.warning(f"Error calculando interferencia: {e}")
                return {}
        else:
            logger.warning("Método _extract_anchors_with_interference no disponible")
            return {}
    
    def analizar_qualia_signature(self, texto: str) -> Dict[str, Any]:
        """
        Analiza la signature de qualia del texto
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Dict con signature de qualia:
            - dominant_type: str (visual|auditory|haptic|olfactory|gustatory|affective)
            - intensity_profile: List[float] (intensidades por modalidad)
            - jnd_threshold: float (umbral de discriminación)
            - saturation: float (0-1, saturación fenomenológica)
            - invariant_patterns: List (patrones invariantes)
            - clusters: List[Dict] (clusters de qualia)
        """
        if hasattr(self.forge, '_build_linguistic_qualia_signature'):
            try:
                # Necesitamos extraer anchors primero
                if hasattr(self.forge, '_extract_anchors_with_interference'):
                    anchors, _, _ = self.forge._extract_anchors_with_interference(texto)
                else:
                    anchors = []
                
                signature = self.forge._build_linguistic_qualia_signature(texto, anchors)
                
                logger.debug(f"Qualia signature: tipo={signature.get('dominant_type')}, saturación={signature.get('saturation', 0):.2f}")
                return signature
            except Exception as e:
                logger.warning(f"Error analizando qualia: {e}")
                return {}
        else:
            logger.warning("Método _build_linguistic_qualia_signature no disponible")
            return {}
    
    def get_modo(self) -> str:
        """Retorna el modo actual del forge"""
        return self.modo
    
    def get_device(self) -> str:
        """Retorna el dispositivo actual"""
        return self.device
    
    def is_ultra(self) -> bool:
        """Retorna True si está usando REMForge Ultra"""
        return self.modo == "ultra"
    
    def get_info(self) -> Dict[str, Any]:
        """
        Retorna información del tokenizador
        
        Returns:
            Dict con información del sistema:
            - modo: str
            - device: str
            - precision: str
            - forge_version: str
            - remforge_available: bool
        """
        return {
            "modo": self.modo,
            "device": self.device,
            "precision": self.precision,
            "forge_version": getattr(self.forge, 'forge_version', 'unknown'),
            "remforge_available": REMFORGE_AVAILABLE,
            "clase_forge": self.forge.__class__.__name__ if self.forge else None
        }


# Funciones de utilidad

def crear_tokenizador_auto() -> TokenizadorFenomenologico:
    """
    Crea un tokenizador con configuración automática
    
    Returns:
        TokenizadorFenomenologico configurado automáticamente
    """
    return TokenizadorFenomenologico(device="auto", modo="auto")


def validar_remforge_disponible() -> bool:
    """
    Valida si REMForge está disponible
    
    Returns:
        True si REMForge puede importarse, False en caso contrario
    """
    return REMFORGE_AVAILABLE


if __name__ == "__main__":
    # Test básico
    import json
    
    print("🧪 Test de TokenizadorFenomenologico\n")
    
    if not REMFORGE_AVAILABLE:
        print("❌ REMForge no disponible")
        exit(1)
    
    # Crear tokenizador
    tokenizador = crear_tokenizador_auto()
    print(f"✅ Tokenizador creado: {json.dumps(tokenizador.get_info(), indent=2)}\n")
    
    # Texto de prueba
    texto_test = "Veo un objeto rojo brillante en la mesa. El sonido ambiental es suave y cálido."
    print(f"📝 Texto de prueba:\n{texto_test}\n")
    
    # Tokenización completa
    print("🔄 Ejecutando tokenización completa...")
    resultado = tokenizador.forge_text_ultra(texto_test, context={"autor": "test"})
    
    print(f"\n✅ Resultado:")
    print(f"  - REM ID: {resultado['header']['rem_id']}")
    print(f"  - Modo intencional: {resultado['noetic_layer']['intentional_mode']}")
    print(f"  - Qualia dominante: {resultado['phenomenal_core']['qualia_signature']['qualia_type']}")
    print(f"  - Interferencia: {resultado['semantic_contamination']['contamination_strength']:.2f}")
    print(f"  - Resolución fenomenológica: {resultado['header']['quality_metrics']['phenomenal_resolution']:.2f} bits/token")
    
    # Test de invariantes
    print("\n🔄 Extrayendo invariantes noéticas...")
    invariantes = tokenizador.extraer_invariantes_noeticas(texto_test)
    if invariantes:
        print(f"  - Modo dominante: {invariantes.get('dominant_mode')}")
        print(f"  - Directedness: {invariantes.get('directedness')}")
    
    # Test de interferencia
    print("\n🔄 Calculando interferencia de tokens...")
    interferencia = tokenizador.calcular_interferencia_tokens(texto_test)
    if interferencia:
        print(f"  - Tokens analizados: {len(interferencia.get('anchors', []))}")
        print(f"  - Promedio interferencia: {interferencia.get('promedio_interferencia', 0):.2f}")
        print(f"  - Nivel de pureza: {interferencia.get('nivel_pureza', 'N/A')}")
        print(f"  - Tokens puros: {', '.join(interferencia.get('tokens_puros', []))}")
    
    print("\n✅ Test completado exitosamente")
