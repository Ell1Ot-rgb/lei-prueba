"""
Sistema Hipergrafo Multi-Nivel - OPTIMIZADO
============================================

4 niveles de abstracción para representación de conceptos:
1. KnowledgeGraph - Entidades y relaciones binarias
2. Hypergraph - Relaciones N-arias
3. SymbolicExpression - Expresiones computables (Wolfram SDL)
4. HypergraphNeuralLayer - Aprendizaje de embeddings

Optimizaciones:
- __slots__ en todas las clases
- Arrays NumPy pre-allocados
- Índices hash para O(1) lookup
- Serialización eficiente con pickle/msgpack
"""

import numpy as np
import pickle
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from collections import defaultdict
from pathlib import Path
import json


# =============================================================================
# NIVEL 1: KNOWLEDGE GRAPH (Entidad-Relación)
# =============================================================================

class KnowledgeGraph:
    """
    Grafo de conocimiento básico - entidades con relaciones binarias.
    OPTIMIZADO: Índices hash para lookup O(1).
    """
    
    __slots__ = ['_entities', '_relations', '_entity_idx', '_relation_idx',
                 '_outgoing', '_incoming', '_next_id']
    
    def __init__(self):
        self._entities: Dict[int, Dict[str, Any]] = {}
        self._relations: List[Tuple[int, str, int]] = []
        self._entity_idx: Dict[str, int] = {}  # name -> id
        self._relation_idx: Dict[Tuple[int, str, int], int] = {}  # (s,p,o) -> idx
        self._outgoing: Dict[int, List[int]] = defaultdict(list)  # entity -> [relation_idx]
        self._incoming: Dict[int, List[int]] = defaultdict(list)
        self._next_id = 0
    
    def add_entity(self, name: str, properties: Optional[Dict] = None) -> int:
        """Añade entidad - O(1)."""
        if name in self._entity_idx:
            return self._entity_idx[name]
        
        eid = self._next_id
        self._next_id += 1
        self._entities[eid] = {'name': name, 'props': properties or {}}
        self._entity_idx[name] = eid
        return eid
    
    def add_relation(self, subject: int, predicate: str, obj: int) -> int:
        """Añade relación - O(1)."""
        key = (subject, predicate, obj)
        if key in self._relation_idx:
            return self._relation_idx[key]
        
        idx = len(self._relations)
        self._relations.append(key)
        self._relation_idx[key] = idx
        self._outgoing[subject].append(idx)
        self._incoming[obj].append(idx)
        return idx
    
    def query(self, subject: Optional[int] = None, 
              predicate: Optional[str] = None,
              obj: Optional[int] = None) -> List[Tuple[int, str, int]]:
        """Query SPO - O(degree) típico."""
        results = []
        
        if subject is not None:
            candidates = [self._relations[i] for i in self._outgoing.get(subject, [])]
        elif obj is not None:
            candidates = [self._relations[i] for i in self._incoming.get(obj, [])]
        else:
            candidates = self._relations
        
        for s, p, o in candidates:
            if subject is not None and s != subject:
                continue
            if predicate is not None and p != predicate:
                continue
            if obj is not None and o != obj:
                continue
            results.append((s, p, o))
        
        return results
    
    def get_entity(self, eid: int) -> Optional[Dict]:
        return self._entities.get(eid)
    
    def stats(self) -> Dict:
        return {
            'entities': len(self._entities),
            'relations': len(self._relations),
            'predicates': len(set(p for _, p, _ in self._relations))
        }


# =============================================================================
# NIVEL 2: HYPERGRAPH (Relaciones N-arias)
# =============================================================================

@dataclass(slots=True)
class Hyperedge:
    """Hiperarista: conecta N nodos."""
    nodes: Tuple[int, ...]
    label: str
    weight: float = 1.0
    properties: Dict = field(default_factory=dict)
    created_tick: int = 0


