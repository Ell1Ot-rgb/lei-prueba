# 🧬 Investigación: Organismos Digitales

## 1. Proyectos Históricos de Vida Artificial

### 1.1 Tierra (Thomas S. Ray, 1990)

**Concepto**: Primer ecosistema de organismos digitales auto-replicantes.

| Característica | Descripción |
|:---------------|:------------|
| **Entorno** | Memoria lineal compartida |
| **Recursos** | CPU time, memoria |
| **Comportamientos Emergentes** | Parásitos, mutualismo, competencia |
| **Acción** | Copiar código a nueva ubicación |

**Comportamientos observados**:
- 🦠 **Parásitos**: Organismos que usan código de otros para replicarse
- 🤝 **Hiperparásitos**: Explotan a los parásitos
- 📉 **Compresión**: Evolución hacia código más eficiente (80→24 instrucciones)

---

### 1.2 Avida (Adami, Ofria, Brown, 1993)

**Concepto**: Plataforma de evolución digital con tareas computacionales.

| Característica | Descripción |
|:---------------|:------------|
| **Entorno** | Grid 2D, cada organismo tiene CPU propia |
| **Recursos** | Ciclos CPU bonus por completar tareas |
| **Tareas** | Operaciones lógicas (AND, OR, XOR, sumas) |
| **Caso de uso** | Estudiar evolución de complejidad |

**Hallazgos clave**:
- Complejidad surge de pasos incrementales
- Mutaciones neutrales son cruciales
- Robustez evoluciona naturalmente

**Relevancia para tu sistema**: S4 ya tiene tareas implícitas (predecir, clasificar). Podrías definir tareas explícitas con recompensas CPU.

---

### 1.3 Lenia (Bert Chan, 2018)

**Concepto**: Autómata celular continuo 2D con vida artificial.

| Característica | Descripción |
|:---------------|:------------|
| **Entorno** | Grid continuo (no discreto) |
| **Estados** | Valores reales [0, 1] |
| **Dinámica** | Convolución + función de crecimiento |
| **Criaturas** | Auto-organizadas, locomotoras |

**Comportamientos**:
- 🌊 Auto-reparación tras daño
- 🚶 Locomoción espontánea
- 🧬 Reproducción por fisión
- ⚖️ Homeostasis de forma

**GitHub**: `Chakazul/Lenia` (Python, MATLAB, JS)

**Relevancia**: Tu sistema ya tiene funciones similares (ESN para dinámica, PAD para "forma" emocional).

---

## 2. Agentes Autónomos RL

### 2.1 Arquitectura Estándar (OpenAI Gym)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CICLO AGENTE-ENTORNO                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│         observation_space          action_space                 │
│               ↓                         ↑                       │
│    ┌─────────────────┐         ┌─────────────────┐             │
│    │    ENTORNO      │ reward  │     AGENTE      │             │
│    │  ┌───────────┐  │ ───────►│  ┌───────────┐  │             │
│    │  │ Estado s  │  │         │  │ Política π│  │             │
│    │  └───────────┘  │◄─────── │  └───────────┘  │             │
│    └─────────────────┘ action  └─────────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Tipos de Espacios

| Tipo | Descripción | Ejemplo | Algoritmo |
|:-----|:------------|:--------|:----------|
| **Discreto** | N acciones finitas | Izq/Der/Arr/Abajo | Q-Learning, DQN |
| **Continuo** | Valores reales | Ángulo [0°, 360°] | DDPG, PPO |
| **Híbrido** | Combo | Tipo + parámetro | Actor-Critic |

### 2.3 Diseño de Recompensa

```python
# Buena práctica: recompensa compuesta
reward = (
    + 10.0 * goal_achieved         # Objetivo principal
    + 1.0 * partial_progress       # Progreso parcial
    - 0.1 * action_cost            # Costo por actuar
    - 5.0 * constraint_violated    # Penalización
)
```

---

## 3. Sistemas Homeostáticos

### 3.1 Homeostasis en Redes Neuronales

**Definición**: Capacidad de mantener estados internos estables.

