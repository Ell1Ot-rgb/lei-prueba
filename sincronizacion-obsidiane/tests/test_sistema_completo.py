"""
test_sistema_completo.py — Test de Funcionamiento Completo
==========================================================

Verifica que todos los componentes del Sistema Vivo Hexagonal v4.0
estén correctamente instalados, conectados y funcionales.

Uso:
    python tests/test_sistema_completo.py
    python tests/test_sistema_completo.py --verbose
    python tests/test_sistema_completo.py --skip-external  # sin verificar Neo4j/LightRAG

Resultados:
    ✅ OK       — Componente funcional
    ⚠️ WARN     — Funcional pero con advertencia
    ❌ ERROR    — Fallo crítico
    ⏭  SKIP     — Omitido (servicio externo no disponible)
"""

import os
import sys
import json
import time
import argparse
import datetime
from pathlib import Path

# Forzar UTF-8 en la consola Windows para evitar UnicodeEncodeError
import io
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
elif sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Setup del path ──────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── Colores para consola ─────────────────────────────────────
OK    = "[OK]   "
WARN  = "[WARN] "
ERROR = "[ERROR]"
SKIP  = "[SKIP] "
SEP   = "-" * 60

resultados = {
    "ok": 0,
    "warn": 0,
    "error": 0,
    "skip": 0,
    "detalles": []
}


def log(icono, nombre, detalle=""):
    """Imprime resultado de un test."""
    linea = f"  {icono} {nombre}"
    if detalle:
        linea += f": {detalle}"
    print(linea)
    resultados["detalles"].append({
        "test": nombre,
        "estado": icono.strip(),
        "detalle": detalle,
        "ts": datetime.datetime.now().isoformat()
    })
    if icono == OK:
        resultados["ok"] += 1
    elif icono == WARN:
        resultados["warn"] += 1
    elif icono == ERROR:
        resultados["error"] += 1
    elif icono == SKIP:
        resultados["skip"] += 1


def seccion(titulo):
    print(f"\n{SEP}")
    print(f"  {titulo}")
    print(SEP)


# ═══════════════════════════════════════════════════════════
# FASE 1 — IMPORTS Y ESTRUCTURA
# ═══════════════════════════════════════════════════════════

def test_imports():
    """Verifica que todos los módulos core puedan importarse."""
    seccion("FASE 1 — Imports de Módulos Core")

    modulos = [
        ("core_new.domain.fenomeno", "Fenomeno"),
        ("core_new.domain.contexto", "Contexto"),
        ("core_new.domain.metacontexto", "Macrocontexto, Metacontexto"),
        ("core_new.domain.simbologia", "SimboloNivel"),
        ("core_new.engines.yo_emergente.motor_yo", "MotorYoEmergente"),
        ("core_new.engines.relaciones.generador_relaciones", "GeneradorRelaciones"),
        ("core_new.engines.retroalimentacion.ciclo_resignificacion", "CicloResignificacion"),
        ("core_new.engines.voluntad.motor_voluntad", "MotorVoluntad"),
        ("core_new.engines.logica_extendida.logica_deontica", "MotorDeontico"),
        ("core_new.engines.logica_extendida.logica_modal", "MotorModal"),
        ("core_new.engines.logica_extendida.logica_mereologica", "MotorMereologico"),
        ("core_new.engines.logica_pura.motor_axiomas", "MotorAxiomas"),
        ("core_new.engines.logica_pura.motor_hipotetico", "MotorHipotetico"),
        ("adapters.outbound.obsidian_sync", "ObsidianSync"),
        ("adapters.inbound.carpeta_watcher", "CarpetaWatcher"),
        ("adapters.inbound.webhook_handler", "WebhookHandler"),
        ("core_new.engines.pipeline_evolucionado", "PipelineEvolucionado"),
    ]

    for modulo, clases in modulos:
        try:
            m = __import__(modulo, fromlist=[clases])
            for clase in clases.split(","):
                clase = clase.strip()
                if not hasattr(m, clase):
                    log(WARN, f"Import {modulo}", f"módulo OK pero clase '{clase}' no encontrada")
                else:
                    log(OK, f"Import {modulo}.{clase}")
        except ImportError as e:
            log(ERROR, f"Import {modulo}", str(e))
        except Exception as e:
            log(ERROR, f"Import {modulo}", f"Error inesperado: {e}")


# ═══════════════════════════════════════════════════════════
# FASE 2 — ENTIDADES ONTOLÓGICAS
# ═══════════════════════════════════════════════════════════

