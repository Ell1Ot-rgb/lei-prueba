"""
Inicializador del Vault de Obsidian — Organismo Vivo v4.0
=========================================================

Crea toda la estructura de carpetas, MOCs, templates y dashboards.
Ejecutar UNA VEZ antes de lanzar el pipeline principal.

Usage:
    python inicializar_vault.py
    python inicializar_vault.py --vault-path "C:\\MiVault"
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv


def obtener_vault_path(args_path=None):
    """Determina el path del vault por argumento, .env o default."""
    if args_path:
        return Path(args_path)
    load_dotenv()
    env_path = os.environ.get("VAULT_PATH", "")
    if env_path:
        return Path(env_path)
    return Path(r"C:\Users\Public\Robot\Zerg")


def crear_estructura(vault: Path):
    """Crea toda la estructura de carpetas del vault."""
    carpetas = [
        "00_MOC",
        "01_PreInstancias",
        "02_Instancias",
        "03_Gradientes",
        "04_Vohexistencias",
        "05_Fenomenos",
        "06_Contextos",
        "07_Macrocontextos",
        "08_Metacontextos",
        "09_YO",
        "10_Voluntad",
        "11_Relaciones",
        "12_Logica/Pura/axiomas",
        "12_Logica/Pura/mundos_hipoteticos",
        "12_Logica/Modal",
        "12_Logica/Mereologica",
        "12_Logica/Deontica",
        "_sistema",
        "50_Entrada",
        "51_Permanente",
        "52_Proyectos",
        "53_Areas",
        "54_Recursos",
        "55_Archivo",
        "_Templates",
        "_Dashboard",
    ]
    for c in carpetas:
        (vault / c).mkdir(parents=True, exist_ok=True)
    print(f"  [OK] {len(carpetas)} carpetas creadas en {vault}")


def crear_template_nota_atomica(vault: Path):
    """Crea el template Templater para notas atómicas del usuario."""
    contenido = r"""---
tipo: nota-atomica
id: "<% tp.date.now("YYYYMMDDHHmm") %>"
titulo: "<% tp.file.title %>"
fenomeno_origen: ""
nivel_ontologico: ""
contexto_personal: ""
tags:
  - personal/atomica
  - estado/<% tp.date.now("YYYY-MM") %>
fecha: "<% tp.date.now("YYYY-MM-DDTHH:mm:ss") %>"
---

# <% tp.file.title %>

## Idea Central

[Tu idea principal en una sola oración]

## Conexión con el Sistema

Fenómeno que la generó: [[]]
Relación: [≈ SE_PARECE_A / ↗ SURGE_DE / ⊃ INCLUYE / ...]

## Elaboración

[Desarrolla la idea]

## Referencias

[Fuentes o notas relacionadas]

## Preguntas Abiertas

- [ ] ...
"""
    ruta = vault / "_Templates" / "Nota_Atomica.md"
    ruta.write_text(contenido, encoding="utf-8")
    print("  [OK] Template: Nota_Atomica.md")


def crear_template_reflexion(vault: Path):
    """Crea el template para reflexión personal sobre un fenómeno del sistema."""
    contenido = r"""---
tipo: reflexion-fenomeno
id: "<% tp.date.now("YYYYMMDDHHmm") %>"
titulo: "<% tp.file.title %>"
fenomeno_id: ""
tipo_fenomeno: ""
intensidad_observada: 0
perspectiva_personal: ""
tags:
  - personal/reflexion
  - nivel/fenomeno
fecha: "<% tp.date.now("YYYY-MM-DDTHH:mm:ss") %>"
---

# ◉ Reflexión: <% tp.file.title %>

## Fenómeno Observado

**Fenómeno:** [[]]
**Tipo:** 
**Intensidad del sistema:** 

## Mi Interpretación

[¿Qué significa este fenómeno para ti?]

## Conexiones Personales

- [[]]  (relación: )
- [[]]  (relación: )

## Preguntas que Genera

- [ ] 
- [ ] 

## Acción / Decisión (⊶)

[¿Este fenómeno requiere una acción de tu parte?]
"""
    ruta = vault / "_Templates" / "Reflexion_Fenomeno.md"
    ruta.write_text(contenido, encoding="utf-8")
    print("  [OK] Template: Reflexion_Fenomeno.md")


def crear_dashboard_sistema(vault: Path):
    """Crea el dashboard Dataview principal del sistema."""
    contenido = """---
tags:
  - dashboard
  - sistema
---

# 🧠 Dashboard — Organismo Vivo

## ☉ Estado del YO

```dataview
TABLE tipo_yo, tipo_nivel, nivel_emergencia, coherencia_promedio, tensiones_detectadas
FROM "09_YO"
SORT fecha DESC
LIMIT 5
```

## ◉ Fenómenos Núcleo Activos

```dataview
TABLE tipo_fenomeno, intensidad, frecuencia, validacion_fenomenologica
FROM "05_Fenomenos"
WHERE es_nucleo = true
SORT intensidad DESC
LIMIT 10
```

## → Proyecciones de Voluntad

```dataview
TABLE direccion, intensidad, prediccion, deontica_permitido
FROM "10_Voluntad"
SORT fecha DESC
LIMIT 5
```

## ⊢ Axiomas Inferidos (S3)

```dataview
TABLE regla_raw, premisa, conclusion, inferencias_generadas
FROM "12_Logica/Pura/axiomas"
SORT fecha DESC
```

## □◇ Mundos Hipotéticos

