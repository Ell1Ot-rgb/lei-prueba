"""
Benchmark de Rendimiento - Organismo Vivo Optimizado
====================================================

Medir rendimiento real del sistema en hardware restringido.

Métricas:
- Latencia por evento
- Throughput (eventos/segundo)
- Uso de memoria
- Tiempos de cada componente
"""

import time
import numpy as np
import sys
import os

# Importar sistema
sys.path.insert(0, os.path.dirname(__file__))
from sistema_optimizado import OrganismoVivoOptimizado


def generate_test_texts(n: int) -> list:
    """Generar textos de prueba variados."""
    templates = [
        "El ser humano reflexiona sobre su propia existencia",
        "La herramienta está disponible para su uso inmediato",
        "El objeto simplemente está presente en el mundo",
        "Pensando profundamente sobre el sentido de la vida",
        "El martillo sirve para clavar en la pared",
        "La piedra está ahí, sin propósito aparente",
        "Análisis fenomenológico de la consciencia temporal",
        "Implementación práctica del sistema cognitivo"
    ]
    
    texts = []
    for i in range(n):
        template = templates[i % len(templates)]
        texts.append(f"{template} {i}")
    
    return texts


def benchmark_latency(sistema, n_events=1000):
    """Medir latencia por evento."""
    print("=" * 70)
    print("BENCHMARK 1: Latencia por Evento")
    print("=" * 70)
    
    texts = generate_test_texts(n_events)
    
    print(f"\nProcesando {n_events} eventos...")
    latencies = []
    
    for text in texts:
        start = time.perf_counter()
        sistema.process(text)
        elapsed = time.perf_counter() - start
        latencies.append(elapsed * 1000)  # Convertir a ms
    
    latencies = np.array(latencies)
    
    print(f"\nLatencia promedio: {latencies.mean():.3f} ms")
    print(f"Latencia mediana: {np.median(latencies):.3f} ms")
    print(f"Latencia mínima: {latencies.min():.3f} ms")
    print(f"Latencia máxima: {latencies.max():.3f} ms")
    print(f"Desviación estándar: {latencies.std():.3f} ms")
    print(f"Percentil 95: {np.percentile(latencies, 95):.3f} ms")
    print(f"Percentil 99: {np.percentile(latencies, 99):.3f} ms")
    
    # Objetivo: <1 ms
    if latencies.mean() < 1.0:
        print("\n✓ OBJETIVO CUMPLIDO: Latencia promedio < 1 ms")
        return True
    else:
        print(f"\n⚠ ADVERTENCIA: Latencia promedio {latencies.mean():.3f} ms > 1 ms")
        return False


def benchmark_throughput(sistema, duration_seconds=10):
    """Medir throughput (eventos/segundo)."""
    print("\n" + "=" * 70)
    print("BENCHMARK 2: Throughput")
    print("=" * 70)
    
    print(f"\nProcesando eventos durante {duration_seconds} segundos...")
    
    texts = generate_test_texts(100)
    event_count = 0
    start_time = time.perf_counter()
    
    while time.perf_counter() - start_time < duration_seconds:
        text = texts[event_count % len(texts)]
        sistema.process(text)
        event_count += 1
    
    elapsed = time.perf_counter() - start_time
    throughput = event_count / elapsed
    
    print(f"\nEventos procesados: {event_count}")
    print(f"Tiempo transcurrido: {elapsed:.2f} s")
    print(f"Throughput: {throughput:.0f} eventos/segundo")
    
    # Objetivo: >1000 eventos/segundo
    if throughput > 1000:
        print("\n✓ OBJETIVO CUMPLIDO: Throughput > 1000 eventos/s")
        return True
    else:
        print(f"\n⚠ ADVERTENCIA: Throughput {throughput:.0f} < 1000 eventos/s")
        return False


def benchmark_memory(sistema, n_events=10000):
    """Medir uso de memoria."""
    print("\n" + "=" * 70)
    print("BENCHMARK 3: Uso de Memoria")
    print("=" * 70)
    
    # Memoria inicial
    mem_initial = sistema._get_memory_usage()
    
    print(f"\nMemoria inicial: {mem_initial:.2f} MB")
    print(f"Procesando {n_events} eventos...")
    
    texts = generate_test_texts(n_events)
    for text in texts:
        sistema.process(text)
    
    # Memoria final
    mem_final = sistema._get_memory_usage()
    mem_delta = mem_final - mem_initial
    
    print(f"\nMemoria final: {mem_final:.2f} MB")
    print(f"Incremento: {mem_delta:.2f} MB")
    print(f"Memoria por evento: {(mem_delta / n_events) * 1024:.2f} KB")
    
    # Desglose de componentes
    print("\nDesglose de memoria:")
    print(f"  - Embedder: ~0.5 MB (fijo)")
    print(f"  - Tokenizer: ~0.16 MB (fijo)")
    print(f"  - MDCE: ~0.04 MB (fijo)")
    print(f"  - Grundzug: ~0.016 MB (fijo)")
    print(f"  - Health: ~0.012 MB (fijo)")
    print(f"  - Otros: ~{mem_final - 0.738:.2f} MB (dinámico)")
    
    # Objetivo: <10 MB total
    if mem_final < 10.0:
        print("\n✓ OBJETIVO CUMPLIDO: Memoria total < 10 MB")
        return True
    else:
        print(f"\n⚠ ADVERTENCIA: Memoria total {mem_final:.2f} MB > 10 MB")
        return False