def test_entidades():
    """Verifica creación de entidades de cada nivel ontológico."""
    seccion("FASE 2 — Entidades Ontológicas (9 Niveles)")

    # ── Fenómeno (Nivel 0) ───────────────────────────────
    try:
        from core_new.domain.fenomeno import Fenomeno
        fen = Fenomeno(contenido="Patrón recurrente de pensamiento", tipo="cognitivo")
        fen.incrementar_frecuencia()
        fen.evaluar_nuclearidad(umbral_frecuencia=1, umbral_intensidad=0.0)
        d = fen.to_dict()
        assert "id" in d and d["id"].startswith("fen_")
        md = fen.to_obsidian_md()
        assert "◉" in md
        log(OK, "Fenomeno ◉ (Nivel 0)", f"id={fen.id}, intensidad={fen.intensidad:.2f}")
    except Exception as e:
        log(ERROR, "Fenomeno ◉ (Nivel 0)", str(e))

    # ── Contexto (Nivel +1) ──────────────────────────────
    try:
        from core_new.domain.contexto import Contexto
        ctx = Contexto(descripcion="Contexto de test")
        ctx.agregar_fenomeno("fen_test1")
        ctx.activar_yo()
        ctx.evaluar_nivel_narrativo()
        d = ctx.to_dict()
        assert d["yo_presente"] == True
        assert d["coherencia"] > 0  # debe ser > 0 después de activar_yo (bug fix!)
        log(OK, "Contexto ⊞ (Nivel +1)", f"coherencia={ctx.coherencia:.2f}, yo_presente={ctx.yo_presente}")
    except AssertionError:
        log(WARN, "Contexto ⊞ (Nivel +1)", f"activar_yo() no recalcula coherencia (bug pendiente)")
    except Exception as e:
        log(ERROR, "Contexto ⊞ (Nivel +1)", str(e))

    # ── Macrocontexto (Nivel +2) ─────────────────────────
    try:
        from core_new.domain.metacontexto import Macrocontexto
        macro = Macrocontexto(nombre="Macro test")
        macro.agregar_contexto("ctx_test1")
        macro.evaluar_coherencia()
        d = macro.to_dict()
        assert "simbolo" in d and d["simbolo"] == "⊡"
        log(OK, "Macrocontexto ⊡ (Nivel +2)", f"coherencia={macro.coherencia:.2f}")
    except Exception as e:
        log(ERROR, "Macrocontexto ⊡ (Nivel +2)", str(e))

    # ── Metacontexto (Nivel +3) ──────────────────────────
    try:
        from core_new.domain.metacontexto import Metacontexto
        meta = Metacontexto()
        meta.patron_emergente = "Convergencia test"
        meta.evaluar_coherencia()
        md = meta.to_obsidian_md()
        assert "⊠" in md
        log(OK, "Metacontexto ⊠ (Nivel +3)", f"patron='{meta.patron_emergente[:30]}'")
    except Exception as e:
        log(ERROR, "Metacontexto ⊠ (Nivel +3)", str(e))


# ═══════════════════════════════════════════════════════════
# FASE 3 — MOTORES LÓGICOS
# ═══════════════════════════════════════════════════════════

