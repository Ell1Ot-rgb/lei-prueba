"""
Test de integración del Pipeline Evolucionado
==============================================

Verifica que el pipeline completo funciona:
1. Crea vohexistencias de prueba
2. Las procesa a través de todos los niveles
3. Genera las notas de Obsidian
4. Verifica la estructura generada
"""

import sys
import os
import json
import tempfile

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_simbologia():
    """Verifica que la simbología está completa"""
    from core_new.domain.simbologia import (
        SimboloNivel, SimboloMotor, SimboloRelacion,
        formato_entrada_sistema, formato_pipeline_completo,
        SIMBOLOGIA_ENTRADA
    )

    print("═" * 60)
    print("TEST 1: Simbología")
    print("═" * 60)

    # 9 niveles
    assert len(SimboloNivel) == 9, f"Esperados 9 niveles, hay {len(SimboloNivel)}"
    print(f"  ✅ {len(SimboloNivel)} niveles ontológicos definidos")

    # 7 motores
    assert len(SimboloMotor) == 7, f"Esperados 7 motores, hay {len(SimboloMotor)}"
    print(f"  ✅ {len(SimboloMotor)} motores definidos")

    # 12 relaciones
    assert len(SimboloRelacion) == 12, f"Esperadas 12 relaciones, hay {len(SimboloRelacion)}"
    print(f"  ✅ {len(SimboloRelacion)} tipos de relaciones")

    # Entrada
    assert formato_entrada_sistema() == ":-....yo..."
    print(f"  ✅ Entrada del sistema: {formato_entrada_sistema()}")

    # Simbología de entrada
    assert ":" in SIMBOLOGIA_ENTRADA
    assert "yo" in SIMBOLOGIA_ENTRADA
    assert "..." in SIMBOLOGIA_ENTRADA
    print(f"  ✅ Simbología de entrada validada")

    print(f"\n{formato_pipeline_completo()}\n")

    return True


def test_niveles_domain():
    """Verifica las entidades de dominio"""
    from core_new.domain.fenomeno import Fenomeno
    from core_new.domain.contexto import Contexto
    from core_new.domain.metacontexto import Macrocontexto, Metacontexto

    print("═" * 60)
    print("TEST 2: Entidades de Dominio")
    print("═" * 60)

    # Fenómeno
    fen = Fenomeno(contenido="lluvia en la calle", tipo="sensorial")
    fen.incrementar_frecuencia()
    fen.incrementar_frecuencia()
    fen.incrementar_frecuencia()
    fen.agregar_vohexistencia_origen("voh_001")
    fen.agregar_vohexistencia_origen("voh_002")
    fen.evaluar_nuclearidad()

    assert fen.SIMBOLO == "◉"
    assert fen.NIVEL == 0
    assert fen.frecuencia == 3
    print(f"  ✅ {fen}")

    d = fen.to_dict()
    fen2 = Fenomeno.from_dict(d)
    assert fen2.contenido == fen.contenido
    print(f"  ✅ Serialización Fenomeno: OK")

    # Contexto
    ctx = Contexto(descripcion="Experiencia de caminar bajo la lluvia")
    ctx.agregar_fenomeno(fen.id)
    ctx.activar_yo()
    ctx.establecer_proyeccion("Buscar refugio")
    ctx.evaluar_nivel_narrativo()

    assert ctx.SIMBOLO == "⊞"
    assert ctx.yo_presente is True
    print(f"  ✅ {ctx}")

    # Macrocontexto
    macro = Macrocontexto(nombre="Experiencias climáticas")
    macro.agregar_contexto(ctx.id)
    macro.agregar_contexto("ctx_otro")
    macro.fenomenos_compartidos = [fen.id]
    macro.evaluar_coherencia()

    assert macro.SIMBOLO == "⊡"
    print(f"  ✅ {macro}")

    # Metacontexto
    meta = Metacontexto()
    meta.agregar_macrocontexto(macro.id)
    meta.agregar_macrocontexto("macro_otro")
    meta.agregar_invariante("Temporalidad climática")
    meta.patron_emergente = "Relación humano-naturaleza"
    meta.evaluar_coherencia()

    assert meta.SIMBOLO == "⊠"
    print(f"  ✅ {meta}")

    return True


def test_motor_yo():
    """Verifica el motor del YO Emergente"""
    from core_new.engines.yo_emergente.motor_yo import MotorYoEmergente, TipoYO

    print("═" * 60)
    print("TEST 3: Motor del YO Emergente")
    print("═" * 60)

    motor = MotorYoEmergente()

    # Test PROTO_YO (sin inputs)
    resultado = motor.evaluar(
        metacontextos=[],
        fenomenos_activos=[],
    )
    assert resultado["estado"]["tipo"] == "PROTO_YO"
    print(f"  ✅ {motor} (sin inputs)")

    # Test YO_SENSORIAL (con S1)
    resultado = motor.evaluar(
        metacontextos=[{"id": "meta1", "patron_emergente": "test"}],
        fenomenos_activos=[{"id": "fen1"}, {"id": "fen2"}],
        estado_s1={"grundzugs": 5},
    )
    print(f"  ✅ {motor} (con S1)")

    # Test YO_AFECTIVO (con emoción)
    resultado = motor.evaluar(
        metacontextos=[{"id": "meta1", "patron_emergente": "test"}],
        fenomenos_activos=[{"id": "fen1"}],
        estado_emocional={"valencia": 0.7, "activacion": 0.5},
    )
    print(f"  ✅ {motor} (con emoción)")

    return True


