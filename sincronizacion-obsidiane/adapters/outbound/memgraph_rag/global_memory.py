"""
GlobalMemory — Memoria Global de 3 Capas para MemGraphRAG
==========================================================

Implementa la estructura de memoria global descrita en el paper:
  "MemGraphRAG: Memory-based Multi-Agent System for Graph RAG"
  Sección 4.1 — MemGraphRAG Architecture

La Global Memory (M) organiza el conocimiento extraído en 3 capas:

    M_ont (Ontology Layer):
        - Almacena esquemas s=(t_h, r, t_t) con frecuencias de extracción
        - Un esquema se "estabiliza" cuando su frecuencia ≥ umbral
        - Solo hechos con esquemas estables pasan al grafo de indexación

    M_fac (Fact Layer):
        - Almacena hechos concretos f=(e_h, r, e_t)
        - Vinculados a sus esquemas para consistencia
        - Sujetos a detección de conflictos por A_det

    M_pas (Passage Layer):
        - Preserva los pasajes textuales originales de evidencia
        - Función ψ: fact → passage para trazabilidad
        - Permite a A_res adjudicar conflictos con evidencia real

Referencia: Section 4.1 + Appendix D.2 del paper
"""

import time
import logging
import hashlib
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Estructuras de datos
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Schema:
    """
    Esquema s = (t_h, r, t_t) — Define una restricción lógica válida.
    
    Ejemplo: (person, born_in, country)
    
    El esquema se promueve a "estable" cuando su frecuencia de extracción
    supera el umbral SCHEMA_FREQ_THRESHOLD (default: 2).
    """
    tipo_head: str           # t_h — tipo del sujeto (e.g. "persona")
    relacion: str            # r  — relación semántica (e.g. "born_in")
    tipo_tail: str           # t_t — tipo del objeto (e.g. "país")
    frecuencia: int = 1      # Contador de veces que se ha observado
    estable: bool = False    # True cuando frecuencia >= umbral
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            contenido = f"{self.tipo_head}|{self.relacion}|{self.tipo_tail}"
            self.id = hashlib.md5(contenido.encode()).hexdigest()[:12]

    def clave(self) -> str:
        return f"{self.tipo_head}|{self.relacion}|{self.tipo_tail}"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "tipo_head": self.tipo_head,
            "relacion": self.relacion,
            "tipo_tail": self.tipo_tail,
            "frecuencia": self.frecuencia,
            "estable": self.estable,
        }


@dataclass
class Fact:
    """
    Hecho f = (e_h, r, e_t) — Instancia concreta de un esquema.
    
    Ejemplo: (Einstein, born_in, Alemania)
    
    Vinculado a su esquema (schema_id) y a su pasaje fuente (passage_id).
    """
    entidad_head: str        # e_h — entidad sujeto (e.g. "Einstein")
    relacion: str            # r   — relación concreta
    entidad_tail: str        # e_t — entidad objeto (e.g. "Alemania")
    schema_id: str           # Referencia al esquema padre
    passage_id: str          # Referencia al pasaje de evidencia ψ(f)=p
    confianza: float = 1.0   # Puntuación de confianza (0-1)
    activo: bool = True      # False si fue marcado como inválido por A_res
    timestamp: float = field(default_factory=time.time)
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            contenido = (
                f"{self.entidad_head}|{self.relacion}|{self.entidad_tail}"
                f"|{self.passage_id}"
            )
            self.id = hashlib.md5(contenido.encode()).hexdigest()[:16]

    def clave(self) -> str:
        return f"{self.entidad_head}|{self.relacion}|{self.entidad_tail}"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entidad_head": self.entidad_head,
            "relacion": self.relacion,
            "entidad_tail": self.entidad_tail,
            "schema_id": self.schema_id,
            "passage_id": self.passage_id,
            "confianza": self.confianza,
            "activo": self.activo,
            "timestamp": self.timestamp,
        }


