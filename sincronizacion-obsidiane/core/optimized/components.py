"""
Organismo Vivo v100 - Sistema Optimizado
=========================================

Arquitectura optimizada para hardware restringido:
- CPU: 2 núcleos
- RAM: 4 GB
- Memoria del sistema: < 1 MB persistente
- Latencia: < 1 ms por evento
"""

import numpy as np
from typing import List, Dict, Any, Callable
from collections import defaultdict, deque
import time
import mmh3


class TokenizerLite:
    """
    ESPECIFICACIÓN: TokenizerLite
    - Vocabulario: 8,192 tokens (BPE pre-entrenado)
    - Entrada: string UTF-8
    - Salida: List[int] de índices de tokens
    - Memoria: 160 KB (vocabulario) + O(|texto|) temporal
    - Complejidad: O(|texto| * log(vocab_size))
    """
    
    def __init__(self, vocab_path: str = None):
        self.vocab_size = 8192
        self.token_to_id = {}
        self.id_to_token = []
        
        # Vocabulario básico (en producción cargar desde archivo)
        if vocab_path:
            self._load_vocab(vocab_path)
        else:
            self._init_basic_vocab()
    
    def _init_basic_vocab(self):
        """Inicializar vocabulario básico para testing."""
        # Caracteres comunes + tokens especiales
        chars = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:!?-\n")
        for i, char in enumerate(chars):
            self.token_to_id[char] = i
            self.id_to_token.append(char)
        
        # Palabras comunes (simplificado)
        common_words = ["el", "la", "de", "que", "y", "a", "en", "un", "ser", "se"]
        for word in common_words:
            if word not in self.token_to_id:
                idx = len(self.id_to_token)
                self.token_to_id[word] = idx
                self.id_to_token.append(word)
    
    def _load_vocab(self, vocab_path: str):
        """Cargar vocabulario desde archivo."""
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f):
                    if idx >= self.vocab_size:
                        break
                    token = line.strip()
                    self.token_to_id[token] = idx
                    self.id_to_token.append(token)
        except FileNotFoundError:
            self._init_basic_vocab()
    
    def encode(self, text: str, max_tokens: int = 128) -> List[int]:
        """Tokenizar texto usando BPE greedy simplificado."""
        if not text:
            return []
        
        # Simplificación: tokenización por caracteres
        tokens = []
        for char in text[:max_tokens]:
            token_id = self.token_to_id.get(char, 0)  # 0 = UNK
            tokens.append(token_id)
        
        return tokens[:max_tokens]
    
    def decode(self, token_ids: List[int]) -> str:
        """Reconstruir texto desde tokens."""
        chars = []
        for tid in token_ids:
            if 0 <= tid < len(self.id_to_token):
                chars.append(self.id_to_token[tid])
        return ''.join(chars)


class EmbedderCompact:
    """
    ESPECIFICACIÓN: EmbedderCompact
    - Dimensión de embedding: 64 (reducido de 768 típico)
    - Cuantización: int8 con escala float32
    - Memoria: 8192 * 64 * 1 byte = 512 KB
    - Lookup: O(1)
    - Agregación: promedio de tokens
    """
    
    def __init__(self, vocab_size: int = 8192, embed_dim: int = 64):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        
        # Embeddings cuantizados a int8
        self.embeddings = np.random.randint(-128, 127, 
                                           size=(vocab_size, embed_dim), 
                                           dtype=np.int8)
        self.scale = 0.02
        self.zero_point = 0
    
    def load_quantized(self, path: str):
        """Cargar embeddings pre-cuantizados."""
        try:
            data = np.load(path)
            self.embeddings = data['embeddings']
            self.scale = float(data['scale'])
            self.zero_point = float(data['zero_point'])
        except FileNotFoundError:
            pass  # Usar embeddings aleatorios inicializados
    
    def embed(self, token_ids: List[int]) -> np.ndarray:
        """
        Retorna embedding float32 de dimensión 64.
        
        Pasos:
        1. Lookup de embeddings int8
        2. Dequantización: float = (int8 - zero_point) * scale
        3. Promedio sobre tokens
        """
        if not token_ids:
            return np.zeros(self.embed_dim, dtype=np.float32)
        
        # Filtrar IDs válidos
        valid_ids = [tid for tid in token_ids if 0 <= tid < self.vocab_size]
        if not valid_ids:
            return np.zeros(self.embed_dim, dtype=np.float32)
        
        emb_int = self.embeddings[valid_ids]  # (n, 64) int8
        emb_float = (emb_int.astype(np.float32) - self.zero_point) * self.scale
        return emb_float.mean(axis=0)


