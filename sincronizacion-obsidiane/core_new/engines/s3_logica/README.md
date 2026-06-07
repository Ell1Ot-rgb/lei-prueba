# Módulo: Lógica Pura

## 📋 Descripción

Este módulo implementa un motor de **razonamiento sobre mundos hipotéticos** definidos puramente por lógica y relaciones simbólicas, sin necesidad de input sensorial. Permite crear universos abstractos cerrados donde los conceptos emergen desde axiomas y relaciones, no desde datos empíricos.

## 🎯 Objetivos

1. **Razonamiento Abstracto**: Procesar mundos definidos solo por propiedades lógicas
2. **Inferencia Deductiva**: Aplicar axiomas para descubrir nuevas propiedades
3. **Análisis Formal de Conceptos (FCA)**: Extraer conceptos desde relaciones puras
4. **Integración Híbrida**: Fusionar conocimiento empírico con conocimiento lógico

## 🏗️ Arquitectura

```
logica_pura/
├── mundo_hipotetico.py       # Contenedor de universos abstractos
├── motor_hipotetico.py        # Procesador de mundos y FCA
├── instancia_abstracta.py     # Objetos puramente lógicos
└── motor_axiomas.py           # Motor de inferencia lógica
```

## 🧠 Filosofía

Este módulo implementa **RACIONALISMO PURO**, complementando el **EMPIRISMO FENOMENOLÓGICO** del sistema principal.

| Aspecto | Sistema Principal | Lógica Pura |
|---------|-------------------|-------------|
| **Input** | Archivos sensoriales | Definiciones simbólicas |
| **Procesamiento** | REMForge, qualia | Axiomas, FCA |
| **Output** | Conceptos empíricos | Conceptos abstractos |
| **Certeza** | Probabilística (0-1) | Lógica (0 o 1) |
| **Ejemplo** | "Lluvia" de 45 archivos | "Artefactos" de 3 definiciones |

## 📖 Ejemplo de Uso: Mundo de 3 Objetos

```python
from logica_pura.mundo_hipotetico import MundoHipotetico
from logica_pura.motor_hipotetico import MotorHipotetico

# 1. Crear mundo abstracto
mundo = MundoHipotetico("mundo_3_objetos")

# 2. Definir objetos con propiedades lógicas
mundo.agregar_objeto("carro", {
    "artificial": True,
    "movil": True,
    "grande": True
})

mundo.agregar_objeto("manzana", {
    "natural": True,
    "comestible": True,
    "pequeño": True
})

mundo.agregar_objeto("mesa", {
    "artificial": True,
    "inmovil": True,
    "soporte": True,
    "grande": True
})

# 3. Definir relaciones espaciales
mundo.agregar_relacion("manzana", "sobre", "mesa")
mundo.agregar_relacion("carro", "cerca_de", "mesa")

# 4. Agregar axiomas (lógica de primer orden)
mundo.agregar_axioma("∀x (comestible(x) → organico(x))")
mundo.agregar_axioma("∀x (natural(x) → ¬artificial(x))")
mundo.agregar_axioma("∀x,y (sobre(x, y) → soporte(y))")

# 5. Procesar mundo
motor = MotorHipotetico()
resultado = motor.ingestar_mundo(mundo)

print(f"Instancias generadas: {resultado['num_instancias']}")
print(f"Conceptos emergidos: {len(resultado['conceptos_generados'])}")

# Visualizar instancias con propiedades inferidas
for inst in resultado['instancias']:
    print(f"{inst['concepto']}: {inst['propiedades']}")
```

**Salida esperada:**

```
Instancias generadas: 5

Instancias (con inferencias aplicadas):
  - carro: {artificial=True, movil=True, grande=True}
  - manzana: {natural=True, comestible=True, pequeño=True, organico=True}  ← Inferido
  - mesa: {artificial=True, inmovil=True, soporte=True, grande=True}
  - manzana_sobre_mesa: {tipo_relacion=sobre, sujeto=manzana, objeto=mesa}
  - carro_cerca_de_mesa: {tipo_relacion=cerca_de, sujeto=carro, objeto=mesa}

Conceptos Abstractos (FCA):
  - GRUPO_ARTIFICIAL: {carro, mesa}
  - GRUPO_GRANDE: {carro, mesa}
  - GRUPO_NATURAL: {manzana}
  - GRUPO_COMESTIBLE: {manzana}
```

## 🔧 Componentes

### 1. MundoHipotetico

Contenedor de un universo lógico cerrado.

```python
mundo = MundoHipotetico("nombre")
mundo.agregar_objeto(nombre, propiedades_dict)
mundo.agregar_relacion(obj1, relacion, obj2)
mundo.agregar_axioma(regla_logica)
instancias = mundo.instanciar()  # Genera instancias con inferencias
```

### 2. InstanciaAbstracta

Objeto puramente lógico (sin qualia).

**Diferencias con InstanciaFenomenologica:**
- No tiene `energia`, `entropia`, `hash_fisico`
- `coherencia` siempre es `1.0` (certeza lógica)
- `tipo_yo` es `"LOGICO"` (no narrativo/reflexivo)

### 3. MotorAxiomas

Procesador de lógica de primer orden.

**Axiomas soportados:**
- Implicación: `P(x) → Q(x)`
- Negación: `¬P(x)`
- Cuantificación: `∀x` (universal)

**Algoritmo:**
- Iteración hasta punto fijo
- Forward chaining sobre modus ponens

### 4. MotorHipotetico

Orquestador que aplica FCA sobre instancias.

**Pipeline:**
1. Instanciar mundo (objetos + relaciones + axiomas)
2. Construir contexto formal (objetos, atributos, incidencia)
3. Aplicar FCA
4. Retornar conceptos abstractos