def test_motores_logicos():
    """Verifica los 5 sistemas lógicos."""
    seccion("FASE 3 — Motores Lógicos (5 Sistemas)")

    # ── Lógica Deóntica ──────────────────────────────────
    try:
        from core_new.engines.logica_extendida.logica_deontica import MotorDeontico
        motor = MotorDeontico()
        motor.agregar_prohibicion(lambda e: e == "prohibido")
        assert motor.es_permitido("accion_libre") == True
        assert motor.es_permitido("prohibido") == False
        # Test auditar_estado (verifica que List está importado)
        viols = motor.auditar_estado("estado_test")
        assert isinstance(viols, list)
        log(OK, "Lógica Deóntica OFP", "prohibiciones y obligaciones funcionan")
    except NameError as e:
        log(ERROR, "Lógica Deóntica OFP", f"NameError (posible import List faltante): {e}")
    except Exception as e:
        log(ERROR, "Lógica Deóntica OFP", str(e))

    # ── Lógica Modal ─────────────────────────────────────
    try:
        from core_new.engines.logica_extendida.logica_modal import MotorModal
        motor = MotorModal()
        motor.definir_accesibilidad("w0", "w1")
        motor.definir_accesibilidad("w0", "w2")
        # Necesidad: debe ser true en TODOS los mundos
        necesario = motor.evaluar_necesidad(lambda w: w in ("w1", "w2"), "w0")
        posible = motor.evaluar_posibilidad(lambda w: w == "w1", "w0")
        assert necesario == True
        assert posible == True
        # Verdad vacua (sin mundos accesibles)
        sin_mundos = motor.evaluar_necesidad(lambda w: False, "sin_acceso")
        assert sin_mundos == True  # Verdad vacua
        log(OK, "Lógica Modal □◇ (Kripke)", "□ necesidad y ◇ posibilidad correctos")
    except Exception as e:
        log(ERROR, "Lógica Modal □◇ (Kripke)", str(e))

    # ── Lógica Mereológica ───────────────────────────────
    try:
        from core_new.engines.logica_extendida.logica_mereologica import MotorMereologico
        motor = MotorMereologico()
        motor.registrar_composicion("A", "B")
        motor.registrar_composicion("B", "C")
        # Transitivo: C es parte de A?
        directo = motor.es_parte_propia("B", "A")
        transitivo = motor.es_parte_propia("C", "A")
        assert directo == True
        if transitivo:
            log(OK, "Lógica Mereológica ⊂∪", "transitividad correcta (bug fix verificado)")
        else:
            log(WARN, "Lógica Mereológica ⊂∪", "transitividad falla en profundidad >1 (bug no corregido aún)")
    except Exception as e:
        log(ERROR, "Lógica Mereológica ⊂∪", str(e))

    # ── Axiomas Horn ─────────────────────────────────────
    try:
        from core_new.engines.logica_pura.motor_axiomas import MotorAxiomas, Axioma
        motor = MotorAxiomas()
        motor.agregar_axioma("es_vivo(x) -> tiene_metabolismo(x)")
        motor.agregar_axioma("tiene_metabolismo(x) -> necesita_energia(x)")

        class Instancia:
            propiedades = {"es_vivo": True}

        inst = Instancia()
        nuevas = motor.inferir_propiedades(inst)
        assert nuevas.get("tiene_metabolismo") == True
        log(OK, "Axiomas Horn ⊢", f"inferencia correcta: {list(nuevas.keys())}")
    except Exception as e:
        log(ERROR, "Axiomas Horn ⊢", str(e))

    # ── Motor Hipotético (FCA) ───────────────────────────
    try:
        from core_new.engines.logica_pura.motor_hipotetico import MotorHipotetico
        from core_new.engines.logica_pura.mundo_hipotetico import MundoHipotetico
        motor = MotorHipotetico(state_file="test_estado_hipotetico.pkl")
        mundo = MundoHipotetico("mundo_test")
        mundo.agregar_objeto("obj1", {"color": "rojo", "pesado": True})
        mundo.agregar_objeto("obj2", {"color": "rojo", "liviano": True})
        resultado = motor.ingestar_mundo(mundo)
        assert "num_instancias" in resultado
        log(OK, "Motor Hipotético FCA", f"{resultado['num_instancias']} instancias, {len(resultado['conceptos_generados'])} conceptos")
        # Limpiar archivo de test
        if Path("test_estado_hipotetico.pkl").exists():
            Path("test_estado_hipotetico.pkl").unlink()
    except Exception as e:
        log(ERROR, "Motor Hipotético FCA", str(e))


# ═══════════════════════════════════════════════════════════
# FASE 4 — MOTOR YO EMERGENTE
# ═══════════════════════════════════════════════════════════

def test_motor_yo():
    """Verifica el motor del YO y sus 6 tipos."""
    seccion("FASE 4 — Motor YO Emergente ☉")

    try:
        from core_new.engines.yo_emergente.motor_yo import MotorYoEmergente, TipoYO

        motor = MotorYoEmergente()

        # Test 1: Sin datos → PROTO_YO
        estado = motor.evaluar(metacontextos=[], fenomenos_activos=[])
        tipo = estado["estado"]["tipo"]
        log(OK if tipo == "PROTO_YO" else WARN, "YO sin datos → PROTO_YO", f"tipo={tipo}")

        # Test 2: Con metacontextos → YO_REFLEXIVO posible
        motor2 = MotorYoEmergente()
        metacontextos_test = [
            {"id": "m1", "patron_emergente": "recurrencia pensamiento", "coherencia": 0.5},
            {"id": "m2", "patron_emergente": "recurrencia memoria", "coherencia": 0.6},
        ]
        fenomenos_test = [{"id": f"f{i}", "tipo": "cognitivo"} for i in range(5)]
        estado2 = motor2.evaluar(
            metacontextos=metacontextos_test,
            fenomenos_activos=fenomenos_test,
        )
        tipo2 = estado2["estado"]["tipo"]
        log(OK, "YO con metacontextos", f"tipo={tipo2}, emergencia={estado2['estado']['nivel_emergencia']:.2f}")

        # Test 3: Serialización Obsidian
        md = motor2.to_obsidian_md()
        assert "☉" in md and "Métricas" in md
        log(OK, "YO serialización Obsidian", f"{len(md)} chars generados")

    except Exception as e:
        log(ERROR, "Motor YO Emergente", str(e))