class ClassifierYO:
    """
    ESPECIFICACIÓN: ClassifierYO
    - Clases: 3 (Dasein, Vorhandene, Zuhandene)
    - Modelo: Regresión logística multinomial
    - Parámetros: 3 * 64 + 3 = 195 floats = 780 bytes
    - Entrenamiento: SGD online con learning rate decay
    - Inferencia: O(64 * 3) = O(192) operaciones
    """
    
    CLASSES = ['Dasein', 'Vorhandene', 'Zuhandene']
    
    def __init__(self, embed_dim: int = 64):
        self.embed_dim = embed_dim
        self.W = np.random.randn(3, embed_dim).astype(np.float32) * 0.01
        self.b = np.zeros(3, dtype=np.float32)
        self.t = 0
    
    def predict(self, embedding: np.ndarray) -> int:
        """Retorna índice de clase (0, 1, 2)."""
        logits = embedding @ self.W.T + self.b
        return int(np.argmax(logits))
    
    def predict_proba(self, embedding: np.ndarray) -> np.ndarray:
        """Retorna probabilidades softmax."""
        logits = embedding @ self.W.T + self.b
        exp_logits = np.exp(logits - logits.max())
        return exp_logits / exp_logits.sum()
    
    def update(self, embedding: np.ndarray, true_label: int):
        """
        SGD step con cross-entropy loss.
        Learning rate: η_t = η_0 / sqrt(t)
        """
        self.t += 1
        eta = 0.1 / np.sqrt(self.t)
        
        probs = self.predict_proba(embedding)
        probs[true_label] -= 1  # Gradiente de cross-entropy
        
        self.W -= eta * np.outer(probs, embedding)
        self.b -= eta * probs


