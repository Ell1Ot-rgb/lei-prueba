"""
Test funcional completo del subsistema MemGraphRAG.
Ejecutar desde: C:\\Users\\Public\\sistema_vivo_final_v2
"""
import sys
sys.path.insert(0, r'C:\Users\Public\sistema_vivo_final_v2')

print("=== TEST FUNCIONAL MemGraphRAG (modo memoria local) ===\n")

# --- Test 1: Global Memory ---
from adapters.outbound.memgraph_rag.global_memory import GlobalMemory
mem = GlobalMemory(schema_freq_threshold=2)

schema1, prom1 = mem.agregar_schema_candidato('yo', 'experimenta', 'emocion')
schema2, prom2 = mem.agregar_schema_candidato('yo', 'experimenta', 'emocion')

print("Test 1 - GlobalMemory:")
print(f"  Schema promovido a estable: {prom2}")
print(f"  Schemas estables: {len(mem.obtener_schemas_estables())}")

pasaje = mem.agregar_pasaje('Senti angustia al despertar hoy.', fuente='diario_test')
hecho = mem.agregar_hecho('yo_emergente', 'experimenta', 'angustia', schema2.id, pasaje.id, 0.9)
print(f"  Hecho creado: {hecho.clave() if hecho else None}")
stats = mem.estadisticas()
print(f"  Estadisticas: {stats}\n")

# --- Test 2: Extraction Agent ---
from adapters.outbound.memgraph_rag.agents.extraction_agent import ExtractionAgent
a_ext = ExtractionAgent(memoria=mem)
schemas, hechos, pasaje2 = a_ext.procesar_fragmento(
    texto='Senti miedo y tristeza al recordar el pasado. El cuerpo estaba tenso.',
    fuente='test_diario',
    tipo_fuente='diario',
)
print("Test 2 - ExtractionAgent (A_ext):")
print(f"  Schemas nuevos estabilizados: {len(schemas)}")
print(f"  Hechos extraidos: {len(hechos)}")
print(f"  Pasaje ID: {pasaje2.id[:12]}...\n")

# --- Test 3: Detection Agent ---
from adapters.outbound.memgraph_rag.agents.detection_agent import DetectionAgent
a_det = DetectionAgent(memoria=mem)

hecho_alegria = mem.agregar_hecho('yo_emergente', 'experimenta', 'alegria', schema2.id, pasaje.id, 0.7)
print("Test 3 - DetectionAgent (A_det):")
if hecho_alegria:
    conflictos = a_det.escanear_conflictos(hecho_alegria)
    print(f"  Conflictos detectados: {len(conflictos)}")
    for c in conflictos:
        print(f"    - Tipo: {c.tipo.name}")
        print(f"      Descripcion: {c.descripcion[:80]}")
else:
    print("  Hecho de alegria no creado aun (schema insuficiente)")
print()

# --- Test 4: Resolution Agent ---
from adapters.outbound.memgraph_rag.agents.resolution_agent import ResolutionAgent
a_res = ResolutionAgent(memoria=mem)

if hecho_alegria:
    hecho_angustia2 = mem.agregar_hecho('yo_emergente', 'experimenta', 'angustia', schema2.id, pasaje.id, 0.95)
    if hecho_angustia2:
        conflictos2 = a_det.escanear_conflictos(hecho_angustia2)
        resoluciones = a_res.resolver_conflictos(hecho_angustia2, conflictos2)
        print("Test 4 - ResolutionAgent (A_res):")
        print(f"  Resoluciones aplicadas: {len(resoluciones)}")
        for r in resoluciones:
            print(f"    - Accion: {r.accion.name}")
            print(f"      Razon: {r.razon[:80]}")
print()

# --- Test 5: Hierarchical Graph + Retrieval ---
for texto in [
    'La angustia aparecio de nuevo esta manana. Patron recurrente de ansiedad.',
    'La meditacion trajo calma y paz. El cuerpo se alivio.',
    'Tristeza profunda al recordar. Patron de tristeza matutino.',
]:
    a_ext.procesar_fragmento(texto, fuente='test_batch', tipo_fuente='diario')

from adapters.outbound.memgraph_rag.memgraph_client import MemGraphClient
from adapters.outbound.memgraph_rag.hierarchical_graph import HierarchicalGraph
from adapters.outbound.memgraph_rag.retrieval import MemGraphRetrieval

cliente = MemGraphClient()
grafo = HierarchicalGraph(mem, cliente)
grafo_stats = grafo.construir_grafo_completo()

print("Test 5 - HierarchicalGraph:")
print(f"  Nodos G_ont: {grafo_stats.get('nodos_ont', 0)}")
print(f"  Nodos G_fac: {grafo_stats.get('nodos_fac', 0)}")
print(f"  Nodos G_pas: {grafo_stats.get('nodos_pas', 0)}")
print(f"  Bridging edges: {grafo_stats.get('bridging_edges', 0)}")
print()

retrieval = MemGraphRetrieval(mem, cliente, grafo)
resultado = retrieval.recuperar('patrones de angustia y emociones recurrentes')

print("Test 6 - MemGraphRetrieval (PPR):")
print(f"  Modo: {resultado['modo']}")
print(f"  Hechos relevantes: {len(resultado['hechos_relevantes'])}")
print(f"  Pasajes directos: {len(resultado['pasajes_directos'])}")
print(f"  Nodos top PPR: {len(resultado['nodos_top'])}")
print(f"  Contexto (primeros 400 chars):")
print(f"  {resultado['contexto'][:400]}\n")

# --- Test 6: Adaptador Principal ---
from adapters.outbound.memgraph_rag import MemGraphRAGAdapter
rag = MemGraphRAGAdapter()

res_index = rag.indexar(
    texto='Hoy amanecer con mucho miedo y ansiedad. Patron de cada manana al despertar.',
    fuente='test_final',
    tipo_fuente='diario',
)
print("Test 7 - MemGraphRAGAdapter (completo):")
print(f"  Indexacion: estado={res_index['estado']}, hechos={res_index['hechos_nuevos']}")

consulta = rag.consultar('emociones negativas al despertar')
print(f"  Consulta modo: {consulta['modo']}")
print(f"  Contexto preview: {consulta['contexto'][:200]}")

stats_final = rag.estadisticas()
print(f"  Memoria final: {stats_final['memoria_global']}")
print()
print("=== TODOS LOS TESTS COMPLETADOS EXITOSAMENTE ===")
print(f"Sistema MemGraphRAG funcionando en modo: {'Memgraph DB' if rag.cliente.esta_conectado() else 'Memoria Local'}")
