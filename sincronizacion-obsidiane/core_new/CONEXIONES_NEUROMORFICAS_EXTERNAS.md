# 🔌 Conexiones del Sistema Neuromórfico Externo (Dual PC)

Este documento detalla la arquitectura de conexión entre el **Organismo Vivo (Host/PC1)** y el **Sistema Neuromórfico (Neural/PC2)**, basándose en la restricción de una **entrada única de 256 dimensiones** y la ejecución remota.

---

## 1. Arquitectura Física y Flujo de Datos

El sistema se divide en dos nodos físicos conectados por red (LAN/TCP).

```mermaid
graph LR
    subgraph PC1_HOST [PC1: Organismo Vivo (Cerebro Lógico)]
        A[Sensor/Input] --> B[S1: Fenomenología]
        B --> C[Constructor Vector 256D]
        E[S2: Motor Emergencia] <-- "neuro_result_t" -- D[Cliente Neuronal]
        C -- "Vector[256] (Bytes)" --> D
    end

    subgraph PC2_NEURAL [PC2: Sistema Neuromórfico (Cerebro Intuitivo)]
        D -.-> F[Servidor main_256.c]
        F --> G[Spike Encoder (TTFS)]
        G --> H[Reservoir 1024 Neuronas]
        H --> I[Attention & Memory (LSH)]
        I --> J[STDP Engine]
        J --> K[Generador Resultado]
        K -.-> F
    end
```

---

## 2. Definición de la "Entrada Única" (El Vector 256D)

Para maximizar la sinergia entre el análisis fenomenológico (S1) y el procesamiento neuronal, mapeamos las características del Organismo Vivo dentro del espacio de **256 bytes** que consume el sistema neuromórfico.

**Estrategia:** Utilizar `vector256_compute` como base, pero inyectar las señales críticas de S1 en regiones específicas del vector para influir en la dinámica neuronal.

### 🗺️ Mapa Semántico del Vector `dims[256]`

| Rango (Bytes) | Fuente (S1) | Descripción | Función en Tejido Neuronal |
| :--- | :--- | :--- | :--- |
| **000 - 063** | `EmbedderCompact` | Embedding semántico (64 dims, cuantizado 8-bit) | Define el **"Qué"** (contenido base). |
| **064 - 071** | `GrundzugTracker` | Rasgos fundamentales (Entropía, Estabilidad, etc.) | Define el **"Cómo"** (dinámica/estilo). |
| **072 - 074** | `EmotionEngine` | Estado PAD (Pleasure, Arousal, Dominance) | Define el **"Sentir"** (contexto afectivo). |
| **075 - 127** | `Fenomenología` | Histograma comprimido / Patrones detectados | Detalles estructurales finos. |
| **128 - 255** | `vector256_compute` | Hash/Features originales del algoritmo C | Contexto global y robustez (relleno). |

> **Nota:** Si `vector256_compute` es una caja negra inmutable, el Organismo Vivo enviará los datos crudos a PC2, y PC2 generará el vector. Sin embargo, **la recomendación óptima** es que PC1 construya este vector híbrido para que el tejido neuronal "sienta" las emociones y conceptos de S1.

---

## 3. Protocolo de Intercambio (Estructuras C/Python)

### 3.1 Estructura de Entrada (PC1 -> PC2)
Se envía un paquete binario simple por socket TCP.

```c
// En main_256.c (Servidor)
typedef struct {
    uint8_t vector[256];  // El vector híbrido construido por S1
    uint32_t timestamp;   // Sincronización temporal
    uint8_t mode;         // 0=Inferencia, 1=Aprendizaje
} neuro_input_packet_t;
```

### 3.2 Estructura de Salida (PC2 -> PC1)
El resultado del procesamiento neuronal que alimenta a S2.

