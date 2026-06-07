"""
Adaptador de Salida: Sincronización con Obsidian (Zettelkasten)
================================================================

Patrón: Adaptador Hexagonal (Outbound)
Versión: 4.0 — Refinamiento Definitivo (análisis v4)

CORRECCIONES respecto a versión anterior:
  - Símbolo Nivel +3 corregido: ⊠  Metacontexto (era ⊡ que es Macrocontexto)
  - Voluntad es carpeta 10_Voluntad/, NO nivel numerado
  - Se agrega carpeta 12_Logica/ con subsistemas (Modal, Mereológica, Deóntica, Pura)
  - Frontmatter YAML expandido con campos de lógica para cada nivel
  - Retroalimentación ⟳ reflejada en notas de instancias
  - 6 tipos de TipoYO en frontmatter de notas ☉
  - Coexistencia MOCs Python + Dataview del usuario
  - 12 relaciones fenomenológicas en carpeta 11_Relaciones/

Estructura del vault generada:
    Zerg/
    ├── 00_MOC/                     ← MOCs generados por Python
    │   ├── MOC_Pipeline.md         ← Tabla motores + conteo por nivel
    │   ├── MOC_Niveles.md          ← Índice todas las entidades
    │   └── MOC_Relaciones.md       ← Mapa 12 tipos de relaciones
    ├── 01_PreInstancias/           ← ø  Nivel -4
    ├── 02_Instancias/              ← •  Nivel -3
    ├── 03_Gradientes/              ← ∇  Nivel -2
    ├── 04_Vohexistencias/          ← ◊  Nivel -1
    ├── 05_Fenomenos/               ← ◉  Nivel  0
    ├── 06_Contextos/               ← ⊞  Nivel +1
    ├── 07_Macrocontextos/          ← ⊡  Nivel +2
    ├── 08_Metacontextos/           ← ⊠  Nivel +3  (lógica modal aquí)
    ├── 09_YO/                      ← ☉  Nivel +4  (6 tipos TipoYO)
    ├── 10_Voluntad/                ← →  Proyecciones Entwurf (deóntica aquí)
    ├── 11_Relaciones/              ← 12 tipos de relaciones fenomenológicas
    ├── 12_Logica/                  ← [NUEVO] Sistemas lógicos
    │   ├── Pura/
    │   │   ├── axiomas/            ← Reglas Horn inferidas
    │   │   └── mundos_hipoteticos/ ← Mundos lógicos cerrados
    │   ├── Modal/                  ← □ necesidad / ◇ posibilidad
    │   ├── Mereologica/            ← ⊂ parte-todo / ∪ fusión
    │   └── Deontica/               ← O obligación / F prohibición
    └── _sistema/                   ← Config y estado
        ├── estado_actual.md
        └── log_procesamiento.md
"""

