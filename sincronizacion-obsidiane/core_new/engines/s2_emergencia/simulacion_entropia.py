"""
Simulación de Emergencia de Entropía
=====================================

Este script demuestra cómo el concepto abstracto de ENTROPÍA emerge
a partir de observaciones puramente relacionales sobre sistemas desconocidos.

Pasos:
1. Definir sistemas con propiedades ocultas (entropía real)
2. Ejecutar experimentos de comportamiento (predicibilidad, reversibilidad, etc.)
3. Detectar patrones en los resultados
4. Emerger el concepto "Propiedad P" (Entropía)
5. Grounding con teoría termodinámica
"""

import sys
import os
import json
from datetime import datetime

# Agregar path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emergencia_concepto.motor_emergencia import MotorEmergenciaConceptos
from emergencia_concepto.sistema_observado import SistemaObservado
from emergencia_concepto.experimento import TipoExperimento


def ejecutar_simulacion():
    print("\n" + "="*60)
    print("🧪 SIMULACIÓN: EMERGENCIA DE ENTROPÍA DESDE RELACIONES")
    print("="*60)
    
    # 1. Inicializar Motor
    motor = MotorEmergenciaConceptos()
    
    # 2. Crear Sistemas "Misteriosos" (con entropía oculta)
    print("\n[1] Creando sistemas desconocidos...")
    
    sistemas_data = [
        ("sistema_A", 0.01, "Cristal Perfecto"),
        ("sistema_B", 2.5, "Gas Ordenado"),
        ("sistema_C", 4.8, "Líquido"),
        ("sistema_D", 8.2, "Gas Aleatorio"),
        ("sistema_E", 12.7, "Plasma Caótico")
    ]
    
    for nombre, entropia_real, desc in sistemas_data:
        sis = SistemaObservado(nombre)
        # Definimos la propiedad oculta que el sistema NO conoce conscientemente aún
        sis.definir_propiedad_oculta("entropia", entropia_real)
        motor.agregar_sistema(sis)
        print(f"  - {nombre} creado (Realidad oculta: {desc})")

    # 3. Ejecutar Experimentos
    print("\n[2] Ejecutando batería de experimentos comportamentales...")
    
    tipos_experimentos = [
        TipoExperimento.PREDICIBILIDAD,
        TipoExperimento.REVERSIBILIDAD,
        TipoExperimento.DIVERSIDAD,
        TipoExperimento.EVOLUCION_TEMPORAL
    ]
    
    experimentos = motor.ejecutar_bateria_experimentos(tipos_experimentos)
    
    for exp in experimentos:
        print(f"  > Experimento '{exp.tipo.value}' completado.")
        # Mostrar un ejemplo de resultado
        res_a = exp.resultados["sistema_A"]
        res_e = exp.resultados["sistema_E"]
        print(f"    - A: {res_a}")
        print(f"    - E: {res_e}")

    # 4. Detectar Patrones
    print("\n[3] Analizando correlaciones y detectando patrones...")
    patron = motor.detectar_patrones()
    print(f"  - Patrón detectado: {patron.nombre}")
    print(f"  - Certeza del patrón: {patron.certeza:.2f}")
    print(f"  - Hipótesis generada:\n    {patron.generar_hipotesis()}")

    # 5. Emerger Concepto
    print("\n[4] Emergiendo concepto abstracto...")
    concepto = motor.emergir_concepto("MEDIDA_DE_DESORDEN")
    
    print(f"  - Concepto provisional: {concepto.nombre_provisional}")
    print(f"  - Definición relacional:\n    {concepto.definicion_relacional}")
    print(f"  - Leyes descubiertas:")
    for ley in concepto.leyes_cualitativas:
        print(f"    * {ley}")
    
    print(f"  - Valores calculados para sistemas:")
    for sis, val in concepto.valores.items():
        print(f"    * {sis}: {val}")

    # 6. Grounding (Momento "Aha!")
    print("\n[5] Realizando Grounding con Teoría Termodinámica...")
    print("  ...leyendo 'termodinamica_estadistica.pdf'...")
    
    # Simulación de coincidencia con teoría
    concepto.ground_with_theory(
        nombre_teorico="ENTROPÍA (S)",
        formula="S = k_B * ln(Ω)",
        certeza_match=0.96
    )
    
    print(f"  ¡MATCH ENCONTRADO!")
    print(f"  - Nombre Real: {concepto.nombre_real}")
    print(f"  - Fórmula: {concepto.definicion_formal}")
    print(f"  - Certeza Final: {concepto.certeza:.2f}")

    # 7. Generar Reporte Final
    print("\n[6] Generando reporte final...")
    reporte = motor.generar_reporte_completo()
    
    # Guardar reporte
    output_path = os.path.join(os.path.dirname(__file__), "reporte_emergencia_entropia.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"  - Reporte guardado en: {output_path}")
    print("\n" + "="*60)
    print("SIMULACIÓN COMPLETADA CON ÉXITO")
    print("="*60)


if __name__ == "__main__":
    ejecutar_simulacion()