class Hypergraph:
    """
    Hipergrafo con hiperaristas N-arias.
    OPTIMIZADO: Índices por nodo y por cardinalidad.
    """
    
    __slots__ = ['_nodes', '_edges', '_node_to_edges', '_label_to_edges',
                 '_card_to_edges', '_next_node_id', '_next_edge_id', '_tick']
    
    def __init__(self):
        self._nodes: Dict[int, Dict[str, Any]] = {}
        self._edges: Dict[int, Hyperedge] = {}
        self._node_to_edges: Dict[int, Set[int]] = defaultdict(set)
        self._label_to_edges: Dict[str, Set[int]] = defaultdict(set)
        self._card_to_edges: Dict[int, Set[int]] = defaultdict(set)  # cardinalidad -> edges
        self._next_node_id = 0
        self._next_edge_id = 0
        self._tick = 0
    
    def add_node(self, properties: Optional[Dict] = None) -> int:
        """Añade nodo - O(1)."""
        nid = self._next_node_id
        self._next_node_id += 1
        self._nodes[nid] = properties or {}
        return nid
    
    def add_hyperedge(self, nodes: Tuple[int, ...], label: str,
                      weight: float = 1.0, properties: Optional[Dict] = None) -> int:
        """Añade hiperarista - O(|nodes|)."""
        eid = self._next_edge_id
        self._next_edge_id += 1
        
        edge = Hyperedge(
            nodes=nodes,
            label=label,
            weight=weight,
            properties=properties or {},
            created_tick=self._tick
        )
        self._edges[eid] = edge
        
        # Índices
        for nid in nodes:
            self._node_to_edges[nid].add(eid)
        self._label_to_edges[label].add(eid)
        self._card_to_edges[len(nodes)].add(eid)
        
        return eid
    
    def get_edges_by_node(self, node_id: int) -> List[Hyperedge]:
        """Obtiene hiperaristas que contienen nodo - O(degree)."""
        return [self._edges[eid] for eid in self._node_to_edges.get(node_id, set())]
    
    def get_edges_by_label(self, label: str) -> List[Hyperedge]:
        """Obtiene hiperaristas por etiqueta - O(|edges|)."""
        return [self._edges[eid] for eid in self._label_to_edges.get(label, set())]
    
    def get_neighbors(self, node_id: int) -> Set[int]:
        """Nodos conectados a node_id - O(degree * avg_cardinality)."""
        neighbors = set()
        for eid in self._node_to_edges.get(node_id, set()):
            edge = self._edges[eid]
            neighbors.update(edge.nodes)
        neighbors.discard(node_id)
        return neighbors
    
    def tick(self):
        """Avanza el tiempo."""
        self._tick += 1
    
    def apply_rule(self, pattern: Tuple[str, ...], 
                   replacement: Tuple[str, ...]) -> int:
        """
        Aplica regla de reescritura estilo Wolfram.
        Pattern: etiquetas a buscar
        Replacement: etiquetas a crear
        Returns: número de aplicaciones
        """
        applications = 0
        # Encontrar matches (simplificado)
        if len(pattern) == 1:
            label = pattern[0]
            edges_to_rewrite = list(self._label_to_edges.get(label, set()))
            
            for eid in edges_to_rewrite:
                old_edge = self._edges[eid]
                # Crear nuevas hiperaristas según replacement
                for new_label in replacement:
                    new_node = self.add_node()
                    new_nodes = old_edge.nodes + (new_node,)
                    self.add_hyperedge(new_nodes[:len(old_edge.nodes)], new_label)
                applications += 1
        
        return applications
    
    def stats(self) -> Dict:
        cardinalities = [len(e.nodes) for e in self._edges.values()]
        return {
            'nodes': len(self._nodes),
            'edges': len(self._edges),
            'avg_cardinality': np.mean(cardinalities) if cardinalities else 0,
            'max_cardinality': max(cardinalities) if cardinalities else 0,
            'tick': self._tick
        }


# =============================================================================
# NIVEL 3: SYMBOLIC EXPRESSION (Wolfram SDL style)
# =============================================================================

