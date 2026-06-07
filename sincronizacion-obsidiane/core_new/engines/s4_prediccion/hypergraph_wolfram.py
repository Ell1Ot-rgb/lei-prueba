"""
Wolfram Physics Hypergraph - Implementación Fundamental
========================================================

Implementación fiel al modelo de Wolfram Physics Project:
- Hipergrafo puro sin labels (solo estructura)
- Pattern matching con variables (x_, y_, z_)
- Sistema de eventos de actualización
- Causal graph de dependencias entre eventos
- Multiway branching (opcional)

Notación Wolfram:
  Hipergrafo: {{1,2}, {2,3}, {3,1}}
  Regla: {{x_, y_}, {x_, z_}} → {{x_, z_}, {x_, w_}, {y_, w_}, {z_, w_}}

Referencias:
  - wolframphysics.org
  - stephenwolfram.com/publications/project-find-fundamental-theory-physics/
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, FrozenSet, Iterator
from collections import defaultdict
from itertools import combinations, permutations
import json
from pathlib import Path


# =============================================================================
# TIPOS FUNDAMENTALES
# =============================================================================

# Un elemento es solo un entero (identidad pura, sin propiedades)
Element = int

# Una hiperarista es un conjunto inmutable de elementos
# Wolfram usa tuplas ordenadas, aquí usamos FrozenSet para simplicidad
Edge = FrozenSet[Element]

# Un hipergrafo es un conjunto de hiperaristas
HypergraphState = FrozenSet[Edge]


# =============================================================================
# PATRÓN DE REESCRITURA (Pattern Matching)
# =============================================================================

@dataclass(frozen=True)
class PatternEdge:
    """
    Una hiperarista en un patrón de regla.
    Variables usan prefijo '_' (ej: '_x', '_y').
    """
    elements: Tuple[str, ...]
    
    def __repr__(self):
        return "{" + ",".join(self.elements) + "}"
    
    @property
    def variables(self) -> Set[str]:
        """Retorna las variables en esta arista."""
        return {e for e in self.elements if e.startswith('_')}
    
    def is_variable(self, elem: str) -> bool:
        return elem.startswith('_')


@dataclass
class RewriteRule:
    """
    Regla de reescritura estilo Wolfram.
    
    Ejemplo:
        lhs = [PatternEdge(('_x', '_y')), PatternEdge(('_y', '_z'))]
        rhs = [PatternEdge(('_x', '_z')), PatternEdge(('_z', '_w'))]
        
        Significa: {{x,y}, {y,z}} → {{x,z}, {z,w}}
        Donde w es un NUEVO elemento creado.
    """
    lhs: List[PatternEdge]  # Patrón a buscar
    rhs: List[PatternEdge]  # Patrón de reemplazo
    name: str = ""
    
    def __post_init__(self):
        self._lhs_vars = set()
        for edge in self.lhs:
            self._lhs_vars.update(edge.variables)
        
        self._rhs_vars = set()
        for edge in self.rhs:
            self._rhs_vars.update(edge.variables)
        
        # Variables nuevas = están en RHS pero no en LHS
        self._new_vars = self._rhs_vars - self._lhs_vars
    
    def __repr__(self):
        lhs_str = "{" + ", ".join(str(e) for e in self.lhs) + "}"
        rhs_str = "{" + ", ".join(str(e) for e in self.rhs) + "}"
        return f"{lhs_str} → {rhs_str}"
    
    @property
    def new_variables(self) -> Set[str]:
        """Variables que aparecen solo en RHS (nuevos elementos)."""
        return self._new_vars
    
    def find_matches(self, hypergraph: 'WolframHypergraph', 
                      max_matches: int = 50) -> List[Dict[str, Element]]:
        """
        Encuentra bindings posibles del LHS en el hipergrafo.
        OPTIMIZADO: Indexación por cardinalidad + límite de matches.
        
        Args:
            hypergraph: Hipergrafo donde buscar
            max_matches: Máximo de matches a retornar (evita explosión)
        
        Returns:
            Lista de diccionarios {variable: elemento}
        """
        if not self.lhs:
            return [{}]
        
        # OPTIMIZACIÓN 1: Indexar aristas por cardinalidad
        edges_by_card: Dict[int, List[Edge]] = defaultdict(list)
        for edge in hypergraph.edges:
            edges_by_card[len(edge)].append(edge)
        
        matches = []
        first_pattern = self.lhs[0]
        card = len(first_pattern.elements)
        
        # Solo buscar en aristas de cardinalidad correcta
        candidate_edges = edges_by_card.get(card, [])
        
        for edge in candidate_edges:
            if len(matches) >= max_matches:
                break
            
            # OPTIMIZACIÓN 2: Binding directo sin permutaciones completas
            bindings = self._try_bind_edge(first_pattern, edge)
            
            for binding in bindings:
                if len(matches) >= max_matches:
                    break
                    
                # Verificar resto de aristas del patrón
                full_matches = self._extend_match_opt(
                    binding, 1, edges_by_card, max_matches - len(matches)
                )
                matches.extend(full_matches)
        
        return matches[:max_matches]
    
    def _try_bind_edge(self, pattern: PatternEdge, 
                       edge: Edge) -> List[Dict[str, Element]]:
        """
        Intenta hacer binding de un patrón a una arista.
        OPTIMIZADO: Solo genera bindings válidos.
        """
        edge_list = list(edge)
        n = len(edge_list)
        
        # Si la arista tiene 2 elementos, solo hay 2 permutaciones
        # Si tiene 3+, limitar a pocas permutaciones
        if n <= 2:
            perms = list(permutations(edge_list))
        else:
            # Solo probar algunas permutaciones (la original y rotaciones)
            perms = [tuple(edge_list)]
            for i in range(1, min(n, 3)):
                perms.append(tuple(edge_list[i:] + edge_list[:i]))
        
        results = []
        for perm in perms:
            binding = {}
            valid = True
            
            for var, elem in zip(pattern.elements, perm):
                if pattern.is_variable(var):
                    if var in binding and binding[var] != elem:
                        valid = False
                        break
                    binding[var] = elem
                elif int(var) != elem:
                    valid = False
                    break
            
            if valid and binding not in results:
                results.append(binding)
        
        return results
    
    def _extend_match_opt(self, binding: Dict[str, Element], 
                          pattern_idx: int,
                          edges_by_card: Dict[int, List[Edge]],
                          max_remaining: int) -> List[Dict[str, Element]]:
        """
        Extiende un binding parcial al resto del patrón.
        OPTIMIZADO: Usa índice por cardinalidad + límite.
        """
        if pattern_idx >= len(self.lhs):
            return [binding.copy()]
        
        if max_remaining <= 0:
            return []
        
        pattern = self.lhs[pattern_idx]
        card = len(pattern.elements)
        candidate_edges = edges_by_card.get(card, [])
        
        results = []
        
        for edge in candidate_edges:
            if len(results) >= max_remaining:
                break
            
            # OPTIMIZACIÓN: Verificar si la arista puede matchear con el binding actual
            edge_elements = set(edge)
            
            # Variables ya bound deben estar en la arista
            bound_vars = {v: e for v, e in binding.items() 
                          if v in [p for p in pattern.elements if pattern.is_variable(p)]}
            
            if not all(e in edge_elements for e in bound_vars.values()):
                continue
            
            bindings = self._try_bind_edge(pattern, edge)
            
            for new_partial in bindings:
                # Verificar consistencia con binding existente
                consistent = True
                merged = binding.copy()
                
                for var, elem in new_partial.items():
                    if var in merged:
                        if merged[var] != elem:
                            consistent = False
                            break
                    else:
                        merged[var] = elem
                
                if consistent:
                    extended = self._extend_match_opt(
                        merged, pattern_idx + 1, edges_by_card, 
                        max_remaining - len(results)
                    )
                    results.extend(extended)
                    
                    if len(results) >= max_remaining:
                        break
        
        return results
    
    def apply(self, hypergraph: 'WolframHypergraph', 
              binding: Dict[str, Element]) -> Tuple[Set[Edge], Set[Edge], Dict[str, Element]]:
        """
        Aplica la regla con un binding específico.
        
        Returns:
            (consumed_edges, produced_edges, full_binding con nuevas vars)
        """
        # Construir aristas consumidas
        consumed = set()
        for pattern in self.lhs:
            elements = []
            for var in pattern.elements:
                if pattern.is_variable(var):
                    elements.append(binding[var])
                else:
                    elements.append(int(var))
            consumed.add(frozenset(elements))
        
        # Asignar nuevos elementos para variables nuevas
        full_binding = binding.copy()
        for new_var in self._new_vars:
            full_binding[new_var] = hypergraph._new_element()
        
        # Construir aristas producidas
        produced = set()
        for pattern in self.rhs:
            elements = []
            for var in pattern.elements:
                if pattern.is_variable(var):
                    elements.append(full_binding[var])
                else:
                    elements.append(int(var))
            produced.add(frozenset(elements))
        
        return consumed, produced, full_binding


# =============================================================================
# EVENTO DE ACTUALIZACIÓN
# =============================================================================

@dataclass
class UpdateEvent:
    """
    Un evento de actualización en el hipergrafo.
    Cada aplicación de una regla crea un evento.
    """
    id: int
    tick: int
    rule_name: str
    binding: Dict[str, Element]
    consumed: Set[Edge]
    produced: Set[Edge]
    parent_events: Set[int] = field(default_factory=set)
    
    def __repr__(self):
        return f"Event({self.id}@t{self.tick}: {self.rule_name})"


# =============================================================================
# WOLFRAM HYPERGRAPH
# =============================================================================

class WolframHypergraph:
    """
    Hipergrafo estilo Wolfram Physics.
    
    Características:
    - Aristas son FrozenSet[int] sin labels
    - Evoluciona aplicando reglas de reescritura
    - Mantiene historial de eventos
    - Construye causal graph
    
    Uso:
        hg = WolframHypergraph()
        hg.add_edges([{1,2}, {2,3}, {3,1}])
        
        rule = RewriteRule(
            lhs=[PatternEdge(('_x', '_y'))],
            rhs=[PatternEdge(('_x', '_y')), PatternEdge(('_y', '_z'))],
            name="grow"
        )
        
        hg.evolve(rule, steps=5)
    """
    
    __slots__ = ['_edges', '_next_element', '_tick', '_events', 
                 '_causal_edges', '_edge_to_event', '_rng']
    
    def __init__(self, seed: int = 42):
        self._edges: Set[Edge] = set()
        self._next_element: int = 1
        self._tick: int = 0
        self._events: List[UpdateEvent] = []
        self._causal_edges: List[Tuple[int, int]] = []  # (from_event, to_event)
        self._edge_to_event: Dict[Edge, int] = {}  # Qué evento creó cada edge
        self._rng = np.random.default_rng(seed)
    
    @property
    def edges(self) -> FrozenSet[Edge]:
        return frozenset(self._edges)
    
    @property
    def elements(self) -> Set[Element]:
        """Todos los elementos actuales."""
        result = set()
        for edge in self._edges:
            result.update(edge)
        return result
    
    @property
    def tick(self) -> int:
        return self._tick
    
    @property
    def events(self) -> List[UpdateEvent]:
        return self._events
    
    @property
    def causal_graph(self) -> Tuple[List[UpdateEvent], List[Tuple[int, int]]]:
        """Retorna (eventos, aristas_causales)."""
        return (self._events, self._causal_edges)
    
    def _new_element(self) -> Element:
        """Genera un nuevo elemento único."""
        elem = self._next_element
        self._next_element += 1
        return elem
    
    def add_edges(self, edges: List[Set[int]]):
        """Añade aristas iniciales."""
        for edge in edges:
            frozen = frozenset(edge)
            self._edges.add(frozen)
            # Actualizar next_element si es necesario
            for elem in edge:
                if elem >= self._next_element:
                    self._next_element = elem + 1
    
    def add_edge(self, *elements: int) -> Edge:
        """Añade una arista."""
        edge = frozenset(elements)
        self._edges.add(edge)
        for elem in elements:
            if elem >= self._next_element:
                self._next_element = elem + 1
        return edge
    
    def step(self, rule: RewriteRule, 
             deterministic: bool = False) -> Optional[UpdateEvent]:
        """
        Aplica una regla una vez.
        
        Args:
            rule: Regla a aplicar
            deterministic: Si True, usa primer match; si False, aleatorio
            
        Returns:
            UpdateEvent si se aplicó, None si no hubo match
        """
        matches = rule.find_matches(self)
        
        if not matches:
            return None
        
        # Seleccionar match
        if deterministic:
            binding = matches[0]
        else:
            idx = self._rng.integers(0, len(matches))
            binding = matches[idx]
        
        # Aplicar regla
        consumed, produced, full_binding = rule.apply(self, binding)
        
        # Encontrar eventos padre (de aristas consumidas)
        parent_events = set()
        for edge in consumed:
            if edge in self._edge_to_event:
                parent_events.add(self._edge_to_event[edge])
        
        # Crear evento
        event = UpdateEvent(
            id=len(self._events),
            tick=self._tick,
            rule_name=rule.name,
            binding=full_binding,
            consumed=consumed,
            produced=produced,
            parent_events=parent_events
        )
        self._events.append(event)
        
        # Actualizar causal edges
        for parent_id in parent_events:
            self._causal_edges.append((parent_id, event.id))
        
        # Actualizar hipergrafo
        self._edges -= consumed
        self._edges |= produced
        
        # Registrar qué evento creó cada nueva arista
        for edge in produced:
            self._edge_to_event[edge] = event.id
        
        self._tick += 1
        return event
    
    def evolve(self, rule: RewriteRule, steps: int = 10,
               deterministic: bool = False) -> List[UpdateEvent]:
        """
        Evoluciona el hipergrafo aplicando la regla múltiples veces.
        """
        events = []
        for _ in range(steps):
            event = self.step(rule, deterministic)
            if event:
                events.append(event)
            else:
                break  # No más matches
        return events
    
    def evolve_multi(self, rules: List[RewriteRule], steps: int = 10) -> List[UpdateEvent]:
        """
        Evoluciona con múltiples reglas, eligiendo aleatoriamente.
        """
        events = []
        for _ in range(steps):
            # Intentar cada regla hasta que una funcione
            self._rng.shuffle(rules)
            applied = False
            for rule in rules:
                event = self.step(rule, deterministic=False)
                if event:
                    events.append(event)
                    applied = True
                    break
            if not applied:
                break
        return events
    
    # --- Estadísticas ---
    
    def stats(self) -> Dict:
        """Estadísticas del hipergrafo."""
        cardinalities = [len(e) for e in self._edges]
        elements = self.elements
        
        return {
            'elements': len(elements),
            'edges': len(self._edges),
            'min_element': min(elements) if elements else 0,
            'max_element': max(elements) if elements else 0,
            'avg_cardinality': float(np.mean(cardinalities)) if cardinalities else 0,
            'max_cardinality': max(cardinalities) if cardinalities else 0,
            'tick': self._tick,
            'events': len(self._events),
            'causal_edges': len(self._causal_edges)
        }
    
    # --- Serialización ---
    
    def to_wolfram_notation(self) -> str:
        """Convierte a notación Wolfram: {{1,2}, {2,3}, ...}"""
        edges_str = ", ".join(
            "{" + ",".join(str(e) for e in sorted(edge)) + "}"
            for edge in sorted(self._edges, key=lambda e: tuple(sorted(e)))
        )
        return "{" + edges_str + "}"
    
    def __repr__(self):
        return f"WolframHypergraph({self.to_wolfram_notation()})"


# =============================================================================
# CAUSAL NETWORK (Análisis del Causal Graph)
# =============================================================================

class CausalNetwork:
    """
    Análisis del grafo causal derivado de eventos.
    """
    
    __slots__ = ['_events', '_edges', '_in_degree', '_out_degree', '_depth']
    
    def __init__(self, hypergraph: WolframHypergraph):
        self._events, self._edges = hypergraph.causal_graph
        self._in_degree: Dict[int, int] = defaultdict(int)
        self._out_degree: Dict[int, int] = defaultdict(int)
        self._depth: Dict[int, int] = {}
        
        self._compute_degrees()
        self._compute_depths()
    
    def _compute_degrees(self):
        for src, dst in self._edges:
            self._out_degree[src] += 1
            self._in_degree[dst] += 1
    
    def _compute_depths(self):
        """Compute depth (longest path from root) for each event."""
        for event in self._events:
            self._depth[event.id] = self._compute_event_depth(event.id, set())
    
    def _compute_event_depth(self, event_id: int, visited: Set[int]) -> int:
        if event_id in self._depth:
            return self._depth[event_id]
        
        if event_id in visited:
            return 0  # Cycle (shouldn't happen in DAG)
        
        visited.add(event_id)
        
        event = self._events[event_id]
        if not event.parent_events:
            return 0
        
        max_parent_depth = max(
            self._compute_event_depth(p, visited) 
            for p in event.parent_events
        )
        return max_parent_depth + 1
    
    def get_roots(self) -> List[int]:
        """Eventos sin padres."""
        return [e.id for e in self._events if self._in_degree[e.id] == 0]
    
    def get_leaves(self) -> List[int]:
        """Eventos sin hijos."""
        return [e.id for e in self._events if self._out_degree[e.id] == 0]
    
    def timelike_separated(self, event_a: int, event_b: int) -> bool:
        """True si hay camino causal entre A y B."""
        # BFS desde A
        visited = set()
        queue = [event_a]
        while queue:
            current = queue.pop(0)
            if current == event_b:
                return True
            if current in visited:
                continue
            visited.add(current)
            # Añadir hijos
            for src, dst in self._edges:
                if src == current:
                    queue.append(dst)
        
        # También checar dirección inversa
        visited = set()
        queue = [event_b]
        while queue:
            current = queue.pop(0)
            if current == event_a:
                return True
            if current in visited:
                continue
            visited.add(current)
            for src, dst in self._edges:
                if src == current:
                    queue.append(dst)
        
        return False
    
    def max_depth(self) -> int:
        """Profundidad máxima del causal graph."""
        return max(self._depth.values()) if self._depth else 0
    
    def stats(self) -> Dict:
        if not self._events:
            return {'events': 0, 'edges': 0}
        
        return {
            'events': len(self._events),
            'causal_edges': len(self._edges),
            'roots': len(self.get_roots()),
            'leaves': len(self.get_leaves()),
            'max_depth': self.max_depth(),
            'avg_in_degree': np.mean(list(self._in_degree.values())) if self._in_degree else 0,
            'avg_out_degree': np.mean(list(self._out_degree.values())) if self._out_degree else 0
        }


# =============================================================================
# VISUALIZADOR
# =============================================================================

class WolframVisualizer:
    """
    Visualización ASCII de hipergrafos y grafos causales.
    """
    
    __slots__ = ['width']
    
    def __init__(self, width: int = 60):
        self.width = width
    
    def visualize_hypergraph(self, hg: WolframHypergraph) -> str:
        """Visualiza el estado actual del hipergrafo."""
        lines = [
            "╔" + "═" * (self.width - 2) + "╗",
            "║" + " WOLFRAM HYPERGRAPH ".center(self.width - 2) + "║",
            "╠" + "═" * (self.width - 2) + "╣",
        ]
        
        stats = hg.stats()
        lines.append("║" + f" Elements: {stats['elements']}  Edges: {stats['edges']}  Tick: {stats['tick']} ".ljust(self.width - 2) + "║")
        lines.append("╠" + "─" * (self.width - 2) + "╣")
        
        # Mostrar aristas
        lines.append("║" + " Edges:".ljust(self.width - 2) + "║")
        notation = hg.to_wolfram_notation()
        
        # Wrap notation
        max_line = self.width - 4
        while notation:
            chunk = notation[:max_line]
            notation = notation[max_line:]
            lines.append("║ " + chunk.ljust(self.width - 3) + "║")
        
        lines.append("╚" + "═" * (self.width - 2) + "╝")
        return "\n".join(lines)
    
    def visualize_causal(self, cn: CausalNetwork) -> str:
        """Visualiza estadísticas del grafo causal."""
        lines = [
            "╔" + "═" * (self.width - 2) + "╗",
            "║" + " CAUSAL NETWORK ".center(self.width - 2) + "║",
            "╠" + "═" * (self.width - 2) + "╣",
        ]
        
        stats = cn.stats()
        lines.append("║" + f" Events: {stats['events']}  Causal edges: {stats['causal_edges']} ".ljust(self.width - 2) + "║")
        lines.append("║" + f" Roots: {stats['roots']}  Leaves: {stats['leaves']}  Max depth: {stats['max_depth']} ".ljust(self.width - 2) + "║")
        
        lines.append("╚" + "═" * (self.width - 2) + "╝")
        return "\n".join(lines)
    
    def visualize_events(self, events: List[UpdateEvent], max_events: int = 10) -> str:
        """Visualiza eventos recientes."""
        lines = ["─── EVENTS ───"]
        for event in events[-max_events:]:
            consumed = "{" + ",".join(str(set(e)) for e in event.consumed) + "}"
            produced = "{" + ",".join(str(set(e)) for e in event.produced) + "}"
            lines.append(f"  [{event.id}] t={event.tick} {event.rule_name}: {consumed} → {produced}")
        return "\n".join(lines)


# =============================================================================
# MULTIWAY SYSTEM (Branching Evolution)
# =============================================================================

@dataclass
class BranchState:
    """Estado de una rama en el multiway system."""
    id: int
    hypergraph_state: HypergraphState
    parent_branch: Optional[int]
    event: Optional[UpdateEvent]
    depth: int
    
    def __hash__(self):
        return hash((self.id, self.hypergraph_state))


class MultiwaySystem:
    """
    Sistema Multiway estilo Wolfram.
    
    Explora TODAS las posibles aplicaciones de reglas,
    manteniendo múltiples ramas de evolución simultáneas.
    
    Uso:
        mw = MultiwaySystem(triangle())
        mw.evolve(rule_simple_growth(), steps=3)
        print(f"Ramas: {mw.num_branches}")
    """
    
    __slots__ = ['_branches', '_branch_edges', '_next_branch_id', 
                 '_initial_state', '_rule', '_max_branches']
    
    def __init__(self, initial_hypergraph: WolframHypergraph, max_branches: int = 100):
        self._initial_state = initial_hypergraph.edges
        self._branches: Dict[int, BranchState] = {}
        self._branch_edges: List[Tuple[int, int]] = []  # (parent, child)
        self._next_branch_id = 0
        self._max_branches = max_branches
        self._rule: Optional[RewriteRule] = None
        
        # Crear rama inicial
        initial_branch = BranchState(
            id=self._next_branch_id,
            hypergraph_state=self._initial_state,
            parent_branch=None,
            event=None,
            depth=0
        )
        self._branches[initial_branch.id] = initial_branch
        self._next_branch_id += 1
    
    @property
    def num_branches(self) -> int:
        return len(self._branches)
    
    @property
    def leaves(self) -> List[BranchState]:
        """Ramas sin hijos (estados finales)."""
        parents = {src for src, _ in self._branch_edges}
        return [b for b in self._branches.values() if b.id not in parents]
    
    def _state_to_hg(self, state: HypergraphState) -> WolframHypergraph:
        """Convierte un estado frozen a un WolframHypergraph."""
        hg = WolframHypergraph()
        hg._edges = set(state)
        # Calcular next_element
        for edge in state:
            for elem in edge:
                if elem >= hg._next_element:
                    hg._next_element = elem + 1
        return hg
    
    def evolve(self, rule: RewriteRule, steps: int = 3, 
                max_matches_per_leaf: int = 5) -> int:
        """
        Evoluciona el sistema multiway.
        
        En cada paso, para cada rama hoja:
        - Encuentra hasta max_matches_per_leaf matches
        - Crea una nueva rama por cada match
        
        Args:
            rule: Regla a aplicar
            steps: Número de pasos de evolución
            max_matches_per_leaf: Máximo de matches por hoja (evita explosión)
        
        Returns:
            Número total de ramas generadas
        """
        self._rule = rule
        
        for step in range(steps):
            current_leaves = self.leaves.copy()
            
            for leaf in current_leaves:
                if len(self._branches) >= self._max_branches:
                    break
                
                # Crear hipergrafo temporal
                hg = self._state_to_hg(leaf.hypergraph_state)
                
                # Encontrar matches (limitado para evitar explosión)
                all_matches = rule.find_matches(hg)
                matches = all_matches[:max_matches_per_leaf]  # Limitar
                
                if not matches:
                    continue
                
                # Crear una rama por cada match
                for binding in matches:
                    if len(self._branches) >= self._max_branches:
                        break
                    
                    # Aplicar regla
                    consumed, produced, full_binding = rule.apply(hg, binding)
                    
                    # Calcular nuevo estado
                    new_edges = set(leaf.hypergraph_state) - consumed | produced
                    new_state = frozenset(new_edges)
                    
                    # Crear evento
                    event = UpdateEvent(
                        id=self._next_branch_id,
                        tick=step,
                        rule_name=rule.name,
                        binding=full_binding,
                        consumed=consumed,
                        produced=produced
                    )
                    
                    # Crear nueva rama
                    new_branch = BranchState(
                        id=self._next_branch_id,
                        hypergraph_state=new_state,
                        parent_branch=leaf.id,
                        event=event,
                        depth=leaf.depth + 1
                    )
                    
                    self._branches[new_branch.id] = new_branch
                    self._branch_edges.append((leaf.id, new_branch.id))
                    self._next_branch_id += 1
        
        return len(self._branches)
    
    def unique_states(self) -> Set[HypergraphState]:
        """Estados únicos alcanzados."""
        return {b.hypergraph_state for b in self._branches.values()}
    
    def convergent_branches(self) -> List[List[int]]:
        """Encuentra ramas que convergen al mismo estado."""
        state_to_branches: Dict[HypergraphState, List[int]] = defaultdict(list)
        for branch in self._branches.values():
            state_to_branches[branch.hypergraph_state].append(branch.id)
        
        return [branches for branches in state_to_branches.values() if len(branches) > 1]
    
    def stats(self) -> Dict:
        return {
            'total_branches': len(self._branches),
            'unique_states': len(self.unique_states()),
            'leaf_branches': len(self.leaves),
            'max_depth': max(b.depth for b in self._branches.values()),
            'convergent_groups': len(self.convergent_branches())
        }
    
    def visualize(self) -> str:
        """Visualización ASCII del multiway graph."""
        lines = [
            "╔════════════════════════════════════════════════════════╗",
            "║               MULTIWAY SYSTEM                          ║",
            "╠════════════════════════════════════════════════════════╣",
        ]
        
        stats = self.stats()
        lines.append(f"║ Branches: {stats['total_branches']}  Unique: {stats['unique_states']}  Leaves: {stats['leaf_branches']} ║".ljust(59) + "║")
        lines.append(f"║ Max depth: {stats['max_depth']}  Convergent: {stats['convergent_groups']} ║".ljust(59) + "║")
        
        lines.append("╚════════════════════════════════════════════════════════╝")
        return "\n".join(lines)


# =============================================================================
# WOLFRAM NEURAL LAYER (Embeddings from Structure)
# =============================================================================

class WolframNeuralLayer:
    """
    Capa neural que computa embeddings directamente desde
    la estructura del hipergrafo Wolfram.
    
    A diferencia de HypergraphNeuralLayer del archivo anterior,
    esta versión:
    - No usa labels (solo estructura)
    - Incorpora información causal
    - Usa características topológicas puras
    
    OPTIMIZADO: Vectorización NumPy
    """
    
    __slots__ = ['dim', 'W_struct', 'W_causal', 'W_combine', 
                 '_element_emb', '_edge_emb', '_rng']
    
    def __init__(self, dim: int = 64, seed: int = 42):
        self.dim = dim
        self._rng = np.random.default_rng(seed)
        
        # Parámetros (inicialización Xavier)
        scale = np.sqrt(2.0 / dim)
        self.W_struct = self._rng.standard_normal((dim, dim)) * scale
        self.W_causal = self._rng.standard_normal((dim, dim)) * scale
        self.W_combine = self._rng.standard_normal((dim * 2, dim)) * scale
        
        self._element_emb: Optional[Dict[int, np.ndarray]] = None
        self._edge_emb: Optional[Dict[Edge, np.ndarray]] = None
    
    def compute_embeddings(self, hg: WolframHypergraph, 
                           causal: Optional[CausalNetwork] = None) -> Dict[int, np.ndarray]:
        """
        Computa embeddings para todos los elementos.
        
        Características usadas:
        - Grado (número de hiperaristas que contienen al elemento)
        - Cardinalidad promedio de hiperaristas
        - Vecindario (elementos conectados)
        - (Opcional) Profundidad causal
        """
        elements = list(hg.elements)
        if not elements:
            return {}
        
        max_elem = max(elements) + 1
        
        # Feature 1: Degree (número de edges que contienen al elemento)
        degree = np.zeros(max_elem)
        for edge in hg.edges:
            for elem in edge:
                degree[elem] += 1
        
        # Feature 2: Cardinalidad promedio de edges conteniendo al elemento
        avg_card = np.zeros(max_elem)
        for elem in elements:
            cards = [len(e) for e in hg.edges if elem in e]
            avg_card[elem] = np.mean(cards) if cards else 0
        
        # Feature 3: Número de vecinos
        neighbors = np.zeros(max_elem)
        for elem in elements:
            neighbor_set = set()
            for edge in hg.edges:
                if elem in edge:
                    neighbor_set.update(edge)
            neighbor_set.discard(elem)
            neighbors[elem] = len(neighbor_set)
        
        # Feature 4: Clustering local (edges entre vecinos / posibles)
        clustering = np.zeros(max_elem)
        for elem in elements:
            neighbor_set = set()
            for edge in hg.edges:
                if elem in edge:
                    neighbor_set.update(edge)
            neighbor_set.discard(elem)
            
            if len(neighbor_set) > 1:
                possible = len(neighbor_set) * (len(neighbor_set) - 1) / 2
                actual = 0
                for edge in hg.edges:
                    in_neighbors = sum(1 for n in edge if n in neighbor_set)
                    if in_neighbors >= 2:
                        actual += 1
                clustering[elem] = actual / possible if possible > 0 else 0
        
        # Crear feature vectors
        features = np.zeros((max_elem, 4))
        for elem in elements:
            features[elem] = [
                degree[elem] / (max(degree) + 1e-8),
                avg_card[elem] / 10,  # Normalizado
                neighbors[elem] / (max(neighbors) + 1e-8),
                clustering[elem]
            ]
        
        # Project to embedding space
        # Pad features to dim size, then apply transformation
        padded_features = np.zeros((max_elem, self.dim))
        padded_features[:, :4] = features
        
        # Random projection for initial embeddings
        random_proj = self._rng.standard_normal((4, self.dim)) * 0.1
        embeddings = features @ random_proj
        
        # Apply learned transformation
        embeddings = np.tanh(embeddings @ self.W_struct)
        
        # Add causal information if available
        if causal is not None and causal._events:
            causal_features = np.zeros((max_elem, self.dim))
            
            # For each element, find events that produced edges containing it
            for event in causal._events:
                for edge in event.produced:
                    for elem in edge:
                        if elem < max_elem:
                            # Encode event depth
                            depth = causal._depth.get(event.id, 0)
                            causal_features[elem, depth % self.dim] += 1
            
            # Normalize and transform
            causal_features = causal_features / (np.linalg.norm(causal_features, axis=1, keepdims=True) + 1e-8)
            causal_transformed = np.tanh(causal_features @ self.W_causal)
            
            # Combine structural and causal
            combined = np.concatenate([embeddings, causal_transformed], axis=1)
            embeddings = np.tanh(combined @ self.W_combine)
        
        # Normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8
        embeddings = embeddings / norms
        
        self._element_emb = {elem: embeddings[elem] for elem in elements}
        return self._element_emb
    
    def compute_edge_embeddings(self, hg: WolframHypergraph) -> Dict[Edge, np.ndarray]:
        """Computa embeddings para hiperaristas (agregación de elementos)."""
        if self._element_emb is None:
            self.compute_embeddings(hg)
        
        self._edge_emb = {}
        for edge in hg.edges:
            elem_vecs = np.array([self._element_emb[e] for e in edge if e in self._element_emb])
            if len(elem_vecs) > 0:
                # Mean + Max pooling
                mean_pool = elem_vecs.mean(axis=0)
                max_pool = elem_vecs.max(axis=0)
                self._edge_emb[edge] = (mean_pool + max_pool) / 2
        
        return self._edge_emb
    
    def similarity(self, elem1: int, elem2: int) -> float:
        """Similaridad coseno entre elementos."""
        if self._element_emb is None:
            return 0.0
        if elem1 not in self._element_emb or elem2 not in self._element_emb:
            return 0.0
        
        v1, v2 = self._element_emb[elem1], self._element_emb[elem2]
        return float(np.dot(v1, v2))
    
    def find_similar(self, elem: int, top_k: int = 5) -> List[Tuple[int, float]]:
        """Encuentra los k elementos más similares."""
        if self._element_emb is None or elem not in self._element_emb:
            return []
        
        target = self._element_emb[elem]
        similarities = []
        
        for other, vec in self._element_emb.items():
            if other != elem:
                sim = float(np.dot(target, vec))
                similarities.append((other, sim))
        
        return sorted(similarities, key=lambda x: -x[1])[:top_k]
    
    def stats(self) -> Dict:
        return {
            'dim': self.dim,
            'element_embeddings': len(self._element_emb) if self._element_emb else 0,
            'edge_embeddings': len(self._edge_emb) if self._edge_emb else 0
        }


# =============================================================================
# REGLAS PREDEFINIDAS
# =============================================================================

def rule_simple_growth() -> RewriteRule:
    """{{x,y}} → {{x,y}, {y,z}} - Crecimiento simple"""
    return RewriteRule(
        lhs=[PatternEdge(('_x', '_y'))],
        rhs=[PatternEdge(('_x', '_y')), PatternEdge(('_y', '_z'))],
        name="grow"
    )


def rule_split() -> RewriteRule:
    """{{x,y,z}} → {{x,y}, {y,z}, {z,x}} - División"""
    return RewriteRule(
        lhs=[PatternEdge(('_x', '_y', '_z'))],
        rhs=[PatternEdge(('_x', '_y')), 
             PatternEdge(('_y', '_z')), 
             PatternEdge(('_z', '_x'))],
        name="split"
    )


def rule_wolfram_110() -> RewriteRule:
    """{{x,y}, {x,z}} → {{x,z}, {x,w}, {y,w}, {z,w}} - Regla similar a Rule 110"""
    return RewriteRule(
        lhs=[PatternEdge(('_x', '_y')), PatternEdge(('_x', '_z'))],
        rhs=[PatternEdge(('_x', '_z')), 
             PatternEdge(('_x', '_w')), 
             PatternEdge(('_y', '_w')), 
             PatternEdge(('_z', '_w'))],
        name="wolfram110"
    )


# =============================================================================
# FÁBRICA DE HIPERGRAFOS
# =============================================================================

def triangle() -> WolframHypergraph:
    """Crea un triángulo inicial: {{1,2}, {2,3}, {3,1}}"""
    hg = WolframHypergraph()
    hg.add_edges([{1, 2}, {2, 3}, {3, 1}])
    return hg


def line(n: int = 5) -> WolframHypergraph:
    """Crea una línea: {{1,2}, {2,3}, ..., {n-1,n}}"""
    hg = WolframHypergraph()
    hg.add_edges([{i, i+1} for i in range(1, n)])
    return hg


def star(n: int = 5) -> WolframHypergraph:
    """Crea una estrella: {{1,2}, {1,3}, ..., {1,n}}"""
    hg = WolframHypergraph()
    hg.add_edges([{1, i} for i in range(2, n+1)])
    return hg


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  WOLFRAM PHYSICS HYPERGRAPH - TEST")
    print("=" * 60)
    
    # Crear visualizador
    viz = WolframVisualizer()
    
    # 1. Crear hipergrafo triangular
    print("\n📐 Estado Inicial: Triángulo")
    hg = triangle()
    print(viz.visualize_hypergraph(hg))
    
    # 2. Definir regla de crecimiento
    print("\n📜 Regla: {{x,y}} → {{x,y}, {y,z}}")
    rule = rule_simple_growth()
    print(f"   {rule}")
    
    # 3. Evolucionar
    print("\n⚡ Evolucionando 10 pasos...")
    events = hg.evolve(rule, steps=10)
    print(f"   Eventos generados: {len(events)}")
    
    # 4. Estado final
    print("\n📊 Estado Final:")
    print(viz.visualize_hypergraph(hg))
    
    # 5. Causal network
    print("\n🔗 Red Causal:")
    cn = CausalNetwork(hg)
    print(viz.visualize_causal(cn))
    
    # 6. Mostrar eventos
    print("\n📋 Eventos:")
    print(viz.visualize_events(events))
    
    # 7. Test con regla Wolfram-110
    print("\n" + "=" * 60)
    print("  TEST: Regla tipo Wolfram-110")
    print("=" * 60)
    
    hg2 = star(4)
    print("\n📐 Estado Inicial: Estrella(4)")
    print(f"   {hg2.to_wolfram_notation()}")
    
    rule110 = rule_wolfram_110()
    print(f"\n📜 Regla: {rule110}")
    
    events2 = hg2.evolve(rule110, steps=5)
    print(f"\n⚡ Eventos: {len(events2)}")
    print(viz.visualize_hypergraph(hg2))
    
    cn2 = CausalNetwork(hg2)
    print(viz.visualize_causal(cn2))
    
    print("\n" + "=" * 60)
    print("  WOLFRAM HYPERGRAPH FUNCIONANDO ✓")
    print("=" * 60)
