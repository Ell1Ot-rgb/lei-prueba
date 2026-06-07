---
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
