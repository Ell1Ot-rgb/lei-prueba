# 🏗️ Nueva Estructura Hexagonal

Esta carpeta contiene la reorganización del sistema en arquitectura hexagonal.

## 📊 Resumen

| Carpeta | Archivos | Contenido |
|:--------|:--------:|:----------|
| `core_new/domain/` | 4 | Entidades (instancia, preinstancia, vohexistencia) |
| `core_new/engines/s1_fenomenologia/` | 8 | Tokenizer, Embedder, Clasificador, componentes |
| `core_new/engines/s2_emergencia/` | 9 | Motor emergencia, FCA, patrones |
| `core_new/engines/s3_logica/` | 8 | Axiomas, mundos hipotéticos |
| `core_new/engines/chaos/` | 3 | Autómatas 1D, v2 |
| `core_new/engines/bio/` | 34 | 17 subsistemas biológicos |
| `adapters/inbound/` | 2 | Redis listener |
| `adapters/outbound/` | 7 | Neo4j, n8n, Supabase, Gemini |
| `interfaces/` | 6 | Puertos neuronales, facade, health |
| `tests/` | 5 | Validación, demos |
| **TOTAL** | **99** | - |

## 🔌 Puntos de Entrada

- **Sistema Principal**: `interfaces/neural_ports.py`
- **Health Monitor**: `interfaces/health_monitor.py`
- **Benchmark**: `interfaces/benchmark.py`

## 📁 Estructura Original

La estructura original (`core/`, `procesadores/`, etc.) se mantiene intacta.
La nueva estructura está en carpetas separadas (`core_new/`, `adapters/`, etc.)
para permitir migración gradual.
