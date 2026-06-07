# Módulo: Emergencia de Conceptos

## 📋 Descripción

Este módulo implementa un sistema de **emergencia de conceptos abstractos** basado en patrones relacionales observables. Permite que conceptos complejos (como entropía, información, momentum) emerjan a partir de experimentos comportamentales sobre sistemas, sin necesidad de conocer sus propiedades internas a priori.

## 🎯 Objetivos

1. **Descubrimiento Relacional**: Identificar propiedades ocultas mediante observación de comportamientos
2. **Abstracción Progresiva**: Construir conceptos de nivel superior desde observaciones de nivel inferior
3. **Grounding Teórico**: Conectar conceptos emergentes con teorías formales existentes
4. **Validación Empírica**: Verificar que los conceptos emergidos coincidan con mediciones reales

## 🏗️ Arquitectura

```
emergencia_concepto/
├── motor_emergencia.py      # Orquestador principal
├── sistema_observado.py      # Sistemas con propiedades ocultas
├── experimento.py            # Batería de experimentos comportamentales
├── patron_relacional.py      # Detección de correlaciones y patrones
├── concepto_emergente.py     # Representación de conceptos abstractos
└── simulacion_entropia.py    # Demostración: emergencia de entropía
```

## 🔬 Tipos de Experimentos

| Tipo | Descripción | Métricas |
|------|-------------|----------|
| **PREDICIBILIDAD** | Mide qué tan predecible es el sistema | predicibilidad (0-1), cambios_observados |
| **REVERSIBILIDAD** | Evalúa si los cambios son reversibles | reversibilidad (0-1), estado_final |
| **DIVERSIDAD** | Cuenta configuraciones únicas posibles | configuraciones_unicas, sorpresa_promedio |
| **EVOLUCION_TEMPORAL** | Observa tendencias temporales | P_inicial, P_final, tendencia |
| **INTERACCION_AGENTE** | Respuesta a agentes externos | reaccion, tiempo_atencion |
| **RESPUESTA_PERTURBACION** | Amplificación de perturbaciones | amplificacion |

## 📖 Ejemplo de Uso

```python
from emergencia_concepto.motor_emergencia import MotorEmergenciaConceptos
from emergencia_concepto.sistema_observado import SistemaObservado
from emergencia_concepto.experimento import TipoExperimento

# 1. Crear motor
motor = MotorEmergenciaConceptos()

# 2. Definir sistemas con propiedades ocultas
sistema_A = SistemaObservado("cristal")
sistema_A.definir_propiedad_oculta("entropia", 0.01)

sistema_B = SistemaObservado("plasma")
sistema_B.definir_propiedad_oculta("entropia", 12.7)

motor.agregar_sistema(sistema_A)
motor.agregar_sistema(sistema_B)

# 3. Ejecutar experimentos
experimentos = motor.ejecutar_bateria_experimentos([
    TipoExperimento.PREDICIBILIDAD,
    TipoExperimento.REVERSIBILIDAD,
    TipoExperimento.DIVERSIDAD,
    TipoExperimento.EVOLUCION_TEMPORAL
])

# 4. Detectar patrones
patron = motor.detectar_patrones(threshold_correlacion=0.8)
print(patron.generar_hipotesis())

# 5. Emerger concepto
concepto = motor.emergir_concepto("MEDIDA_DE_DESORDEN")

print(f"Valores: {concepto.valores}")
print(f"Leyes: {concepto.leyes_cualitativas}")
print(f"Certeza: {concepto.certeza}")

# 6. Grounding con teoría
concepto.ground_with_theory(
    nombre_teorico="ENTROPÍA",
    formula="S = k_B * ln(Ω)",
    certeza_match=0.96
)

print(f"Concepto real: {concepto.nombre_real}")
```

## 🧪 Simulación Completa: Entropía

Ejecutar la simulación de emergencia de entropía:

```bash
python -m emergencia_concepto.simulacion_entropia
```

**Salida esperada:**
```
===== SIMULACIÓN: EMERGENCIA DE ENTROPÍA DESDE RELACIONES =====

[1] Creando sistemas desconocidos...
  - sistema_A creado (Realidad oculta: Cristal Perfecto)
  - sistema_E creado (Realidad oculta: Plasma Caótico)

[2] Ejecutando batería de experimentos comportamentales...
  > Experimento 'predicibilidad' completado
  > Experimento 'reversibilidad' completado
  
[3] Analizando correlaciones y detectando patrones...
  - Hipótesis: P parece medir el DESORDEN del sistema

[4] Emergiendo concepto abstracto...
  - Definición relacional descubierta
  - Leyes: "P nunca decrece espontáneamente (dP/dt ≥ 0)"
  
[5] Grounding con Teoría Termodinámica...
  ¡MATCH ENCONTRADO! MEDIDA_DE_DESORDEN ≡ ENTROPÍA
  Certeza: 0.96
```

## 🔧 Configuración

### Dependencias

```
numpy>=1.21.0
scikit-learn>=1.0.0
```

### Parámetros Clave

- `threshold_correlacion`: Umbral para considerar correlación significativa (default: 0.8)
- `eps` (clustering): Radio para DBSCAN (default: 0.5)
- `min_samples`: Muestras mínimas por cluster (default: 2)

## 📊 Métricas de Calidad

| Métrica | Fórmula | Interpretación |
|---------|---------|----------------|
| **Certeza** | min(1.0, num_experimentos / 4.0) | Confianza en el concepto emergido |
| **Correlaciones** | \|r\| > threshold | Número de correlaciones fuertes |
| **Convergencia** | Punto fijo en inferencias | Estabilidad del concepto |

## 🎓 Conceptos Emergibles

### Nivel 1: Propiedades Físicas Simples
- **Entropía** (S): Medida de desorden (10-100 obs.)
- **Temperatura** (T): Energía cinética promedio (20-50 obs.)

### Nivel 2: Cantidades Conservadas
- **Momentum** (p): Cantidad de movimiento (30-80 obs.)
- **Energía** (E): Capacidad de realizar trabajo (40-100 obs.)

### Nivel 3: Conceptos Abstractos
- **Información** (I): Contenido Shannon (50-150 obs.)
- **Complejidad** (K): Complejidad de Kolmogorov (100-300 obs.)

## 🚀 Roadmap

- [x] Sistema base de emergencia
- [x] Experimentos básicos (4 tipos)
- [x] Detección de patrones (FCA + clustering)
- [x] Simulación de entropía
- [ ] Integración con Neo4j para persistir conceptos emergidos
- [ ] Visualización de patrones relacionales
- [ ] Experimentos avanzados (6+ tipos)
- [ ] Auto-diseño de experimentos basado en incertidumbre
- [ ] Multi-nivel: conceptos derivados de conceptos

## 📝 Notas

- **Limitación**: Los valores de propiedades ocultas se usan solo para simulación. En un sistema real, estas emergirían completamente de las observaciones.
- **Extensibilidad**: Nuevos experimentos pueden agregarse heredando de la clase `Experimento`.

## 🤝 Integración con YO Estructural

Este módulo se integra con:
- **motor_yo/**: Los conceptos emergidos se convierten en Grundzugs
- **procesadores/fca_processor**: Usa FCA para extraer conceptos formales
- **Neo4j**: Persiste conceptos emergidos como nodos `ConceptoAbstracto`

## 📚 Referencias

- Ganter, B. & Wille, R. (1999). *Formal Concept Analysis*.
- Shannon, C. (1948). *A Mathematical Theory of Communication*.
- Boltzmann, L. (1877). *Über die Beziehung zwischen dem zweiten Hauptsatze...*.
