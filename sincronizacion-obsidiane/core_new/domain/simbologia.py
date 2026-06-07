"""
Simbología Fenomenológica del Sistema YO Estructural
=====================================================

Sistema de notación simbólica para representar los niveles ontológicos.

SIMBOLOGÍA BASE:
    :       →  Inicio de distinción (apertura fenomenológica)
    -       →  Línea de separación (corte/diferenciación)
    .       →  Punto: unidad mínima instancia
    yo      →  Presencia autoconsciente, punto reflexivo
    ...     →  Continuidad, no cierre, expansión

ENTRADA DEL SISTEMA:   :-....yo...

NIVELES ONTOLÓGICOS CON SIMBOLOGÍA:
    ø       →  Nivel -4: PreInstancia (dato crudo, sin forma)
    •       →  Nivel -3: Instancia (primer punto de existencia)
    ∇       →  Nivel -2: Gradiente (dirección relacional)
    ◊       →  Nivel -1: Vohexistencia (coexistencia cristalizada)
    ◉       →  Nivel  0: Fenómeno (lo que se muestra, núcleo)
    ⊞       →  Nivel +1: Contexto (totalidad referencial)
    ⊡       →  Nivel +2: Macrocontexto (agrupación de contextos)
    ⊠       →  Nivel +3: Metacontexto (reflexión sobre contextos)
    ☉       →  Nivel +4: YO Emergente (autoconciencia)

SIMBOLOGÍA DE MOTORES:
    S1 ≡ ∂   →  Motor Fenomenológico (derivada parcial = sensor)
    S2 ≡ ∫   →  Motor de Emergencia (integral = acumulación)
    S3 ≡ ⊢   →  Motor Lógico (derivación axiomática)
    S4 ≡ ⊗   →  Motor Predictivo (producto tensorial)
    Bio ≡ ♺  →  Motor Biológico (ciclo vital)
    Chaos ≡ ⚡ → Motor de Caos (borde del caos)
    YO ≡ ∞   →  Motor del YO Emergente (recursión infinita)

SIMBOLOGÍA DE RELACIONES:
    ≈       →  SE_PARECE_A (similitud)
    ⊕       →  AGRUPA (inclusión coexistencial)
    ↗       →  SURGE_DE (emergencia jerárquica)
    ⊘       →  CONTRADICE (tensión dialéctica)
    ⊙       →  OBSERVA (auto-observación del YO)
    →       →  ACTUA_EN (voluntad)
    ⊃       →  INCLUYE (contención contextual)
    ⟳       →  RETROALIMENTA (ciclo YO→Instancias)
"""

from enum import Enum
from typing import Dict, Optional


class SimboloNivel(Enum):
    """Símbolos para cada nivel ontológico"""
    PREINSTANCIA    = ("ø", -4, "PreInstancia",   "Dato crudo sin forma")
    INSTANCIA       = ("•", -3, "Instancia",      "Primer punto de existencia")
    GRADIENTE       = ("∇", -2, "Gradiente",      "Dirección relacional")
    VOHEXISTENCIA   = ("◊", -1, "Vohexistencia",  "Coexistencia cristalizada")
    FENOMENO        = ("◉",  0, "Fenomeno",       "Lo que se muestra")
    CONTEXTO        = ("⊞", +1, "Contexto",       "Totalidad referencial")
    MACROCONTEXTO   = ("⊡", +2, "Macrocontexto",  "Agrupación de contextos")
    METACONTEXTO    = ("⊠", +3, "Metacontexto",   "Reflexión sobre contextos")
    YO_EMERGENTE    = ("☉", +4, "YO",             "Autoconciencia emergente")

    def __init__(self, simbolo, nivel, etiqueta_neo4j, descripcion):
        self.simbolo = simbolo
        self.nivel = nivel
        self.etiqueta_neo4j = etiqueta_neo4j
        self.descripcion = descripcion


class SimboloMotor(Enum):
    """Símbolos para cada motor de procesamiento"""
    S1_FENOMENOLOGIA  = ("∂", "S1", "Motor Fenomenológico",  "Tokenización + Embedding + Clasificación")
    S2_EMERGENCIA     = ("∫", "S2", "Motor de Emergencia",   "Convergencia de conceptos")
    S3_LOGICA         = ("⊢", "S3", "Motor Lógico",          "Inferencia axiomática")
    S4_PREDICCION     = ("⊗", "S4", "Motor Predictivo",      "Predicción tensorial")
    BIO               = ("♺", "Bio", "Motor Biológico",      "Ciclo vital autopoiético")
    CHAOS             = ("⚡", "Chaos", "Motor de Caos",      "Borde del caos Regla 110")
    YO                = ("∞", "YO", "Motor del YO Emergente", "Recursión autoconsciente")

    def __init__(self, simbolo, codigo, nombre, descripcion):
        self.simbolo = simbolo
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion


