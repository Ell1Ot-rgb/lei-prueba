"""
Tests de Validación Matemática
================================

Verificar propiedades teóricas del sistema optimizado:
1. Preservación de distancias (Johnson-Lindenstrauss)
2. Convergencia de SGD
3. Error de Count-Min Sketch
"""

import numpy as np
from scipy.spatial.distance import pdist
from collections import defaultdict
import sys
import os

# Importar componentes
sys.path.insert(0, os.path.dirname(__file__))
from components import ClassifierYO, GrundzugTracker


def test_jl_preservation(original_dim=768, reduced_dim=64, n_points=1000):
    """
    Test 1: Preservación de Distancias (Johnson-Lindenstrauss)
    
    Verificar que la proyección de dimensión 768 → 64 preserva distancias
    con error relativo < 10% (ε=0.1)
    """
    print("=" * 70)
    print("TEST 1: Preservación de Distancias (Johnson-Lindenstrauss)")
    print("=" * 70)
    
    # Puntos aleatorios en dimensión original
    np.random.seed(42)
    X = np.random.randn(n_points, original_dim)
    
    # Matriz de proyección (Achlioptas sparse)
    R = np.random.choice([-1, 0, 0, 0, 0, 1], 
                        size=(original_dim, reduced_dim)) * np.sqrt(3)
    
    # Proyectar
    X_proj = X @ R / np.sqrt(reduced_dim)
    
    # Calcular distancias originales y proyectadas
    print(f"\nCalculando distancias entre {n_points} puntos...")
    dist_orig = pdist(X)
    dist_proj = pdist(X_proj)
    
    # Verificar error relativo
    error = np.abs(dist_proj - dist_orig) / (dist_orig + 1e-10)
    
    print(f"\nDimensión original: {original_dim}")
    print(f"Dimensión reducida: {reduced_dim}")
    print(f"Reducción: {(1 - reduced_dim/original_dim)*100:.1f}%")
    print(f"\nError relativo promedio: {error.mean():.4f}")
    print(f"Error relativo máximo: {error.max():.4f}")
    print(f"Error relativo mediana: {np.median(error):.4f}")
    print(f"\nCumple JL (ε=0.1): {(error < 0.1).mean()*100:.1f}% de pares")
    print(f"Cumple JL (ε=0.2): {(error < 0.2).mean()*100:.1f}% de pares")
    
    if error.mean() < 0.15:
        print("\n✓ APROBADO: Preservación de distancias aceptable")
        return True
    else:
        print("\n✗ FALLIDO: Error muy alto")
        return False


