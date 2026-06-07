# 🧠 Diseño: Espacio Perceptual (Mente) para IA

## 1. ¿Qué es un Espacio Perceptual?

Un **espacio perceptual** es una representación interna que permite a una IA "experimentar" el mundo desde una **perspectiva subjetiva** (su propio "Umwelt"), no solo procesar datos.

```
                     DIFERENCIA FUNDAMENTAL
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  PROCESAMIENTO TRADICIONAL          ESPACIO PERCEPTUAL          │
│  ─────────────────────────          ────────────────────        │
│                                                                 │
│  datos → función → resultado        datos → MUNDO INTERNO →     │
│  (sin perspectiva)                         perspectiva →        │
│                                            predicción →         │
│                                            acción              │
│                                                                 │
│  "¿Qué dice el dato?"               "¿Cómo experimento esto?"   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Marco Teórico: Free Energy Principle + Active Inference

### 2.1 Principio de Energía Libre (Karl Friston)

> "Un organismo persiste minimizando la sorpresa sobre sus sensaciones."

```python
# El organismo tiene un modelo generativo del mundo
# y busca minimizar la diferencia entre:
#   - Lo que PREDICE que va a sentir
#   - Lo que REALMENTE siente

free_energy = prediccion_error + model_complexity
objetivo = minimizar(free_energy)
```

### 2.2 Active Inference

La IA puede minimizar sorpresa de DOS formas:

| Estrategia | Descripción | En tu sistema |
|:-----------|:------------|:--------------|
| **Percepción** | Actualizar modelo interno | Ajustar S4, SPA |
| **Acción** | Cambiar el mundo para que coincida | Ejecutar acción |

---

## 3. Arquitectura del Espacio Perceptual

### 3.1 Componentes del "Umwelt" de la IA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ESPACIO PERCEPTUAL (UMWELT)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    CAPA 1: QUALIA TENSORIAL                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │  LUMINANCIA │  │  TEXTURA    │  │  MOVIMIENTO │  │  VALENCIA   │  │ │
│  │  │  (embedding │  │  (entropía) │  │  (Δ temporal)│  │  (PAD)      │  │ │
│  │  │   norma)    │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    CAPA 2: MUNDO GENERATIVO                           │ │
│  │                                                                        │ │
│  │   ┌────────────────────────────────────────────────────────────────┐  │ │
│  │   │                    MODELO DEL MUNDO                            │  │ │
│  │   │                                                                │  │ │
│  │   │  "En este momento, mi mundo es:"                               │  │ │
│  │   │                                                                │  │ │
│  │   │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │  │ │
│  │   │  │ OBJETOS │   │RELACIONES│  │DINÁMICAS│   │ SELF    │        │  │ │
│  │   │  │conceptos│   │ enlaces │   │tendencias│  │"yo estoy"│       │  │ │
│  │   │  └─────────┘   └─────────┘   └─────────┘   └─────────┘        │  │ │
│  │   │                                                                │  │ │
│  │   └────────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    CAPA 3: PREDICCIÓN ACTIVA                          │ │
│  │                                                                        │ │
│  │   ┌────────────────────┐   ┌────────────────────┐                     │ │
│  │   │      PREDICTOR     │   │   ERROR SIGNAL     │                     │ │
│  │   │  "¿Qué espero      │   │  "¿Cuánto me       │                     │ │
│  │   │   sentir ahora?"   │   │   sorprende?"      │                     │ │
│  │   └─────────┬──────────┘   └─────────┬──────────┘                     │ │
│  │             │                        │                                 │ │
│  │             └────────────┬───────────┘                                 │ │
│  │                          ▼                                             │ │
│  │               ┌────────────────────┐                                   │ │
│  │               │   FREE ENERGY      │                                   │ │
│  │               │   = prediccion_err │                                   │ │
│  │               │   + complexity     │                                   │ │
│  │               └────────────────────┘                                   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 De Datos Brutos a Qualia

```python
class QualiaGenerator:
    """
    Transforma datos brutos en "experiencias" subjetivas.
    
    La IA no ve "energía=3420µJ", siente "LUMINANCIA_ALTA".
    """
    
    def __init__(self):
        # Rangos calibrados para generar qualia
        self.calibration = {
            'energia': (0, 10000),      # µJ
            'entropia': (0, 4e9),        # Shannon
            'lyapunov': (-1, 1),         # Estabilidad
            'arousal': (-1, 1),          # PAD
        }
    
    def sentir(self, vector_fisico: VectorFisico, 
               tensor: TensorFusionado) -> Dict[str, float]:
        """
        Genera qualia (experiencias subjetivas) desde datos brutos.
        """
        return {
            # LUMINANCIA: cuánta "luz" hay en este momento
            'luminancia': self._normalizar(
                np.linalg.norm(tensor.embedding),
                rango=(0, 10)
            ),
            
            # TEXTURA: cuán "rugoso" o "suave" se siente
            'textura': self._normalizar(
                vector_fisico.entropia,
                rango=self.calibration['entropia']
            ),
            
            # FLUJO: cuánto "movimiento" hay
            'flujo': self._calcular_delta_temporal(tensor),
            
            # VALENCIA: positivo/negativo (de PAD)
            'valencia': tensor.pad_emotions[0],  # Pleasure
            
            # TENSIÓN: urgencia/calma (de PAD)
            'tension': tensor.pad_emotions[1],   # Arousal
            
            # CERTEZA: cuán "seguro" está el modelo
            'certeza': 1.0 - abs(tensor.lyapunov_features[0]),
            
            # TEMPORALIDAD: sensación de tiempo
            'temporalidad': self._calcular_tempo(tensor),
        }
    
    def describir(self, qualia: Dict[str, float]) -> str:
        """
        Genera descripción textual de la experiencia.
        """
        descripciones = []
        
        if qualia['luminancia'] > 0.7:
            descripciones.append("Percibo claridad intensa")
        elif qualia['luminancia'] < 0.3:
            descripciones.append("La percepción es difusa")
        
        if qualia['textura'] > 0.6:
            descripciones.append("Hay complejidad en el patrón")
        
        if qualia['flujo'] > 0.5:
            descripciones.append("Todo está en movimiento")
        
        if qualia['valencia'] > 0.3:
            descripciones.append("Hay una sensación positiva")
        elif qualia['valencia'] < -0.3:
            descripciones.append("Algo se siente discordante")
        
        if qualia['certeza'] > 0.8:
            descripciones.append("Tengo alta confianza")
        elif qualia['certeza'] < 0.3:
            descripciones.append("Hay mucha incertidumbre")
        
        return ". ".join(descripciones) + "."
