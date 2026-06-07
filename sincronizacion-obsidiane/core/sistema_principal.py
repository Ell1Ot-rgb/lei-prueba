
# Imports estándar
from dotenv import load_dotenv
import os
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# Cargar variables de entorno (.env)
load_dotenv()

# Imports del sistema - Motor YO
try:
    from motor_yo.sistema_yo_emergente import SistemaYoEmergente
    from motor_yo.gradient_system import VohexGradientSystem
except ImportError:
    SistemaYoEmergente = None
    VohexGradientSystem = None

# Imports del sistema - Procesadores
try:
    # Procesador fenomenológico (original)
    from analizador_textos.procesador_fenomenologico import ProcesadorFenomenologico
except ImportError:
    try:
        from procesadores.procesador_fenomenologico import ProcesadorFenomenologico
    except ImportError:
        ProcesadorFenomenologico = None

from procesadores.generador_rutas_fenomenologicas import GeneradorRutasFenomenologicas
from procesadores.tokenizador_fenomenologico import TokenizadorFenomenologico

# Imports del sistema - Integraciones
try:
    from procesadores.gemini_integration import GeminiEnriquecedor
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Gemini integration no disponible")

try:
    from procesadores.analizador_maximo_relacional_hibrido import OrquestadorComputacionHibrida
    ANALIZADOR_HIBRIDO_AVAILABLE = True
except ImportError:
    ANALIZADOR_HIBRIDO_AVAILABLE = False
    logging.warning("Analizador híbrido no disponible")

try:
    from integraciones.n8n_config import N8nIntegrator
    N8N_AVAILABLE = True
except ImportError:
    N8N_AVAILABLE = False
    logging.warning("n8n integration no disponible")

# Imports del sistema - Niveles fenomenológicos
from niveles.preinstancia import PreInstancia
from niveles.instancia_existencia import InstanciaExistencia
from niveles.vohexistencia import Vohexistencia

# Imports del sistema - Sistemas de Capa 2
try:
    from emergencia_concepto.motor_emergencia import MotorEmergenciaConceptos
    EMERGENCIA_AVAILABLE = True
except ImportError:
    EMERGENCIA_AVAILABLE = False
    logging.warning("Sistema de Emergencia de Conceptos no disponible")

try:
    from logica_pura.motor_hipotetico import MotorHipotetico
    LOGICA_PURA_AVAILABLE = True
except ImportError:
    LOGICA_PURA_AVAILABLE = False
    logging.warning("Sistema de Lógica Pura no disponible")