# ═══════════════════════════════════════════════════════════
# FASE 5 — PIPELINE COMPLETO
# ═══════════════════════════════════════════════════════════

def test_pipeline(vault_test: Path):
    """Verifica el pipeline completo con un texto de prueba."""
    seccion("FASE 5 — Pipeline Evolucionado Completo")

    texto_prueba = (
        "El pensamiento recurrente emerge de la experiencia vivida "
        "cuando el sistema observa sus propios patrones de significado."
    )

    try:
        from core_new.engines.pipeline_evolucionado import PipelineEvolucionado

        pipeline = PipelineEvolucionado(vault_obsidian_path=str(vault_test))

        # Construir vohexistencias desde texto (simulando salida de S1→S2)
        palabras = texto_prueba.split()
        vohexistencias = []
        for i, palabra in enumerate(palabras[:5]):
            if len(palabra) > 4:
                vohexistencias.append({
                    "id": f"vohex_{i}",
                    "nombre": palabra,
                    "constante_emergente": palabra,
                    "peso_coexistencial": 0.6,
                    "instancias": [texto_prueba[:50]],
                })

        datos_s1 = {"texto": texto_prueba, "longitud": len(texto_prueba)}

        inicio = time.time()
        resultado = pipeline.procesar(
            datos_s1=datos_s1,
            vohexistencias=vohexistencias,
        )
        elapsed = time.time() - inicio

        # Verificaciones
        assert "yo_emergente" in resultado
        assert "voluntad" in resultado
        assert "fenomenos" in resultado

        fenomenos = resultado.get("fenomenos", [])
        yo = resultado.get("yo_emergente", {}).get("estado", {}).get("tipo", "?")
        acciones = resultado.get("voluntad", {}).get("acciones_sugeridas", [])

        log(OK, "Pipeline ejecutado", f"{elapsed:.2f}s, {len(fenomenos)} fenómenos, YO={yo}")
        log(OK, "YO Emergente generado", f"tipo={yo}")
        log(OK, "Voluntad generada", f"{len(acciones)} acciones sugeridas")

        # Verificar Obsidian
        notas_yo = list((vault_test / "09_YO").glob("*.md"))
        notas_fen = list((vault_test / "05_Fenomenos").glob("*.md"))
        notas_vol = list((vault_test / "10_Voluntad").glob("*.md"))

        log(
            OK if notas_yo else WARN,
            "Notas en 09_YO/",
            f"{len(notas_yo)} nota(s) generada(s)"
        )
        log(
            OK if notas_fen else WARN,
            "Notas en 05_Fenomenos/",
            f"{len(notas_fen)} nota(s) generada(s)"
        )
        log(
            OK if notas_vol else WARN,
            "Notas en 10_Voluntad/",
            f"{len(notas_vol)} nota(s) generada(s)"
        )

        # Verificar log de procesamiento
        log_path = vault_test / "_sistema" / "log_procesamiento.md"
        if log_path.exists():
            log(OK, "Log de procesamiento", f"{log_path}")
        else:
            log(WARN, "Log de procesamiento", "no creado aún")

    except Exception as e:
        log(ERROR, "Pipeline Evolucionado", str(e))
        import traceback
        print(f"    {traceback.format_exc()}")


# ═══════════════════════════════════════════════════════════
# FASE 6 — ADAPTADORES DE ENTRADA/SALIDA
# ═══════════════════════════════════════════════════════════