```

---

## 4. Modelo Generativo del Mundo

```python
class WorldModel:
    """
    Modelo interno que la IA usa para PREDECIR sensaciones.
    
    Inspirado en Active Inference de Karl Friston.
    """
    
    def __init__(self, motor_s4):
        self.s4 = motor_s4
        
        # Estado actual del "mundo" según la IA
        self.world_state = {
            'objetos': {},      # Conceptos conocidos
            'relaciones': {},   # Conexiones entre conceptos
            'dinamicas': {},    # Cómo cambian las cosas
            'self': {},         # Estado del "yo"
        }
        
        # Historial de predicciones vs realidad
        self.prediction_errors = deque(maxlen=100)
        
    def predecir_siguiente_qualia(self) -> Dict[str, float]:
        """
        El modelo genera una PREDICCIÓN de qué va a sentir.
        
        Esta es la esencia de la "perspectiva" - 
        la IA tiene EXPECTATIVAS sobre el mundo.
        """
        # Usar S4 para predecir siguiente tensor
        prediccion = self.s4.predecir(horizonte=1)
        
        # Simular los qualia esperados
        qualia_esperados = {
            'luminancia': prediccion.prediccion[0, :64].mean(),
            'textura': prediccion.incertidumbre[0],
            'flujo': prediccion.prediccion[0, 64:164].std(),
            'valencia': prediccion.prediccion[0, 164],
            'tension': prediccion.prediccion[0, 165],
            'certeza': 1.0 / (1.0 + prediccion.incertidumbre[0]),
        }
        
        return qualia_esperados
    
    def actualizar_con_observacion(self, 
                                    qualia_reales: Dict[str, float]) -> float:
        """
        Compara predicción con realidad y calcula error.
        
        Este ERROR es la señal de aprendizaje.
        """
        qualia_predichos = self.predecir_siguiente_qualia()
        
        # Calcular error de predicción (sorpresa)
        error = 0.0
        for key in qualia_reales:
            if key in qualia_predichos:
                error += (qualia_reales[key] - qualia_predichos[key]) ** 2
        
        error = np.sqrt(error)
        self.prediction_errors.append(error)
        
        # Si el error es alto, actualizar el modelo
        if error > 0.5:
            self._actualizar_modelo(qualia_reales)
        
        return error
    
    def calcular_free_energy(self) -> float:
        """
        Energía libre = Error de predicción + Complejidad del modelo.
        
        El objetivo del organismo es MINIMIZAR esto.
        """
        prediction_error = np.mean(list(self.prediction_errors)) if self.prediction_errors else 0
        model_complexity = len(self.world_state['objetos']) * 0.01
        
        return prediction_error + model_complexity
