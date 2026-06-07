import os
import sys
import logging
import json
import time
from dotenv import load_dotenv

# Cargar entorno y resolver encoding issues en Windows
load_dotenv()
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

# Logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("MAIN_ABSOLUTO")

# Importar el Pipeline Hexagonal de la v4.0
try:
    from core_new.engines.pipeline_evolucionado import PipelineEvolucionado
except ImportError as e:
    logger.error(f"Fallo al importar la nueva arquitectura: {e}")
    sys.exit(1)

def ejectutar_absoluto(datos: str):
    logger.info("="*70)
    logger.info("INICIANDO ORGANISMO VIVO v4.0 (NÚCLEO ABSOLUTO)")
    logger.info("="*70)

    # 1. Configurar paths 
    vault_path = os.getenv("VAULT_PATH", r"C:\Users\Public\Robot\Zerg")

    # 2. Inicializar Pipeline Evolucionado (El que inyecta en Obsidian)
    pipeline = PipelineEvolucionado(vault_obsidian_path=vault_path)

    # 3. Importación y Carga de Sistemas Históricos (19 Subsistemas Bio-Digitales + S1, S2, S3)
    logger.info("Encendiendo Motores Primordiales y Subsistemas Biológo-Digitales...")
    try:
        from core.orquestador_capa2 import OrquestadorCapa2
        # Usa una configuración base para arrancar Neo4j (si está disponible local o en .env)
        config_path = "config/config_4gb.yaml" 
        orquestador_bio = OrquestadorCapa2(config_path) if os.path.exists(config_path) else None
        
        # Extraer módulos cargados dentro de OrquestadorCapa2
        motor_s1 = orquestador_bio.sistema_principal.tokenizador if orquestador_bio and hasattr(orquestador_bio.sistema_principal, "tokenizador") else None
        motor_s2 = orquestador_bio.sistema_emergencia if orquestador_bio else None
        motor_s3 = orquestador_bio.sistema_logica if orquestador_bio else None
    except Exception as e:
        logger.warning(f"⚠️ No se pudo inicializar la Capa 2 completa: {e}")
        orquestador_bio = None
        motor_s1 = motor_s2 = motor_s3 = None

    # 4. Importar Wolfram Hypergraph (S4 - Mundos Posibles Computacionales)
    try:
        from core_new.engines.s4_prediccion.hypergraph_wolfram import WolframHypergraph
        wolfram = WolframHypergraph()
        logger.info("✅ Wolfram Hypergraph S4 activo")
    except Exception as e:
        logger.warning(f"⚠️ Wolfram Hypergraph no disponible: {e}")
        wolfram = None

    # 5. Inyectar motores históricos al Pipeline
    pipeline.conectar_motores_existentes(
        s1=motor_s1,
        s2=motor_s2,
        s3=motor_s3,
        s4=wolfram,
        bio=orquestador_bio,
    )
    logger.info("✅ Todos los subsistemas inyectados en la Arquitectura Hexagonal")

    # 6. Transformación del dato bruto usando TODO el sistema
    logger.info(f"Procesando bruto absoluto: '{datos[:50]}...'")
    
    # a) Si S1 (Tokenizador Fenomenológico / REMForge) existe, procesamos a través de él.
    if motor_s1 and orquestador_bio and getattr(orquestador_bio, "sistema_principal", None):
        try:
            logger.info("➜ Pasando dato crudo por REMForge (Tokenizador S1)")
            datos_s1 = orquestador_bio.sistema_principal.procesar_texto_fenomenologico(texto=datos)
            
            logger.info("➜ Pasando por Motor Lógico y Sistema de Emergencia (S2/S3)")
            evento_test = {
                'intensidad': 0.8,
                'complejidad': 0.9,
                'tipo_base': 'narrativo_sintetico',
                'origen_fisico': {'hash': 'input_console', 'energia_uj': 12000, 'ciclos': 50000}
            }
            res_bio = orquestador_bio.procesar_evento_fisico(evento_test)
            conceptos = res_bio.get("s2_resultado", {}).get("conceptos", [])
            datos_s2 = {"conceptos": conceptos}
            
            # Generar Vohexistencias basadas en la emergencia
            from niveles.vohexistencia import Vohexistencia
            vohex = [
                {"id": f"vox_{time.time()}", "nombre": c.get('nombre', 'c'), "peso_coexistencial": c.get('certeza', 0.5), "constante_emergente": c.get('nombre', 'c')}
                for c in conceptos
            ]
        except Exception as e:
            logger.error(f"Falla durante la computación profunda: {e}")
            datos_s1 = None
            datos_s2 = None
            vohex = [{"id": "vox_mock", "nombre": "fallback_absoluto", "peso_coexistencial": 0.9}]
    else:
        logger.info("⚠️ Procesando en modo FALLBACK (Motores pesados no levantaron).")
        datos_s1 = None
        datos_s2 = None
        vohex = [{"id": f"vox_{time.time()}", "nombre": datos[:20], "peso_coexistencial": 0.9}]

    # b) Pasar al Pipeline Evolucionado (Cascada hasta Obsidian)
    estado_emocional = {"valencia": 2.5, "arousal": 7.0} # PAD basal de alerta
    
    logger.info("➜ Proyectando hacia Obsidian (Cascada Hexagonal)...")
    resultado_final = pipeline.procesar(
        datos_s1=datos_s1,
        datos_s2=datos_s2,
        vohexistencias=vohex,
        estado_emocional=estado_emocional
    )

    logger.info("="*70)
    logger.info(f"✅ CICLO ABSOLUTO COMPLETADO. Nivel YO Alcanzado: {resultado_final.get('yo_emergente', {}).get('estado', {}).get('nivel', 'Desconocido')}")
    logger.info("Revisa la interfaz del vault en Obsidian para observar los resultados proyectados.")
    return resultado_final

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--texto", type=str, default="Input sensorial desde entorno. El mundo digital está despertando estructuralmente.")
    args = parser.parse_args()

    ejectutar_absoluto(args.texto)