def test_sgd_convergence(n_samples=10000):
    """
    Test 2: Convergencia de SGD
    
    Verificar que el clasificador converge con datos sintéticos.
    """
    print("\n" + "=" * 70)
    print("TEST 2: Convergencia de SGD (Clasificador YO)")
    print("=" * 70)
    
    np.random.seed(42)
    classifier = ClassifierYO(embed_dim=64)
    
    # Datos sintéticos: 3 clusters gaussianos para las 3 clases
    centers = [
        np.array([1.0, 0.0] + [0.0] * 62),   # Dasein
        np.array([0.0, 1.0] + [0.0] * 62),   # Vorhandene
        np.array([-1.0, -1.0] + [0.0] * 62)  # Zuhandene
    ]
    
    print("\nGenerando datos sintéticos...")
    X = []
    y = []
    for label in range(3):
        samples = np.random.randn(n_samples // 3, 64) * 0.3 + centers[label]
        X.extend(samples)
        y.extend([label] * (n_samples // 3))
    
    X = np.array(X)
    y = np.array(y)
    
    # Shuffle
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    # Entrenamiento
    print(f"Entrenando con {n_samples} muestras...")
    losses = []
    accuracies = []
    
    for i in range(n_samples):
        xi, yi = X[i], y[i]
        
        # Calcular loss antes del update
        probs = classifier.predict_proba(xi)
        loss = -np.log(probs[yi] + 1e-10)
        losses.append(loss)
        
        # Update
        classifier.update(xi, yi)
        
        # Calcular accuracy cada 1000 muestras
        if (i + 1) % 1000 == 0:
            predictions = [classifier.predict(X[j]) for j in range(min(1000, len(X)))]
            accuracy = np.mean([predictions[j] == y[j] for j in range(len(predictions))])
            accuracies.append(accuracy)
    
    # Verificar convergencia
    window = 100
    loss_early = np.mean(losses[:window])
    loss_late = np.mean(losses[-window:])
    acc_final = accuracies[-1] if accuracies else 0
    
    print(f"\nLoss inicial (primeras {window}): {loss_early:.4f}")
    print(f"Loss final (últimas {window}): {loss_late:.4f}")
    print(f"Reducción de loss: {(1 - loss_late/loss_early)*100:.1f}%")
    print(f"\nAccuracy final: {acc_final*100:.1f}%")
    
    if loss_late < loss_early and acc_final > 0.7:
        print("\n✓ APROBADO: Convergencia verificada")
        return True
    else:
        print("\n✗ FALLIDO: No convergió adecuadamente")
        return False


def test_cm_sketch_error(n_events=100000, n_features=10000):
    """
    Test 3: Error de Count-Min Sketch
    
    Verificar que el error del sketch está dentro de las cotas teóricas.
    Cota teórica: ε = e/width = 2.718/2048 ≈ 0.00133
    """
    print("\n" + "=" * 70)
    print("TEST 3: Error de Count-Min Sketch")
    print("=" * 70)
    
    np.random.seed(42)
    tracker = GrundzugTracker(width=2048, depth=4)
    true_counts = defaultdict(int)
    
    # Generar eventos con distribución Zipf (más realista)
    print(f"\nGenerando {n_events} eventos con distribución Zipf...")
    features = np.random.zipf(2, n_events) % n_features
    
    print("Actualizando sketch...")
    for f in features:
        tracker.update(f)
        true_counts[f] += 1
    
    # Verificar error
    print("Verificando errores...")
    errors = []
    overestimations = []
    
    for f in list(true_counts.keys())[:1000]:  # Verificar 1000 features
        estimated = tracker.estimate(f)
        true_val = true_counts[f]
        error = (estimated - true_val) / n_events  # Error relativo
        errors.append(abs(error))
        overestimations.append(estimated - true_val)
    
    # Cotas teóricas
    epsilon_teorico = np.e / 2048
    
    print(f"\nAncho del sketch: 2048")
    print(f"Profundidad del sketch: 4")
    print(f"Cota teórica (ε): {epsilon_teorico:.6f}")
    print(f"\nError relativo promedio: {np.mean(errors):.6f}")
    print(f"Error relativo máximo: {np.max(errors):.6f}")
    print(f"Error relativo mediana: {np.median(errors):.6f}")
    print(f"\nSobreestimación promedio: {np.mean(overestimations):.2f} eventos")
    print(f"Sobreestimación máxima: {np.max(overestimations):.2f} eventos")
    
    # CM Sketch solo sobreestima, nunca subestima
    underestimates = sum(1 for o in overestimations if o < 0)
    print(f"\nNúmero de subestimaciones: {underestimates} (debería ser 0)")
    
    if np.mean(errors) < epsilon_teorico * 2 and underestimates == 0:
        print("\n✓ APROBADO: Error dentro de cotas teóricas")
        return True
    else:
        print("\n✗ FALLIDO: Error fuera de cotas")
        return False


def run_all_tests():
    """Ejecutar todos los tests de validación."""
    print("\n" + "=" * 70)
    print("SUITE DE VALIDACIÓN MATEMÁTICA - ORGANISMO VIVO v100")
    print("=" * 70)
    
    results = {}
    
    try:
        results['JL_Preservation'] = test_jl_preservation()
    except Exception as e:
        print(f"\n✗ ERROR en test JL: {e}")
        results['JL_Preservation'] = False
    
    try:
        results['SGD_Convergence'] = test_sgd_convergence()
    except Exception as e:
        print(f"\n✗ ERROR en test SGD: {e}")
        results['SGD_Convergence'] = False
    
    try:
        results['CM_Sketch_Error'] = test_cm_sketch_error()
    except Exception as e:
        print(f"\n✗ ERROR en test CM Sketch: {e}")
        results['CM_Sketch_Error'] = False
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ APROBADO" if passed else "✗ FALLIDO"
        print(f"{test_name:30s} : {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests aprobados ({passed/total*100:.0f}%)")
    
    return results


if __name__ == "__main__":
    run_all_tests()