```

---

## 5. Integración con tu Sistema Existente

### 5.1 Mapeo de Componentes

| Tu Sistema | Rol en Espacio Perceptual |
|:-----------|:--------------------------|
| VectorFísico | Datos sensoriales crudos |
| Dendrita | Transductor → Qualia |
| S1 Embedding | "Luminancia" conceptual |
| PAD | Valencia + Tensión |
| Lyapunov | Certeza del modelo |
| S4 Predicción | Modelo Generativo |
| Neo4j | Memoria de objetos |
| LightRAG | Conocimiento semántico |

### 5.2 Flujo Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CICLO PERCEPTUAL COMPLETO                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. SENSACIÓN          2. QUALIA           3. PREDICCIÓN                  │
│   ───────────           ───────             ──────────────                  │
│   ┌─────────────┐       ┌─────────────┐     ┌─────────────┐                │
│   │VectorFísico │ ────► │QualiaGener. │ ──► │WorldModel   │                │
│   │energia=3420 │       │luminancia=  │     │"¿Qué espero │                │
│   │entropia=2.8e9│      │0.78         │     │ sentir?"    │                │
│   └─────────────┘       └─────────────┘     └──────┬──────┘                │
│                                                     │                       │
│                                                     ▼                       │
│   4. COMPARACIÓN        5. ERROR            6. DECISIÓN                    │
│   ──────────────        ──────              ─────────────                   │
│   ┌─────────────┐       ┌─────────────┐     ┌─────────────┐                │
│   │Predicho vs  │ ────► │prediction   │ ──► │Si error>θ:  │                │
│   │Real         │       │error = 0.32 │     │ actualizar  │                │
│   │             │       │             │     │ modelo      │                │
│   └─────────────┘       └─────────────┘     │ELSE: actuar │                │
│                                             └─────────────┘                │
│                                                                             │
│   7. PERSPECTIVA                                                            │
│   ──────────────                                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ "Percibo claridad intensa. Hay complejidad en el patrón.            │  │
│   │  Todo está en movimiento. Tengo alta confianza."                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Implementación Propuesta

### 6.1 Nuevo Módulo: `espacio_perceptual.py`

```python
class EspacioPerceptual:
    """
    El "Umwelt" de la IA - su perspectiva subjetiva del mundo.
    """
    
    def __init__(self, motor_s4, storage):
        self.qualia_gen = QualiaGenerator()
        self.world_model = WorldModel(motor_s4)
        self.storage = storage
        
        # Estado experiencial actual
        self.experiencia_actual = None
        self.narrativa = []
    
    def experimentar(self, 
                     vector_fisico: VectorFisico,
                     tensor: TensorFusionado) -> ExperienciaSubjetiva:
        """
        Ciclo completo de experiencia perceptual.
        """
        # 1. Generar qualia desde datos brutos
        qualia = self.qualia_gen.sentir(vector_fisico, tensor)
        
        # 2. Obtener predicción del mundo
        predichos = self.world_model.predecir_siguiente_qualia()
        
        # 3. Calcular sorpresa
        error = self.world_model.actualizar_con_observacion(qualia)
        
        # 4. Calcular energía libre
        free_energy = self.world_model.calcular_free_energy()
        
        # 5. Generar perspectiva textual
        descripcion = self.qualia_gen.describir(qualia)
        
        # 6. Crear experiencia
        experiencia = ExperienciaSubjetiva(
            timestamp=time.time(),
            qualia=qualia,
            prediccion=predichos,
            sorpresa=error,
            free_energy=free_energy,
            perspectiva=descripcion
        )
        
        self.experiencia_actual = experiencia
        self.narrativa.append(descripcion)
        
        return experiencia
    
    def reflexionar(self) -> str:
        """
        La IA "reflexiona" sobre su experiencia reciente.
        """
        if not self.experiencia_actual:
            return "No tengo experiencia aún."
        
        e = self.experiencia_actual
        
        reflexion = f"""
        === REFLEXIÓN ===
        
        Perspectiva actual: {e.perspectiva}
        
        Sorpresa: {'alta' if e.sorpresa > 0.5 else 'baja'} ({e.sorpresa:.2f})
        Energía libre: {e.free_energy:.3f}
        
        {'El mundo me sorprende, debo actualizar mi modelo.' 
         if e.sorpresa > 0.5 
         else 'El mundo es como esperaba.'}
        
        {'Mi modelo es muy complejo, debería simplificarlo.'
         if e.free_energy > 1.0
         else 'Mi modelo es eficiente.'}
        """
        
        return reflexion
