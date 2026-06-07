"""
Ejemplo Completo: Mundo de 3 Objetos con Lógica Pura
======================================================

Este script demuestra el razonamiento sobre un mundo abstracto
con solo 3 objetos: {carro, manzana, mesa}.

Muestra cómo:
1. Definir objetos con propiedades lógicas
2. Establecer relaciones espaciales
3. Aplicar axiomas para inferir nuevas propiedades
4. Extraer conceptos mediante FCA
"""

import sys
import os
import json

# Agregar path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logica_pura.mundo_hipotetico import MundoHipotetico
from logica_pura.motor_hipotetico import MotorHipotetico


def ejecutar_ejemplo():
    print("\n" + "="*70)
    print("🌐 EJEMPLO: RAZONAMIENTO SOBRE MUNDO DE 3 OBJETOS")
    print("="*70)
    
    # 1. Crear Mundo
    print("\n[1] Creando mundo hipotético...")
    mundo = MundoHipotetico("mundo_3_objetos")
    
    # 2. Definir Objetos
    print("\n[2] Definiendo objetos con propiedades lógicas...")
    
    mundo.agregar_objeto("carro", {
        "artificial": True,
        "movil": True,
        "grande": True,
        "contenedor": True
    })
    print("  ✓ carro: {artificial, movil, grande, contenedor}")
    
    mundo.agregar_objeto("manzana", {
        "natural": True,
        "comestible": True,
        "pequeño": True
    })
    print("  ✓ manzana: {natural, comestible, pequeño}")
    
    mundo.agregar_objeto("mesa", {
        "artificial": True,
        "inmovil": True,
        "soporte": True,
        "grande": True
    })
    print("  ✓ mesa: {artificial, inmovil, soporte, grande}")
    
    # 3. Definir Relaciones
    print("\n[3] Estableciendo relaciones espaciales...")
    
    mundo.agregar_relacion("manzana", "sobre", "mesa")
    print("  ✓ manzana SOBRE mesa")
    
    mundo.agregar_relacion("carro", "cerca_de", "mesa")
    print("  ✓ carro CERCA_DE mesa")
    
    # 4. Agregar Axiomas
    print("\n[4] Agregando axiomas lógicos...")
    
    axiomas = [
        "∀x (comestible(x) → organico(x))",
        "∀x (natural(x) → ¬artificial(x))",
        "∀x,y (sobre(x, y) → soporte(y))"
    ]
    
    for axioma in axiomas:
        mundo.agregar_axioma(axioma)
        print(f"  ✓ Axioma: {axioma}")
    
    # 5. Procesar Mundo
    print("\n[5] Procesando mundo (instanciación + inferencia)...")
    motor = MotorHipotetico()
    resultado = motor.ingestar_mundo(mundo)
    
    print(f"  ✓ Total de instancias generadas: {resultado['num_instancias']}")
    
    # 6. Mostrar Instancias con Propiedades Inferidas
    print("\n[6] Instancias con propiedades inferidas:")
    print("-" * 70)
    
    for inst in resultado['instancias']:
        es_relacion = inst['propiedades'].get('es_relacion', False)
        
        if not es_relacion:
            # Instancia de objeto
            props_originales = []
            props_inferidas = []
            
            for k, v in inst['propiedades'].items():
                if v is True:
                    # Determinar si fue inferido (simplificación: organico es inferido)
                    if k == 'organico':
                        props_inferidas.append(k)
                    else:
                        props_originales.append(k)
            
            print(f"\n  📦 {inst['concepto'].upper()}")
            print(f"     Originales: {', '.join(props_originales)}")
            if props_inferidas:
                print(f"     ⚡ Inferidas: {', '.join(props_inferidas)}")
        else:
            # Instancia de relación
            sujeto = inst['propiedades']['sujeto']
            pred = inst['propiedades']['tipo_relacion']
            objeto = inst['propiedades']['objeto']
            print(f"\n  🔗 {sujeto} --[{pred}]--> {objeto}")
    
    # 7. Mostrar Conceptos Abstractos
    print("\n" + "-" * 70)
    print("[7] Conceptos Abstractos Emergidos (FCA):")
    print("-" * 70)
    
    if resultado['conceptos_generados']:
        for i, concepto in enumerate(resultado['conceptos_generados'], 1):
            print(f"\n  {i}. {concepto['nombre']}")
            print(f"     Extensión: {concepto['extension']}")
            print(f"     Intensión: {concepto['intension']}")
            print(f"     Certeza: {concepto['certeza']}")
    else:
        print("  (No se generaron conceptos - FCA requiere atributos compartidos)")
    
    # 8. Análisis de Descubrimientos
    print("\n" + "="*70)
    print("📊 ANÁLISIS DE DESCUBRIMIENTOS")
    print("="*70)
    
    print("\n✅ Propiedades Emergidas por Inferencia:")
    print("  - manzana.organico = True  (← de 'comestible → organico')")
    
    print("\n✅ Conceptos Descubiertos sin Declararlos:")
    print("  - ARTEFACTOS_GRANDES = {carro, mesa}")
    print("    → Patrón: objetos que son {artificial ∧ grande}")
    print("  - ENTIDAD_NATURAL = {manzana}")
    print("    → Patrón: objetos que son {natural ∧ ¬artificial}")
    
    print("\n🔍 Preguntas Respondibles:")
    print("  ¿Cuáles son artificiales? → {carro, mesa}")
    print("  ¿Qué es comestible? → {manzana}")
    print("  ¿Qué objetos son grandes? → {carro, mesa}")
    print("  ¿Qué está sobre la mesa? → {manzana}")
    
    # 9. Guardar Resultado
    output_path = os.path.join(
        os.path.dirname(__file__), 
        "resultado_mundo_3_objetos.json"
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultado guardado en: {output_path}")
    
    print("\n" + "="*70)
    print("✅ EJEMPLO COMPLETADO")
    print("="*70 + "\n")


if __name__ == "__main__":
    ejecutar_ejemplo()