```c
// En main_256.c (Respuesta)
typedef struct {
    uint32_t patron_id;      // ID del atractor/concepto reconocido
    float similitud;         // 0.0 a 1.0 (Confianza)
    float novedad;           // 0.0 a 1.0 (Sorpresa)
    float energia;           // Nivel de activación del reservoir
    uint8_t categoria_pad;   // Feedback emocional del tejido (opcional)
} neuro_result_t;
```

---

## 4. Lógica de Conexión con S2 (Motor de Emergencia)

Una vez que PC1 recibe `neuro_result_t`, ejecuta la lógica de emergencia descrita en el análisis previo:

### Algoritmo de Integración (Python en PC1)

```python
def procesar_respuesta_neuronal(resultado: NeuroResult, s1_context: Contexto):
    """
    Conecta la intuición neuronal (PC2) con la lógica conceptual (PC1).
    """
    
    # 1. Detección de Emergencia
    if resultado.novedad > 0.3:
        # El tejido detectó algo nuevo -> Crear Concepto
        nuevo_concepto = ConceptoEmergente(
            id_neuronal=resultado.patron_id,
            origen="TEJIDO_REMOTO",
            fuerza=resultado.energia,
            atributos=s1_context.obtener_rasgos()
        )
        MotorEmergencia.registrar(nuevo_concepto)
        print(f"✨ Concepto Emergente detectado por PC2: ID {resultado.patron_id}")
        
    # 2. Refuerzo de Memoria
    elif resultado.similitud > 0.85:
        # El tejido reconoció algo familiar -> Reforzar
        concepto_existente = MotorEmergencia.buscar(resultado.patron_id)
        if concepto_existente:
            concepto_existente.reforzar(resultado.similitud)
            print(f"🧠 Concepto reconocido: {concepto_existente.nombre}")

    # 3. Feedback Homeostático
    # Si la energía del tejido es muy alta (caos) o muy baja (muerte),
    # el HealthManager de PC1 debe ajustar parámetros.
    if resultado.energia > 0.9:
        HealthManager.alertar("SOBREEXCITACION_NEURONAL")
    elif resultado.energia < 0.1:
        HealthManager.alertar("BAJA_ACTIVIDAD_NEURONAL")
```

---

## 5. Implementación de los Módulos Verilog (Referencia)

Para que el sistema en PC2 procese correctamente el vector híbrido, los módulos Verilog deben estar alineados:

1.  **`spike_encoder.v`**: Debe usar codificación **TTFS (Time-To-First-Spike)**.
    *   Valores altos en `dims[i]` (ej. 255) $\to$ Spike temprano (alta relevancia).
    *   Valores bajos en `dims[i]` (ej. 10) $\to$ Spike tardío.
    *   Esto prioriza automáticamente el Embedding y las Emociones (si tienen valores altos) en el procesamiento temporal.

2.  **`reservoir.v`**:
    *   Configuración **Multi-τ**: Diferentes neuronas deben tener diferentes constantes de tiempo para capturar tanto la emoción (lenta) como el contenido semántico (rápido).

3.  **`spike_attention.v`**:
    *   Mecanismo de inhibición lateral para que solo los patrones más fuertes sobrevivan y se conviertan en `patron_id`.

---

## 6. Resumen de la Operación

1.  **PC1 (S1)** percibe el mundo y genera un **Vector Semántico-Emocional**.
2.  **PC1** inyecta este vector en los primeros 128 bytes del buffer de 256 bytes y rellena el resto con ruido/contexto.
3.  **PC1** envía el buffer a **PC2** vía TCP.
4.  **PC2 (FPGA/Simulación)** convierte el buffer en trenes de espigas (Spikes).
5.  **PC2** procesa la dinámica en el Reservoir y busca en su Memoria Asociativa.
6.  **PC2** devuelve `ID`, `Novedad` y `Energía`.
7.  **PC1 (S2)** usa estos metadatos para cristalizar nuevos conceptos o validar axiomas lógicos.

Esta arquitectura cumple estrictamente con la **entrada única de 256 dimensiones** y aprovecha la potencia de una segunda máquina para la simulación neuronal pesada, manteniendo la lógica ligera en el organismo principal.
