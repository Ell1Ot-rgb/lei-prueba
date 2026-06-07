"""
main.py — Punto de Entrada Principal del Organismo Vivo v4.0
=============================================================

Modos de ejecución:
    python main.py pipeline --input "texto de entrada"
    python main.py pipeline --file datos.json
    python main.py watcher
    python main.py server
    python main.py init
    python main.py status

Configuración:
    Usa .env para VAULT_PATH, NEO4J_URI, etc.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Asegurar que el directorio raíz del proyecto esté en el path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("OrganismoVivo")


def obtener_vault_path():
    return os.environ.get("VAULT_PATH", r"C:\Users\Public\Robot\Zerg")


def obtener_input_path():
    return os.environ.get("INPUT_PATH", str(ROOT / "input"))


# ──────────────────────────────────────────────────────────
# MODO: PIPELINE (ejecución directa)
# ──────────────────────────────────────────────────────────

def ejecutar_pipeline(datos: dict) -> dict:
    """Ejecuta el pipeline completo sobre datos de entrada."""
    from adapters.outbound.obsidian_sync import ObsidianSync

    vault_path = obtener_vault_path()
    obsidian = ObsidianSync(vault_path)

    logger.info("Pipeline iniciado")
    logger.info(f"  Vault: {vault_path}")

    texto = datos.get("texto", str(datos))

    # Importar pipeline
    try:
        from core_new.engines.pipeline_evolucionado import PipelineEvolucionado
        pipeline = PipelineEvolucionado(vault_obsidian_path=vault_path)

        # Construir vohexistencias basicas desde el texto de entrada
        # (simulando la salida de S1->S2 cuando no hay motores S1/S2 conectados)
        palabras = texto.split()
        vohexistencias = []
        for i, palabra in enumerate(palabras[:5]):  # Max 5 vohexistencias por entrada
            if len(palabra) > 3:  # Ignorar palabras muy cortas
                vohexistencias.append({
                    "id": f"vohex_{i}_{palabra[:4]}",
                    "nombre": palabra,
                    "constante_emergente": palabra,
                    "peso_coexistencial": min(1.0, 0.4 + (len(palabra) / 20.0)),
                    "instancias": [texto[:50]],
                })

        # Datos de S1 (basico desde el texto)
        datos_s1 = {
            "texto": texto,
            "formato": datos.get("formato", "texto"),
            "longitud": len(texto),
        }

        resultado = pipeline.procesar(
            datos_s1=datos_s1,
            vohexistencias=vohexistencias,
        )
        tipo_yo = resultado.get('yo_emergente', {}).get('estado', {}).get('tipo', '?')
        logger.info(f"Pipeline completado: YO={tipo_yo}")
        return resultado
    except ImportError as e:
        logger.warning(f"Pipeline completo no disponible ({e}), usando modo simplificado")
        return _pipeline_simplificado(datos, obsidian)


def _pipeline_simplificado(datos: dict, obsidian) -> dict:
    """Pipeline simplificado cuando faltan dependencias pesadas (numpy, etc.)."""
    from core_new.domain.fenomeno import Fenomeno
    from core_new.engines.yo_emergente.motor_yo import MotorYoEmergente

    texto = datos.get("texto", str(datos))

    # Crear fenómeno básico
    fen = Fenomeno(contenido=texto[:200], tipo="cognitivo")
    fen.incrementar_frecuencia()
    fen.evaluar_nuclearidad(umbral_frecuencia=1, umbral_intensidad=0.0)

    # Evaluar YO
    motor_yo = MotorYoEmergente()
    estado_yo = motor_yo.evaluar(
        metacontextos=[{"patron_emergente": texto[:50]}],
        fenomenos_activos=[fen.to_dict()],
    )

    # Sincronizar con Obsidian
    obsidian.guardar_entidad(0, fen.id, fen.to_obsidian_md())
    obsidian.guardar_entidad(4, motor_yo.id, motor_yo.to_obsidian_md())
    obsidian.generar_moc_pipeline()
    obsidian.generar_moc_niveles()
    obsidian.generar_moc_relaciones()
    obsidian.actualizar_estado({
        "tipo_yo": estado_yo.get("estado", {}).get("tipo", "PROTO_YO"),
        "fenomenos": 1,
    })
    obsidian.log_procesamiento(
        f"Pipeline simplificado: fen={fen.id}, YO={estado_yo.get('estado', {}).get('tipo', '?')}",
        tipo="ok"
    )

    return {
        "fenomeno": fen.to_dict(),
        "yo": estado_yo,
        "vault": str(obsidian.vault_path),
    }


def cmd_pipeline(args):
    """Handler del comando pipeline."""
    if args.input:
        datos = {"texto": args.input}
    elif args.file:
        ruta = Path(args.file)
        if not ruta.exists():
            print(f"Error: archivo no encontrado: {args.file}")
            sys.exit(1)
        contenido = ruta.read_text(encoding="utf-8")
        if ruta.suffix == ".json":
            datos = json.loads(contenido)
        else:
            datos = {"texto": contenido, "formato": ruta.suffix.lstrip(".")}
    else:
        print("Error: especifica --input o --file")
        sys.exit(1)

    resultado = ejecutar_pipeline(datos)
    print(json.dumps(resultado, indent=2, ensure_ascii=True, default=str))


# ──────────────────────────────────────────────────────────
# MODO: WATCHER (monitor de carpeta)
# ──────────────────────────────────────────────────────────

def cmd_watcher(args):
    """Handler del comando watcher."""
    from adapters.inbound.carpeta_watcher import CarpetaWatcher

    input_path = args.path or obtener_input_path()
    print("=" * 50)
    print("  ORGANISMO VIVO v4.0 — Modo WATCHER")
    print(f"  Carpeta: {input_path}")
    print(f"  Vault:   {obtener_vault_path()}")
    print("=" * 50)

    watcher = CarpetaWatcher(
        carpeta=input_path,
        callback=ejecutar_pipeline,
    )

    if args.procesar_existentes:
        print("[INFO] Procesando archivos existentes...")
        watcher.procesar_existentes()

    watcher.iniciar(bloquear=True)


# ──────────────────────────────────────────────────────────
# MODO: SERVER (webhook para n8n)
# ──────────────────────────────────────────────────────────

def cmd_server(args):
    """Handler del comando server."""
    from adapters.inbound.webhook_handler import WebhookHandler

    port = args.port or 5679
    print("=" * 50)
    print("  ORGANISMO VIVO v4.0 — Modo SERVER")
    print(f"  Puerto: {port}")
    print(f"  Vault:  {obtener_vault_path()}")
    print("=" * 50)

    def obtener_estado():
        from adapters.outbound.obsidian_sync import ObsidianSync
        vault = obtener_vault_path()
        return {"vault": vault, "status": "online"}

    handler = WebhookHandler(
        callback_procesar=ejecutar_pipeline,
        callback_estado=obtener_estado,
        port=port,
    )
    handler.iniciar()


# ──────────────────────────────────────────────────────────
# MODO: INIT (inicializar vault)
# ──────────────────────────────────────────────────────────

def cmd_init(args):
    """Handler del comando init."""
    vault = args.vault_path or obtener_vault_path()
    sys.argv = ["inicializar_vault.py", "--vault-path", vault]
    from inicializar_vault import main as init_main
    init_main()


# ──────────────────────────────────────────────────────────
# MODO: STATUS (verificar estado)
# ──────────────────────────────────────────────────────────

def cmd_status(args):
    """Handler del comando status."""
    vault = Path(obtener_vault_path())
    print("=" * 50)
    print("  ORGANISMO VIVO v4.0 — Estado del Sistema")
    print("=" * 50)
    print()

    # Verificar vault
    existe_vault = vault.exists()
    print(f"  Vault: {vault}")
    print(f"  Existe: {'[OK] Si' if existe_vault else '[X] No'}")

    if existe_vault:
        carpetas_sistema = [
            "01_PreInstancias", "02_Instancias", "05_Fenomenos",
            "09_YO", "10_Voluntad", "12_Logica",
        ]
        for c in carpetas_sistema:
            p = vault / c
            n = len(list(p.glob("*.md"))) if p.exists() else 0
            estado = "[OK]" if p.exists() else "[X]"
            print(f"    {estado} {c}: {n} notas")

    # Verificar .env
    print()
    env_keys = ["VAULT_PATH", "NEO4J_URI", "N8N_BASE_URL", "INPUT_PATH"]
    for key in env_keys:
        val = os.environ.get(key, "")
        estado = "[OK]" if val else "[!] no configurado"
        print(f"  {key}: {estado}")

    # Verificar dependencias
    print()
    deps = ["flask", "watchdog", "dotenv", "numpy"]
    for dep in deps:
        try:
            __import__(dep.replace("dotenv", "dotenv"))
            print(f"  dep {dep}: [OK]")
        except ImportError:
            print(f"  dep {dep}: [X] instalar con: pip install {dep}")


# ──────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Organismo Vivo v4.0 — Sistema Hexagonal Completo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modos de ejecución:
  init       Inicializa el vault de Obsidian
  pipeline   Ejecuta el pipeline sobre texto o archivo
  watcher    Monitorea carpeta por archivos nuevos
  server     Inicia servidor webhook (para n8n)
  status     Verifica estado del sistema

Ejemplos:
  python main.py init
  python main.py pipeline --input "Hoy observé un patrón recurrente"
  python main.py pipeline --file datos.json
  python main.py watcher --path ./input
  python main.py server --port 5679
  python main.py status
        """,
    )

    subparsers = parser.add_subparsers(dest="comando", help="Modo de ejecución")

    # init
    p_init = subparsers.add_parser("init", help="Inicializar vault de Obsidian")
    p_init.add_argument("--vault-path", type=str, default=None)

    # pipeline
    p_pipe = subparsers.add_parser("pipeline", help="Ejecutar pipeline")
    p_pipe.add_argument("--input", type=str, help="Texto de entrada")
    p_pipe.add_argument("--file", type=str, help="Archivo de entrada")

    # watcher
    p_watch = subparsers.add_parser("watcher", help="Monitor de carpeta")
    p_watch.add_argument("--path", type=str, default=None, help="Carpeta a monitorear")
    p_watch.add_argument(
        "--procesar-existentes", action="store_true",
        help="Procesar archivos existentes al iniciar"
    )

    # server
    p_srv = subparsers.add_parser("server", help="Servidor webhook")
    p_srv.add_argument("--port", type=int, default=5679)

    # status
    subparsers.add_parser("status", help="Verificar estado")

    args = parser.parse_args()

    if args.comando is None:
        parser.print_help()
        sys.exit(0)

    cmds = {
        "init": cmd_init,
        "pipeline": cmd_pipeline,
        "watcher": cmd_watcher,
        "server": cmd_server,
        "status": cmd_status,
    }
    cmds[args.comando](args)


if __name__ == "__main__":
    main()