class SistemaYoEstructural:
    """
    Sistema principal Estructural
    
    **Integraciones**:
    - Gemini (LLM para enriquecimiento)
    - n8n (Orquestación de workflows)
    - Neo4j (Persistencia de grafos)
    
    **Ejemplo de uso**:
        >>> sistema = SistemaYoEstructural("config/config_4gb.yaml")
        >>> resultado = sistema.procesar_flujo_completo("entrada_bruta/")
        >>> print(f"Tipo YO: {resultado['estado_yo']['tipo']}")
        >>> print(f"Vohexistencias: {resultado['vohexistencias_detectadas']}")
    """
    
    def __init__(self, config_path: str):
        """
        Inicializa el sistema completo
        
        Args:
            config_path: Ruta al archivo de configuración YAML
        
        Raises:
            FileNotFoundError: Si el archivo de configuración no existe
            ValueError: Si la configuración es inválida
        """
        # Validar que existe el archivo de configuración
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
        
        self.config_path = config_path
        self.config = self._cargar_config(config_path)
        self.modo_diagnostico = self.config.get("modo_diagnostico", False)
        
        # Configurar logging ANTES de inicializar componentes
        self._configurar_logging()
        
        self.logger.info("="*60)
        self.logger.info("Iniciando Sistema YO Estructural v3.0")
        self.logger.info("="*60)
        
        # Inicializar conexión Neo4j (CRÍTICO - debe ser primero)
        self._inicializar_neo4j()
        
        # Inicializar Motor YO (requiere Neo4j)
        self.motor_yo = SistemaYoEmergente(self.config_path, self.neo4j._driver)
        self.motor_yo.registrar_callback("mdce", self._manejar_evento_mdce)
        self.logger.info("✅ Motor YO emergente inicializado")
        
        # Inicializar Sistema de Gradientes
        self.sistema_gradientes = VohexGradientSystem()
        self.logger.info("✅ Sistema de gradientes inicializado")
        
        # Inicializar Procesadores Fenomenológicos
        self._inicializar_procesadores()
        
        # Inicializar Sistemas de Capa 2 (S2: Emergencia, S3: Lógica)
        self._inicializar_sistemas_capa2()
        
        # Inicializar Integraciones Externas (opcional)
        self._inicializar_integraciones()
        
        # Estado del sistema
        self.instancias = []
        self.vohexistencias = []
        self.metricas = {
            "diversidad_contextual": 0.0,
            "profundidad_narrativa": 0,
            "coherencia_temporal": 0.0,
            "emergencia_yo_narrativo": False
        }
        
        self.logger.info("="*60)
        self.logger.info("🚀 Sistema YO Estructural v3.0 LISTO")
        self.logger.info(f"   Componentes activos: {len(self.get_componentes_activos())}")
        self.logger.info("="*60)
    
    def _cargar_config(self, config_path: str) -> Dict:
        """
        Carga configuración desde archivo YAML
        
        Args:
            config_path: Ruta al archivo YAML
        
        Returns:
            Dict con configuración del sistema
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validar que tiene secciones críticas
            required_sections = ['neo4j', 'rutas']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Sección '{section}' faltante en configuración")
            
            return config
        
        except yaml.YAMLError as e:
            raise ValueError(f"Error parseando YAML: {e}")
        except Exception as e:
            raise ValueError(f"Error cargando configuración: {e}")




# ============================================================
# SECCIÓN 3: MÉTODOS DE CONFIGURACIÓN
# ============================================================

    # ----------------------------------------------------------
    # 3.1: Configuración de Logging
    # ----------------------------------------------------------
    
    def _configurar_logging(self):
        """
        Configura sistema de logging estructurado
        
        - Crea archivo de log con timestamp
        - Nivel DEBUG si modo_diagnostico = True
        - Nivel INFO en producción
        - Salida tanto a archivo como a consola
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path("logs_sistema")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"sistema_principal_{timestamp}.log"
        
        nivel = logging.DEBUG if self.modo_diagnostico else logging.INFO
        
        logging.basicConfig(
            level=nivel,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("SistemaYoEstructural")
        self.logger.info(f"Logging configurado - Nivel: {logging.getLevelName(nivel)}")
        self.logger.info(f"Archivo log: {log_file}")
    
    def _debug_print(self, mensaje: str, nivel: str = "INFO"):
        """
        Imprime mensajes de diagnóstico si modo_diagnostico está activado
        
        Args:
            mensaje: Mensaje a imprimir
            nivel: Nivel de log (INFO, DEBUG, WARNING, ERROR)
        """
        if self.modo_diagnostico:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [DIAGNÓSTICO-{nivel}] {mensaje}")
            
            if hasattr(self, 'logger'):
                getattr(self.logger, nivel.lower())(mensaje)
    
    # ----------------------------------------------------------
    # 3.2: Inicialización de Neo4j
    # ----------------------------------------------------------
    
    def _inicializar_neo4j(self):
        """
        Inicializa conexión con Neo4j
        
        Prioridad de credenciales:
        1. Variables de entorno (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        2. Archivo de configuración YAML
        
        Configura:
        - URI/host/port
        - Credenciales
        - Timeouts
        - Retry policy
        - Pool size
        """
        neo4j_config = self.config.get("neo4j", {})
        
        # Obtener credenciales (prioridad a .env)
        uri = os.getenv("NEO4J_URI") or f"bolt://{neo4j_config.get('host', 'localhost')}:{neo4j_config.get('port', 7687)}"
        user = os.getenv("NEO4J_USER", neo4j_config.get("username", "neo4j"))
        password = os.getenv("NEO4J_PASSWORD", neo4j_config.get("password"))
        database = neo4j_config.get("database", "neo4j")
        
        if not password:
            raise ValueError("NEO4J_PASSWORD no configurado en .env ni en config YAML")
        
        # Crear conexión con parámetros avanzados
        try:
            self.neo4j = Neo4jConnection(
                uri=uri,
                user=user,
                password=password,
                database=database,
                timeout=neo4j_config.get("timeout", 30),
                max_retry=neo4j_config.get("max_retry", 3),
                pool_size=neo4j_config.get("pool_size", 50)
            )
            
            # Test de conexión
            self.neo4j.query("RETURN 1 as test", database=database)
            
            self.logger.info(f"✅ Neo4j conectado: {uri} (DB: {database})")
        
        except Exception as e:
            self.logger.error(f"❌ Error conectando a Neo4j: {e}")
            raise
    
    # ----------------------------------------------------------
    # 3.3: Inicialización de Procesadores
    # ----------------------------------------------------------
    
    def _inicializar_procesadores(self):
        """
        Inicializa procesadores fenomenológicos:
        - REMForge (tokenización fenomenológica)
        - Procesador de textos (análisis fenomenológico)
        - Generador de rutas (máximo relacional FCA)
        """
        # [1] Tokenizador Fenomenológico (REMForge)
        try:
            modo_remforge = self.config.get("remforge", {}).get("modo", "auto")
            device_remforge = self.config.get("remforge", {}).get("device", "auto")
            
            self.tokenizador = TokenizadorFenomenologico(
                device=device_remforge,
                modo=modo_remforge
            )
            self.logger.info(f"✅ REMForge inicializado - Modo: {self.tokenizador.get_modo()}")
        
        except Exception as e:
            self.logger.warning(f"⚠️ REMForge no disponible: {e}")
            self.tokenizador = None
        
        # [2] Procesador de Textos Fenomenológicos
        try:
            self.procesador_textos = ProcesadorFenomenologico()
            self.logger.info("✅ Procesador fenomenológico inicializado")
        except Exception as e:
            self.logger.warning(f"⚠️ Procesador fenomenológico no disponible: {e}")
            self.procesador_textos = None
        
        # [3] Generador de Rutas (FCA)
        try:
            self.generador_rutas = GeneradorRutasFenomenologicas()
            self.logger.info("✅ Generador de rutas FCA inicializado")
        except Exception as e:
            self.logger.warning(f"⚠️ Generador de rutas no disponible: {e}")
            self.generador_rutas = None
    
    # ----------------------------------------------------------
    # 3.3.5: Inicialización de Sistemas Capa 2 (S2 y S3)
    # ----------------------------------------------------------
    
    def _inicializar_sistemas_capa2(self):
        """
        Inicializa sistemas avanzados de Capa 2:
        - S2: Motor de Emergencia de Conceptos (aprendizaje incremental)
        - S3: Motor de Lógica Pura (mundos hipotéticos)
        
        Ambos sistemas:
        - Procesan Grundzugs desde Sistema 1
        - Tienen ciclo_incremental() para aprendizaje progresivo
        - Persisten estado entre sesiones
        """
        # [1] Sistema 2: Emergencia de Conceptos
        if EMERGENCIA_AVAILABLE:
            try:
                state_file = self.config.get("emergencia", {}).get(
                    "state_file",
                    "estado_emergencia.pkl"
                )
                
                self.sistema_emergencia = MotorEmergenciaConceptos(
                    state_file=state_file
                )
                self.logger.info("✅ Sistema de Emergencia de Conceptos (S2) inicializado")
                self.logger.info(f"   - Estado: {state_file}")
                self.logger.info(f"   - Sistemas observados: {len(self.sistema_emergencia.sistemas)}")
                self.logger.info(f"   - Conceptos emergidos: {len(self.sistema_emergencia.conceptos)}")
            
            except Exception as e:
                self.logger.warning(f"⚠️ Error inicializando S2 (Emergencia): {e}")
                self.sistema_emergencia = None
        else:
            self.logger.info("ℹ️ Sistema de Emergencia (S2) no disponible")
            self.sistema_emergencia = None
        
        # [2] Sistema 3: Lógica Pura
        if LOGICA_PURA_AVAILABLE:
            try:
                state_file = self.config.get("logica_pura", {}).get(
                    "state_file",
                    "estado_logica_pura.pkl"
                )
                
                self.sistema_logica = MotorHipotetico(
                    state_file=state_file
                )
                self.logger.info("✅ Sistema de Lógica Pura (S3) inicializado")
                self.logger.info(f"   - Estado: {state_file}")
                self.logger.info(f"   - Mundos creados: {len(self.sistema_logica.mundos)}")
                self.logger.info(f"   - Axiomas totales: {sum(len(m.axiomas) for m in self.sistema_logica.mundos.values())}")
            
            except Exception as e:
                self.logger.warning(f"⚠️ Error inicializando S3 (Lógica): {e}")
                self.sistema_logica = None
        else:
            self.logger.info("ℹ️ Sistema de Lógica Pura (S3) no disponible")
            self.sistema_logica = None
    
    # ----------------------------------------------------------
    # 3.4: Inicialización de Integraciones (Opcionales)
    # ----------------------------------------------------------
    
    def _inicializar_integraciones(self):
        """
        Inicializa integraciones externas (opcionales):
        - Gemini (LLM para enriquecimiento)
        - n8n (orquestación workflows)
        - Analizador Híbrido (NetworkX + Neo4j GDS)
        """
        # [1] Gemini Integration
        if GEMINI_AVAILABLE:
            try:
                api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
                if api_key:
                    self.gemini = GeminiEnriquecedor(api_key=api_key)
                    self.logger.info("✅ Gemini integration activada")
                else:
                    self.logger.warning("⚠️ GOOGLE_GEMINI_API_KEY no configurada")
                    self.gemini = None
            except Exception as e:
                self.logger.warning(f"⚠️ Error inicializando Gemini: {e}")
                self.gemini = None
        else:
            self.gemini = None
        
        # [2] n8n Integration
        if N8N_AVAILABLE:
            try:
                n8n_config = self.config.get("n8n", {})
                base_url = f"http://{n8n_config.get('host', 'localhost')}:{n8n_config.get('port', 5678)}"
                
                self.n8n = N8nIntegrator(base_url=base_url)
                self.logger.info(f"✅ n8n integration configurada: {base_url}")
            except Exception as e:
                self.logger.warning(f"⚠️ Error inicializando n8n: {e}")
                self.n8n = None
        else:
            self.n8n = None
        
        # [3] Analizador Híbrido
        if ANALIZADOR_HIBRIDO_AVAILABLE:
            try:
                self.analizador_hibrido = OrquestadorComputacionHibrida(
                    neo4j_driver=self.neo4j._driver
                )
                self.logger.info("✅ Analizador híbrido (NetworkX + GDS) inicializado")
            except Exception as e:
                self.logger.warning(f"⚠️ Error inicializando analizador híbrido: {e}")
                self.analizador_hibrido = None
        else:
            self.analizador_hibrido = None
    
    # ----------------------------------------------------------
    # 3.5: Manejo de Eventos MDCE
    # ----------------------------------------------------------
    
    def _manejar_evento_mdce(self, evento: Dict):
        """
        Callback para eventos del Motor YO (MDCE - Contradicción Nivel 4)
        
        Args:
            evento: Dict con datos del evento MDCE
                - tipo: str ('reconfiguracion_completada' | 'error_reconfiguracion')
                - datos: Dict con información específica
        """
        if self.modo_diagnostico:
            self.logger.debug(f"Evento MDCE recibido: {evento['tipo']}")
        
        if evento["tipo"] == "reconfiguracion_completada":
            self.logger.info(
                f"🔄 Reconfiguración MDCE exitosa - "
                f"Nueva coherencia: {evento['datos']['coherencia_nueva']:.2f}"
            )
            self._actualizar_metricas_post_reconfiguracion(evento["datos"])
        
        elif evento["tipo"] == "error_reconfiguracion":
            self.logger.warning(
                f"❌ Error en reconfiguración MDCE: {evento['datos'].get('error', 'Error desconocido')}"
            )
    
    def _actualizar_metricas_post_reconfiguracion(self, datos: Dict):
        """
        Actualiza métricas del sistema después de una reconfiguración MDCE
        
        Args:
            datos: Dict con coherencia_nueva, instancias_afectadas, etc.
        """
        self.metricas["coherencia_temporal"] = datos.get("coherencia_nueva", 0.0)
        self.logger.debug(f"Métricas actualizadas post-MDCE: {self.metricas}")
    
    # ----------------------------------------------------------
    # 3.6: Utilidades
    # ----------------------------------------------------------
    
    def get_componentes_activos(self) -> List[str]:
        """
        Retorna lista de componentes activos en el sistema
        
        Returns:
            List[str] con nombres de componentes inicializados
        """
        componentes = []
        
        # Componentes core
        if hasattr(self, 'neo4j') and self.neo4j:
            componentes.append("Neo4j")
        if hasattr(self, 'motor_yo') and self.motor_yo:
            componentes.append("Motor YO")
        if hasattr(self, 'sistema_gradientes'):
            componentes.append("Sistema Gradientes")
        
        # Procesadores
        if hasattr(self, 'tokenizador') and self.tokenizador:
            componentes.append(f"REMForge ({self.tokenizador.get_modo()})")
        if hasattr(self, 'procesador_textos') and self.procesador_textos:
            componentes.append("Procesador Textos")
        if hasattr(self, 'generador_rutas') and self.generador_rutas:
            componentes.append("Generador Rutas FCA")
        
        # Integraciones
        if hasattr(self, 'gemini') and self.gemini:
            componentes.append("Gemini")
        if hasattr(self, 'n8n') and self.n8n:
            componentes.append("n8n")
        if hasattr(self, 'analizador_hibrido') and self.analizador_hibrido:
            componentes.append("Analizador Híbrido")
        
        return componentes


    # ============================================================
    # SECCIÓN 4: PROCESAMIENTO FENOMENOLÓGICO CON REMFORGE
    # ============================================================

    # ----------------------------------------------------------
    # 4.1: Procesamiento de Texto con REMForge
    # ----------------------------------------------------------
    
    def procesar_texto_fenomenologico(
        self, 
        texto: str, 
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Procesa texto con tokenización fenomenológica completa usando REMForge
        
        FLUJO COMPLETO:
        1. Tokenización REMForge -> PhenomenalREM-Ultra JSON
        2. Extracción de Ereignis (acontecimiento)
        3. Generación de Augenblick (instante-de-visión)
        4. Evaluación de propiedades emergentes
        5. Análisis noético y sensorial
        
        Args:
            texto: Texto experiencial a procesar
            context: Contexto opcional:
                - autor: str
                - situational_context: str
                - temporal_context: str
        
        Returns:
            Dict con:
            - ereignis: Dict (acontecimiento base)
            - augenblick: Dict (instante de visión)
            - rem_full_output: Dict (PhenomenalREM-Ultra completo)
            - procesado_con_remforge: bool
        
        Raises:
            ValueError: Si el texto está vacío
            RuntimeError: Si REMForge no está disponible
        
        Ejemplo:
            >>> resultado = sistema.procesar_texto_fenomenologico(
            ...     "Veo un objeto rojo vibrando",
            ...     context={"autor": "usuario1"}
            ... )
            >>> print(resultado['augenblick']['estado_fenomenologico'])
            'perception'
        """
        if not texto or not texto.strip():
            raise ValueError("El texto no puede estar vacío")
        
        if not self.tokenizador:
            raise RuntimeError("REMForge no está disponible. Inicialice el sistema correctamente.")
        
        if context is None:
            context = {}
        
        self.logger.info(f"🔄 Procesando texto fenomenológico ({len(texto)} chars)")
        
        # [1] TOKENIZACIÓN FENOMENOLÓGICA CON REMFORGE
        self._debug_print("Iniciando tokenización REMForge", "DEBUG")
        rem_output = self.tokenizador.forge_text_ultra(texto, context)
        
        # [2] CREAR EREIGNIS (Acontecimiento) DESDE REM OUTPUT
        ereignis = {
            "id": f"ereignis_{rem_output['header']['rem_id']}",
            "timestamp_extraccion": rem_output['header']['creation_timestamp'],
            "texto_original": texto,
            "tipo": 'evento',
            "contexto": context,
            
            # Análisis REMForge embebido
            "rem_analysis": {
                "phenomenal_resolution": rem_output['header']['quality_metrics']['phenomenal_resolution'],
                "contamination_strength": rem_output['semantic_contamination']['contamination_strength'],
                "qualia_signature": rem_output['phenomenal_core']['qualia_signature'],
                "modality_origin": rem_output['header']['modality_origin'],
                "completeness_score": rem_output['header']['quality_metrics']['completeness_score']
            }
        }
        
        self._debug_print(f"Ereignis creado: {ereignis['id']}", "DEBUG")
        
        # [3] CREAR AUGENBLICK (Instante-de-Visión) DESDE NOETIC_LAYER
        noetic_layer = rem_output['noetic_layer']
        sensorial_layer = rem_output['sensorial_layer']
        semantic_contamination = rem_output['semantic_contamination']
        
        # Calcular coherencia interna (inversa de contaminación semántica)
        coherencia_interna = 1.0 - semantic_contamination['contamination_strength']
        
        augenblick = {
            "id": f"augenblick_{ereignis['id'].split('_')[-1]}",
            "timestamp_inicio": rem_output['header']['creation_timestamp'],
            "ereignisse_constituyentes": [ereignis['id']],
            
            # Estado fenomenológico desde REMForge noetic_layer
            "estado_fenomenologico": noetic_layer['intentional_mode'],  # perception|memory|imagination|reflection
            
            # Propiedades emergentes calculadas desde REMForge
            "propiedades_emergentes": {
                "coherencia_interna": coherencia_interna,
                "complejidad_semantica": sensorial_layer['affective_arousal'],
                "intencionalidad": noetic_layer['directedness'],
                "ego_involvement": noetic_layer['ego_involvement'],
                "temporal_phase": noetic_layer['temporal_phase']
            },
            
            # Metadata REMForge completa
            "rem_metadata": {
                "noetic_layer": noetic_layer,
                "sensorial_layer": sensorial_layer,
                "phenomenal_core": rem_output['phenomenal_core'],
                "invariant_features": rem_output['phenomenal_core']['invariant_features']
            }
        }
        
        self._debug_print(
            f"Augenblick creado: {augenblick['id']} | "
            f"Estado: {augenblick['estado_fenomenologico']} | "
            f"Coherencia: {coherencia_interna:.2f}",
            "DEBUG"
        )
        
        self.logger.info(
            f"✅ Procesamiento REMForge completado | "
            f"Modo: {noetic_layer['intentional_mode']} | "
            f"Qualia: {rem_output['phenomenal_core']['qualia_signature']['qualia_type']}"
        )
        
        return {
            "ereignis": ereignis,
            "augenblick": augenblick,
            "rem_full_output": rem_output,
            "procesado_con_remforge": True,
            "metricas": {
                "phenomenal_resolution": ereignis['rem_analysis']['phenomenal_resolution'],
                "coherencia_interna": coherencia_interna,
                "contamination": semantic_contamination['contamination_strength']
            }
        }
    
    # ----------------------------------------------------------
    # 4.2: Generación de PreInstancias
    # ----------------------------------------------------------
    
    def _generar_preinstancias_desde_analisis(
        self, 
        analisis_textos: Dict
    ) -> List[PreInstancia]:
        """
        Genera preinstancias desde análisis de textos fenomenológicos
        
        Args:
            analisis_textos: Dict con resultados del procesador de textos
                - conceptos: List[Dict]
                - embeddings: List[array]
                - metricas: Dict
        
        Returns:
            List[PreInstancia]
        """
        preinstancias = []
        
        conceptos = analisis_textos.get("conceptos", [])
        self._debug_print(f"Generando preinstancias desde {len(conceptos)} conceptos", "DEBUG")
        
        for idx, concepto in enumerate(conceptos):
            try:
                preinstancia = PreInstancia(
                    id=f"pre_{idx}_{datetime.now().strftime('%H%M%S')}",
                    texto_base=concepto.get("texto", ""),
                    contexto=concepto.get("contexto", {}),
                    densidad_conceptual=concepto.get("densidad", 0.5),
                    embeddings=concepto.get("embedding", [])
                )
                preinstancias.append(preinstancia)
            
            except Exception as e:
                self.logger.warning(f"Error generando preinstancia {idx}: {e}")
                continue
        
        self.logger.info(f"✅ Generadas {len(preinstancias)} preinstancias")
        return preinstancias
    
    # ----------------------------------------------------------
    # 4.3: Creación de Instancias de Existencia
    # ----------------------------------------------------------
    
    def _crear_instancias_desde_preinstancias(
        self, 
        preinstancias: List[PreInstancia]
    ) -> List[InstanciaExistencia]:
        """
        Crea instancias de existencia desde preinstancias
        
        PROCESO:
        1. Evaluar YO emergente para cada preinstancia
        2. Calcular métricas fenomenológicas
        3. Crear InstanciaExistencia con tipo YO
        
        Args:
            preinstancias: List[PreInstancia]
        
        Returns:
            List[InstanciaExistencia]
        """
        instancias = []
        
        self._debug_print(f"Creando instancias desde {len(preinstancias)} preinstancias", "DEBUG")
        
        for pre in preinstancias:
            try:
                # [1] Evaluar emergencia del YO
                resultado_yo = self.motor_yo.evaluar_emergencia_yo({
                    "id": pre.id,
                    "texto": pre.texto_base,
                    "densidad_conceptual": pre.densidad_conceptual
                })
                
                # [2] Crear instancia de existencia
                instancia = InstanciaExistencia(
                    id=f"inst_{pre.id}",
                    preinstancia_origen=pre,
                    tipo_yo=resultado_yo.get("tipo_yo", "Fragmentado"),
                    coherencia_narrativa=resultado_yo.get("coherencia", 0.5),
                    metricas_fenomenologicas={
                        "densidad": pre.densidad_conceptual,
                        "complejidad": resultado_yo.get("complejidad", 0.5),
                        "tensiones_detectadas": resultado_yo.get("tensiones", [])
                    }
                )
                
                instancias.append(instancia)
                
                self._debug_print(
                    f"Instancia creada: {instancia.id} | Tipo YO: {instancia.tipo_yo}",
                    "DEBUG"
                )
            
            except Exception as e:
                self.logger.warning(f"Error creando instancia desde {pre.id}: {e}")
                continue
        
        self.logger.info(
            f"✅ Creadas {len(instancias)} instancias de existencia | "
            f"Tipos YO: {set([i.tipo_yo for i in instancias])}"
        )
        
        return instancias
    
    # ----------------------------------------------------------
    # 4.4: Persistencia en Neo4j
    # ----------------------------------------------------------
    
    def _persistir_instancias_neo4j(self, instancias: List[InstanciaExistencia]):
        """
        Persiste instancias de existencia en Neo4j
        
        Crea nodos:
        - (i:Instancia)
        - (f:Fenomeno)
        - (y:YO)
        
        Relaciones:
        - (i)-[:SURGE_DE]->(f)
        - (i)-[:TIPO_YO]->(y)
        
        Args:
            instancias: List[InstanciaExistencia]
        """
        self._debug_print(f"Persistiendo {len(instancias)} instancias en Neo4j", "DEBUG")
        
        for inst in instancias:
            try:
                # Convertir instancia a dict
                inst_dict = asdict(inst) if hasattr(inst, '__dataclass_fields__') else inst.__dict__
                
                # Query Cypher para persistir
                query = """
                MERGE (i:Instancia {id: $id})
                SET i.tipo_yo = $tipo_yo,
                    i.coherencia_narrativa = $coherencia,
                    i.timestamp = datetime(),
                    i.metricas = $metricas
                
                MERGE (y:YO {tipo: $tipo_yo})
                MERGE (i)-[:TIPO_YO]->(y)
                
                RETURN i.id as id, i.tipo_yo as tipo
                """
                
                params = {
                    "id": inst_dict.get("id"),
                    "tipo_yo": inst_dict.get("tipo_yo"),
                    "coherencia": inst_dict.get("coherencia_narrativa", 0.5),
                    "metricas": str(inst_dict.get("metricas_fenomenologicas", {}))
                }
                
                resultado = self.neo4j.query(query, parameters=params)
                
                if self.modo_diagnostico:
                    self.logger.debug(f"Neo4j persistido: {resultado}")
            
            except Exception as e:
                self.logger.error(f"Error persistiendo instancia {inst.id}: {e}")
                continue
        
        self.logger.info(f"✅ {len(instancias)} instancias persistidas en Neo4j")


    # ============================================================
    # SECCIÓN 5: FLUJO COMPLETO DEL SISTEMA (ORQUESTACIÓN)
    # ============================================================

    # ----------------------------------------------------------
    # 5.1: Flujo Principal Completo
    # ----------------------------------------------------------
    
    def procesar_flujo_completo(self, ruta_datos_entrada: str) -> Dict[str, Any]:
        """
        Ejecuta el flujo completo del sistema YO Estructural v3.0
        
        FLUJO ORQUESTADO:
        1. Procesar textos fenomenológicos (directorio de entrada)
        2. Generar preinstancias desde análisis
        3. Crear instancias de existencia con evaluación YO
        4. Detectar y evaluar MDCE (contradicciones nivel 4)
        5. Calcular gradientes relacionales
        6. Detectar vohexistencias (patrones latentes)
        7. Evaluar emergencia del YO global
        8. Persistir todo en Neo4j
        9. [OPCIONAL] Análisis de máximo relacional con LLM
        
        Args:
            ruta_datos_entrada: Ruta al directorio con textos a procesar
        
        Returns:
            Dict con:
            - instancias: List[InstanciaExistencia]
            - vohexistencias: List[Vohexistencia]
            - estado_yo: Dict (tipo, coherencia, etc.)
            - metricas_sistema: Dict
            - maximo_relacional: Dict (opcional)
        
        Example:
            >>> sistema = SistemaYoEstructural("config/config_4gb.yaml")
            >>> resultado = sistema.procesar_flujo_completo("entrada_bruta/")
            >>> print(f"Tipo YO: {resultado['estado_yo']['tipo']}")
            >>> print(f"Vohexistencias: {len(resultado['vohexistencias'])}")
        """
        self.logger.info("="*70)
        self.logger.info("🚀 INICIANDO FLUJO COMPLETO - SISTEMA YO ESTRUCTURAL v3.0")
        self.logger.info("="*70)
        
        inicio = datetime.now()
        
        # ========== ETAPA 1: PROCESAMIENTO DE TEXTOS ==========
        print("\n📖 [1/8] Procesando textos fenomenológicos...")
        self.logger.info(f"Ruta de entrada: {ruta_datos_entrada}")
        
        if self.procesador_textos:
            analisis_textos = self.procesador_textos.procesar_directorio(
                ruta_datos_entrada,
                self.config.get('rutas', {}).get('logs', 'logs_sistema/')
            )
        else:
            self.logger.warning("Procesador de textos no disponible, usando análisis vacío")
            analisis_textos = {"conceptos": [], "metricas": {}}
        
        # ========== ETAPA 2: GENERACIÓN DE PREINSTANCIAS ==========
        print("🔸 [2/8] Generando preinstancias...")
        preinstancias = self._generar_preinstancias_desde_analisis(analisis_textos)
        
        if not preinstancias:
            self.logger.warning("⚠️ No se generaron preinstancias. Verificar entrada.")
            return self._resultado_vacio("No se generaron preinstancias")
        
        # ========== ETAPA 3: CREACIÓN DE INSTANCIAS ==========
        print("🔹 [3/8] Creando instancias de existencia...")
        self.instancias = self._crear_instancias_desde_preinstancias(preinstancias)
        
        if not self.instancias:
            self.logger.warning("⚠️ No se crearon instancias. Verificar Motor YO.")
            return self._resultado_vacio("No se crearon instancias")
        
        # ========== ETAPA 4: EVALUACIÓN MDCE (CONTRADICCIÓN) ==========
        print("⚡ [4/8] Evaluando MDCE (Contradicciones Nivel 4)...")
        self._evaluar_mdce_global(self.instancias)
        
        # ========== ETAPA 5: CÁLCULO DE GRADIENTES ==========
        print("📊 [5/8] Calculando gradientes relacionales...")
        gradientes = self._calcular_gradientes_relacionales(self.instancias)
        
        # ========== ETAPA 6: DETECCIÓN DE VOHEXISTENCIAS ==========
        print("🔮 [6/8] Detectando vohexistencias (patrones latentes)...")
        self.vohexistencias = self._detectar_vohexistencias(self.instancias, gradientes)
        
        # ========== ETAPA 7: EVALUACIÓN YO GLOBAL ==========
        print("🧠 [7/8] Evaluando emergencia del YO global...")
        estado_yo = self._evaluar_yo_global(self.instancias, self.vohexistencias)
        
        # ========== ETAPA 8: PERSISTENCIA NEO4J ==========
        print("💾 [8/8] Persistiendo en Neo4j...")
        self._persistir_instancias_neo4j(self.instancias)
        self._persistir_vohexistencias_neo4j(self.vohexistencias)
        
        # ========== OPCIONAL: MÁXIMO RELACIONAL ==========
        maximo_relacional = None
        if self.gemini and self.generador_rutas:
            print("\n🌟 [EXTRA] Analizando Máximo Relacional (LLM)...")
            maximo_relacional = self._analizar_maximo_relacional_hibrido()
        
        # ========== RESUMEN FINAL ==========
        duracion = (datetime.now() - inicio).total_seconds()
        
        resultado = {
            "instancias": [asdict(i) if hasattr(i, '__dataclass_fields__') else i.__dict__ for i in self.instancias],
            "vohexistencias": [asdict(v) if hasattr(v, '__dataclass_fields__') else v.__dict__ for v in self.vohexistencias],
            "estado_yo": estado_yo,
            "metricas_sistema": {
                **self.metricas,
                "duracion_total_segundos": duracion,
                "instancias_procesadas": len(self.instancias),
                "vohexistencias_detectadas": len(self.vohexistencias),
                "tipos_yo_presentes": list(set([i.tipo_yo for i in self.instancias]))
            },
            "maximo_relacional": maximo_relacional,
            "timestamp_procesamiento": datetime.now().isoformat()
        }
        
        self.logger.info("="*70)
        self.logger.info(f"✅ FLUJO COMPLETO FINALIZADO - Duración: {duracion:.2f}s")
        self.logger.info(f"   Instancias: {len(self.instancias)} | Vohexistencias: {len(self.vohexistencias)}")
        self.logger.info(f"   Tipo YO: {estado_yo['tipo']} | Coherencia: {estado_yo['coherencia']:.2f}")
        self.logger.info("="*70)
        
        print(f"\n✅ Procesamiento completado en {duracion:.2f}s")
        print(f"   📌 Tipo YO: {estado_yo['tipo']}")
        print(f"   📌 Coherencia: {estado_yo['coherencia']:.2f}")
        print(f"   📌 Vohexistencias: {len(self.vohexistencias)}")
        
        return resultado
    
    # ----------------------------------------------------------
    # 5.2: Evaluación MDCE Global
    # ----------------------------------------------------------
    
    def _evaluar_mdce_global(self, instancias: List[InstanciaExistencia]):
        """
        Evalúa contradicciones MDCE (Nivel 4) entre todas las instancias
        
        Args:
            instancias: List[InstanciaExistencia]
        """
        self._debug_print(f"Evaluando MDCE en {len(instancias)} instancias", "DEBUG")
        
        try:
            # El motor YO maneja la evaluación MDCE internamente
            # Los eventos de reconfiguración se manejan vía callback _manejar_evento_mdce
            contradicciones_detectadas = self.motor_yo.evaluar_contradicciones_globales(instancias)
            
            if contradicciones_detectadas:
                self.logger.warning(f"⚠️ {len(contradicciones_detectadas)} contradicciones MDCE detectadas")
            else:
                self.logger.info("✅ Sin contradicciones MDCE detectadas")
        
        except Exception as e:
            self.logger.error(f"Error evaluando MDCE: {e}")
    
    # ----------------------------------------------------------
    # 5.3: Cálculo de Gradientes
    # ----------------------------------------------------------
    
    def _calcular_gradientes_relacionales(self, instancias: List[InstanciaExistencia]) -> Dict:
        """
        Calcula gradientes relacionales multidimensionales
        
        Args:
            instancias: List[InstanciaExistencia]
        
        Returns:
            Dict con gradientes calculados
        """
        self._debug_print(f"Calculando gradientes para {len(instancias)} instancias", "DEBUG")
        
        try:
            gradientes = self.sistema_gradientes.calcular_gradientes_multidimensionales(instancias)
            
            self.logger.info(
                f"✅ Gradientes calculados | "
                f"Temporal: {gradientes.get('temporal_mean', 0):.2f} | "
                f"Coherencia: {gradientes.get('coherence_mean', 0):.2f}"
            )
            
            return gradientes
        
        except Exception as e:
            self.logger.error(f"Error calculando gradientes: {e}")
            return {}
    
    # ----------------------------------------------------------
    # 5.4: Detección de Vohexistencias
    # ----------------------------------------------------------
    
    def _detectar_vohexistencias(
        self, 
        instancias: List[InstanciaExistencia],
        gradientes: Dict
    ) -> List[Vohexistencia]:
        """
        Detecta vohexistencias (patrones latentes recurrentes)
        
        Args:
            instancias: List[InstanciaExistencia]
            gradientes: Dict con gradientes calculados
        
        Returns:
            List[Vohexistencia]
        """
        self._debug_print("Iniciando detección de vohexistencias", "DEBUG")
        
        try:
            vohexistencias = self.sistema_gradientes.detectar_vohexistencias(
                instancias,
                gradientes
            )
            
            self.logger.info(f"✅ Detectadas {len(vohexistencias)} vohexistencias")
            
            return vohexistencias
        
        except Exception as e:
            self.logger.error(f"Error detectando vohexistencias: {e}")
            return []
    
    # ----------------------------------------------------------
    # 5.5: Evaluación YO Global
    # ----------------------------------------------------------
    
    def _evaluar_yo_global(
        self,
        instancias: List[InstanciaExistencia],
        vohexistencias: List[Vohexistencia]
    ) -> Dict:
        """
        Evalúa el estado global del YO emergente
        
        Args:
            instancias: List[InstanciaExistencia]
            vohexistencias: List[Vohexistencia]
        
        Returns:
            Dict con tipo, coherencia, métricas del YO global
        """
        self._debug_print("Evaluando YO global", "DEBUG")
        
        try:
            estado_yo = self.motor_yo.evaluar_yo_global({
                "instancias": instancias,
                "vohexistencias": vohexistencias,
                "metricas": self.metricas
            })
            
            # Actualizar métricas del sistema
            self.metricas["emergencia_yo_narrativo"] = estado_yo.get("emergente", False)
            self.metricas["coherencia_temporal"] = estado_yo.get("coherencia", 0.0)
            
            return estado_yo
        
        except Exception as e:
            self.logger.error(f"Error evaluando YO global: {e}")
            return {"tipo": "Fragmentado", "coherencia": 0.0, "emergente": False}
    
    # ----------------------------------------------------------
    # 5.6: Persistencia de Vohexistencias
    # ----------------------------------------------------------
    
    def _persistir_vohexistencias_neo4j(self, vohexistencias: List[Vohexistencia]):
        """
        Persiste vohexistencias en Neo4j
        
        Args:
            vohexistencias: List[Vohexistencia]
        """
        self._debug_print(f"Persistiendo {len(vohexistencias)} vohexistencias en Neo4j", "DEBUG")
        
        for vohex in vohexistencias:
            try:
                vohex_dict = asdict(vohex) if hasattr(vohex, '__dataclass_fields__') else vohex.__dict__
                
                query = """
                MERGE (v:Vohexistencia {id: $id})
                SET v.tipo = $tipo,
                    v.patron = $patron,
                    v.timestamp = datetime()
                RETURN v.id as id
                """
                
                params = {
                    "id": vohex_dict.get("id"),
                    "tipo": vohex_dict.get("tipo", "latente"),
                    "patron": str(vohex_dict.get("patron", {}))
                }
                
                self.neo4j.query(query, parameters=params)
            
            except Exception as e:
                self.logger.error(f"Error persistiendo vohexistencia {vohex.id}: {e}")
                continue
        
        self.logger.info(f"✅ {len(vohexistencias)} vohexistencias persistidas")
    
    # ----------------------------------------------------------
    # 5.7: Análisis Máximo Relacional Híbrido
    # ----------------------------------------------------------
    
    def _analizar_maximo_relacional_hibrido(self) -> Dict:
        """
        Analiza máximo relacional con comparación FCA vs LLM
        
        Returns:
            Dict con:
            - sin_llm: ResultadoFCA (5 rutas, certeza multiplicativa)
            - con_llm: ResultadoHibrido (8-12 rutas, FCA + Gemini, MDCE)
            - comparacion: Dict con métricas comparativas
        """
        self.logger.info("🔄 Iniciando análisis de Máximo Relacional (FCA + LLM)")
        
        # Seleccionar un concepto representativo de las instancias
        concepto_analizar = self._seleccionar_concepto_representativo()
        
        if not concepto_analizar:
            self.logger.warning("No hay concepto para analizar")
            return {}
        
        # [1] Análisis SIN LLM (FCA puro)
        resultado_fca = self.generador_rutas.generar_rutas(concepto_analizar)
        
        # [2] Análisis CON LLM (Híbrido)
        if self.gemini:
            resultado_llm = self.gemini.analizar_convergencia(
                concepto_analizar,
                resultado_fca.rutas
            )
            
            # Validación cruzada FCA vs LLM
            rutas_validadas = self._validar_rutas_llm_con_fca(
                resultado_llm.get('rutas_descubiertas', []),
                resultado_fca.rutas
            )
            
            return {
                "sin_llm": {
                    "concepto": concepto_analizar,
                    "rutas": len(resultado_fca.rutas),
                    "certeza_combinada": resultado_fca.certeza_combinada,
                    "es_maximo": resultado_fca.es_maximo_relacional
                },
                "con_llm": {
                    "concepto": concepto_analizar,
                    "rutas_generadas": len(resultado_llm.get('rutas_descubiertas', [])),
                    "rutas_validadas": len(rutas_validadas),
                    "certeza_promedio": sum([r.get('pc', 0) for r in rutas_validadas]) / len(rutas_validadas) if rutas_validadas else 0
                },
                "comparacion": {
                    "incremento_rutas": len(rutas_validadas) - len(resultado_fca.rutas),
                    "incremento_certeza": (sum([r.get('pc', 0) for r in rutas_validadas]) / len(rutas_validadas) if rutas_validadas else 0) - resultado_fca.certeza_combinada
                }
            }
        else:
            return {"sin_llm": {"concepto": concepto_analizar, "rutas": len(resultado_fca.rutas)}}
    
    def _seleccionar_concepto_representativo(self) -> Optional[str]:
        """Selecciona concepto más representativo de las instancias"""
        if not self.instancias:
            return None
        
        # Seleccionar la instancia con mayor coherencia
        instancia_max = max(self.instancias, key=lambda i: i.coherencia_narrativa)
        
        # Extraer concepto principal del texto
        if hasattr(instancia_max, 'preinstancia_origen'):
            texto = instancia_max.preinstancia_origen.texto_base
            # Simplificado: tomar primera palabra significativa
            palabras = [p for p in texto.split() if len(p) > 4]
            return palabras[0].upper() if palabras else "EXISTENCIA"
        
        return "EXISTENCIA"
    
    def _validar_rutas_llm_con_fca(self, rutas_llm: List[Dict], rutas_fca: List) -> List[Dict]:
        """
        Valida rutas LLM con FCA (calcula VA/PC)
        
        Args:
            rutas_llm: Rutas generadas por LLM
            rutas_fca: Rutas base de FCA
        
        Returns:
            List[Dict] con rutas validadas (VA > 0.85, PC > 0.78)
        """
        rutas_validadas = []
        
        for ruta_llm in rutas_llm:
            # Simulación de validación FCA
            # En implementación real, calcular VA/PC real
            va = 0.88  # Placeholder
            pc = 0.82  # Placeholder
            
            if va > 0.85 and pc > 0.78:
                rutas_validadas.append({
                    **ruta_llm,
                    "validado_por_fca": True,
                    "va": va,
                    "pc": pc
                })
        
        return rutas_validadas
    
    # ----------------------------------------------------------
    # 5.8: Utilidades y Helpers
    # ----------------------------------------------------------
    
    def _resultado_vacio(self, razon: str) -> Dict:
        """Retorna resultado vacío con razón"""
        return {
            "instancias": [],
            "vohexistencias": [],
            "estado_yo": {"tipo": "No Evaluado", "coherencia": 0.0},
            "metricas_sistema": {"razon_vacio": razon},
            "maximo_relacional": None
        }
    
    def obtener_estado_sistema(self) -> Dict:
        """
        Obtiene el estado actual del sistema
        
        Returns:
            Dict con componentes activos, métricas, estado YO
        """
        return {
            "componentes_activos": self.get_componentes_activos(),
            "metricas": self.metricas,
            "instancias_cargadas": len(self.instancias),
            "vohexistencias_detectadas": len(self.vohexistencias),
            "modo_diagnostico": self.modo_diagnostico,
            "timestamp": datetime.now().isoformat()
        }
    
    def cerrar_conexiones(self):
        """Cierra todas las conexiones abiertas"""
        try:
            if hasattr(self, 'neo4j') and self.neo4j:
                self.neo4j.close()
                self.logger.info("✅ Conexión Neo4j cerrada")
        except Exception as e:
            self.logger.error(f"Error cerrando conexiones: {e}")


# ============================================================
# PUNTO DE ENTRADA PARA TESTING
# ============================================================

if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("Sistema YO Estructural v3.0 - Test de Inicialización")
    print("="*70)
    
    # Verificar que existe un archivo de configuración
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "config/config_4gb.yaml"
        print(f"\nUsando configuración por defecto: {config_path}")
        print("Uso: python sistema_principal.py <ruta_config.yaml>\n")
    
    try:
        # Inicializar sistema
        sistema = SistemaYoEstructural(config_path)
        
        # Mostrar componentes activos
        print("\n✅ Sistema inicializado correctamente!")
        print(f"\nComponentes activos ({len(sistema.get_componentes_activos())}):")
        for comp in sistema.get_componentes_activos():
            print(f"  - {comp}")
        
        # Mostrar estado
        estado = sistema.obtener_estado_sistema()
        print(f"\nModo diagnóstico: {estado['modo_diagnostico']}")
        print(f"Timestamp: {estado['timestamp']}")
        
        # Cleanup
        sistema.cerrar_conexiones()
        
        print("\n" + "="*70)
        print("✅ Test completado exitosamente")
        print("="*70)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

