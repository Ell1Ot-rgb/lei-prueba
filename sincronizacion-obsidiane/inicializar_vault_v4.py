"""
inicializar_vault_v4.py
========================
Inicializa el vault de Obsidian con la estructura completa v4.0.

Uso:
    python inicializar_vault_v4.py --vault "C:/Users/Public/Robot/Zerg"

Crea:
    - Carpetas 00_MOC hasta 12_Logica/ + _sistema/ + capas usuario
    - MOC_Pipeline.md con simbología completa
    - MOC_Niveles.md con índice de niveles
    - MOC_Relaciones.md con 12 tipos de relaciones
    - Templates/ con Nota_Atomica.md y Reflexion_Fenomeno.md
    - _Dashboard/ con MOC_Personal.md y MOC_Sistema.md

Arquitectura v4.0 — Sistema Vivo Hexagonal Final v2
"""

import argparse
import pathlib
import datetime
import sys

VAULT_DEFAULT = r"C:\Users\Public\Robot\Zerg"


def crear_dashboard_sistema(vault: pathlib.Path):
    """Crea el dashboard Dataview con todos los sistemas lógicos."""
    contenido = '''---
tags:
  - dashboard
  - sistema
---

# 🧠 Dashboard — Organismo Vivo Hexagonal

## ☉ Estado del YO Emergente

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

## ⊢ Axiomas S3 (Lógica Pura)

```dataview
TABLE regla_raw, premisa, conclusion, inferencias_generadas
FROM "12_Logica/Pura/axiomas"
SORT fecha DESC
```

## □◇ Mundos Hipotéticos

```dataview
TABLE id, length(proposiciones_verificadas) AS Proposiciones
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

## 🕸️ Relaciones Recientes

```dataview
TABLE tipo, simbolo, origen_id, destino_id, peso
FROM "11_Relaciones"
SORT fecha DESC
LIMIT 20
```

## ⟳ Resignificaciones del YO

```dataview
LIST
FROM "02_Instancias" OR "04_Vohexistencias"
WHERE contains(file.content, "Resignificación del YO")
SORT file.mtime DESC
LIMIT 10
```

## 📓 Tus Notas Sin Enlace al Sistema

```dataview
LIST
FROM "51_Permanente"
WHERE tipo = "nota-atomica" AND (fenomeno_origen = "" OR !fenomeno_origen)
SORT file.mtime DESC
```
'''
    ruta = vault / "_Dashboard" / "MOC_Sistema.md"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def crear_dashboard_personal(vault: pathlib.Path):
    """Crea el dashboard personal del usuario."""
    contenido = '''---
tags:
  - dashboard
  - personal
---

# 🌱 Mi Cerebro Digital

## Notas Recientes

```dataview
TABLE fenomeno_origen, nivel_ontologico, fecha
FROM "51_Permanente"
WHERE tipo = "nota-atomica"
SORT fecha DESC
LIMIT 10
```

## Proyectos Activos

```dataview
LIST
FROM "52_Proyectos"
WHERE !contains(tags, "archivado")
```

## Áreas de Responsabilidad

```dataview
LIST
FROM "53_Areas"
```

## Captura Pendiente

```dataview
LIST
FROM "50_Entrada"
WHERE !procesado
SORT file.mtime DESC
```

## Estado del Sistema Hoy

![[_sistema/estado_actual]]
'''
    ruta = vault / "_Dashboard" / "MOC_Personal.md"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def crear_template_nota_atomica(vault: pathlib.Path):
    """Template Templater para notas atómicas del usuario."""
    # Escribimos con <% %> como texto plano (no Templater activo)
    contenido = '''---
tipo: nota-atomica
id: "<% tp.date.now("YYYYMMDDHHmm") %>"
titulo: "<% tp.file.title %>"
fenomeno_origen: ""
nivel_ontologico: ""
contexto_personal: ""
tags:
  - personal/atomica
fecha: "<% tp.date.now("YYYY-MM-DDTHH:mm:ss") %>"
---

# <% tp.file.title %>

## Idea Central

[Una sola oración que capture la esencia]

## Conexión con el Sistema

- Fenómeno que la generó: [[]]
- Tipo de relación: [≈ SE_PARECE_A | ↗ SURGE_DE | ⊃ INCLUYE | ⊘ CONTRADICE]

## Desarrollo

[Elabora la idea aquí]

## Preguntas Abiertas

- [ ] ...

## Referencias

- ...
'''
    ruta = vault / "_Templates" / "Nota_Atomica.md"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def crear_template_reflexion(vault: pathlib.Path):
    """Template para reflexiones sobre fenómenos del sistema."""
    contenido = '''---
tipo: reflexion-fenomeno
fenomeno_id: ""
simbolo: "◉"
tags:
  - personal/reflexion
  - nivel/fenomeno
fecha: "<% tp.date.now("YYYY-MM-DDTHH:mm:ss") %>"
---

# Reflexión: <% tp.file.title %>

## Fenómeno que inspira esta nota

[[]] ← enlaza aquí el fenómeno ◉

## ¿Qué observo?

[Lo que se muestra a tu conciencia al leer este fenómeno]

## ¿Qué significa para mí?

[Tu interpretación personal]

## ¿Qué acción sugiere?

- [ ] ...

## ¿Cómo se conecta con lo que ya sé?

[Links a otras notas en 51_Permanente/]
'''
    ruta = vault / "_Templates" / "Reflexion_Fenomeno.md"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def crear_estado_inicial(vault: pathlib.Path):
    """Crea el estado inicial del sistema."""
    ts = datetime.datetime.now().isoformat()
    contenido = f"""---
tags:
  - sistema/estado
date: {datetime.datetime.now().strftime('%Y-%m-%d')}
---

# Estado del Sistema — Organismo Vivo Hexagonal v4.0

**Inicializado:** {ts}

## Entrada del Sistema

```
:-....yo...
: → inicio de distinción
- → línea de separación
. → punto: unidad mínima instancia
yo → presencia autoconsciente
... → continuidad, expansión
```

## Estado del Pipeline

| Motor | Símbolo | Estado |
|:------|:-------:|:------:|
| S1 Fenomenológico | ∂ | ⏸ En espera |
| S2 Emergencia | ∫ | ⏸ En espera |
| S3 Lógico | ⊢ | ⏸ En espera |
| S4 Predictivo | ⊗ | ⏸ En espera |
| Bio | ♺ | ⏸ En espera |
| Chaos | ⚡ | ⏸ En espera |
| YO | ∞ | ⏸ PROTO_YO |

## Niveles Ontológicos

| Símbolo | Nivel | Entidades |
|:-------:|:-----:|:---------:|
| ø | -4 | 0 |
| • | -3 | 0 |
| ∇ | -2 | 0 |
| ◊ | -1 | 0 |
| ◉ | 0 | 0 |
| ⊞ | +1 | 0 |
| ⊡ | +2 | 0 |
| ⊠ | +3 | 0 |
| ☉ | +4 | 0 |

> Vault inicializado correctamente. Listo para recibir datos.
"""
    ruta = vault / "_sistema" / "estado_actual.md"
    ruta.write_text(contenido, encoding="utf-8")

    log_contenido = f"""---
tags:
  - sistema/log
---

# Log de Procesamiento — Organismo Vivo v4.0

Entrada: `:-....yo...`

- ✅ [{ts}] Vault inicializado — Sistema Vivo Hexagonal Final v2
"""
    log_ruta = vault / "_sistema" / "log_procesamiento.md"
    log_ruta.write_text(log_contenido, encoding="utf-8")
    return ruta


