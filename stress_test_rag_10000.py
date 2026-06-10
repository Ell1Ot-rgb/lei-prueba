import requests
import threading
import time
import random
import string
import json
import sys

# Configuración
LIGHTRAG_URL = "http://localhost:8000/refinar"
MEMGRAPH_RAG_URL = "http://localhost:7688/indexar"
TOTAL_REQUESTS = 10000 # El usuario pidió 10000
BATCH_SIZE = 50 # Concurrencia
TIMEOUT = 10

# Estadísticas
results = {
    "lightrag": {"success": 0, "error": 0, "latencies": []},
    "memgraph": {"success": 0, "error": 0, "latencies": []}
}
lock = threading.Lock()

def random_text(length=50):
    return ''.join(random.choices(string.ascii_letters + string.digits + " ", k=length))

def test_lightrag(i):
    global results
    payload = {
        "texto": f"Evento de estres {i}: {random_text(100)}",
        "contexto": f"StressTest_{i % 10}",
        "nivel_refinamiento": "rapido"
    }
    t0 = time.perf_counter()
    try:
        r = requests.post(LIGHTRAG_URL, json=payload, timeout=TIMEOUT)
        latency = (time.perf_counter() - t0) * 1000
        with lock:
            if r.status_code == 200:
                results["lightrag"]["success"] += 1
            else:
                results["lightrag"]["error"] += 1
                print(f"[LightRAG Error] {r.status_code}: {r.text[:100]}")
            results["lightrag"]["latencies"].append(latency)
    except Exception as e:
        with lock:
            results["lightrag"]["error"] += 1
            print(f"[LightRAG Exception] {e}")

def test_memgraph(i):
    global results
    payload = {
        "texto": f"Fragmento de estres {i}: {random_text(200)}",
        "fuente": "stress_test",
        "metadata": {"index": i}
    }
    t0 = time.perf_counter()
    try:
        r = requests.post(MEMGRAPH_RAG_URL, json=payload, timeout=TIMEOUT)
        latency = (time.perf_counter() - t0) * 1000
        with lock:
            if r.status_code == 200:
                results["memgraph"]["success"] += 1
            else:
                results["memgraph"]["error"] += 1
                print(f"[MemGraph Error] {r.status_code}: {r.text[:100]}")
            results["memgraph"]["latencies"].append(latency)
    except Exception as e:
        with lock:
            results["memgraph"]["error"] += 1
            print(f"[MemGraph Exception] {e}")

def run_stress_test():
    print(f"🚀 Iniciando prueba de estrés: {TOTAL_REQUESTS} peticiones totales.")
    print(f"   - 5000 a LightRAG ({LIGHTRAG_URL})")
    print(f"   - 5000 a MemGraphRAG ({MEMGRAPH_RAG_URL})")
    print(f"   Concurrencia: {BATCH_SIZE}")
    
    threads = []
    t_start = time.perf_counter()
    
    for i in range(TOTAL_REQUESTS // 2):
        # LightRAG
        t1 = threading.Thread(target=test_lightrag, args=(i,))
        threads.append(t1)
        t1.start()
        
        # MemGraphRAG
        t2 = threading.Thread(target=test_memgraph, args=(i,))
        threads.append(t2)
        t2.start()
        
        # Control de concurrencia simple
        if len(threads) >= BATCH_SIZE:
            for t in threads:
                t.join()
            threads = []
            if (i + 1) % 100 == 0:
                print(f"   > Progreso: {(i + 1) * 2} / {TOTAL_REQUESTS} peticiones enviadas...")

    # Esperar a los últimos hilos
    for t in threads:
        t.join()
        
    t_end = time.perf_counter()
    total_time = t_end - t_start
    
    print("\n" + "=" * 50)
    print("RESULTADOS DE LA PRUEBA DE ESTRES")
    print("=" * 50)
    print(f"Tiempo Total: {total_time:.2f} s")
    print(f"Throughput: {TOTAL_REQUESTS / total_time:.2f} req/s")
    
    for system in ["lightrag", "memgraph"]:
        res = results[system]
        print(f"\nSISTEMA: {system.upper()}")
        print(f"  - Exitos: {res['success']}")
        print(f"  - Errores: {res['error']}")
        if res["latencies"]:
            import numpy as np
            print(f"  - Latencia Media: {np.mean(res['latencies']):.2f} ms")
            print(f"  - Latencia P95: {np.percentile(res['latencies'], 95):.2f} ms")
        else:
            print("  - Sin datos de latencia.")
            
    print("=" * 50)

if __name__ == "__main__":
    run_stress_test()