## 🎓 Casos de Uso

### Caso 1: Razonamiento sobre Estado Sin Sensores

**Problema**: Tienes 3 objetos abstractos {carro, manzana, mesa}. ¿Cuál es rojo?

**Solución (Enfoque 1 - Etiquetas)**:
```python
mundo.agregar_objeto("manzana", {
    "etiqueta_color": "rojo"
})

# Sistema identifica: manzana
# Pero NO sabe qué ES "rojo"
```

**Solución (Enfoque 2 - Definición Física)**:
```python
mundo.agregar_objeto("manzana", {
    "reflectancia_620_750nm": 0.85
})
mundo.agregar_axioma("∀x (reflectancia_620_750nm(x) > 0.7 → rojo(x))")

# Sistema infiere: manzana.rojo = True
# Sabe la FÍSICA del rojo, pero no la QUALIA
```

### Caso 2: Validación de Ontologías

```python
# Definir ontología de vehículos
mundo.agregar_objeto("auto", {"vehiculo": True, "motor": "combustion"})
mundo.agregar_objeto("bicicleta", {"vehiculo": True, "motor": "humano"})
mundo.agregar_objeto("mesa", {"mueble": True})

mundo.agregar_axioma("∀x (vehiculo(x) → transporta(x))")

# Verificar consistencia
instancias = mundo.instanciar()
# auto.transporta = True ✓
# bicicleta.transporta = True ✓
# mesa.transporta = False ✓
```

### Caso 3: Mundos Contrafactuales

```python
# ¿Qué pasaría si las leyes físicas fueran diferentes?
mundo_alien = MundoHipotetico("fisica_alien")
mundo_alien.agregar_axioma("∀x (luz(x) → gravedad_repele(x))")

# Simular consecuencias sin violar física real
```

## 📊 Comparación: Empírico vs. Abstracto

| Concepto | Método Empírico | Método Abstracto |
|----------|-----------------|------------------|
| **Lluvia** | 45 archivos → 93% certeza | Imposible (requiere qualia) |
| **Artefactos** | 20+ objetos analizados | 2 objetos + axioma "artificial" |
| **Entropía** | 100 observaciones → 96% | Definición: P(desorden) = axiomas |
| **Tiempo** | Horas-días | Segundos |

## 🔗 Integración con Sistema Principal

### Modo Híbrido

```python
from emergencia_concepto.motor_emergencia import MotorEmergenciaConceptos
from logica_pura.mundo_hipotetico import MundoHipotetico

# Empírico: Descubrir "lluvia" desde datos
motor_emp = MotorEmergenciaConceptos()
# ... procesar archivos de lluvia ...
concepto_lluvia = motor_emp.emergir_concepto("lluvia")  # 93% certeza

# Abstracto: Definir "agua" lógicamente
mundo = MundoHipotetico("hibrido")
mundo.agregar_objeto("agua", {"liquido": True, "H2O": True})
mundo.agregar_relacion("lluvia", "es_forma_de", "agua")

# Fusión: Conectar empírico con abstracto
# lluvia (empírico 93%) + agua (lógico 100%) → conocimiento completo
```

### Persistencia en Neo4j

```cypher
// Instancias abstractas
CREATE (:InstanciaAbstracta {
  concepto: "carro",
  propiedades_json: '{"artificial": true, "movil": true}',
  tipo_yo: "LOGICO",
  coherencia: 1.0,
  mundo_origen: "mundo_3_objetos"
})

// Relaciones sin Ereignis físico
CREATE (i1:InstanciaAbstracta {concepto: "manzana"})
CREATE (i2:InstanciaAbstracta {concepto: "mesa"})
CREATE (i1)-[:RELACION_LOGICA {tipo: "sobre", certeza: 1.0}]->(i2)

// Conceptos abstractos
CREATE (:ConceptoAbstracto {
  nombre: "ARTEFACTOS_GRANDES",
  extension_json: '["carro", "mesa"]',
  intension_json: '["artificial", "grande"]',
  certeza: 1.0,
  tipo: "logico_puro"
})
```

## 🚀 Roadmap

- [x] Sistema base de mundos hipotéticos
- [x] Motor de axiomas simple (implicación)
- [x] FCA básico sobre instancias
- [ ] Motor de axiomas completo (lógica de primer orden completa)
- [ ] Detección de inconsistencias (proof by contradiction)
- [ ] Generación automática de contraejemplos
- [ ] Visualización de retículos de conceptos
- [ ] Integración con solvers SMT (Z3)
- [ ] Mundos probabilísticos (lógica fuzzy)

## ⚠️ Limitaciones

1. **Sin Qualia**: No puede experimentar "cómo se ve el rojo", solo manipular el símbolo "rojo"
2. **Mundos Cerrados**: Solo conoce lo declarado explícitamente
3. **Axiomas Incorrectos**: Si los axiomas son falsos, toda inferencia es inválida
4. **Escalabilidad**: FCA tiene complejidad exponencial en peor caso

## 📚 Referencias

- Leibniz, G.W. (1686). *Discourse on Metaphysics*.
- Ganter, B. & Wille, R. (1999). *Formal Concept Analysis*.
- Russell, B. & Whitehead, A.N. (1910). *Principia Mathematica*.
- Platón. *La República* (Alegoría de la Caverna - Mundo de las Ideas).

## 🤝 Contribución al YO Estructural

Este módulo permite que el sistema:
- Razone sobre **escenarios hipotéticos** sin datos
- Valide **consistencia lógica** de conocimientos emergidos
- Genere **predicciones deductivas** (certeza 100%)
- Complete **gaps** en conocimiento empírico con razonamiento lógico

**El sistema completo es ahora HÍBRIDO: Fenomenológico (experiencia) + Racionalista (lógica).** 🧠