def main():
    parser = argparse.ArgumentParser(
        description="Inicializa el vault Obsidian del Sistema Vivo Hexagonal v4.0"
    )
    parser.add_argument(
        "--vault", default=VAULT_DEFAULT,
        help=f"Ruta al vault de Obsidian (default: {VAULT_DEFAULT})"
    )
    args = parser.parse_args()

    vault = pathlib.Path(args.vault)
    print(f"\n🧠 Sistema Vivo Hexagonal — Inicializando vault v4.0")
    print(f"   Vault: {vault}\n")

    # ── Importar ObsidianSync ──────────────────────────────────
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).parent))
        from adapters.outbound.obsidian_sync import ObsidianSync
        sync = ObsidianSync(vault_path=str(vault))
        print("✅ ObsidianSync importado")
    except ImportError as e:
        print(f"⚠️  ObsidianSync no disponible ({e})")
        print("   Creando estructura de carpetas manualmente...")
        # Crear carpetas manualmente si no hay acceso al módulo
        carpetas = [
            "00_MOC", "01_PreInstancias", "02_Instancias", "03_Gradientes",
            "04_Vohexistencias", "05_Fenomenos", "06_Contextos",
            "07_Macrocontextos", "08_Metacontextos", "09_YO",
            "10_Voluntad", "11_Relaciones",
            "12_Logica/Pura/axiomas", "12_Logica/Pura/mundos_hipoteticos",
            "12_Logica/Modal", "12_Logica/Mereologica", "12_Logica/Deontica",
            "_sistema", "_Templates", "_Dashboard",
            "50_Entrada", "51_Permanente", "52_Proyectos",
            "53_Areas", "54_Recursos", "55_Archivo",
        ]
        for c in carpetas:
            (vault / c).mkdir(parents=True, exist_ok=True)
        sync = None

    # ── Carpetas del usuario ───────────────────────────────────
    for carpeta in ["50_Entrada", "51_Permanente", "52_Proyectos",
                    "53_Areas", "54_Recursos", "55_Archivo",
                    "_Templates", "_Dashboard"]:
        (vault / carpeta).mkdir(parents=True, exist_ok=True)

    # ── MOCs del sistema ───────────────────────────────────────
    if sync:
        sync.generar_moc_pipeline()
        print("✅ MOC_Pipeline.md generado")
        sync.generar_moc_niveles()
        print("✅ MOC_Niveles.md generado")
        sync.generar_moc_relaciones()
        print("✅ MOC_Relaciones.md generado")

    # ── Estado inicial ─────────────────────────────────────────
    crear_estado_inicial(vault)
    print("✅ _sistema/estado_actual.md creado")

    # ── Templates ──────────────────────────────────────────────
    crear_template_nota_atomica(vault)
    print("✅ _Templates/Nota_Atomica.md creado")
    crear_template_reflexion(vault)
    print("✅ _Templates/Reflexion_Fenomeno.md creado")

    # ── Dashboards ─────────────────────────────────────────────
    crear_dashboard_sistema(vault)
    print("✅ _Dashboard/MOC_Sistema.md creado")
    crear_dashboard_personal(vault)
    print("✅ _Dashboard/MOC_Personal.md creado")

    print(f"\n🎉 Vault inicializado correctamente en: {vault}")
    print("\n   Próximos pasos:")
    print("   1. Abre Obsidian y selecciona esta carpeta como vault")
    print("   2. Instala plugins: Dataview, Templater, Graph View")
    print("   3. Ejecuta el pipeline: python main.py")
    print("   4. Las notas aparecerán automáticamente en 05_Fenomenos/, 09_YO/, etc.")


if __name__ == "__main__":
    main()