class MDCEManager:
    """
    ESPECIFICACIÓN: MDCEManager (Resolución de Contradicciones)
    - Estructura: Union-Find con path compression
    - Capacidad: 10,000 instancias máximo
    - Memoria: 10,000 * 4 bytes = 40 KB
    - Operaciones: O(α(n)) ≈ O(1) amortizado
    """
    
    def __init__(self, max_instances: int = 10000):
        self.max_instances = max_instances
        # Empaquetado: [parent:20][rank:4][type:8]
        self.data = np.arange(max_instances, dtype=np.int32) << 12
        self.instance_count = 0
    
    def _pack(self, parent: int, rank: int, type_yo: int) -> int:
        return (parent << 12) | (rank << 8) | (type_yo & 0xFF)
    
    def _unpack(self, val: int) -> tuple:
        parent = val >> 12
        rank = (val >> 8) & 0xF
        type_yo = val & 0xFF
        return parent, rank, type_yo
    
    def find(self, x: int) -> int:
        """Find con path compression."""
        if x >= self.instance_count:
            return x
        
        root = x
        parent, _, _ = self._unpack(self.data[root])
        while parent != root:
            root = parent
            parent, _, _ = self._unpack(self.data[root])
        
        # Path compression
        while x != root:
            parent, rank, type_yo = self._unpack(self.data[x])
            self.data[x] = self._pack(root, rank, type_yo)
            x = parent
        
        return root
    
    def union(self, x: int, y: int, new_type: int = None):
        """Union by rank con asignación de tipo."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        
        px, rankx, typex = self._unpack(self.data[rx])
        py, ranky, typey = self._unpack(self.data[ry])
        
        # Union by rank
        if rankx < ranky:
            rx, ry = ry, rx
            rankx, ranky = ranky, rankx
            typex, typey = typey, typex
        
        self.data[ry] = self._pack(rx, ranky, new_type if new_type else typex)
        if rankx == ranky:
            self.data[rx] = self._pack(rx, rankx + 1, typex)
    
    def add_instance(self, type_yo: int) -> int:
        """Registrar nueva instancia, retorna ID."""
        if self.instance_count >= self.max_instances:
            raise MemoryError("Límite de instancias alcanzado")
        
        idx = self.instance_count
        self.data[idx] = self._pack(idx, 0, type_yo)
        self.instance_count += 1
        return idx
    
    def check_contradiction(self, i: int, j: int, 
                           similarity: float, threshold: float = 0.8) -> bool:
        """Detectar si i,j están en contradicción."""
        if i >= self.instance_count or j >= self.instance_count:
            return False
        
        _, _, type_i = self._unpack(self.data[self.find(i)])
        _, _, type_j = self._unpack(self.data[self.find(j)])
        
        return similarity > threshold and type_i != type_j


class GrundzugTracker:
    """
    ESPECIFICACIÓN: GrundzugTracker
    - Algoritmo: Count-Min Sketch con Conservative Update
    - Parámetros: width=2048, depth=4
    - Memoria: 4 * 2048 * 2 bytes = 16 KB
    - Error: ε = e/2048 ≈ 0.00133
    - Probabilidad de fallo: δ = e^(-4) ≈ 0.018
    """
    
    def __init__(self, width: int = 2048, depth: int = 4, 
                 window_size: int = 1000, threshold: float = 0.01):
        self.width = width
        self.depth = depth
        self.threshold = threshold
        self.window_size = window_size
        
        # Sketch principal (total)
        self.sketch = np.zeros((depth, width), dtype=np.uint16)
        # Sketch de ventana (reciente)
        self.window_sketch = np.zeros((depth, width), dtype=np.uint16)
        # Cola para ventana deslizante
        self.window_queue = deque(maxlen=window_size)
        
        self.total_count = 0
    
    def _hash(self, item: int, seed: int) -> int:
        return mmh3.hash(str(item), seed) % self.width
    
    def _get_indices(self, item: int) -> List[int]:
        return [self._hash(item, d) for d in range(self.depth)]
    
    def update(self, feature: int):
        """Actualizar sketches con conservative update."""
        indices = self._get_indices(feature)
        
        # Conservative update para sketch principal
        min_val = min(self.sketch[d, idx] for d, idx in enumerate(indices))
        for d, idx in enumerate(indices):
            self.sketch[d, idx] = max(self.sketch[d, idx], min_val + 1)
        
        # Actualizar sketch de ventana
        for d, idx in enumerate(indices):
            if self.window_sketch[d, idx] < 65535:
                self.window_sketch[d, idx] += 1
        
        # Mantener ventana deslizante
        if len(self.window_queue) == self.window_size:
            old_feature = self.window_queue[0]
            old_indices = self._get_indices(old_feature)
            for d, idx in enumerate(old_indices):
                if self.window_sketch[d, idx] > 0:
                    self.window_sketch[d, idx] -= 1
        
        self.window_queue.append(feature)
        self.total_count += 1
    
    def estimate(self, feature: int) -> int:
        """Estimar frecuencia total."""
        indices = self._get_indices(feature)
        return min(self.sketch[d, idx] for d, idx in enumerate(indices))
    
    def estimate_window(self, feature: int) -> int:
        """Estimar frecuencia en ventana."""
        indices = self._get_indices(feature)
        return min(self.window_sketch[d, idx] for d, idx in enumerate(indices))
    
    def is_grundzug(self, feature: int) -> bool:
        """
        Un feature es Grundzug si:
        1. Frecuencia total relativa > threshold
        2. Frecuencia en ventana relativa > threshold
        """
        if self.total_count == 0 or len(self.window_queue) == 0:
            return False
        
        freq_total = self.estimate(feature) / self.total_count
        freq_window = self.estimate_window(feature) / len(self.window_queue)
        
        return freq_total > self.threshold and freq_window > self.threshold


class EmotionEngine:
    """
    ESPECIFICACIÓN: EmotionEngine
    - Modelo: PAD (Pleasure-Arousal-Dominance)
    - Estado: 3 floats = 12 bytes
    - Dinámica: S_{t+1} = λS_t + (1-λ)E_t, λ=0.9
    - Rango: [-1, 1]^3
    """
    
    def __init__(self, decay: float = 0.9):
        self.state = np.zeros(3, dtype=np.float32)  # [P, A, D]
        self.decay = decay
    
    def update(self, event_vector: np.ndarray):
        """
        Actualizar estado emocional.
        event_vector: primeras 3 dimensiones del embedding.
        """
        # Normalizar evento al rango [-1, 1]
        event_norm = np.tanh(event_vector[:3])
        
        # Dinámica exponencial
        self.state = self.decay * self.state + (1 - self.decay) * event_norm
    
    def get_state(self) -> np.ndarray:
        return self.state.copy()
    
    def get_valence(self) -> str:
        """Interpretar estado emocional."""
        p, a, d = self.state
        if p > 0.3 and a > 0.3:
            return "entusiasta"
        elif p > 0.3 and a < -0.3:
            return "relajado"
        elif p < -0.3 and a > 0.3:
            return "ansioso"
        elif p < -0.3 and a < -0.3:
            return "deprimido"
        else:
            return "neutral"