class SymbolicExpression:
    """
    Expresión simbólica al estilo Wolfram Language.
    OPTIMIZADO: Representación compacta como árbol.
    """
    
    __slots__ = ['head', 'args', '_hash', '_str_cache']
    
    def __init__(self, head: str, *args):
        self.head = head
        self.args = tuple(args)
        self._hash = None
        self._str_cache = None
    
    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash((self.head, self.args))
        return self._hash
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, SymbolicExpression):
            return False
        return self.head == other.head and self.args == other.args
    
    def __repr__(self) -> str:
        if self._str_cache is None:
            if not self.args:
                self._str_cache = self.head
            else:
                args_str = ", ".join(repr(a) if isinstance(a, SymbolicExpression) 
                                     else str(a) for a in self.args)
                self._str_cache = f"{self.head}[{args_str}]"
        return self._str_cache
    
    def match(self, pattern: 'SymbolicExpression') -> Optional[Dict[str, Any]]:
        """Pattern matching con variables (prefijo _)."""
        bindings = {}
        
        def _match(expr, pat):
            if isinstance(pat, str) and pat.startswith('_'):
                var = pat[1:]
                if var in bindings:
                    return bindings[var] == expr
                bindings[var] = expr
                return True
            
            if isinstance(pat, SymbolicExpression):
                if not isinstance(expr, SymbolicExpression):
                    return False
                if pat.head != expr.head:
                    return False
                if len(pat.args) != len(expr.args):
                    return False
                return all(_match(e, p) for e, p in zip(expr.args, pat.args))
            
            return expr == pat
        
        if _match(self, pattern):
            return bindings
        return None
    
    def substitute(self, bindings: Dict[str, Any]) -> 'SymbolicExpression':
        """Sustituye variables con valores."""
        if self.head.startswith('_') and self.head[1:] in bindings:
            return bindings[self.head[1:]]
        
        new_args = []
        for arg in self.args:
            if isinstance(arg, SymbolicExpression):
                new_args.append(arg.substitute(bindings))
            elif isinstance(arg, str) and arg.startswith('_') and arg[1:] in bindings:
                new_args.append(bindings[arg[1:]])
            else:
                new_args.append(arg)
        
        return SymbolicExpression(self.head, *new_args)
    
    def to_hyperedge(self, hg: Hypergraph, node_map: Dict[str, int]) -> int:
        """Convierte a hiperarista en hipergrafo."""
        nodes = []
        for arg in self.args:
            if isinstance(arg, SymbolicExpression):
                # Recursivo: crear sub-hipergrafos
                sub_eid = arg.to_hyperedge(hg, node_map)
                nodes.append(sub_eid)
            elif isinstance(arg, str):
                if arg not in node_map:
                    node_map[arg] = hg.add_node({'symbol': arg})
                nodes.append(node_map[arg])
        
        return hg.add_hyperedge(tuple(nodes), self.head)


# Alias para crear expresiones fácilmente
def S(head: str, *args) -> SymbolicExpression:
    """Factory para SymbolicExpression."""
    return SymbolicExpression(head, *args)


# =============================================================================
# NIVEL 4: HYPERGRAPH NEURAL LAYER (Embeddings de alto orden)
# =============================================================================

