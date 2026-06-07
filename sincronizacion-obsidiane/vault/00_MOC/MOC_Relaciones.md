---
tags:
  - MOC
  - MOC/relaciones
date: 2026-06-04
---

# 🕸️ Mapa de Relaciones Fenomenológicas — 12 Tipos

| Símbolo | Tipo | Bidireccional | Peso Mínimo | Descripción |
|:-------:|:-----|:-------------:|:-----------:|:------------|
| ≈ | SE_PARECE_A | ✓ | 0.3 | Similitud coseno entre embeddings |
| ⊕ | AGRUPA | — | 0.5 | Inclusión coexistencial |
| ↗ | SURGE_DE | — | 0.6 | Emergencia jerárquica (salto 1 nivel) |
| ⊘ | CONTRADICE | ✓ | 0.5 | Tensión dialéctica (marcadores adversativos) |
| ⊙ | OBSERVA | — | 0.7 | Auto-observación del YO ☉ sobre instancias |
| → | ACTUA_EN | — | 0.6 | Acción de la Voluntad sobre el sistema |
| ⊃ | INCLUYE | — | 0.4 | Contención contextual |
| — | RELACION | — | 0.1 | Gradiente general |
| ⇒ | TRANSFORMA_EN | — | 0.5 | Metamorfosis ontológica |
| ⤴ | EMERGE_COMO | — | 0.6 | Emergencia (salto >1 nivel) |
| ⊳ | GENERA | — | 0.5 | Producción de nuevos niveles |
| ⊶ | DECIDE | — | 0.7 | Decisión existencial del Dasein |

## Relaciones Archivadas

```dataview
TABLE tipo, simbolo, origen_id, destino_id, peso
FROM "11_Relaciones"
SORT fecha DESC
LIMIT 50
```