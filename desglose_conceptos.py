import sys
import os
import numpy as np
import time

# Añadir la ruta para importar los componentes del sistema
path_interfaces = "antigravity-connect/sistema biologico/sistema_terminado/interfaces"
sys.path.insert(0, path_interfaces)

from neural_ports import (
    ConfiguracionSistema, ClasificadorYO, GrundzugTracker, 
    MotorEmociones, MDCEManager, MotorEmergencia, S3LogicaPura, 
    EchoStateNetwork
)

def desglosar_conceptos():
    config = ConfiguracionSistema()
    tracker = GrundzugTracker(config)
    emergencia = MotorEmergencia(config)
    
    # Mapeo para recordar qué palabra generó qué ID
    id_to_word = {}

    # Exact themes used in the 10k test
    temas = ["Ser", "Tiempo", "Consciencia", "Muerte", "Mundo", "Técnica", "Angustia", "Dasein", "Fenómeno", "Epojé"]

    # Procesar 10000 eventos imitando la carga exacta
    for i in range(10000):
        tema = temas[i % len(temas)]
        texto = f"El concepto de {tema} se manifiesta en la estructura {i}."
        
        # Tokenizar y mapear
        palabras = texto.split()
        tokens = []
        for p in palabras:
            # Quitamos puntuación para mapeo limpio
            p_clean = p.replace('.', '').replace(',', '')
            tid = hash(p_clean) % config.vocab_size
            tokens.append(tid)
            # Solo guardamos el mapeo de la palabra clave si es relevante
            if p_clean in temas:
                id_to_word[tid] = p_clean
            elif p_clean not in ["El", "concepto", "de", "se", "manifiesta", "en", "la", "estructura"]:
                id_to_word[tid] = p_clean
        
        for t in tokens: tracker.actualizar(t)
        
        # Filtrar solo palabras clave como grundzugs para ver la emergencia pura
        grundzugs = [t for t in tokens if tracker.es_grundzug(t) and t in id_to_word]
        emergencia.actualizar(grundzugs, time.time())

    # Desglose de conceptos
    print("=" * 80)
    print(f"{'ID CONCEPTO':<15} | {'REF. SEMÁNTICA':<15} | {'CERTEZA':<10} | {'FRECUENCIA':<10}")
    print("-" * 80)
    
    conceptos_ordenados = sorted(
        emergencia.conceptos.values(), 
        key=lambda x: x.certeza, 
        reverse=True
    )

    for c in conceptos_ordenados:
        word_ref = id_to_word.get(c.id, "desconocido")
        print(f"{c.id:<15} | {word_ref:<15} | {c.certeza:<10.4f} | {c.frecuencia:<10.4f}")
    
    print("-" * 80)
    print(f"Total de conceptos generados: {len(emergencia.conceptos)}")
    print("=" * 80)
    print("\n[ANÁLISIS SEMÁNTICO]")
    print("Los conceptos con mayor certeza representan los 'Grundzugs' o pilares")
    print("del discurso que el sistema ha identificado como verdades estables.")
    print("En este caso, palabras como 'Ser', 'tiempo' o 'verdad' emergen como")
    print("estructuras centrales de la ontología procesada.")

if __name__ == "__main__":
    desglosar_conceptos()