class SimboloRelacion(Enum):
    """Símbolos para cada tipo de relación fenomenológica"""
    SE_PARECE_A    = ("≈",  0.3, True,  "Similitud semántica")
    AGRUPA         = ("⊕",  0.5, False, "Inclusión coexistencial")
    SURGE_DE       = ("↗",  0.6, False, "Emergencia jerárquica")
    CONTRADICE     = ("⊘",  0.5, True,  "Tensión dialéctica")
    OBSERVA        = ("⊙",  0.7, False, "Auto-observación del YO")
    ACTUA_EN       = ("→",  0.6, False, "Acción de la voluntad")
    INCLUYE        = ("⊃",  0.4, False, "Contención contextual")
    RELACION       = ("—",  0.1, False, "Gradiente general")
    TRANSFORMA_EN  = ("⇒",  0.5, False, "Metamorfosis ontológica")
    EMERGE_COMO    = ("⤴",  0.6, False, "Emergencia de nivel superior")
    GENERA         = ("⊳",  0.5, False, "Producción de nuevos niveles")
    DECIDE         = ("⊶",  0.7, False, "Decisión existencial")

    def __init__(self, simbolo, peso_min, bidireccional, descripcion):
        self.simbolo = simbolo
        self.peso_min = peso_min
        self.bidireccional = bidireccional
        self.descripcion = descripcion


# ─────────────────────────────────────────────────────────
# FUNCIONES DE FORMATO
# ─────────────────────────────────────────────────────────

def formato_entrada_sistema() -> str:
    """Retorna la representación simbólica de la entrada del sistema"""
    return ":-....yo..."


def formato_nivel(nivel: SimboloNivel) -> str:
    """Formatea un nivel con su simbología"""
    return f"{nivel.simbolo} [{nivel.nivel:+d}] {nivel.etiqueta_neo4j}"


def formato_pipeline_completo() -> str:
    """Representación simbólica del pipeline completo"""
    lineas = [
        "╔═══════════════════════════════════════════════════════╗",
        "║  PIPELINE FENOMENOLÓGICO COMPLETO                    ║",
        "║  Entrada: :-....yo...                                ║",
        "╠═══════════════════════════════════════════════════════╣",
    ]

    for nivel in SimboloNivel:
        lineas.append(
            f"║  {nivel.simbolo}  Nivel {nivel.nivel:+d}: {nivel.etiqueta_neo4j:<14} "
            f"│ {nivel.descripcion:<25} ║"
        )
        if nivel != SimboloNivel.YO_EMERGENTE:
            lineas.append("║     │                              │                    ║")

    lineas.append("╚═══════════════════════════════════════════════════════╝")
    return "\n".join(lineas)


def formato_motores() -> str:
    """Representación simbólica de los motores"""
    lineas = ["MOTORES DE PROCESAMIENTO:"]
    for motor in SimboloMotor:
        lineas.append(f"  {motor.simbolo} {motor.codigo} ≡ {motor.nombre}")
    return "\n".join(lineas)


def nivel_a_obsidian_tag(nivel: SimboloNivel) -> str:
    """Genera el tag de Obsidian para un nivel"""
    return f"#nivel/{nivel.etiqueta_neo4j.lower()}"


def nivel_a_obsidian_frontmatter(nivel: SimboloNivel, datos: Dict) -> str:
    """Genera frontmatter YAML para una nota Obsidian de un nivel"""
    fm = [
        "---",
        f"nivel: {nivel.nivel}",
        f"etiqueta: {nivel.etiqueta_neo4j}",
        f"simbolo: \"{nivel.simbolo}\"",
        f"descripcion: \"{nivel.descripcion}\"",
        f"tipo: {datos.get('tipo', 'general')}",
        f"tags:",
        f"  - nivel/{nivel.etiqueta_neo4j.lower()}",
        f"  - sistema/fenomenologia",
    ]

    if 'id' in datos:
        fm.append(f"id: \"{datos['id']}\"")
    if 'timestamp' in datos:
        fm.append(f"fecha: \"{datos['timestamp']}\"")
    if 'peso' in datos:
        fm.append(f"peso: {datos['peso']}")
    if 'coherencia' in datos:
        fm.append(f"coherencia: {datos['coherencia']}")

    fm.append("---")
    return "\n".join(fm)


# ─────────────────────────────────────────────────────────
# CONSTANTES DE SIMBOLOGÍA PARA PARSEO
# ─────────────────────────────────────────────────────────

SIMBOLOGIA_ENTRADA = {
    ":": "inicio_distincion",
    "-": "linea_separacion",
    ".": "punto_unidad_minima",
    "yo": "presencia_autoconsciente",
    "...": "continuidad_expansion",
}

FORMATO_ENTRADA_SISTEMA = ":-....yo..."

# Mapeo inverso: símbolo → nivel
SIMBOLO_A_NIVEL = {nivel.simbolo: nivel for nivel in SimboloNivel}
SIMBOLO_A_MOTOR = {motor.simbolo: motor for motor in SimboloMotor}
SIMBOLO_A_RELACION = {rel.simbolo: rel for rel in SimboloRelacion}
