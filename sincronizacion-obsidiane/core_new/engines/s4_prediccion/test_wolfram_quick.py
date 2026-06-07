"""Test rápido del sistema Wolfram Hypergraph optimizado."""
import time
from hypergraph_wolfram import *

print("=" * 50)
print("  TEST WOLFRAM HYPERGRAPH OPTIMIZADO")
print("=" * 50)

# Test 1: Evolución simple
print("\n1. Evolución simple...")
t0 = time.time()
hg = triangle()
events = hg.evolve(rule_simple_growth(), steps=5)
t1 = time.time()
print(f"   OK: {len(events)} eventos en {t1-t0:.3f}s")
print(f"   Edges: {len(hg.edges)}")

# Test 2: Neural layer
print("\n2. Neural layer...")
t0 = time.time()
neural = WolframNeuralLayer(32)
emb = neural.compute_embeddings(hg)
t1 = time.time()
print(f"   OK: {len(emb)} embeddings en {t1-t0:.3f}s")

# Test 3: Multiway (limitado)
print("\n3. Multiway System (limitado)...")
t0 = time.time()
hg2 = triangle()
mw = MultiwaySystem(hg2, max_branches=10)
n = mw.evolve(rule_simple_growth(), steps=1, max_matches_per_leaf=2)
t1 = time.time()
print(f"   OK: {n} ramas en {t1-t0:.3f}s")

print("\n" + "=" * 50)
print("  TODOS LOS TESTS PASARON")
print("=" * 50)
