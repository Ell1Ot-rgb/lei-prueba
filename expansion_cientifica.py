import time
import sys
import os
import numpy as np

# Rutas para el contenedor
sys.path.insert(0, "/app/antigravity-connect/sistema biologico/sistema_terminado/interfaces")

from neural_ports import (
    ConfiguracionSistema, GrundzugTracker, 
    MotorEmergencia, S3LogicaPura
)

def expansion_cientifica():
    print("=" * 80)
    print("EXPANSIÓN CIENTÍFICA: INYECTANDO 50 CONCEPTOS TÉCNICOS")
    print("=" * 80)
    
    config = ConfiguracionSistema()
    tracker = GrundzugTracker(config)
    emergencia = MotorEmergencia(config)
    logica = S3LogicaPura(config)
    
    # 1. Re-anclamos los 13 filosóficos para asegurar su presencia inicial
    filosoficos = ["Ser", "Tiempo", "Mundo", "Fenómeno", "Angustia", "Consciencia", "Muerte", "Técnica", "Dasein", "Epojé", "Ereignis", "Gestell", "Habitar"]
    for f in filosoficos:
        emergencia.inyectar_concepto(f, certeza=0.99)
    
    print(f"Base filosófica restaurada: {len(emergencia.conceptos)} conceptos.")

    # 2. Lista de 50 conceptos científicos/técnicos
    cientificos = [
        "Entropía", "Cuántico", "Relatividad", "Genética", "Neurona", "Agujero_Negro", "Superposición", "ADN", "Átomo", "Bit",
        "Algoritmo", "Cifrado", "Sintaxis", "Red_Neuronal", "Energía", "Materia_Oscura", "Evolución", "Célula", "Proteína", "Gravedad",
        "Termodinámica", "Fisión", "Fusión", "Capa_Ozono", "Biodiversidad", "Ecosistema", "Quarks", "Fotón", "Láser", "Fibra_Óptica",
        "Supercomputación", "Blockchain", "Ciberseguridad", "Robot", "Nanotecnología", "Hidrógeno", "Isótopo", "Teoría_Caos", "Fractal", "Big_Bang",
        "Radiación", "Magnetismo", "Electrón", "Protón", "Neutrón", "Genoma", "Clonación", "Sintético", "Interferencia", "Resonancia"
    ]

    # Inyección concentrada (Aprendizaje por ráfagas)
    print("\nIniciando inyección de ráfagas científicas...")
    for i, c_name in enumerate(cientificos):
        # Cada concepto recibe 100 ráfagas para superar el umbral de Grundzug
        tid = hash(c_name) % config.vocab_size
        for _ in range(100):
            tracker.actualizar(tid)
        
        # Inyectar en S2
        emergencia.inyectar_concepto(c_name, certeza=0.95)
        
        if (i+1) % 10 == 0:
            print(f"  > {i+1}/50 conceptos inyectados...")

    # 3. Aplicar ciclo de vida (Apoptosis)
    print("\n[FASE BIOLÓGICA] Aplicando ciclo de vida y decaimiento...")
    muertos = emergencia.aplicar_apoptosis(decay=0.95, umbral_muerte=0.2)
    
    # 4. Procesar Lógica
    logica.procesar_conceptos(emergencia.conceptos, time.time())

    # --- RESULTADOS ---
    print("\n" + "=" * 80)
    print("INVENTARIO FINAL DE LA ONTOLOGÍA")
    print("=" * 80)
    
    # Clasificar para el reporte
    finales = list(emergencia.conceptos.values())
    filo_vivos = [c for c in finales if c.nombre in filosoficos]
    cien_vivos = [c for c in finales if c.nombre in cientificos]
    
    print(f"Conceptos Totales: {len(finales)}")
    print(f"Filosóficos que sobrevivieron: {len(filo_vivos)}/13")
    print(f"Científicos consolidados: {len(cien_vivos)}/50")
    print(f"Bajas por Apoptosis: {muertos}")
    
    print("\n[MUESTRA DE CONOCIMIENTO (Top 10 Certeza)]")
    sorted_vivos = sorted(finales, key=lambda x: x.certeza, reverse=True)
    for c in sorted_vivos[:10]:
        print(f"  - {c.nombre:<15} | Certeza: {c.certeza:.4f} | Estabilidad: {c.estabilidad:.4f}")

    print("\n[REACCIÓN DEL SISTEMA]")
    if len(finales) > 60:
        print("El cerebro se ha expandido exitosamente. La ontología es ahora HÍBRIDA.")
    else:
        print("El sistema muestra una fuerte resistencia a la nueva información (Inmunidad Cognitiva).")
    print("=" * 80)

if __name__ == "__main__":
    expansion_cientifica()