| Mecanismo | Biológico | Artificial |
|:----------|:----------|:-----------|
| Regulación de actividad | Plasticidad sináptica | Normalización batch |
| Auto-reparación | Neuroplasticidad | Dropout + retraining |
| Equilibrio metabólico | ATP/ADP | Learning rate scheduling |

### 3.2 Homeostatic RL

**Concepto**: El agente aprende a **mantener estados internos** en vez de maximizar recompensa externa.

```python
class HomeostaticAgent:
    def __init__(self):
        self.target_states = {
            'energy': 0.7,
            'entropy': 0.5,  # Borde del caos
            'lyapunov': 0.0   # Estabilidad crítica
        }
    
    def compute_reward(self, current_state):
        # Reward = -distancia al estado objetivo
        reward = 0
        for key, target in self.target_states.items():
            reward -= abs(current_state[key] - target)
        return reward
```

**Relevancia directa**: Tu sistema YA tiene Lyapunov, entropía, PAD. Podrías definir estados objetivo homeostáticos.

---

## 4. Comportamientos Observados en Organismos Digitales

### 4.1 Catálogo de Comportamientos

| Comportamiento | Descripción | Cómo Emerge |
|:---------------|:------------|:------------|
| **Auto-replicación** | Copiar a sí mismo | Presión evolutiva |
| **Parasitismo** | Explotar recursos de otros | Optimización egoísta |
| **Cooperación** | Beneficio mutuo | Reciprocidad |
| **Especialización** | Nichos ecológicos | Competencia por recursos |
| **Adaptación** | Cambiar ante entorno | Selección natural |
| **Auto-reparación** | Restaurar tras daño | Redundancia |
| **Exploración** | Buscar recursos | Escasez |
| **Homeostasis** | Mantener equilibrio | Supervivencia |

### 4.2 Condiciones para Emergencia

```
INGREDIENTES MÍNIMOS
====================
1. Variación     → Mutaciones aleatorias
2. Selección     → Recursos limitados
3. Herencia      → Copiar información
4. Tiempo        → Muchas generaciones

TU SISTEMA
==========
1. Variación     → Ruido en ESN ✅
2. Selección     → ¿Cuál es el recurso limitado? ❌
3. Herencia      → ¿Qué se "copia"? ❌
4. Tiempo        → Historial de tensores ✅
```

---

## 5. Mapeo a Tu Sistema

### 5.1 Componentes Existentes → Organismos Digitales

| Tu Sistema | Análogo en Vida Artificial |
|:-----------|:---------------------------|
| VectorFísico | Señal sensorial |
| Dendrita | Transductor biológico |
| ESN/RMN | Red neuronal recurrente |
| PAD | Estado emocional/homeostático |
| S4 Predicción | Anticipación |
| Lyapunov | Medida de estabilidad |
| Neo4j | Memoria a largo plazo |

### 5.2 Lo que FALTA para ser "Organismo"

| Característica | Estado | Propuesta |
|:---------------|:------:|:----------|
| **Metabolismo** | ❌ | Consumo/generación de recursos |
| **Acción** | ❌ | ActionSpace con 12 acciones |
| **Objetivo endógeno** | ❌ | Estado homeostático target |
| **Auto-replicación** | ❌ | Clonar configuración a otro nodo |
| **Mortalidad** | ❌ | Condición de "muerte" (recursos=0) |

---

## 6. Propuesta: Organismo Vivo Completo

### 6.1 Definición de Metabolismo

```python
class Metabolismo:
    """Energía del organismo digital."""
    
    def __init__(self):
        self.energia = 100.0       # Empieza lleno
        self.energia_max = 100.0
        self.consumo_base = 0.1    # Por tick
        
    def tick(self):
        """Cada ciclo consume energía base."""
        self.energia -= self.consumo_base
        if self.energia <= 0:
            return "MUERTE"
        return "VIVO"
    
    def comer(self, alimento: float):
        """Ganar energía de fuente externa."""
        self.energia = min(self.energia + alimento, self.energia_max)
    
    def costo_accion(self, accion: int) -> float:
        """Cada acción tiene costo."""
        costos = {
            0: 1.0,   # TRIGGER_N8N (caro)
            3: 0.1,   # MODIFY_PAD (barato)
            6: 2.0,   # WRITE_NEO4J (muy caro)
        }
        return costos.get(accion, 0.5)
```

