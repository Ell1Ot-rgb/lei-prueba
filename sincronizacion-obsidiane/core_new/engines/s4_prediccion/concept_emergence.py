"""
Emergencia de Conceptos desde Estructura Pura
==============================================

Sistema Wolfram-style donde los conceptos NO son nodos etiquetados,
sino patrones estructurales que emergen de:
1. Co-ocurrencia de percepciones
2. Reglas de binding automático
3. Persistencia y estabilidad estructural

Principio fundamental:
  "Un concepto es un patrón topológico que se repite
   cuando ciertas percepciones coexisten."

Uso:
    from concept_emergence import ConceptEmergence
    from hypergraph_wolfram import WolframHypergraph
    
    hg = WolframHypergraph()
    ce = ConceptEmergence(hg)
    
    # Inyectar percepciones (solo números, sin semántica)
    ce.inject_perception([1, 100])  # sensor_onda_450nm
    ce.inject_perception([1, 101])  # contexto_cielo
    ce.inject_perception([1, 102])  # contexto_mar
    
    # Aplicar binding
    ce.apply_binding_rules()
    
    # Detectar conceptos emergentes
    concepts = ce.detect_concepts()
    # → {1: 0.95, ...}  elemento 1 es un concepto (alto score)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, FrozenSet
from collections import defaultdict
from hypergraph_wolfram import WolframHypergraph, Edge, Element, RewriteRule, PatternEdge


# =============================================================================
# TIPOS
# =============================================================================

@dataclass
class PerceptionEvent:
    """Un evento de percepción inyectado al sistema."""
    id: int
    tick: int
    elements: FrozenSet[int]
    source: str = ""  # Opcional: identificador de fuente
    
    def __hash__(self):
        return hash((self.id, self.elements))


@dataclass
class EmergentConcept:
    """Un concepto detectado como patrón emergente."""
    core_element: int           # Elemento central del concepto
    score: float                # Score de "conceptualidad"
    degree: int                 # Número de hiperaristas que lo contienen
    contexts: Set[FrozenSet]    # Hiperaristas donde aparece
    neighbors: Set[int]         # Elementos conectados
    persistence: int            # Ticks que ha sobrevivido
    
    def __repr__(self):
        return f"Concept(elem={self.core_element}, score={self.score:.3f}, deg={self.degree})"


# =============================================================================
# REGLAS DE BINDING
# =============================================================================

def rule_cooccurrence_bind() -> RewriteRule:
    """
    Regla: Si dos hiperaristas comparten un elemento, 
           crear conexión entre los otros elementos.
    
    {{x,a}, {x,b}} → {{x,a}, {x,b}, {a,b}}
    """
    return RewriteRule(
        lhs=[PatternEdge(('_x', '_a')), PatternEdge(('_x', '_b'))],
        rhs=[PatternEdge(('_x', '_a')), PatternEdge(('_x', '_b')), PatternEdge(('_a', '_b'))],
        name="cooccur_bind"
    )


def rule_transitivity() -> RewriteRule:
    """
    Regla: Si a→b y b→c, entonces a→c
    
    {{a,b}, {b,c}} → {{a,b}, {b,c}, {a,c}}
    """
    return RewriteRule(
        lhs=[PatternEdge(('_a', '_b')), PatternEdge(('_b', '_c'))],
        rhs=[PatternEdge(('_a', '_b')), PatternEdge(('_b', '_c')), PatternEdge(('_a', '_c'))],
        name="transitivity"
    )


def rule_merge_common() -> RewriteRule:
    """
    Regla: Dos hiperaristas con 2+ elementos comunes se fusionan.
    
    {{a,b,c}, {a,b,d}} → {{a,b,c,d}}
    
    Nota: Esta regla es más compleja, la implementamos manualmente.
    """
    return None  # Implementación manual en ConceptEmergence


# =============================================================================
# SISTEMA DE EMERGENCIA DE CONCEPTOS
# =============================================================================

class ConceptEmergence:
    """
    Sistema de emergencia de conceptos desde estructura pura.
    
    Los conceptos NO son etiquetas - son patrones estructurales
    que emergen cuando:
    1. Un elemento aparece en múltiples contextos (alto degree)
    2. Los contextos son diversos (alta diversidad de vecinos)
    3. El patrón persiste en el tiempo (estabilidad)
    
    Atributos:
        hg: WolframHypergraph subyacente
        perception_history: Historial de percepciones
        concept_threshold: Umbral mínimo de score para ser concepto
    """
    
    __slots__ = ['hg', '_perceptions', '_tick', '_element_first_seen',
                 '_element_last_seen', 'concept_threshold', '_rng']
    
    def __init__(self, hg: Optional[WolframHypergraph] = None,
                 concept_threshold: float = 0.3,
                 seed: int = 42):
        self.hg = hg or WolframHypergraph()
        self._perceptions: List[PerceptionEvent] = []
        self._tick = 0
        self._element_first_seen: Dict[int, int] = {}
        self._element_last_seen: Dict[int, int] = {}
        self.concept_threshold = concept_threshold
        self._rng = np.random.default_rng(seed)
    
    @property
    def tick(self) -> int:
        return self._tick
    
    def advance_tick(self):
        """Avanza el tiempo del sistema."""
        self._tick += 1
        self.hg._tick += 1  # Avanzar también el tick del hipergrafo
    
    # -------------------------------------------------------------------------
    # INYECCIÓN DE PERCEPCIONES
    # -------------------------------------------------------------------------
    
    def inject_perception(self, elements: List[int], 
                          source: str = "") -> PerceptionEvent:
        """
        Inyecta una percepción como hiperarista.
        
        Args:
            elements: Lista de elementos que co-ocurren
            source: Identificador opcional de la fuente
            
        Returns:
            PerceptionEvent creado
        """
        frozen = frozenset(elements)
        
        # Registrar primera/última vez visto para cada elemento
        for elem in elements:
            if elem not in self._element_first_seen:
                self._element_first_seen[elem] = self._tick
            self._element_last_seen[elem] = self._tick
        
        # Añadir al hipergrafo
        self.hg.add_edge(*elements)
        
        # Crear evento
        event = PerceptionEvent(
            id=len(self._perceptions),
            tick=self._tick,
            elements=frozen,
            source=source
        )
        self._perceptions.append(event)
        
        return event
    
    def inject_batch(self, perceptions: List[List[int]]):
        """Inyecta múltiples percepciones."""
        for p in perceptions:
            self.inject_perception(p)
    
    # -------------------------------------------------------------------------
    # REGLAS DE BINDING
    # -------------------------------------------------------------------------
    
    def apply_binding_rules(self, max_iterations: int = 5) -> int:
        """
        Aplica reglas de binding por co-ocurrencia.
        
        Regla principal: Si dos elementos aparecen juntos frecuentemente,
        se crea una conexión directa entre ellos.
        
        Returns:
            Número de nuevas hiperaristas creadas
        """
        total_new = 0
        
        for iteration in range(max_iterations):
            new_edges = self._apply_cooccurrence_binding()
            
            if not new_edges:
                break
            
            total_new += len(new_edges)
        
        return total_new
    
    def _apply_cooccurrence_binding(self) -> Set[Edge]:
        """
        Detecta pares de elementos que co-ocurren en múltiples hiperaristas
        y crea conexiones directas entre ellos.
        """
        # Contar co-ocurrencias
        cooccur_count: Dict[Tuple[int, int], int] = defaultdict(int)
        
        for edge in self.hg.edges:
            edge_list = sorted(edge)
            for i, a in enumerate(edge_list):
                for b in edge_list[i+1:]:
                    cooccur_count[(a, b)] += 1
        
        # Crear conexiones para pares con alta co-ocurrencia
        new_edges = set()
        threshold = 2  # Mínimo 2 co-ocurrencias
        
        for (a, b), count in cooccur_count.items():
            if count >= threshold:
                edge = frozenset({a, b})
                if edge not in self.hg.edges:
                    self.hg.add_edge(a, b)
                    new_edges.add(edge)
        
        return new_edges
    
    def apply_merge_rule(self) -> int:
        """
        Fusiona hiperaristas con 2+ elementos en común.
        
        {{a,b,c}, {a,b,d}} → {{a,b,c,d}}
        
        Returns:
            Número de fusiones realizadas
        """
        edges_list = list(self.hg.edges)
        to_remove = set()
        to_add = set()
        merges = 0
        
        for i, e1 in enumerate(edges_list):
            if e1 in to_remove:
                continue
            for e2 in edges_list[i+1:]:
                if e2 in to_remove:
                    continue
                
                # Calcular intersección
                common = e1 & e2
                if len(common) >= 2:
                    # Fusionar
                    merged = e1 | e2
                    to_remove.add(e1)
                    to_remove.add(e2)
                    to_add.add(merged)
                    merges += 1
                    break
        
        # Aplicar cambios
        for edge in to_remove:
            self.hg._edges.discard(edge)
        for edge in to_add:
            self.hg._edges.add(edge)
        
        return merges
    
    # -------------------------------------------------------------------------
    # DETECCIÓN DE CONCEPTOS
    # -------------------------------------------------------------------------
    
    def detect_concepts(self, top_k: int = 10) -> List[EmergentConcept]:
        """
        Detecta elementos que son "conceptos emergentes".
        
        Un concepto es un elemento con:
        - Alto degree (aparece en muchas hiperaristas)
        - Alta diversidad (vecinos diversos)
        - Alta persistencia (visto muchas veces)
        
        Returns:
            Lista de EmergentConcept ordenados por score
        """
        concepts = []
        elements = self.hg.elements
        
        if not elements:
            return []
        
        max_degree = 1
        max_diversity = 1
        
        # Calcular estadísticas normalizadoras
        for elem in elements:
            edges_with = [e for e in self.hg.edges if elem in e]
            neighbors = set()
            for e in edges_with:
                neighbors.update(e)
            neighbors.discard(elem)
            
            max_degree = max(max_degree, len(edges_with))
            max_diversity = max(max_diversity, len(neighbors))
        
        # Calcular score para cada elemento
        for elem in elements:
            edges_with = [e for e in self.hg.edges if elem in e]
            degree = len(edges_with)
            
            neighbors = set()
            for e in edges_with:
                neighbors.update(e)
            neighbors.discard(elem)
            diversity = len(neighbors)
            
            # Persistencia: ticks desde primera vez visto
            first_seen = self._element_first_seen.get(elem, self._tick)
            persistence = self._tick - first_seen + 1
            
            # Score compuesto normalizado
            degree_norm = degree / max_degree
            diversity_norm = diversity / max_diversity if max_diversity > 0 else 0
            persistence_norm = min(1.0, persistence / 10)  # Saturar en 10 ticks
            
            # Fórmula: promedio ponderado
            score = (0.4 * degree_norm + 
                     0.4 * diversity_norm + 
                     0.2 * persistence_norm)
            
            if score >= self.concept_threshold:
                concept = EmergentConcept(
                    core_element=elem,
                    score=score,
                    degree=degree,
                    contexts=set(frozenset(e) for e in edges_with),
                    neighbors=neighbors,
                    persistence=persistence
                )
                concepts.append(concept)
        
        # Ordenar por score
        concepts.sort(key=lambda c: -c.score)
        
        return concepts[:top_k]
    
    def get_concept_cluster(self, core_element: int, 
                            depth: int = 2) -> Set[int]:
        """
        Obtiene el "cluster" de un concepto: todos los elementos
        conectados hasta cierta profundidad.
        """
        cluster = {core_element}
        frontier = {core_element}
        
        for _ in range(depth):
            new_frontier = set()
            for elem in frontier:
                neighbors = set()
                for edge in self.hg.edges:
                    if elem in edge:
                        neighbors.update(edge)
                new_frontier.update(neighbors - cluster)
            cluster.update(new_frontier)
            frontier = new_frontier
        
        return cluster
    
    # -------------------------------------------------------------------------
    # VISUALIZACIÓN
    # -------------------------------------------------------------------------
    
    def visualize_concepts(self, concepts: List[EmergentConcept]) -> str:
        """Genera visualización ASCII de conceptos detectados."""
        lines = [
            "╔══════════════════════════════════════════════════════════╗",
            "║            EMERGENT CONCEPTS                             ║",
            "╠══════════════════════════════════════════════════════════╣",
        ]
        
        if not concepts:
            lines.append("║  No concepts detected above threshold                     ║")
        else:
            for c in concepts[:5]:
                ctx_str = f"{len(c.contexts)} contexts"
                neigh_str = f"{len(c.neighbors)} neighbors"
                line = f"║  Element {c.core_element:3d}: score={c.score:.3f} deg={c.degree:2d} {ctx_str} {neigh_str}"
                lines.append(line.ljust(60) + "║")
        
        lines.append("╚══════════════════════════════════════════════════════════╝")
        return "\n".join(lines)
    
    def stats(self) -> Dict:
        """Estadísticas del sistema."""
        concepts = self.detect_concepts()
        return {
            'tick': self._tick,
            'perceptions': len(self._perceptions),
            'elements': len(self.hg.elements),
            'edges': len(self.hg.edges),
            'concepts_detected': len(concepts),
            'top_concept_score': concepts[0].score if concepts else 0
        }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  CONCEPT EMERGENCE - TEST")
    print("=" * 60)
    
    # Crear sistema
    ce = ConceptEmergence()
    
    print("\n📥 Inyectando percepciones de 'AZUL'...")
    
    # Simular percepciones del concepto "azul"
    # Elemento 1 = patrón que aparecerá en todos los contextos
    
    # Contexto: cielo
    ce.inject_perception([1, 10, 11])  # elem 1 + cielo-related
    # Contexto: mar
    ce.inject_perception([1, 20, 21])  # elem 1 + mar-related
    # Contexto: tristeza
    ce.inject_perception([1, 30, 31])  # elem 1 + tristeza-related
    # Contexto: frío
    ce.inject_perception([1, 40, 41])  # elem 1 + frío-related
    # Contexto: onda 450nm
    ce.inject_perception([1, 50])      # elem 1 + física
    
    ce.advance_tick()
    
    print(f"   Percepciones: {len(ce._perceptions)}")
    print(f"   Hipergrafo: {ce.hg.to_wolfram_notation()}")
    
    print("\n🔗 Aplicando reglas de binding...")
    new_edges = ce.apply_binding_rules()
    print(f"   Nuevas conexiones: {new_edges}")
    
    print("\n🧠 Detectando conceptos emergentes...")
    concepts = ce.detect_concepts()
    
    print(ce.visualize_concepts(concepts))
    
    if concepts:
        top = concepts[0]
        print(f"\n🔵 Concepto principal: Elemento {top.core_element}")
        print(f"   Score: {top.score:.3f}")
        print(f"   Aparece en: {top.degree} contextos")
        print(f"   Conectado a: {sorted(top.neighbors)}")
        
        cluster = ce.get_concept_cluster(top.core_element, depth=1)
        print(f"   Cluster (depth=1): {sorted(cluster)}")
    
    print("\n" + "=" * 60)
    print("  CONCEPT EMERGENCE OK ✓")
    print("=" * 60)