```dataview
TABLE hechos_base, length(proposiciones_verificadas) AS "Proposiciones"
FROM "12_Logica/Pura/mundos_hipoteticos"
SORT fecha DESC
LIMIT 5
```

## ⊠ Metacontextos con Lógica Modal

```dataview
TABLE patron_emergente, coherencia, necesidad_evaluada, posibilidad_detectada
FROM "08_Metacontextos"
WHERE necesidad_evaluada = true OR posibilidad_detectada = true
SORT fecha DESC
```

## 🕸 Relaciones Recientes

```dataview
TABLE tipo, simbolo, origen_id, destino_id, peso
FROM "11_Relaciones"
SORT fecha DESC
LIMIT 20
```

## 📓 Notas Personales Sin Enlace

```dataview
LIST
FROM "51_Permanente"
WHERE tipo = "nota-atomica" AND (fenomeno_origen = "" OR !fenomeno_origen)
SORT file.mtime DESC
```

## ⟳ Resignificaciones Recientes

```dataview
LIST
FROM "02_Instancias" OR "04_Vohexistencias"
WHERE contains(file.content, "⟳ Resignificación")
SORT file.mtime DESC
LIMIT 10
```
"""
    ruta = vault / "_Dashboard" / "MOC_Sistema.md"
    ruta.write_text(contenido, encoding="utf-8")
    print("  [OK] Dashboard: MOC_Sistema.md")


def crear_dashboard_personal(vault: Path):
    """Crea el MOC personal del usuario."""
    contenido = """---
tags:
  - dashboard
  - personal
---

# 📝 Mi Cerebro Digital — MOC Personal

## Notas Recientes

```dataview
TABLE titulo, fenomeno_origen, nivel_ontologico, fecha
FROM "51_Permanente"
SORT fecha DESC
LIMIT 15
```

## Reflexiones sobre Fenómenos

```dataview
TABLE fenomeno_id, perspectiva_personal, fecha
FROM "51_Permanente" OR "_Templates"
WHERE tipo = "reflexion-fenomeno"
SORT fecha DESC
LIMIT 10
```

## Proyectos Activos (PARA)

```dataview
LIST
FROM "52_Proyectos"
SORT file.mtime DESC
```

## Áreas de Responsabilidad

```dataview
LIST
FROM "53_Areas"
SORT file.name ASC
```

## Captura Rápida (Fleeting)

```dataview
LIST
FROM "50_Entrada"
SORT file.mtime DESC
LIMIT 10
```

## Enlace al Sistema

→ [[_Dashboard/MOC_Sistema|Dashboard del Sistema]]
→ [[00_MOC/MOC_Pipeline|Pipeline Completo]]
→ [[00_MOC/MOC_Niveles|Mapa de Niveles]]
→ [[00_MOC/MOC_Relaciones|Mapa de Relaciones]]
"""
    ruta = vault / "_Dashboard" / "MOC_Personal.md"
    ruta.write_text(contenido, encoding="utf-8")
    print("  [OK] Dashboard: MOC_Personal.md")


def generar_mocs_iniciales(vault: Path):
    """Genera los MOCs automáticos usando ObsidianSync."""
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from adapters.outbound.obsidian_sync import ObsidianSync
        sync = ObsidianSync(str(vault))
        sync.generar_moc_pipeline()
        sync.generar_moc_niveles()
        sync.generar_moc_relaciones()
        sync.actualizar_estado({
            "status": "inicializado",
            "tipo_yo": "PROTO_YO",
            "fenomenos": 0,
            "contextos": 0,
            "macrocontextos": 0,
            "metacontextos": 0,
        })
        sync.log_procesamiento("Vault inicializado correctamente", tipo="ok")
        print("  [OK] MOCs generados: Pipeline, Niveles, Relaciones")
        print("  [OK] Estado inicial y log creados")
    except Exception as e:
        print(f"  [WARN] No se pudieron generar MOCs automáticos: {e}")
        print("         (Se generarán al ejecutar el pipeline por primera vez)")


def main():
    parser = argparse.ArgumentParser(
        description="Inicializar vault de Obsidian — Organismo Vivo v4.0"
    )
    parser.add_argument(
        "--vault-path", type=str, default=None,
        help="Ruta del vault (default: VAULT_PATH en .env o C:\\Users\\Public\\Robot\\Zerg)"
    )
    args = parser.parse_args()

    vault = obtener_vault_path(args.vault_path)

    print("=" * 60)
    print("  INICIALIZACIÓN DEL VAULT — Organismo Vivo v4.0")
    print(f"  Vault: {vault}")
    print("=" * 60)
    print()

    print("[1/6] Creando estructura de carpetas...")
    crear_estructura(vault)

    print("[2/6] Creando template: Nota Atómica...")
    crear_template_nota_atomica(vault)

    print("[3/6] Creando template: Reflexión Fenómeno...")
    crear_template_reflexion(vault)

    print("[4/6] Creando dashboard: Sistema...")
    crear_dashboard_sistema(vault)

    print("[5/6] Creando dashboard: Personal...")
    crear_dashboard_personal(vault)

    print("[6/6] Generando MOCs automáticos...")
    generar_mocs_iniciales(vault)

    print()
    print("=" * 60)
    print("  [OK] VAULT INICIALIZADO CORRECTAMENTE")
    print(f"  Abre Obsidian -> Open folder as vault -> {vault}")
    print("  Instala plugins: Dataview, Templater")
    print("=" * 60)


if __name__ == "__main__":
    main()