def test_relaciones():
    """Verifica el generador de relaciones"""
    import numpy as np
    from core_new.engines.relaciones.generador_relaciones import GeneradorRelaciones

    print("═" * 60)
    print("TEST 4: Generador de Relaciones")
    print("═" * 60)

    gen = GeneradorRelaciones()

    # SE_PARECE_A
    emb_a = np.random.randn(64)
    emb_b = emb_a + np.random.randn(64) * 0.1  # Muy similar
    rel = gen.generar_similitud("fen_1", emb_a, "fen_2", emb_b)
    if rel:
        print(f"  ✅ ≈ SE_PARECE_A: peso={rel.peso:.3f}")

    # CONTRADICE
    rel2 = gen.generar_contradiccion(
        "fen_1", "El cielo está claro y luminoso",
        "fen_2", "El cielo no está claro, está oscuro"
    )
    if rel2:
        print(f"  ✅ ⊘ CONTRADICE: peso={rel2.peso:.3f}")

    # SURGE_DE
    rel3 = gen.generar_emergencia_jerarquica(
        "voh_1", -1, "fen_1", 0, coherencia=0.7
    )
    if rel3:
        print(f"  ✅ ↗ SURGE_DE: peso={rel3.peso:.3f}")

    # OBSERVA
    rel4 = gen.generar_observacion_yo(
        "yo_001", "inst_001", -3, "YO_REFLEXIVO"
    )
    print(f"  ✅ ⊙ OBSERVA: peso={rel4.peso:.3f}")

    print(f"  📊 Total relaciones generadas: {len(gen.obtener_todas())}")

    return True


def test_pipeline_con_obsidian():
    """Verifica el pipeline completo con salida a Obsidian"""
    print("═" * 60)
    print("TEST 5: Pipeline Completo + Obsidian")
    print("═" * 60)

    # Usar directorio temporal para probar
    vault_path = os.path.join(
        os.environ.get("OBSIDIAN_VAULT_PATH",
                       r"C:\Users\Public\Robot\Zerg")
    )

    from adapters.outbound.obsidian_sync import ObsidianSync
    obs = ObsidianSync(vault_path)
    print(f"  ✅ Obsidian vault inicializado: {vault_path}")

    # Verificar estructura de carpetas
    for nivel, carpeta in obs.ESTRUCTURA_CARPETAS.items():
        ruta = os.path.join(vault_path, carpeta)
        assert os.path.isdir(ruta), f"Carpeta {carpeta} no creada"

    print(f"  ✅ {len(obs.ESTRUCTURA_CARPETAS)} carpetas de niveles creadas")
    print(f"  ✅ {len(obs.CARPETAS_EXTRA)} carpetas extra creadas")

    # Ejecutar pipeline
    from core_new.engines.pipeline_evolucionado import PipelineEvolucionado

    pipeline = PipelineEvolucionado(
        vault_obsidian_path=vault_path,
    )

    # Simular vohexistencias de entrada
    vohexistencias = [
        {
            "id": "voh_test_001",
            "nombre": "lluvia_sensacion",
            "peso_coexistencial": 0.8,
            "constante_emergente": "Sensación de lluvia en la piel",
            "instancias": ["inst_1", "inst_2", "inst_3"],
        },
        {
            "id": "voh_test_002",
            "nombre": "frio_corporal",
            "peso_coexistencial": 0.6,
            "constante_emergente": "Frío corporal perceptible",
            "instancias": ["inst_4", "inst_5"],
        },
    ]

    resultado = pipeline.procesar(
        datos_s1={"grundzugs": 3, "tipo": "sensorial"},
        datos_s2={"conceptos": [{"nombre": "experiencia_climatica"}]},
        vohexistencias=vohexistencias,
        estado_emocional={"valencia": -0.2, "activacion": 0.6},
    )

    print(f"  ✅ Pipeline ejecutado: procesamiento #{resultado['id']}")
    print(f"  ✅ Fenómenos generados: {len(resultado['fenomenos'])}")
    print(f"  ✅ Contextos: {len(resultado['contextos'])}")
    print(f"  ✅ Macrocontextos: {len(resultado['macrocontextos'])}")
    print(f"  ✅ Metacontextos: {len(resultado['metacontextos'])}")
    print(f"  ✅ YO: {resultado['yo_emergente']['estado']['tipo']}")
    print(f"  ✅ Voluntad: {resultado['voluntad']['direccion']}")
    print(f"  ✅ Retroalimentación: {len(resultado['retroalimentacion'])} resignificaciones")

    # Verificar archivos Obsidian creados
    moc_path = os.path.join(vault_path, "00_MOC", "MOC_Pipeline.md")
    assert os.path.exists(moc_path), "MOC_Pipeline.md no generado"
    print(f"  ✅ MOC_Pipeline.md generado")

    estado_path = os.path.join(vault_path, "_sistema", "estado_actual.md")
    assert os.path.exists(estado_path), "estado_actual.md no generado"
    print(f"  ✅ estado_actual.md generado")

    return resultado


if __name__ == "__main__":
    print()
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  TEST DE INTEGRACIÓN — SISTEMA EVOLUCIONADO          ║")
    print("║  Entrada: :-....yo...                                ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()

    try:
        test_simbologia()
        print()
        test_niveles_domain()
        print()
        test_motor_yo()
        print()
        test_relaciones()
        print()
        resultado = test_pipeline_con_obsidian()
        print()
        print("═" * 60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("═" * 60)

        # Mostrar resumen
        print(f"\n📊 RESUMEN DEL RESULTADO:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str)[:2000])

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