### 6.2 Objetivo Homeostático

```python
class ObjetivoHomeostatico:
    """El organismo busca mantener estos estados."""
    
    TARGETS = {
        'lyapunov': 0.0,          # Borde del caos
        'entropy_normalized': 0.5, # Ni muy ordenado ni muy caótico
        'pad_arousal': 0.3,        # Alerta moderada
        'energia': 0.7,            # Energía alta
    }
    
    def compute_fitness(self, state: WorldState) -> float:
        """Fitness = 1 / distancia al target."""
        distance = 0
        for key, target in self.TARGETS.items():
            current = getattr(state, key, 0)
            distance += (current - target) ** 2
        return 1.0 / (1.0 + distance)
```

### 6.3 Ciclo de Vida Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    CICLO DE VIDA ORGANISMO                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────┐                                             │
│   │   PERCIBIR    │ ← Dendritas                                 │
│   │ VectorFísico  │                                             │
│   └───────┬───────┘                                             │
│           ▼                                                     │
│   ┌───────────────┐                                             │
│   │   PROCESAR    │ ← S1→S2→S3→S4                               │
│   │TensorFusionado│                                             │
│   └───────┬───────┘                                             │
│           ▼                                                     │
│   ┌───────────────┐     ┌───────────────┐                      │
│   │   EVALUAR     │────►│  METABOLISMO  │                      │
│   │  Homeostasis  │     │ energia -= 0.1│                      │
│   └───────┬───────┘     └───────┬───────┘                      │
│           │                     │                               │
│           ▼                     ▼                               │
│   ┌───────────────┐     ┌───────────────┐                      │
│   │   DECIDIR     │     │   ¿VIVO?      │                      │
│   │ PolicyEngine  │     │ energia > 0   │                      │
│   └───────┬───────┘     └───────┬───────┘                      │
│           │                     │                               │
│           ▼                     ▼                               │
│   ┌───────────────┐     ┌───────────────┐                      │
│   │   ACTUAR      │     │   SI: seguir  │                      │
│   │ energia -= 1  │     │   NO: MUERTE  │                      │
│   └───────┬───────┘     └───────────────┘                      │
│           │                                                     │
│           ▼                                                     │
│   ┌───────────────┐                                             │
│   │   RECOMPENSAR │ ← Homeostasis fitness                       │
│   │ update policy │                                             │
│   └───────┬───────┘                                             │
│           │                                                     │
│           └──────────────────────────────────────────► REPEAT   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Casos de Uso Identificados

| Caso | Descripción | Inspiración |
|:-----|:------------|:------------|
| **Asistente Autónomo** | IA que busca información sin prompt | Tierra (exploración) |
| **Monitor Adaptativo** | Ajusta sensibilidad según contexto | Avida (tareas) |
| **Agente Creativo** | Genera contenido buscando novedad | Lenia (auto-org) |
| **Sistema Resiliente** | Se recupera de fallos | Homeostasis |
| **Colonia Distribuida** | Múltiples organismos cooperando | Ecosistemas |

---

## 8. Conclusiones

Tu sistema **YA TIENE** la base de un organismo digital:
- ✅ Percepción (dendritas, vectores)
- ✅ Procesamiento (S1→S2→S3→S4)
- ✅ Memoria (ESN, Neo4j)
- ✅ Dinámica (Lyapunov, DMD)

**FALTA** para ser "organismo vivo":
- ❌ **Metabolismo** (energía finita)
- ❌ **Acción** (12 acciones definidas)
- ❌ **Objetivo homeostático** (estados target)
- ❌ **Ciclo de vida** (nacimiento→muerte)

**Inspiración clave**: Lenia + Homeostatic RL = Organismo que busca estabilidad en el borde del caos.
