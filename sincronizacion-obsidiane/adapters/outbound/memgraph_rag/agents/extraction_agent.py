"""
ExtractionAgent (A_ext) — Agente de Extracción para MemGraphRAG
================================================================

Implementa el Agente de Extracción A_ext descrito en el paper:
  "MemGraphRAG: Memory-based Multi-Agent System for Graph RAG"
  Sección 4.2.1 — Thematic Denoising via Unified Schema Filtering

Función principal:
    Dado un fragmento de texto ci, A_ext transforma el texto en entradas
    estructuradas para las 3 capas de la Global Memory:
    
    1. Genera esquemas candidatos (t_h, r, t_t) → M_ont
    2. Extrae hechos instanciados (e_h, r, e_t) → M_fac (solo si esquema estable)
    3. Preserva pasajes de evidencia → M_pas (con grounding ψ: fact → passage)

Mecanismo de filtrado temático:
    Los nuevos esquemas son CANDIDATOS hasta que su frecuencia alcanza el umbral.
    Solo hechos de esquemas ESTABLES son activados, filtrando tripletas irrelevantes.

Adaptado al dominio del Sistema Vivo Fenomenológico:
    Los tipos de entidades y relaciones son específicos al dominio de
    experiencias subjetivas, S1-S4, yo emergente y fenomenología.

Referencia: Section 4.2 + Appendix D.3.1 del paper
"""

import json
import logging
import re
import os
from typing import Any, Dict, List, Optional, Tuple

from ..global_memory import GlobalMemory, Schema, Fact, Passage

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Ontología del dominio fenomenológico
# ─────────────────────────────────────────────────────────────────────────────

# Tipos de entidades del dominio del Sistema Vivo
TIPOS_DOMINIO = {
    "fenomeno": "Experiencia o fenómeno subjetivo",
    "emocion": "Estado emocional o afectivo",
    "pensamiento": "Pensamiento, creencia o cognición",
    "cuerpo": "Sensación o estado corporal",
    "yo": "Yo emergente, identidad o narrativa del self",
    "contexto": "Contexto situacional o circunstancial",
    "patron": "Patrón recurrente o estructura emergente",
    "recurso": "Recurso existencial o estrategia de afrontamiento",
    "relacion": "Vínculo interpersonal o relación social",
    "tiempo": "Marcador temporal, fecha o período",
    "lugar": "Lugar físico o espacio",
    "entidad": "Entidad genérica sin tipo específico",
    "nivel_s": "Nivel del sistema (S1 corporal, S2 emocional, S3 cognitivo, S4 transpersonal)",
    "sombra": "Aspecto de sombra o contenido inconsciente",
    "apertura": "Apertura o momento de expansión",
}

# Esquemas de relación preestablecidos para el dominio
ESQUEMAS_BASE_DOMINIO = [
    # Relaciones causales
    ("fenomeno", "causa", "emocion"),
    ("emocion", "activa", "pensamiento"),
    ("pensamiento", "modifica", "fenomeno"),
    ("cuerpo", "expresa", "emocion"),
    ("emocion", "bloquea", "recurso"),
    ("patron", "perpetua", "fenomeno"),
    # Relaciones de composición
    ("yo", "integra", "fenomeno"),
    ("yo", "contiene", "sombra"),
    ("nivel_s", "procesa", "fenomeno"),
    ("contexto", "contiene", "fenomeno"),
    # Relaciones temporales
    ("fenomeno", "precede", "fenomeno"),
    ("fenomeno", "ocurre_en", "tiempo"),
    ("fenomeno", "relacionado_con", "lugar"),
    # Relaciones de transformación
    ("fenomeno", "transforma_en", "fenomeno"),
    ("sombra", "emerge_como", "recurso"),
    ("recurso", "facilita", "apertura"),
    # Relaciones de similitud/contraste
    ("fenomeno", "similar_a", "fenomeno"),
    ("patron", "contrasta_con", "patron"),
    # Relaciones S1-S4
    ("nivel_s", "integra_a", "nivel_s"),
    ("yo", "transciende_a", "nivel_s"),
]


