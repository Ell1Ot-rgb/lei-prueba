import time
import sys
import os
import numpy as np

# Rutas para el contenedor
sys.path.insert(0, "/app/antigravity-connect/sistema biologico/sistema_terminado/interfaces")

from neural_ports import (
    ConfiguracionSistema, ClasificadorYO, GrundzugTracker, 
    MotorEmociones, MDCEManager, MotorEmergencia, S3LogicaPura, 
    EchoStateNetwork, Instancia
)

def run_mega_test(num_events=5000):
    print("=" * 80)
    print(f"ULTRA STRESS TEST: {num_events} EVENTOS (DOCKER MODE)")
    print("=" * 80)
    
    config = ConfiguracionSistema()
    tracker = GrundzugTracker(config)
    emociones = MotorEmociones(config)
    emergencia = MotorEmergencia(config)
    logica = S3LogicaPura(config)
    
    temas = ["Ser", "Tiempo", "Consciencia", "Muerte", "Mundo", "Técnica", "Angustia", "Dasein", "Fenómeno", "Epojé"]
    
    latencias = []
    t_start = time.perf_counter()
    
    for i in range(num_events):
        t0 = time.perf_counter()
        
        # Simular evento con mayor variabilidad
        tema = temas[i % len(temas)]
        texto = f"El concepto de {tema} se manifiesta en la estructura {i}."
        tokens = [hash(c) % config.vocab_size for c in texto.split()]
        embedding = np.random.randn(config.embed_dim).astype(np.float32) * 0.1
        
        # Procesamiento
        for t in tokens: tracker.actualizar(t)
        grundzugs = [t for t in tokens if tracker.es_grundzug(t)]
        emociones.actualizar(embedding)
        emergencia.actualizar(grundzugs, time.time())
        
        # Lógica reflexiva cada 500 eventos
        if i % 500 == 0:
            logica.procesar_conceptos(emergencia.conceptos, time.time())
            print(f"Progreso: {i}/{num_events} events ({(i/num_events)*100:.1f}%)")
            
        t1 = time.perf_counter()
        latencias.append((t1 - t0) * 1000)
        
    t_end = time.perf_counter()
    
    # Análisis final de S3
    logica.procesar_conceptos(emergencia.conceptos, time.time())

    print("\n" + "=" * 80)
    print("RESULTADOS DEL ULTRA TEST (5000)")
    print("=" * 80)
    print(f"Tiempo Total: {t_end - t_start:.2f} s")
    print(f"Latencia Media: {np.mean(latencias):.3f} ms")
    print(f"Conceptos Emergidos: {len(emergencia.conceptos)}")
    print(f"Axiomas Generados: {len(logica.axiomas)}")
    print(f"Throughput: {num_events / (t_end - t_start):.2f} ops/s")
    print("=" * 80)

if __name__ == "__main__":
    import sys
    count = 5000
    if len(sys.argv) > 1: count = int(sys.argv[1])
    run_mega_test(count)

if __name__ == "__main__":
    run_mega_test()