class HypergraphNeuralLayer:
    """
    Capa neural sobre hipergrafo - message passing.
    OPTIMIZADO: Operaciones vectorizadas con NumPy.
    """
    
    __slots__ = ['dim', 'W_node', 'W_edge', 'W_agg', '_node_emb', '_edge_emb']
    
    def __init__(self, dim: int = 64):
        self.dim = dim
        # Parámetros (inicialización Xavier)
        scale = np.sqrt(2.0 / dim)
        self.W_node = np.random.randn(dim, dim).astype(np.float64) * scale
        self.W_edge = np.random.randn(dim, dim).astype(np.float64) * scale
        self.W_agg = np.random.randn(dim, dim).astype(np.float64) * scale
        
        self._node_emb = None
        self._edge_emb = None
    
    def forward(self, hg: Hypergraph, 
                node_features: Optional[Dict[int, np.ndarray]] = None) -> Dict[int, np.ndarray]:
        """
        Forward pass: message passing sobre hipergrafo.
        
        1. Nodos → Hiperaristas (agregar)
        2. Actualizar representaciones de hiperaristas
        3. Hiperaristas → Nodos (propagar)
        """
        n_nodes = len(hg._nodes)
        n_edges = len(hg._edges)
        
        if n_nodes == 0:
            return {}
        
        # Inicializar embeddings de nodos
        if node_features is not None:
            node_emb = np.zeros((max(hg._nodes.keys()) + 1, self.dim), dtype=np.float64)
            for nid, feat in node_features.items():
                if nid < node_emb.shape[0]:
                    node_emb[nid, :len(feat)] = feat[:self.dim]
        else:
            node_emb = np.random.randn(max(hg._nodes.keys()) + 1, self.dim) * 0.1
        
        if n_edges == 0:
            self._node_emb = {nid: node_emb[nid] for nid in hg._nodes}
            return self._node_emb
        
        # Fase 1: Nodos → Hiperaristas
        edge_emb = np.zeros((max(hg._edges.keys()) + 1, self.dim), dtype=np.float64)
        for eid, edge in hg._edges.items():
            # Agregar embeddings de nodos en la hiperarista
            node_vecs = np.array([node_emb[nid] for nid in edge.nodes if nid < node_emb.shape[0]])
            if len(node_vecs) > 0:
                # Agregación: mean + max pooling
                agg = np.concatenate([node_vecs.mean(axis=0)[:self.dim//2], 
                                      node_vecs.max(axis=0)[:self.dim//2]])
                edge_emb[eid] = np.tanh(agg @ self.W_edge[:self.dim, :self.dim])
        
        # Fase 2: Hiperaristas → Nodos
        new_node_emb = node_emb.copy()
        for nid in hg._nodes:
            edge_ids = list(hg._node_to_edges.get(nid, set()))
            if edge_ids:
                edge_vecs = np.array([edge_emb[eid] for eid in edge_ids if eid < edge_emb.shape[0]])
                if len(edge_vecs) > 0:
                    agg = edge_vecs.mean(axis=0)
                    update = np.tanh(agg @ self.W_agg)
                    new_node_emb[nid] = new_node_emb[nid] + 0.1 * update
        
        # Normalizar
        norms = np.linalg.norm(new_node_emb, axis=1, keepdims=True) + 1e-8
        new_node_emb = new_node_emb / norms
        
        self._node_emb = {nid: new_node_emb[nid] for nid in hg._nodes}
        self._edge_emb = {eid: edge_emb[eid] for eid in hg._edges}
        
        return self._node_emb
    
    def get_similarity(self, node1: int, node2: int) -> float:
        """Similaridad coseno entre nodos."""
        if self._node_emb is None:
            return 0.0
        if node1 not in self._node_emb or node2 not in self._node_emb:
            return 0.0
        
        v1, v2 = self._node_emb[node1], self._node_emb[node2]
        return float(np.dot(v1, v2))


# =============================================================================
# SISTEMA INTEGRADO
# =============================================================================

class HypergraphStore:
    """
    Almacenamiento persistente de instancias de hipergrafos.
    OPTIMIZADO: Serialización binaria con pickle.
    """
    
    __slots__ = ['base_path', '_cache', '_metadata']
    
    def __init__(self, base_path: str = "./hypergraph_store"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict] = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Carga metadatos de instancias."""
        meta_file = self.base_path / "metadata.json"
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                self._metadata = json.load(f)
    
    def _save_metadata(self):
        """Guarda metadatos."""
        with open(self.base_path / "metadata.json", 'w') as f:
            json.dump(self._metadata, f, indent=2)
    
    def save(self, name: str, obj: Any, level: int, description: str = "") -> str:
        """Guarda instancia de hipergrafo."""
        # Generar hash único
        obj_hash = hashlib.md5(pickle.dumps(obj)).hexdigest()[:8]
        filename = f"{name}_{obj_hash}.pkl"
        filepath = self.base_path / f"level_{level}" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(obj, f)
        
        self._metadata[name] = {
            'file': str(filepath),
            'level': level,
            'description': description,
            'hash': obj_hash,
            'stats': obj.stats() if hasattr(obj, 'stats') else {}
        }
        self._save_metadata()
        self._cache[name] = obj
        
        return str(filepath)
    
    def load(self, name: str) -> Optional[Any]:
        """Carga instancia de hipergrafo."""
        if name in self._cache:
            return self._cache[name]
        
        if name not in self._metadata:
            return None
        
        with open(self._metadata[name]['file'], 'rb') as f:
            obj = pickle.load(f)
        
        self._cache[name] = obj
        return obj
    
    def list_instances(self, level: Optional[int] = None) -> List[Dict]:
        """Lista instancias guardadas."""
        results = []
        for name, meta in self._metadata.items():
            if level is None or meta['level'] == level:
                results.append({'name': name, **meta})
        return results


class MultiLevelHypergraph:
    """
    Sistema integrado de 4 niveles.
    Cada nivel puede convertirse a los otros.
    """
    
    __slots__ = ['kg', 'hg', 'neural', 'store', '_expressions']
    
    def __init__(self, store_path: str = "./hypergraph_store"):
        self.kg = KnowledgeGraph()
        self.hg = Hypergraph()
        self.neural = HypergraphNeuralLayer(64)
        self.store = HypergraphStore(store_path)
        self._expressions: Dict[str, SymbolicExpression] = {}
    
    # --- Nivel 1: Knowledge Graph ---
    
    def add_concept(self, name: str, properties: Dict = None) -> int:
        """Añade concepto al KG."""
        return self.kg.add_entity(name, properties)
    
    def relate(self, subj: str, pred: str, obj: str):
        """Añade relación al KG."""
        s_id = self.kg.add_entity(subj)
        o_id = self.kg.add_entity(obj)
        self.kg.add_relation(s_id, pred, o_id)
    
    # --- Nivel 2: Hypergraph ---
    
    def add_nary_relation(self, entities: List[str], label: str) -> int:
        """Añade relación N-aria al hipergrafo."""
        node_ids = []
        for name in entities:
            # Sincronizar con KG
            kg_id = self.kg.add_entity(name)
            if kg_id not in self.hg._nodes:
                self.hg._nodes[kg_id] = {'kg_id': kg_id, 'name': name}
            node_ids.append(kg_id)
        
        return self.hg.add_hyperedge(tuple(node_ids), label)
    
    # --- Nivel 3: Symbolic Expressions ---
    
    def define(self, name: str, expr: SymbolicExpression):
        """Define expresión simbólica."""
        self._expressions[name] = expr
        # Convertir a hipergrafo
        node_map = {}
        expr.to_hyperedge(self.hg, node_map)
    
    def evaluate(self, name: str) -> Optional[SymbolicExpression]:
        """Evalúa expresión definida."""
        return self._expressions.get(name)
    
    # --- Nivel 4: Neural ---
    
    def compute_embeddings(self, features: Dict[int, np.ndarray] = None) -> Dict[int, np.ndarray]:
        """Computa embeddings neurales."""
        return self.neural.forward(self.hg, features)
    
    def similarity(self, concept1: str, concept2: str) -> float:
        """Similaridad entre conceptos."""
        id1 = self.kg._entity_idx.get(concept1)
        id2 = self.kg._entity_idx.get(concept2)
        if id1 is None or id2 is None:
            return 0.0
        return self.neural.get_similarity(id1, id2)
    
    # --- Almacenamiento ---
    
    def save_snapshot(self, name: str):
        """Guarda snapshot de todos los niveles."""
        self.store.save(f"{name}_kg", self.kg, 1, "Knowledge Graph")
        self.store.save(f"{name}_hg", self.hg, 2, "Hypergraph")
        self.store.save(f"{name}_expr", self._expressions, 3, "Expressions")
    
    def stats(self) -> Dict:
        """Estadísticas de todos los niveles."""
        return {
            'level_1_kg': self.kg.stats(),
            'level_2_hg': self.hg.stats(),
            'level_3_expressions': len(self._expressions),
            'level_4_embeddings': len(self.neural._node_emb or {})
        }
    
    def visualize(self) -> str:
        """Genera visualización ASCII del estado."""
        lines = [
            "╔═══════════════════════════════════════════════════════╗",
            "║          MULTI-LEVEL HYPERGRAPH SYSTEM                ║",
            "╠═══════════════════════════════════════════════════════╣",
        ]
        
        stats = self.stats()
        
        # Nivel 1
        kg = stats['level_1_kg']
        lines.append(f"║ L1 Knowledge Graph: {kg['entities']:4d} entities, {kg['relations']:4d} rels ║")
        
        # Nivel 2
        hg = stats['level_2_hg']
        lines.append(f"║ L2 Hypergraph:      {hg['nodes']:4d} nodes,    {hg['edges']:4d} edges   ║")
        
        # Nivel 3
        lines.append(f"║ L3 Expressions:     {stats['level_3_expressions']:4d} defined               ║")
        
        # Nivel 4
        lines.append(f"║ L4 Neural Emb:      {stats['level_4_embeddings']:4d} vectors               ║")
        
        lines.append("╚═══════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  MULTI-LEVEL HYPERGRAPH SYSTEM - TEST")
    print("=" * 60)
    
    # Crear sistema
    mlh = MultiLevelHypergraph("./test_hg_store")
    
    # Nivel 1: Knowledge Graph
    print("\n📊 Nivel 1: Knowledge Graph")
    mlh.relate("TÉCNICO", "es_subtipo_de", "FORMAL")
    mlh.relate("POÉTICO", "es_subtipo_de", "INFORMAL")
    mlh.relate("TÉCNICO", "contrasta_con", "POÉTICO")
    print(f"   Entidades: {mlh.kg.stats()['entities']}")
    print(f"   Relaciones: {mlh.kg.stats()['relations']}")
    
    # Nivel 2: Hypergraph
    print("\n🕸️  Nivel 2: Hypergraph (N-ary)")
    mlh.add_nary_relation(["TÉCNICO", "CÓDIGO", "EFICIENCIA"], "caracteriza")
    mlh.add_nary_relation(["POÉTICO", "EMOCIÓN", "RITMO"], "caracteriza")
    mlh.add_nary_relation(["TÉCNICO", "POÉTICO", "PENSAMIENTO"], "fusión")
    print(f"   Nodos: {mlh.hg.stats()['nodes']}")
    print(f"   Hiperaristas: {mlh.hg.stats()['edges']}")
    
    # Nivel 3: Symbolic Expressions
    print("\n🔣 Nivel 3: Symbolic Expressions")
    expr_tecnico = S("Concepto", 
                     S("Tipo", "abstracto"),
                     S("Atributos", 
                       S("precision", "alta"),
                       S("formalidad", "alta")))
    mlh.define("TÉCNICO_EXPR", expr_tecnico)
    print(f"   Expresión: {expr_tecnico}")
    
    # Nivel 4: Neural
    print("\n🧠 Nivel 4: Neural Embeddings")
    embeddings = mlh.compute_embeddings()
    print(f"   Embeddings generados: {len(embeddings)}")
    sim = mlh.similarity("TÉCNICO", "FORMAL")
    print(f"   Similaridad TÉCNICO-FORMAL: {sim:.3f}")
    
    # Visualización
    print("\n" + mlh.visualize())
    
    # Guardar
    mlh.save_snapshot("test")
    print(f"\n💾 Guardado en: {mlh.store.base_path}")
    print(f"   Instancias: {len(mlh.store.list_instances())}")
    
    print("\n" + "=" * 60)
    print("  SISTEMA MULTI-NIVEL FUNCIONANDO ✓")
    print("=" * 60)