class ExtractionAgent:
    """
    Agente de Extracción (A_ext) del framework MemGraphRAG.

    Responsabilidades:
    1. Extraer esquemas (t_h, r, t_t) del texto
    2. Extraer hechos concretos (e_h, r, e_t)
    3. Preservar pasajes de evidencia para grounding
    4. Filtrar por esquemas estables (filtrado temático)
    
    Estrategia de extracción:
    - Con LLM disponible: extracción guiada por prompts estructurados
    - Sin LLM: extracción por reglas NLP básicas y patrones del dominio
    """

    PROMPT_EXTRACCION = """
Analiza el siguiente fragmento de texto de una experiencia personal subjetiva.
Extrae las tripletas de conocimiento estructurado en formato JSON.

TEXTO:
{texto}

TIPOS DE ENTIDADES VÁLIDOS:
{tipos}

ESQUEMAS BASE DEL DOMINIO (relaciones esperadas):
{esquemas}

Devuelve un JSON con esta estructura exacta:
{{
  "esquemas": [
    {{"tipo_head": "...", "relacion": "...", "tipo_tail": "..."}}
  ],
  "hechos": [
    {{
      "entidad_head": "...",
      "tipo_head": "...",
      "relacion": "...",
      "entidad_tail": "...",
      "tipo_tail": "...",
      "confianza": 0.0-1.0,
      "pasaje": "cita textual del fragmento que evidencia este hecho"
    }}
  ]
}}

Reglas:
- Extrae solo hechos que estén claramente respaldados por el texto
- Las entidades deben ser concretas y específicas (no genéricas)
- La confianza refleja cuán explícito es el hecho en el texto
- El pasaje debe ser la cita mínima que justifica el hecho
- Máximo 10 hechos por fragmento
"""

    def __init__(
        self,
        memoria: GlobalMemory,
        llm_func=None,
        usar_reglas_base: bool = True,
    ):
        """
        Args:
            memoria: Referencia a la Global Memory compartida
            llm_func: Función de LLM callable(prompt: str) -> str.
                      Si None, usa extracción por reglas.
            usar_reglas_base: Si True, inicializa los esquemas base del dominio
        """
        self.memoria = memoria
        self.llm_func = llm_func
        self.usar_reglas_base = usar_reglas_base

        # Inicializar esquemas base del dominio fenomenológico
        if usar_reglas_base:
            self._inicializar_esquemas_dominio()

        logger.info(
            f"[A_ext] Inicializado — LLM: {'sí' if llm_func else 'no (modo reglas)'}, "
            f"Esquemas base: {usar_reglas_base}"
        )

    def _inicializar_esquemas_dominio(self) -> None:
        """
        Pre-carga los esquemas base del dominio fenomenológico.
        Cada esquema base se agrega con frecuencia = umbral (ya estabilizados).
        """
        for tipo_head, relacion, tipo_tail in ESQUEMAS_BASE_DOMINIO:
            for _ in range(self.memoria.schema_freq_threshold):
                self.memoria.agregar_schema_candidato(tipo_head, relacion, tipo_tail)
        
        logger.info(
            f"[A_ext] {len(ESQUEMAS_BASE_DOMINIO)} esquemas base del dominio cargados"
        )

    def procesar_fragmento(
        self,
        texto: str,
        fuente: str = "",
        tipo_fuente: str = "experiencia",
        metadata: Dict = None,
    ) -> Tuple[List[Schema], List[Fact], Passage]:
        """
        Función principal de extracción — Procesa un fragmento de texto.
        
        Implementa el algoritmo del paper:
        1. Almacenar pasaje en M_pas
        2. Extraer esquemas candidatos y actualizar M_ont
        3. Extraer hechos y almacenar en M_fac (si esquema estable)
        4. Devolver los elementos creados

        Args:
            texto: Fragmento de texto a procesar
            fuente: Identificador de fuente (e.g., "diario_2025-01-01")
            tipo_fuente: Categoría del texto ("diario", "conversacion", etc.)
            metadata: Metadatos adicionales para enriquecer la extracción

        Returns:
            (schemas_nuevos, hechos_nuevos, pasaje): Elementos extraídos
        """
        metadata = metadata or {}

        # ── Paso 1: Almacenar pasaje de evidencia en M_pas ──
        pasaje = self.memoria.agregar_pasaje(
            texto=texto,
            fuente=fuente,
            tipo_fuente=tipo_fuente,
        )

        # ── Paso 2: Extraer esquemas y hechos del texto ──
        if self.llm_func:
            datos_extraidos = self._extraer_con_llm(texto, metadata)
        else:
            datos_extraidos = self._extraer_con_reglas(texto, fuente, metadata)

        schemas_nuevos = []
        hechos_nuevos = []

        # ── Paso 3: Agregar esquemas a M_ont ──
        for schema_data in datos_extraidos.get("esquemas", []):
            schema, fue_promovido = self.memoria.agregar_schema_candidato(
                tipo_head=schema_data.get("tipo_head", "entidad"),
                relacion=schema_data.get("relacion", "relacionado_con"),
                tipo_tail=schema_data.get("tipo_tail", "entidad"),
            )
            if fue_promovido:
                schemas_nuevos.append(schema)
                logger.info(f"[A_ext] Nuevo esquema estabilizado: {schema.clave()}")

        # ── Paso 4: Agregar hechos a M_fac (solo si esquema estable) ──
        for hecho_data in datos_extraidos.get("hechos", []):
            # Buscar el esquema correspondiente
            schema_clave = (
                f"{hecho_data.get('tipo_head', 'entidad')}"
                f"|{hecho_data.get('relacion', 'relacionado_con')}"
                f"|{hecho_data.get('tipo_tail', 'entidad')}"
            )
            schema = self.memoria.M_ont.get(schema_clave)
            
            if schema is None:
                # Intentar crear el esquema si no existe
                schema, _ = self.memoria.agregar_schema_candidato(
                    hecho_data.get("tipo_head", "entidad"),
                    hecho_data.get("relacion", "relacionado_con"),
                    hecho_data.get("tipo_tail", "entidad"),
                )

            if schema and schema.estable:
                # Almacenar el pasaje específico del hecho si es diferente
                pasaje_hecho = pasaje
                if hecho_data.get("pasaje") and hecho_data["pasaje"] != texto:
                    pasaje_hecho = self.memoria.agregar_pasaje(
                        texto=hecho_data["pasaje"],
                        fuente=fuente,
                        tipo_fuente=tipo_fuente,
                    )

                hecho = self.memoria.agregar_hecho(
                    entidad_head=str(hecho_data.get("entidad_head", "")).strip(),
                    relacion=str(hecho_data.get("relacion", "relacionado_con")).strip(),
                    entidad_tail=str(hecho_data.get("entidad_tail", "")).strip(),
                    schema_id=schema.id,
                    passage_id=pasaje_hecho.id,
                    confianza=float(hecho_data.get("confianza", 0.8)),
                )
                if hecho:
                    hechos_nuevos.append(hecho)

        logger.info(
            f"[A_ext] Procesado: {len(hechos_nuevos)} hechos, "
            f"{len(schemas_nuevos)} esquemas nuevos, fuente={fuente}"
        )
        return schemas_nuevos, hechos_nuevos, pasaje

    def _extraer_con_llm(self, texto: str, metadata: Dict) -> Dict:
        """Usa un LLM para extracción estructurada con prompts."""
        tipos_str = "\n".join(
            f"  - {tipo}: {desc}" for tipo, desc in TIPOS_DOMINIO.items()
        )
        esquemas_str = "\n".join(
            f"  ({t_h}, {r}, {t_t})" for t_h, r, t_t in ESQUEMAS_BASE_DOMINIO[:15]
        )
        
        prompt = self.PROMPT_EXTRACCION.format(
            texto=texto[:2000],  # Limitar texto para contexto del LLM
            tipos=tipos_str,
            esquemas=esquemas_str,
        )

        try:
            respuesta = self.llm_func(prompt)
            # Intentar parsear JSON de la respuesta
            # Buscar bloque JSON en la respuesta
            json_match = re.search(r"\{.*\}", respuesta, re.DOTALL)
            if json_match:
                datos = json.loads(json_match.group())
                return datos
        except json.JSONDecodeError as e:
            logger.warning(f"[A_ext] Error parseando JSON del LLM: {e}")
        except Exception as e:
            logger.error(f"[A_ext] Error en extracción con LLM: {e}")

        # Fallback a reglas si el LLM falla
        return self._extraer_con_reglas(texto, "", metadata)

    def _extraer_con_reglas(self, texto: str, fuente: str, metadata: Dict) -> Dict:
        """
        Extracción heurística por patrones del dominio fenomenológico.
        
        Usa reglas lingüísticas específicas al dominio para identificar:
        - Emociones y sus causas/efectos
        - Patrones recurrentes
        - Estados corporales
        - Transiciones y transformaciones
        """
        esquemas_extraidos = []
        hechos_extraidos = []
        texto_lower = texto.lower()

        # ── Detectar emociones mencionadas ──
        emociones_detectadas = self._detectar_emociones(texto_lower)
        for emocion in emociones_detectadas:
            esquemas_extraidos.append({
                "tipo_head": "yo",
                "relacion": "experimenta",
                "tipo_tail": "emocion"
            })
            hechos_extraidos.append({
                "entidad_head": "yo_emergente",
                "tipo_head": "yo",
                "relacion": "experimenta",
                "entidad_tail": emocion,
                "tipo_tail": "emocion",
                "confianza": 0.75,
                "pasaje": self._extraer_contexto(texto, emocion),
            })

        # ── Detectar patrones y fenómenos ──
        patrones = self._detectar_patrones(texto_lower)
        for patron in patrones:
            esquemas_extraidos.append({
                "tipo_head": "patron",
                "relacion": "emerge_en",
                "tipo_tail": "fenomeno"
            })
            hechos_extraidos.append({
                "entidad_head": patron,
                "tipo_head": "patron",
                "relacion": "emerge_en",
                "entidad_tail": texto[:50].strip(),
                "tipo_tail": "fenomeno",
                "confianza": 0.65,
                "pasaje": self._extraer_contexto(texto, patron),
            })

        # ── Detectar sensaciones corporales ──
        sensaciones = self._detectar_sensaciones_corporales(texto_lower)
        for sensacion in sensaciones:
            hechos_extraidos.append({
                "entidad_head": "cuerpo",
                "tipo_head": "cuerpo",
                "relacion": "expresa",
                "entidad_tail": sensacion,
                "tipo_tail": "emocion",
                "confianza": 0.70,
                "pasaje": self._extraer_contexto(texto, sensacion),
            })

        # ── Detectar contexto temporal ──
        if metadata.get("fecha"):
            hechos_extraidos.append({
                "entidad_head": "fenomeno_actual",
                "tipo_head": "fenomeno",
                "relacion": "ocurre_en",
                "entidad_tail": str(metadata["fecha"]),
                "tipo_tail": "tiempo",
                "confianza": 1.0,
                "pasaje": texto[:100],
            })

        # ── Detectar nivel S1-S4 activo ──
        nivel = self._detectar_nivel_s(texto_lower)
        if nivel:
            hechos_extraidos.append({
                "entidad_head": nivel,
                "tipo_head": "nivel_s",
                "relacion": "activo_en",
                "entidad_tail": "experiencia_actual",
                "tipo_tail": "fenomeno",
                "confianza": 0.80,
                "pasaje": texto[:100],
            })

        return {
            "esquemas": esquemas_extraidos,
            "hechos": hechos_extraidos,
        }

    def _detectar_emociones(self, texto: str) -> List[str]:
        """Detecta emociones mencionadas en el texto."""
        emociones_base = [
            "miedo", "ansiedad", "tristeza", "alegría", "alegria", "rabia", "ira",
            "vergüenza", "vergonzanza", "culpa", "amor", "soledad", "paz",
            "confusión", "confusion", "claridad", "bloqueo", "apertura",
            "angustia", "gratitud", "frustración", "frustracion", "esperanza",
            "desesperanza", "desconexión", "desconexion", "presencia", "vacío", "vacio",
        ]
        return [e for e in emociones_base if e in texto]

    def _detectar_patrones(self, texto: str) -> List[str]:
        """Detecta menciones de patrones recurrentes."""
        indicadores = [
            "siempre", "nunca", "cuando", "cada vez que",
            "repetidamente", "recurrente", "patrón", "patron",
            "de nuevo", "otra vez", "nuevamente", "igual que",
        ]
        patrones = []
        for ind in indicadores:
            if ind in texto:
                # Extraer fragmento contextual
                idx = texto.find(ind)
                fragmento = texto[max(0, idx-10):min(len(texto), idx+30)].strip()
                patrones.append(fragmento[:40])
        return patrones[:3]  # Máximo 3 patrones por texto

    def _detectar_sensaciones_corporales(self, texto: str) -> List[str]:
        """Detecta sensaciones físicas en el texto."""
        sensaciones = [
            "tensión", "tension", "dolor", "nudo", "presión", "presion",
            "calor", "frío", "frio", "cansancio", "energía", "energia",
            "opresión", "opresion", "alivio", "ligereza", "peso",
            "temblor", "latidos", "respiración", "respiracion",
        ]
        return [s for s in sensaciones if s in texto]

    def _detectar_nivel_s(self, texto: str) -> Optional[str]:
        """Detecta el nivel del sistema S1-S4 más activo en el texto."""
        indicadores = {
            "S1_corporal": [
                "cuerpo", "sensación", "sensacion", "físico", "fisico",
                "respira", "latido", "tensión", "tension",
            ],
            "S2_emocional": [
                "siento", "emoción", "emocion", "afecto", "sentimiento",
                "corazón", "corazon",
            ],
            "S3_cognitivo": [
                "pienso", "creo que", "análisis", "analisis", "mente",
                "idea", "concepto", "comprendo",
            ],
            "S4_transpersonal": [
                "sentido", "propósito", "proposito", "trascendencia",
                "conexión profunda", "unidad", "espiritual",
            ],
        }
        
        max_nivel = None
        max_count = 0
        for nivel, palabras in indicadores.items():
            count = sum(1 for p in palabras if p in texto)
            if count > max_count:
                max_count = count
                max_nivel = nivel
        
        return max_nivel if max_count > 0 else None

    def _extraer_contexto(self, texto: str, termino: str, ventana: int = 100) -> str:
        """Extrae el contexto alrededor de un término en el texto."""
        texto_lower = texto.lower()
        idx = texto_lower.find(termino.lower())
        if idx == -1:
            return texto[:ventana].strip()
        
        inicio = max(0, idx - ventana // 2)
        fin = min(len(texto), idx + len(termino) + ventana // 2)
        return texto[inicio:fin].strip()