import os
import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ObsidianSync:
    """
    Adaptador de salida que sincroniza el estado del sistema
    con un vault de Obsidian en formato Zettelkasten.

    Versión 4.0 — Estructura definitiva confirmada por análisis del código.
    """

    # Niveles ontológicos confirmados desde simbologia.py
    ESTRUCTURA_CARPETAS = {
        -4: "01_PreInstancias",
        -3: "02_Instancias",
        -2: "03_Gradientes",
        -1: "04_Vohexistencias",
         0: "05_Fenomenos",
         1: "06_Contextos",
         2: "07_Macrocontextos",
         3: "08_Metacontextos",      # ⊠  Metacontexto — CORREGIDO (era 07 con nombre incorrecto)
         4: "09_YO",                 # ☉  YO Emergente
    }

    CARPETAS_EXTRA = [
        "00_MOC",
        "10_Voluntad",              # → Proyecciones Entwurf (no es nivel numerado)
        "11_Relaciones",            # 12 tipos de relaciones fenomenológicas
        "12_Logica/Pura/axiomas",
        "12_Logica/Pura/mundos_hipoteticos",
        "12_Logica/Modal",
        "12_Logica/Mereologica",
        "12_Logica/Deontica",
        "_sistema",
    ]

    # Símbolos confirmados desde simbologia.py
    SIMBOLOS = {
        -4: "ø",   # PreInstancia
        -3: "•",   # Instancia
        -2: "∇",   # Gradiente
        -1: "◊",   # Vohexistencia
         0: "◉",   # Fenomeno
         1: "⊞",   # Contexto
         2: "⊡",   # Macrocontexto  ← CORRECTO
         3: "⊠",   # Metacontexto   ← CORREGIDO (antes era ⊡, era el símbolo de Macrocontexto)
         4: "☉",   # YO Emergente
    }

    # Motores de procesamiento — confirmados desde simbologia.py
    MOTORES = {
        "S1": "∂",   # Motor Fenomenológico
        "S2": "∫",   # Motor de Emergencia
        "S3": "⊢",   # Motor Lógico (axiomático)
        "S4": "⊗",   # Motor Predictivo (tensorial)
        "Bio": "♺",  # Motor Biológico
        "Chaos": "⚡", # Motor de Caos (Regla 110)
        "YO": "∞",   # Motor del YO Emergente (recursivo)
    }

    # 12 relaciones fenomenológicas — confirmadas desde generador_relaciones.py
    RELACIONES = {
        "SE_PARECE_A":   {"simbolo": "≈",  "bidir": True,  "peso_min": 0.3},
        "AGRUPA":        {"simbolo": "⊕",  "bidir": False, "peso_min": 0.5},
        "SURGE_DE":      {"simbolo": "↗",  "bidir": False, "peso_min": 0.6},
        "CONTRADICE":    {"simbolo": "⊘",  "bidir": True,  "peso_min": 0.5},
        "OBSERVA":       {"simbolo": "⊙",  "bidir": False, "peso_min": 0.7},
        "ACTUA_EN":      {"simbolo": "→",  "bidir": False, "peso_min": 0.6},
        "INCLUYE":       {"simbolo": "⊃",  "bidir": False, "peso_min": 0.4},
        "RELACION":      {"simbolo": "—",  "bidir": False, "peso_min": 0.1},
        "TRANSFORMA_EN": {"simbolo": "⇒",  "bidir": False, "peso_min": 0.5},
        "EMERGE_COMO":   {"simbolo": "⤴",  "bidir": False, "peso_min": 0.6},
        "GENERA":        {"simbolo": "⊳",  "bidir": False, "peso_min": 0.5},
        "DECIDE":        {"simbolo": "⊶",  "bidir": False, "peso_min": 0.7},
    }

    # 6 Tipos de YO — confirmados desde motor_yo.py (TipoYO enum)
    TIPOS_YO = {
        0: "PROTO_YO",
        1: "YO_SENSORIAL",
        2: "YO_AFECTIVO",
        3: "YO_REFLEXIVO",
        4: "YO_SIMBOLICO",
        5: "YO_NARRATIVO",
    }

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self._inicializar_estructura()

    def _inicializar_estructura(self):
        """Crea la estructura completa de carpetas si no existe."""
        for carpeta in self.ESTRUCTURA_CARPETAS.values():
            (self.vault_path / carpeta).mkdir(parents=True, exist_ok=True)

        for carpeta in self.CARPETAS_EXTRA:
            (self.vault_path / carpeta).mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────────────────────
    # GUARDADO DE ENTIDADES ONTOLÓGICAS
    # ──────────────────────────────────────────────────────

    def guardar_entidad(self, nivel: int, id_entidad: str, contenido_md: str) -> str:
        """Guarda una entidad ontológica como nota Markdown en el vault."""
        carpeta = self.ESTRUCTURA_CARPETAS.get(nivel, "_sistema")
        ruta = self.vault_path / carpeta / f"{id_entidad}.md"
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido_md)
        return str(ruta)

    def guardar_voluntad(self, id_proyeccion: str, contenido_md: str) -> str:
        """Guarda una proyección de Voluntad (Entwurf heideggeriano)."""
        ruta = self.vault_path / "10_Voluntad" / f"{id_proyeccion}.md"
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido_md)
        return str(ruta)

    def guardar_relaciones(self, id_mapa: str, contenido_md: str) -> str:
        """Guarda un mapa de relaciones fenomenológicas."""
        ruta = self.vault_path / "11_Relaciones" / f"{id_mapa}.md"
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido_md)
        return str(ruta)

    # ──────────────────────────────────────────────────────
    # GUARDADO DE SISTEMAS LÓGICOS (NUEVO — v4.0)
    # ──────────────────────────────────────────────────────

    def guardar_axioma(self, id_axioma: str, regla_raw: str, premisa: str,
                       conclusion: str, inferencias: int = 0) -> str:
        """Guarda un axioma inferido por el MotorAxiomas (S3 ⊢)."""
        ts = datetime.datetime.now().isoformat()
        contenido = f"""---
tipo: axioma
simbolo: "⊢"
motor: "S3"
id: "{id_axioma}"
regla_raw: "{regla_raw}"
tipo_regla: "implicacion"
premisa: "{premisa}"
conclusion: "{conclusion}"
inferencias_generadas: {inferencias}
fecha: "{ts}"
tags:
  - logica/pura
  - logica/axioma
  - sistema/generado
---

# ⊢ Axioma: {id_axioma}

**Regla:** `{regla_raw}`

| Campo | Valor |
|:------|:------|
| Premisa | `{premisa}` |
| Conclusión | `{conclusion}` |
| Inferencias generadas | {inferencias} |
| Timestamp | {ts} |

## Interpretación

Si **`{premisa}`** es verdad → entonces **`{conclusion}`** es verdad.

> Generado por Motor S3 ⊢ (lógica de cláusulas Horn)
"""
        ruta = self.vault_path / "12_Logica" / "Pura" / "axiomas" / f"{id_axioma}.md"
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return str(ruta)

    def guardar_mundo_hipotetico(self, id_mundo: str, hechos_base: List[str],
                                  proposiciones: List[Dict]) -> str:
        """Guarda un MundoHipotetico del MotorHipotetico (FCA + S3)."""
        ts = datetime.datetime.now().isoformat()
        hechos_yaml = "\n".join(f"  - \"{h}\"" for h in hechos_base)
        props_yaml = "\n".join(
            f"  - proposicion: \"{p['proposicion']}\"\n    valor: {str(p['valor']).lower()}"
            for p in proposiciones
        )
        props_md = "\n".join(
            f"| `{p['proposicion']}` | {'✅ Verdad' if p['valor'] else '❌ Falso'} |"
            for p in proposiciones
        )
        contenido = f"""---
tipo: mundo-hipotetico
simbolo: "□◇"
motor: "S3+∫"
id: "{id_mundo}"
fecha: "{ts}"
hechos_base:
{hechos_yaml}
proposiciones_verificadas:
{props_yaml}
tags:
  - logica/pura
  - logica/hipotetico
  - sistema/generado
---

# □◇ Mundo Hipotético: {id_mundo}

**Timestamp:** {ts}

## Hechos Base (cerrado)

{chr(10).join(f"- `{h}`" for h in hechos_base)}

## Proposiciones Verificadas

| Proposición | Valor |
|:------------|:------|
{props_md}

> Generado por MotorHipotetico (FCA + cláusulas Horn)
> Un mundo hipotético es un universo lógico cerrado donde
> solo existen los hechos declarados base.
"""
        ruta = self.vault_path / "12_Logica" / "Pura" / "mundos_hipoteticos" / f"{id_mundo}.md"
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return str(ruta)

    def guardar_estado_modal(self, id_meta: str, mundos_accesibles: List[str],
                              necesidad: bool, posibilidad: bool) -> str:
        """Guarda el estado de lógica modal evaluado en un Metacontexto (⊠)."""
        ts = datetime.datetime.now().isoformat()
        mundos_yaml = "\n".join(f"  - \"{m}\"" for m in mundos_accesibles)
        contenido = f"""---
tipo: estado-modal
simbolo: "□◇"
motor: "MotorModal"
id_metacontexto: "{id_meta}"
fecha: "{ts}"
mundos_accesibles:
{mundos_yaml}
necesidad_evaluada: {str(necesidad).lower()}
posibilidad_detectada: {str(posibilidad).lower()}
tags:
  - logica/modal
  - nivel/metacontexto
  - sistema/generado
---

# □ ◇ Estado Modal del Metacontexto {id_meta}

| Operador | Resultado |
|:---------|:----------|
| □ Necesidad (todos los mundos) | {'✅ Verdad' if necesidad else '❌ Falso'} |
| ◇ Posibilidad (algún mundo) | {'✅ Verdad' if posibilidad else '❌ Falso'} |

## Mundos Accesibles (Semántica de Kripke)

{chr(10).join(f"- [[{m}]]" for m in mundos_accesibles) if mundos_accesibles else "*Sin mundos accesibles definidos (verdad vacua)*"}
"""
        ruta = self.vault_path / "12_Logica" / "Modal" / f"modal_{id_meta}.md"
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return str(ruta)

    def guardar_estado_deontico(self, id_proyeccion: str, permitido: bool,
                                 violaciones: List[str]) -> str:
        """Guarda el resultado de la auditoría deóntica de una Voluntad."""
        ts = datetime.datetime.now().isoformat()
        viols_md = "\n".join(f"- ⚠️ {v}" for v in violaciones) if violaciones else "- ✅ Sin violaciones"
        contenido = f"""---
tipo: estado-deontico
simbolo: "OFP"
motor: "MotorDeontico"
id_proyeccion: "{id_proyeccion}"
fecha: "{ts}"
permitido: {str(permitido).lower()}
obligaciones_violadas: {len(violaciones)}
tags:
  - logica/deontica
  - sistema/voluntad
  - sistema/generado
---

# O F P — Auditoría Deóntica: {id_proyeccion}

**Estado:** {'✅ PERMITIDO' if permitido else '🚫 PROHIBIDO'}

## Resultado de Obligaciones

{viols_md}

> O = Obligatorio | F = Prohibido | P = Permitido
> La lógica deóntica regula las normas del Organismo Vivo.
"""
        ruta = self.vault_path / "12_Logica" / "Deontica" / f"deontica_{id_proyeccion}.md"
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return str(ruta)

    def guardar_composicion_mereologica(self, todo_id: str, partes: List[str]) -> str:
        """Guarda la composición mereológica (parte-todo) de una entidad."""
        ts = datetime.datetime.now().isoformat()
        partes_md = "\n".join(f"- ⊂ [[{p}]]" for p in partes)
        contenido = f"""---
tipo: composicion-mereologica
simbolo: "⊂∪"
motor: "MotorMereologico"
id_todo: "{todo_id}"
fecha: "{ts}"
n_partes: {len(partes)}
tags:
  - logica/mereologica
  - sistema/generado
---

# ⊂ Composición Mereológica: {todo_id}

El ente **{todo_id}** está compuesto por las siguientes partes:

{partes_md}

> ⊂ = parte propia | ∪ = fusión mereológica
> Una parte propia satisface: x ⊂ y ↔ (x es parte de y) ∧ (x ≠ y)
"""
        ruta = self.vault_path / "12_Logica" / "Mereologica" / f"mereo_{todo_id}.md"
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return str(ruta)

    # ──────────────────────────────────────────────────────
    # RETROALIMENTACIÓN HERMENÉUTICA ⟳ (NUEVO — v4.0)
    # ──────────────────────────────────────────────────────

    def agregar_resignificacion_a_instancia(
        self, instancia_id: str, yo_id: str, tipo_yo: str,
        sig_original: str, sig_nuevo: str, peso: float
    ):
        """
        Añade una sección de resignificación ⟳ al final de una nota de instancia.
        Implementa el ciclo hermenéutico: YO → OBSERVA → Instancias resignificadas.
        """
        carpetas_instancia = [
            self.ESTRUCTURA_CARPETAS[-3],
            self.ESTRUCTURA_CARPETAS[-2],
            self.ESTRUCTURA_CARPETAS[-1],
        ]

        for carpeta in carpetas_instancia:
            ruta = self.vault_path / carpeta / f"{instancia_id}.md"
            if ruta.exists():
                seccion = (
                    f"\n\n## ⟳ Resignificación del YO\n\n"
                    f"| Campo | Valor |\n|:------|:------|\n"
                    f"| YO | [[{yo_id}]] ({tipo_yo}) |\n"
                    f"| Peso | {peso:.2f} |\n"
                    f"| Timestamp | {datetime.datetime.now().isoformat()} |\n\n"
                    f"> **Original:** {sig_original[:80]}...\n\n"
                    f"> **Resignificado:** {sig_nuevo}\n"
                )
                with open(ruta, 'a', encoding='utf-8') as f:
                    f.write(seccion)
                return

    # ──────────────────────────────────────────────────────
    # GENERACIÓN DE MOCs AUTOMÁTICOS
    # ──────────────────────────────────────────────────────

    def generar_moc_pipeline(self) -> str:
        """Genera el MOC principal del Pipeline con toda la simbología del sistema."""
        ts_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        lineas = [
            "---",
            "tags:",
            "  - MOC",
            "  - sistema/pipeline",
            f"date: {ts_hoy}",
            "---",
            "",
            "# :-....yo... Pipeline Fenomenológico Completo",
            "",
            "## Entrada del Sistema",
            "",
            "```",
            ":-....yo...",
            ": → inicio de distinción",
            "- → línea de separación (corte/diferenciación)",
            ". → punto: unidad mínima instancia",
            "yo → presencia autoconsciente",
            "... → continuidad, no cierre, expansión",
            "```",
            "",
            "## Niveles Ontológicos",
            "",
            "| Símbolo | Nivel | Nombre | Carpeta | Entidades |",
            "|:-------:|:-----:|:-------|:--------|:---------:|",
        ]

        for nivel, carpeta in sorted(self.ESTRUCTURA_CARPETAS.items()):
            simbolo = self.SIMBOLOS[nivel]
            nombre = carpeta.split("_", 1)[1] if "_" in carpeta else carpeta
            carpeta_path = self.vault_path / carpeta
            n = len(list(carpeta_path.glob("*.md"))) if carpeta_path.exists() else 0
            lineas.append(f"| {simbolo} | {nivel:+d} | [[{carpeta}\\|{nombre}]] | `{carpeta}` | {n} |")

        lineas.extend([
            "",
            "## Motores de Procesamiento",
            "",
            "| Motor | Símbolo | Descripción |",
            "|:------|:-------:|:------------|",
            "| S1 | ∂ | Fenomenológico: tokenización + embedding + clasificación |",
            "| S2 | ∫ | Emergencia: convergencia de conceptos (grundzugs) |",
            "| S3 | ⊢ | Lógico: inferencia axiomática (Horn + FCA + Modal) |",
            "| S4 | ⊗ | Predictivo: predicción tensorial (ESN) |",
            "| Bio | ♺ | Biológico: ciclo vital autopoiético |",
            "| Chaos | ⚡ | Caos: borde del caos Regla 110 |",
            "| YO | ∞ | YO Emergente: recursión autoconsciente |",
            "",
            "## Sistemas Lógicos",
            "",
            "| Sistema | Símbolo | Operadores | Nivel |",
            "|:--------|:-------:|:-----------|:------|",
            "| Axiomas Horn | ⊢ | A → B | S3 |",
            "| Mundos Hipotéticos | □◇ | FCA + clausulas | S3+∫ |",
            "| Modal (Kripke) | □◇ | □ necesidad, ◇ posibilidad | ⊠ Metacontexto |",
            "| Mereológica | ⊂∪ | parte-propia, fusión | Transversal |",
            "| Deóntica | OFP | O obligación, F prohibición, P permisión | → Voluntad |",
            "",
            "## 12 Relaciones Fenomenológicas",
            "",
            "| Símbolo | Tipo | Bidireccion | Descripción |",
            "|:-------:|:-----|:-----------:|:------------|",
        ])

        for tipo, cfg in self.RELACIONES.items():
            bidir = "✓" if cfg["bidir"] else "—"
            lineas.append(f"| {cfg['simbolo']} | {tipo} | {bidir} | peso min: {cfg['peso_min']} |")

        lineas.extend([
            "",
            "## 6 Tipos de YO Emergente",
            "",
            "| Nivel | Tipo | Condición de Emergencia |",
            "|:-----:|:-----|:------------------------|",
            "| 0 | PROTO_YO | Bio activo |",
            "| 1 | YO_SENSORIAL | S1 produce grundzugs |",
            "| 2 | YO_AFECTIVO | Valencia emocional presente |",
            "| 3 | YO_REFLEXIVO | yo_presente en contexto (coherencia > 0.4) |",
            "| 4 | YO_SIMBOLICO | S2+S3 producen conceptos/axiomas (coherencia > 0.6) |",
            "| 5 | YO_NARRATIVO | Coherencia > 0.7 + proyección activa |",
            "",
            "## Ciclo Hermenéutico ⟳",
            "",
            "```",
            "Instancias → ... → YO ☉ → OBSERVA ⊙ → Instancias (resignificadas •*)",
            "```",
            "",
            "El YO emergente resignifica las instancias que lo generaron,",
            "enriqueciendo el sistema con nuevas capas de significado.",
            "",
            "## Navegación",
            "",
            "→ [[11_Relaciones\\|Mapa de Relaciones]]",
            "→ [[10_Voluntad\\|Proyecciones (Voluntad)]]",
            "→ [[12_Logica\\|Sistemas Lógicos]]",
            "→ [[_sistema\\\\log_procesamiento.md\\|Log del Sistema]]",
        ])

        ruta = self.vault_path / "00_MOC" / "MOC_Pipeline.md"
        contenido = "\n".join(lineas)
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return contenido

    def generar_moc_niveles(self) -> str:
        """Genera MOC con índice de todas las entidades por nivel."""
        lineas = [
            "---",
            "tags:",
            "  - MOC",
            "  - sistema/niveles",
            f"date: {datetime.datetime.now().strftime('%Y-%m-%d')}",
            "---",
            "",
            "# Mapa de Niveles Ontológicos",
            "",
        ]

        for nivel, carpeta in sorted(self.ESTRUCTURA_CARPETAS.items()):
            simbolo = self.SIMBOLOS[nivel]
            carpeta_path = self.vault_path / carpeta
            lineas.append(f"## {simbolo} Nivel {nivel:+d} — {carpeta}")
            lineas.append("")
            if carpeta_path.exists():
                archivos = sorted(carpeta_path.glob("*.md"))
                if archivos:
                    for archivo in archivos:
                        nombre = archivo.stem
                        lineas.append(f"- [[{carpeta}/{nombre}|{nombre}]]")
                else:
                    lineas.append("*Sin entidades aún*")
            lineas.append("")

        # Agregar sección de lógica
        lineas.extend([
            "## ⊢ □◇ ⊂ OFP — Sistemas Lógicos",
            "",
            "### ⊢ Lógica Pura",
            "- [[12_Logica/Pura/axiomas|Axiomas]]",
            "- [[12_Logica/Pura/mundos_hipoteticos|Mundos Hipotéticos]]",
            "",
            "### □◇ Lógica Modal",
            "- [[12_Logica/Modal|Estados Modales]]",
            "",
            "### ⊂∪ Lógica Mereológica",
            "- [[12_Logica/Mereologica|Composiciones Parte-Todo]]",
            "",
            "### OFP Lógica Deóntica",
            "- [[12_Logica/Deontica|Auditorías Normativas]]",
            "",
        ])

        ruta = self.vault_path / "00_MOC" / "MOC_Niveles.md"
        contenido = "\n".join(lineas)
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return contenido

    def generar_moc_relaciones(self) -> str:
        """Genera MOC de los 12 tipos de relaciones fenomenológicas."""
        ts_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        lineas = [
            "---",
            "tags:",
            "  - MOC",
            "  - MOC/relaciones",
            f"date: {ts_hoy}",
            "---",
            "",
            "# 🕸️ Mapa de Relaciones Fenomenológicas — 12 Tipos",
            "",
            "| Símbolo | Tipo | Bidireccional | Peso Mínimo | Descripción |",
            "|:-------:|:-----|:-------------:|:-----------:|:------------|",
        ]
        descripciones = {
            "SE_PARECE_A":   "Similitud coseno entre embeddings",
            "AGRUPA":        "Inclusión coexistencial",
            "SURGE_DE":      "Emergencia jerárquica (salto 1 nivel)",
            "CONTRADICE":    "Tensión dialéctica (marcadores adversativos)",
            "OBSERVA":       "Auto-observación del YO ☉ sobre instancias",
            "ACTUA_EN":      "Acción de la Voluntad sobre el sistema",
            "INCLUYE":       "Contención contextual",
            "RELACION":      "Gradiente general",
            "TRANSFORMA_EN": "Metamorfosis ontológica",
            "EMERGE_COMO":   "Emergencia (salto >1 nivel)",
            "GENERA":        "Producción de nuevos niveles",
            "DECIDE":        "Decisión existencial del Dasein",
        }
        for tipo, cfg in self.RELACIONES.items():
            bidir = "✓" if cfg["bidir"] else "—"
            desc = descripciones.get(tipo, "")
            lineas.append(
                f"| {cfg['simbolo']} | {tipo} | {bidir} | {cfg['peso_min']} | {desc} |"
            )

        lineas.extend([
            "",
            "## Relaciones Archivadas",
            "",
            "```dataview",
            'TABLE tipo, simbolo, origen_id, destino_id, peso',
            'FROM "11_Relaciones"',
            "SORT fecha DESC",
            "LIMIT 50",
            "```",
        ])

        ruta = self.vault_path / "00_MOC" / "MOC_Relaciones.md"
        contenido = "\n".join(lineas)
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return contenido

    # ──────────────────────────────────────────────────────
    # ESTADO DEL SISTEMA
    # ──────────────────────────────────────────────────────

    def actualizar_estado(self, estado: Dict) -> str:
        """Actualiza la nota de estado actual del sistema con todos los motores."""
        ts = datetime.datetime.now()
        lineas = [
            "---",
            "tags:",
            "  - sistema/estado",
            f"date: {ts.strftime('%Y-%m-%d')}",
            "---",
            "",
            "# Estado Actual del Sistema — Organismo Vivo Hexagonal",
            "",
            f"**Última actualización:** {ts.isoformat()}",
            "",
            "## Pipeline",
            "",
        ]

        for clave, valor in estado.items():
            if isinstance(valor, dict):
                lineas.append(f"### {clave}")
                for k, v in valor.items():
                    lineas.append(f"- **{k}:** {v}")
                lineas.append("")
            else:
                lineas.append(f"- **{clave}:** {valor}")

        # Añadir referencia a los 6 tipos de YO
        lineas.extend([
            "",
            "## Jerarquía de YO",
            "",
            "| Nivel | Tipo | Estado |",
            "|:-----:|:-----|:------:|",
        ])
        tipo_yo_actual = estado.get("tipo_yo", "PROTO_YO")
        for nivel_yo, nombre_yo in self.TIPOS_YO.items():
            activo = "☉ ACTIVO" if nombre_yo == tipo_yo_actual else "—"
            lineas.append(f"| {nivel_yo} | {nombre_yo} | {activo} |")

        ruta = self.vault_path / "_sistema" / "estado_actual.md"
        contenido = "\n".join(lineas)
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return str(ruta)

    def log_procesamiento(self, mensaje: str, tipo: str = "info"):
        """Agrega una entrada al log de procesamiento."""
        ruta = self.vault_path / "_sistema" / "log_procesamiento.md"
        if not ruta.exists():
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write("---\ntags:\n  - sistema/log\n---\n\n")
                f.write("# Log de Procesamiento — Organismo Vivo\n\n")
                f.write("Entrada: `:-....yo...`\n\n")

        emojis = {"info": "ℹ️", "warn": "⚠️", "error": "❌", "ok": "✅", "logica": "⊢"}
        emoji = emojis.get(tipo, "📌")

        with open(ruta, 'a', encoding='utf-8') as f:
            f.write(
                f"- {emoji} [{datetime.datetime.now().isoformat()}] {mensaje}\n"
            )