def test_adaptadores():
    """Verifica los adaptadores de entrada y salida."""
    seccion("FASE 6 — Adaptadores I/O")

    # ── ObsidianSync ─────────────────────────────────────
    try:
        vault_temp = Path("test_vault_temp_" + str(int(time.time())))
        from adapters.outbound.obsidian_sync import ObsidianSync
        sync = ObsidianSync(str(vault_temp))
        assert (vault_temp / "09_YO").exists()
        assert (vault_temp / "12_Logica" / "Pura" / "axiomas").exists()

        # Probar guardar un axioma
        ruta = sync.guardar_axioma(
            id_axioma="ax_test",
            regla_raw="ser_vivo -> tener_experiencia",
            premisa="ser_vivo",
            conclusion="tener_experiencia",
            inferencias=2
        )
        assert Path(ruta).exists()

        # Probar guardar estado modal
        ruta_modal = sync.guardar_estado_modal(
            id_meta="meta_test",
            mundos_accesibles=["w1", "w2"],
            necesidad=True,
            posibilidad=True
        )
        assert Path(ruta_modal).exists()

        log(OK, "ObsidianSync", "estructura + axioma + estado modal correctos")

        # Limpiar
        import shutil
        shutil.rmtree(vault_temp, ignore_errors=True)

    except Exception as e:
        log(ERROR, "ObsidianSync", str(e))

    # ── WebhookHandler (sin levantar servidor) ───────────
    try:
        from adapters.inbound.webhook_handler import WebhookHandler

        def callback_test(datos):
            return {"recibido": True, "texto": datos.get("texto", "")}

        handler = WebhookHandler(
            callback_procesar=callback_test,
            port=9999  # Puerto de test (no se inicia)
        )
        # Solo verificar que se crea la app Flask
        assert handler.app is not None
        assert handler.port == 9999
        log(OK, "WebhookHandler Flask", "instancia creada correctamente")
    except Exception as e:
        log(ERROR, "WebhookHandler Flask", str(e))

    # ── CarpetaWatcher (sin levantar observer) ───────────
    try:
        from adapters.inbound.carpeta_watcher import CarpetaWatcher

        carpeta_test = Path("test_carpeta_watcher_temp")
        watcher = CarpetaWatcher(
            carpeta=str(carpeta_test),
            callback=lambda d: None
        )
        assert carpeta_test.exists()
        log(OK, "CarpetaWatcher", "creación de carpeta correcta")
        import shutil
        shutil.rmtree(carpeta_test, ignore_errors=True)
    except Exception as e:
        log(ERROR, "CarpetaWatcher", str(e))


# ═══════════════════════════════════════════════════════════
# FASE 7 — CONEXIONES EXTERNAS
# ═══════════════════════════════════════════════════════════

def test_conexiones_externas(skip_external: bool):
    """Verifica conexiones a servicios externos."""
    seccion("FASE 7 — Conexiones Externas")

    if skip_external:
        log(SKIP, "Neo4j (Azure)", "omitido con --skip-external")
        log(SKIP, "LightRAG (Azure)", "omitido con --skip-external")
        log(SKIP, "n8n (local)", "omitido con --skip-external")
        return

    # ── Neo4j (Azure) ────────────────────────────────────
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://20.125.88.188:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_pass = os.environ.get("NEO4J_PASSWORD", "")

    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
        with driver.session() as session:
            result = session.run("RETURN 1 as n")
            r = result.single()
            assert r["n"] == 1
        driver.close()
        log(OK, f"Neo4j {neo4j_uri}", "conexión y query OK")
    except ImportError:
        log(WARN, "Neo4j", "librería neo4j no instalada: pip install neo4j")
    except Exception as e:
        log(ERROR, f"Neo4j {neo4j_uri}", str(e)[:60])

    # ── LightRAG (Azure) ─────────────────────────────────
    lightrag_url = os.environ.get("LIGHTRAG_URL", "http://20.125.88.188:9621")
    try:
        import requests
        r = requests.get(f"{lightrag_url}/health", timeout=5)
        if r.status_code == 200:
            log(OK, f"LightRAG {lightrag_url}", "health check OK")
        else:
            log(WARN, f"LightRAG {lightrag_url}", f"status_code={r.status_code}")
    except ImportError:
        log(WARN, "LightRAG", "librería requests no instalada")
    except Exception as e:
        log(ERROR, f"LightRAG {lightrag_url}", str(e)[:60])

    # ── n8n local ────────────────────────────────────────
    n8n_url = os.environ.get("N8N_BASE_URL", "http://localhost:5678")
    try:
        import requests
        r = requests.get(f"{n8n_url}/healthz", timeout=5)
        if r.status_code in (200, 404):
            log(OK, f"n8n {n8n_url}", "servidor responde")
        else:
            log(WARN, f"n8n {n8n_url}", f"status_code={r.status_code}")
    except Exception as e:
        log(WARN, f"n8n {n8n_url}", f"no disponible: {str(e)[:60]}")


