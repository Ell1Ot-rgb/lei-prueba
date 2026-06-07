---
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