@dataclass
class Passage:
    """
    Pasaje p — Fragmento de texto fuente de evidencia.
    
    Función ψ: fact → passage garantiza que cada hecho tenga
    trazabilidad hacia el texto original que lo generó.
    """
    texto: str               # Contenido textual del fragmento
    fuente: str = ""         # Identificador de la fuente (archivo, fecha, etc.)
    tipo_fuente: str = ""    # "diario", "conversacion", "nota", etc.
    embedding: Optional[np.ndarray] = None  # Vector semántico (opcional)
    timestamp: float = field(default_factory=time.time)
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            contenido = f"{self.fuente}|{self.texto[:100]}"
            self.id = hashlib.md5(contenido.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "texto": self.texto,
            "fuente": self.fuente,
            "tipo_fuente": self.tipo_fuente,
            "timestamp": self.timestamp,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Clase principal GlobalMemory
# ─────────────────────────────────────────────────────────────────────────────

class GlobalMemory:
    """
    Implementa la Memoria Global (M) de 3 capas del paper MemGraphRAG.

    Proporciona un repositorio unificado de conocimiento que permite a los
    agentes mantener un contexto global durante la extracción, detectar
    conflictos inter-documentos y asegurar coherencia estructural.

    Arquitectura de 3 capas:
        M_ont: Capa de ontología (esquemas estabilizados por frecuencia)
        M_fac: Capa de hechos (tripletas concretas con estado de validez)
        M_pas: Capa de pasajes (evidencia textual de grounding)

    Mecanismo de indexación densa:
        - Schema-instance alignment: M_ont ↔ M_fac
        - Fact-evidence grounding: M_fac ↔ M_pas
    """

    def __init__(self, schema_freq_threshold: int = None):
        """
        Args:
            schema_freq_threshold: Umbral de frecuencia para estabilizar esquemas.
                                   Default: env var SCHEMA_FREQ_THRESHOLD o 2.
        """
        # Umbral de frecuencia para promoión de esquemas a "estables"
        self.schema_freq_threshold = int(
            schema_freq_threshold
            or os.environ.get("SCHEMA_FREQ_THRESHOLD", "2")
        )

        # ─── M_ont: Ontology Layer ───
        # Diccionario: clave_esquema → Schema
        self.M_ont: Dict[str, Schema] = {}

        # ─── M_fac: Fact Layer ───
        # Diccionario: id_hecho → Fact
        self.M_fac: Dict[str, Fact] = {}
        # Índice inverso: clave_hecho (sin passage_id) → Set de fact_ids
        self._fac_por_clave: Dict[str, Set[str]] = {}

        # ─── M_pas: Passage Layer ───
        # Diccionario: id_pasaje → Passage
        self.M_pas: Dict[str, Passage] = {}

        # ─── Índices cruzados (indexación densa) ───
        # Schema → Hechos que lo instancian
        self._schema_to_facts: Dict[str, Set[str]] = {}  # schema_id → Set[fact_id]
        # Fact → Pasaje que lo evidencia
        self._fact_to_passage: Dict[str, str] = {}       # fact_id → passage_id
        # Pasaje → Hechos que lo citan
        self._passage_to_facts: Dict[str, Set[str]] = {} # passage_id → Set[fact_id]

        logger.info(
            f"[GlobalMemory] Inicializada — umbral esquemas: {self.schema_freq_threshold}"
        )

    # ─── Capa de Ontología (M_ont) ───────────────────────────────────────────

    def agregar_schema_candidato(
        self,
        tipo_head: str,
        relacion: str,
        tipo_tail: str,
    ) -> Tuple[Schema, bool]:
        """
        Agrega un esquema candidato o incrementa su frecuencia si ya existe.
        
        Un esquema se promueve a 'estable' cuando su frecuencia alcanza el umbral.
        Solo hechos de esquemas estables se activan para construcción del grafo.

        Returns:
            (schema, fue_promovido): El esquema y si fue promovido a estable
        """
        clave = f"{tipo_head}|{relacion}|{tipo_tail}"
        fue_promovido = False

        if clave in self.M_ont:
            schema = self.M_ont[clave]
            schema.frecuencia += 1
            # Verificar si alcanza el umbral de estabilidad
            if not schema.estable and schema.frecuencia >= self.schema_freq_threshold:
                schema.estable = True
                fue_promovido = True
                logger.debug(
                    f"[GlobalMemory] Esquema promovido a estable: {clave} "
                    f"(frecuencia={schema.frecuencia})"
                )
        else:
            schema = Schema(
                tipo_head=tipo_head,
                relacion=relacion,
                tipo_tail=tipo_tail,
                frecuencia=1,
                estable=(self.schema_freq_threshold <= 1),  # Estable inmediato si umbral=1
            )
            self.M_ont[clave] = schema
            self._schema_to_facts[schema.id] = set()

        return schema, fue_promovido

    def obtener_schemas_estables(self) -> List[Schema]:
        """Retorna todos los esquemas estabilizados (frecuencia >= umbral)."""
        return [s for s in self.M_ont.values() if s.estable]

    def obtener_schema_por_id(self, schema_id: str) -> Optional[Schema]:
        """Busca un esquema por su ID."""
        for schema in self.M_ont.values():
            if schema.id == schema_id:
                return schema
        return None

    def esquemas_similares(self, relacion: str, top_k: int = 5) -> List[Schema]:
        """
        Busca esquemas con relaciones semánticamente similares.
        Búsqueda simple por substring para la versión sin embeddings.
        """
        resultados = []
        rel_lower = relacion.lower()
        for schema in self.M_ont.values():
            if schema.estable and (
                rel_lower in schema.relacion.lower()
                or schema.relacion.lower() in rel_lower
            ):
                resultados.append(schema)
        return resultados[:top_k]

    # ─── Capa de Hechos (M_fac) ──────────────────────────────────────────────

    def agregar_hecho(
        self,
        entidad_head: str,
        relacion: str,
        entidad_tail: str,
        schema_id: str,
        passage_id: str,
        confianza: float = 1.0,
    ) -> Optional[Fact]:
        """
        Agrega un hecho a la capa de hechos si su esquema es estable.
        
        Solo hechos con esquemas estables son activados para el grafo.
        Los hechos candidatos (con esquemas inestables) no se agregan.

        Returns:
            El hecho creado, o None si el esquema no está estabilizado
        """
        # Verificar que el esquema esté estabilizado
        schema = self.obtener_schema_por_id(schema_id)
        if schema is None or not schema.estable:
            logger.debug(
                f"[GlobalMemory] Hecho descartado — esquema no estabilizado: "
                f"{entidad_head}|{relacion}|{entidad_tail}"
            )
            return None

        hecho = Fact(
            entidad_head=entidad_head,
            relacion=relacion,
            entidad_tail=entidad_tail,
            schema_id=schema_id,
            passage_id=passage_id,
            confianza=confianza,
        )

        # Almacenar el hecho
        self.M_fac[hecho.id] = hecho

        # Actualizar índice por clave de tripleta
        clave = hecho.clave()
        if clave not in self._fac_por_clave:
            self._fac_por_clave[clave] = set()
        self._fac_por_clave[clave].add(hecho.id)

        # Actualizar indexación densa: schema → facts
        if schema_id in self._schema_to_facts:
            self._schema_to_facts[schema_id].add(hecho.id)

        # Actualizar indexación densa: fact → passage
        self._fact_to_passage[hecho.id] = passage_id
        if passage_id not in self._passage_to_facts:
            self._passage_to_facts[passage_id] = set()
        self._passage_to_facts[passage_id].add(hecho.id)

        return hecho

    def obtener_hechos_similares(
        self,
        entidad_head: str,
        relacion: str,
        entidad_tail: str = None,
    ) -> List[Fact]:
        """
        Obtiene hechos semánticamente similares para detección de conflictos.
        Búsqueda por entidad head + relación (con variantes de la tail).
        """
        resultados = []
        for hecho in self.M_fac.values():
            if not hecho.activo:
                continue
            # Coincidencia en head + relación
            if (
                hecho.entidad_head.lower() == entidad_head.lower()
                and hecho.relacion.lower() == relacion.lower()
            ):
                resultados.append(hecho)
            # Coincidencia en tail + relación (inversa)
            elif (
                entidad_tail
                and hecho.entidad_tail.lower() == entidad_tail.lower()
                and hecho.relacion.lower() == relacion.lower()
            ):
                resultados.append(hecho)
        return resultados

    def desactivar_hecho(self, fact_id: str, razon: str = "") -> None:
        """Marca un hecho como inválido (resultado de resolución de conflicto)."""
        if fact_id in self.M_fac:
            self.M_fac[fact_id].activo = False
            logger.debug(
                f"[GlobalMemory] Hecho desactivado: {fact_id} — {razon}"
            )

    def obtener_hechos_activos(self) -> List[Fact]:
        """Retorna todos los hechos activos (no invalidados)."""
        return [f for f in self.M_fac.values() if f.activo]

    def obtener_hechos_por_schema(self, schema_id: str) -> List[Fact]:
        """Retorna todos los hechos que instancian un esquema dado."""
        fact_ids = self._schema_to_facts.get(schema_id, set())
        return [self.M_fac[fid] for fid in fact_ids if fid in self.M_fac]

    # ─── Capa de Pasajes (M_pas) ─────────────────────────────────────────────

    def agregar_pasaje(
        self,
        texto: str,
        fuente: str = "",
        tipo_fuente: str = "",
        embedding: Optional[np.ndarray] = None,
    ) -> Passage:
        """
        Agrega un pasaje de evidencia a la capa de pasajes.
        
        Los pasajes son la "fuente de verdad" que permite a A_res
        adjudicar conflictos comparando evidencia textual real.
        """
        pasaje = Passage(
            texto=texto,
            fuente=fuente,
            tipo_fuente=tipo_fuente,
            embedding=embedding,
        )

        # Evitar duplicados por ID (el hash incluye texto+fuente)
        if pasaje.id not in self.M_pas:
            self.M_pas[pasaje.id] = pasaje
            self._passage_to_facts[pasaje.id] = set()

        return self.M_pas[pasaje.id]

    def obtener_pasaje(self, passage_id: str) -> Optional[Passage]:
        """Retorna el pasaje de evidencia por su ID."""
        return self.M_pas.get(passage_id)

    def obtener_pasajes_de_hecho(self, fact_id: str) -> Optional[Passage]:
        """
        Función ψ: fact → passage — Trazabilidad de hechos a sus pasajes.
        Permite a A_res recuperar la evidencia textual de cualquier hecho.
        """
        passage_id = self._fact_to_passage.get(fact_id)
        if passage_id:
            return self.M_pas.get(passage_id)
        return None

    def buscar_pasajes_por_similitud(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Tuple[Passage, float]]:
        """
        Busca pasajes por similitud con el query (fallback léxico sin embeddings).
        
        Si los pasajes tienen embeddings, usa similitud coseno.
        Si no, usa matching de palabras clave (TF-IDF simple).
        """
        query_tokens = set(query.lower().split())
        resultados = []

        for pasaje in self.M_pas.values():
            # Similitud por intersección de tokens
            texto_tokens = set(pasaje.texto.lower().split())
            if len(query_tokens | texto_tokens) == 0:
                score = 0.0
            else:
                interseccion = len(query_tokens & texto_tokens)
                union = len(query_tokens | texto_tokens)
                score = interseccion / union  # Jaccard similarity

            resultados.append((pasaje, score))

        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados[:top_k]

    # ─── Estadísticas y utilidades ────────────────────────────────────────────

    def estadisticas(self) -> Dict:
        """Retorna estadísticas de la memoria global."""
        schemas_estables = len([s for s in self.M_ont.values() if s.estable])
        hechos_activos = len([f for f in self.M_fac.values() if f.activo])

        return {
            "ontologia": {
                "total_schemas": len(self.M_ont),
                "schemas_estables": schemas_estables,
                "schemas_candidatos": len(self.M_ont) - schemas_estables,
            },
            "hechos": {
                "total_hechos": len(self.M_fac),
                "hechos_activos": hechos_activos,
                "hechos_inactivos": len(self.M_fac) - hechos_activos,
            },
            "pasajes": {
                "total_pasajes": len(self.M_pas),
            },
            "umbral_schema": self.schema_freq_threshold,
        }

    def exportar(self) -> Dict:
        """Exporta toda la memoria a un diccionario serializable."""
        return {
            "M_ont": {k: v.to_dict() for k, v in self.M_ont.items()},
            "M_fac": {k: v.to_dict() for k, v in self.M_fac.items()},
            "M_pas": {k: v.to_dict() for k, v in self.M_pas.items()},
            "config": {
                "schema_freq_threshold": self.schema_freq_threshold,
            },
            "estadisticas": self.estadisticas(),
        }

    def __repr__(self) -> str:
        stats = self.estadisticas()
        return (
            f"GlobalMemory("
            f"schemas={stats['ontologia']['total_schemas']}, "
            f"hechos={stats['hechos']['total_hechos']}, "
            f"pasajes={stats['pasajes']['total_pasajes']})"
        )