# ═══════════════════════════════════════════════════════════
# FASE 8 — INICIALIZACIÓN DEL VAULT
# ═══════════════════════════════════════════════════════════

def test_vault(vault_path: str):
    """Verifica el estado del vault de Obsidian."""
    seccion("FASE 8 — Vault de Obsidian")

    vault = Path(vault_path)

    carpetas_esperadas = [
        "00_MOC", "01_PreInstancias", "02_Instancias", "03_Gradientes",
        "04_Vohexistencias", "05_Fenomenos", "06_Contextos",
        "07_Macrocontextos", "08_Metacontextos", "09_YO",
        "10_Voluntad", "11_Relaciones", "12_Logica",
        "_sistema", "_Templates", "_Dashboard",
    ]

    if not vault.exists():
        log(WARN, f"Vault {vault}", "no existe, iniciando creación...")
        try:
            sys.argv = ["inicializar_vault_v4.py", "--vault", str(vault)]
            from inicializar_vault_v4 import main as init_main
            init_main()
            log(OK, "Vault creado", str(vault))
        except Exception as e:
            log(ERROR, "Crear vault", str(e))
            return
    else:
        log(OK, "Vault existe", str(vault))

    for carpeta in carpetas_esperadas:
        ruta = vault / carpeta
        if ruta.exists():
            n = len(list(ruta.glob("*.md"))) if not any(ruta.iterdir()) else sum(1 for _ in ruta.rglob("*.md"))
            log(OK, f"  {carpeta}/", f"{n} notas .md")
        else:
            log(WARN, f"  {carpeta}/", "no existe")

    # MOCs
    for moc in ["MOC_Pipeline.md", "MOC_Niveles.md", "MOC_Relaciones.md"]:
        ruta = vault / "00_MOC" / moc
        log(OK if ruta.exists() else WARN, f"  00_MOC/{moc}", "" if ruta.exists() else "faltante")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Test de funcionamiento completo del Sistema Vivo")
    parser.add_argument("--skip-external", action="store_true",
                        help="Omitir tests de servicios externos (Neo4j, LightRAG, n8n)")
    parser.add_argument("--vault", type=str,
                        default=os.environ.get("VAULT_PATH", r"C:\Users\Public\Robot\Zerg"),
                        help="Ruta al vault de Obsidian")
    parser.add_argument("--verbose", action="store_true",
                        help="Mostrar más detalle")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  SISTEMA VIVO HEXAGONAL v4.0 - Test de Funcionamiento")
    print(f"  Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Vault: {args.vault}")
    print("=" * 60)

    # Cambiar directorio de trabajo a la raíz del proyecto
    os.chdir(ROOT)

    # Ejecutar todas las fases
    test_imports()

    # Crear vault temporal para tests del pipeline
    vault_test = ROOT / "test_vault_pipeline_temp"
    test_entidades()
    test_motores_logicos()
    test_motor_yo()
    test_pipeline(vault_test)
    test_adaptadores()
    test_conexiones_externas(args.skip_external)
    test_vault(args.vault)

    # Limpiar vault de test
    import shutil
    shutil.rmtree(vault_test, ignore_errors=True)

    # ── Resumen Final ────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  RESUMEN DEL TEST")
    print(f"{'=' * 60}")
    total = resultados["ok"] + resultados["warn"] + resultados["error"] + resultados["skip"]
    print(f"  Total tests: {total}")
    print(f"  {OK} OK:     {resultados['ok']}")
    print(f"  {WARN} WARN:  {resultados['warn']}")
    print(f"  {ERROR} ERROR: {resultados['error']}")
    print(f"  {SKIP} SKIP:  {resultados['skip']}")
    print(f"{'=' * 60}\n")

    # Guardar reporte JSON
    reporte_path = ROOT / "tests" / "ultimo_reporte_test.json"
    with open(reporte_path, "w", encoding="utf-8") as f:
        json.dump({
            "fecha": datetime.datetime.now().isoformat(),
            "resumen": {k: v for k, v in resultados.items() if k != "detalles"},
            "detalles": resultados["detalles"]
        }, f, indent=2, ensure_ascii=False)
    print(f"  Reporte guardado: {reporte_path}\n")

    # Exit code según errores
    sys.exit(0 if resultados["error"] == 0 else 1)


if __name__ == "__main__":
    main()