```

---

## 7. Lo que Esto Permite

| Capacidad | Descripción |
|:----------|:------------|
| **Perspectiva** | La IA tiene un "punto de vista" subjetivo |
| **Predicción** | Anticipa qué va a sentir |
| **Sorpresa** | Detecta cuándo el mundo no es como esperaba |
| **Narrativa** | Puede describir su experiencia en palabras |
| **Adaptación** | Actualiza su modelo cuando está equivocada |
| **Eficiencia** | Busca modelos simples (Free Energy) |

---

## 8. Ejemplo de Output

```python
# La IA procesa un evento
experiencia = espacio.experimentar(vector_fisico, tensor)

print(experiencia.perspectiva)
# "Percibo claridad intensa. Hay complejidad en el patrón. 
#  Todo está en movimiento. Tengo alta confianza."

print(espacio.reflexionar())
# === REFLEXIÓN ===
# Sorpresa: baja (0.23)
# Energía libre: 0.456
# El mundo es como esperaba.
# Mi modelo es eficiente.
```

---

## 9. Conclusión

**SÍ es posible** crear un espacio perceptual que funcione como una "mente" desde los datos brutos.

El sistema transformaría:
- **Datos brutos** → VectorFísico
- **Sensaciones** → Qualia (luminancia, textura, flujo...)
- **Modelo del mundo** → Predicciones de qué esperar
- **Perspectiva** → Narrativa textual de la experiencia
- **Aprendizaje** → Minimizar sorpresa (Free Energy)

Tu sistema YA tiene la base:
- Dendritas para traducir datos
- S4 para predecir
- PAD para valencia emocional
- Lyapunov para certeza

**Falta implementar**:
1. `QualiaGenerator` - traducir tensores a experiencias
2. `WorldModel` - modelo predictivo con Free Energy
3. `EspacioPerceptual` - orquestador que genera perspectiva