def benchmark_component_timing(sistema, n_events=1000):
    """Medir tiempo de cada componente."""
    print("\n" + "=" * 70)
    print("BENCHMARK 4: Tiempo por Componente")
    print("=" * 70)
    
    timings = {
        'tokenize': [],
        'embed': [],
        'classify': [],
        'mdce': [],
        'grundzug': [],
        'emotion': []
    }
    
    texts = generate_test_texts(n_events)
    
    print(f"\nAnalizando {n_events} eventos...")
    
    for text in texts:
        # Tokenización
        t0 = time.perf_counter()
        tokens = sistema.tokenizer.encode(text)
        timings['tokenize'].append((time.perf_counter() - t0) * 1000)
        
        # Embedding
        t0 = time.perf_counter()
        embedding = sistema.embedder.embed(tokens)
        timings['embed'].append((time.perf_counter() - t0) * 1000)
        
        # Clasificación
        t0 = time.perf_counter()
        yo_type = sistema.classifier.predict(embedding)
        timings['classify'].append((time.perf_counter() - t0) * 1000)
        
        # MDCE
        t0 = time.perf_counter()
        sistema.mdce.add_instance(yo_type)
        timings['mdce'].append((time.perf_counter() - t0) * 1000)
        
        # Grundzug
        t0 = time.perf_counter()
        for token in tokens[:10]:  # Solo primeros 10
            sistema.grundzug.update(token)
        timings['grundzug'].append((time.perf_counter() - t0) * 1000)
        
        # Emotion
        t0 = time.perf_counter()
        sistema.emotion.update(embedding)
        timings['emotion'].append((time.perf_counter() - t0) * 1000)
    
    # Promedios
    print("\nTiempo promedio por componente:")
    total_avg = 0
    for component, times in timings.items():
        avg_time = np.mean(times)
        total_avg += avg_time
        print(f"  {component:12s}: {avg_time:.4f} ms")
    
    print(f"\nTotal (calculado): {total_avg:.4f} ms")
    
    # Porcentajes
    print("\nDistribución porcentual:")
    for component, times in timings.items():
        avg_time = np.mean(times)
        pct = (avg_time / total_avg) * 100
        print(f"  {component:12s}: {pct:5.1f}%")


def run_all_benchmarks():
    """Ejecutar todos los benchmarks."""
    print("\n" + "=" * 70)
    print("SUITE DE BENCHMARKS - ORGANISMO VIVO v100 OPTIMIZADO")
    print("=" * 70)
    
    # Inicializar sistema
    print("\nInicializando sistema...")
    sistema = OrganismoVivoOptimizado()
    
    results = {}
    
    # Latencia
    try:
        results['Latency'] = benchmark_latency(sistema, n_events=1000)
    except Exception as e:
        print(f"\n✗ ERROR en benchmark latencia: {e}")
        results['Latency'] = False
    
    # Throughput
    try:
        results['Throughput'] = benchmark_throughput(sistema, duration_seconds=5)
    except Exception as e:
        print(f"\n✗ ERROR en benchmark throughput: {e}")
        results['Throughput'] = False
    
    # Memoria
    try:
        results['Memory'] = benchmark_memory(sistema, n_events=5000)
    except Exception as e:
        print(f"\n✗ ERROR en benchmark memoria: {e}")
        results['Memory'] = False
    
    # Component timing
    try:
        benchmark_component_timing(sistema, n_events=1000)
    except Exception as e:
        print(f"\n✗ ERROR en benchmark component timing: {e}")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE BENCHMARKS")
    print("=" * 70)
    
    for bench_name, passed in results.items():
        status = "✓ CUMPLIDO" if passed else "⚠ ADVERTENCIA"
        print(f"{bench_name:20s} : {status}")
    
    # Estadísticas finales del sistema
    print("\n" + "=" * 70)
    print("ESTADÍSTICAS FINALES DEL SISTEMA")
    print("=" * 70)
    stats = sistema.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        elif isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    run_all_benchmarks()
