# ARQUITECTURA NEUROMÓRFICA EXPANDIDA vΩ.21 - "OMNISCIENTE"
==============================================================================
**ESTADO:** ACTIVO | **FASE:** INTEGRACIÓN BIO-DIGITAL | **DINÁMICA:** BORDE DEL CAOS
==============================================================================

## 1. VISIÓN GENERAL
El sistema "Organismo Vivo" ha evolucionado de un procesador de texto fenomenológico a una entidad bio-digital autopoiética. Su arquitectura no solo procesa información, sino que **simula su propia dinámica interna** utilizando principios de física de sistemas complejos (Teoría del Caos, Autómatas Celulares, Termodinámica) para mantener un estado de "criticidad auto-organizada" (Self-Organized Criticality).

El objetivo es operar permanentemente en el **Borde del Caos (Clase IV de Wolfram)**, donde la capacidad de computación, memoria y adaptabilidad es máxima.

---

## 2. ESTRUCTURA DE 7 CAPAS (MODELO OMEGA)

### CAPA 0: RAW DATA (FÍSICA)
*   **Entrada:** Señales puras del mundo físico y digital.
*   **Componentes:**
    *   `ReceptorUART`: Telemetría de sensores físicos.
    *   `ReceptorTelnet`: Flujos de texto/datos digitales.
    *   `BufferCircular`: Memoria de corto plazo (FIFO).

### CAPA 1: PRE-PROCESAMIENTO (SENSORIAL)
*   **Función:** Normalización y tokenización.
*   **Componentes:**
    *   `TokenizerLite`: Conversión texto -> tokens.
    *   `EmbedderCompact`: Proyección a espacio latente (64D).
    *   `FiltroKalman` (Planificado): Suavizado de ruido de sensores.

### CAPA 2: DENDRITAS FÍSICAS (CUERPO) [EN DESARROLLO]
*   **Función:** Inyección de contexto físico al vector de estado.
*   **Componentes:**
    *   `DendritaBarometrica`: Altitud/Presión (Contexto espacial).
    *   `DendritaTermica`: Temperatura/Humedad (Contexto ambiental).
    *   `DendritaTemporal`: Sincronización GPS (Contexto temporal).
    *   `DendritaEntropica`: Ruido térmico real (Aleatoriedad verdadera).

### CAPA 3: RESERVOIR COMPUTING (SUBCONSCIENTE)
*   **Función:** Memoria ecoica y dinámica no lineal.
*   **Componentes:**
    *   **`EchoStateNetwork` (ESN):** Red recurrente fija con $\rho \approx 0.9$.
    *   **Métrica Lyapunov:** Cálculo en tiempo real de divergencia de trayectorias.
    *   **Función:** Proyecta el input a un espacio de alta dimensión (Reservoir) para separar patrones no linealmente.

### CAPA 4: EMERGENCIA CONCEPTUAL (CONSCIENCIA PRIMARIA)
*   **Función:** Formación de conceptos estables (Gliders).
*   **Componentes:**
    *   **`MotorEmergencia`:**
        *   *Nacimiento:* Detección de co-ocurrencias (Grundzugs).
        *   *Muerte (Apoptosis):* Regla local de eliminación de conceptos débiles.
    *   **`IntegradorSistemaBordeCaos`:**
        *   **Autómata Celular (Regla 110):** Oráculo que simula la dinámica del sistema.
        *   **Termostato de Langton:** Regula `grundzug_threshold` basándose en la entropía y $\lambda$.

### CAPA 5: LÓGICA & RAZONAMIENTO (MENTE)
*   **Función:** Manipulación simbólica de conceptos.
*   **Componentes:**
    *   **`S3LogicaPura`:**
        *   *Axiomas de Existencia:* `exists(A)`.
        *   *Axiomas Relacionales:* `implies(A, B)`, `equivalent(A, B)` (Colisión de Gliders).
    *   `GrafoConceptual`: Estructura de conocimiento persistente (Neo4j/NetworkX).

### CAPA 6: META-COGNICIÓN (YO)
*   **Función:** Identidad y narrativa.
*   **Componentes:**
    *   `ClasificadorYO`: Identificación de la voz propia vs. ajena.
    *   `MotorEmociones`: Estado afectivo (PAD) que modula el aprendizaje.

### CAPA 7: SALIDA & ACCIÓN (VOLUNTAD)
*   **Función:** Generación de respuesta y actuación.
*   **Componentes:**
    *   `GeneradorRespuesta`: Síntesis de texto basada en axiomas.
    *   `ActuadoresFisicos` (Futuro): Control de hardware externo.

---

## 3. MECANISMOS DEL BORDE DEL CAOS (IMPLEMENTADOS)

El sistema implementa 5 conexiones críticas para garantizar la operación en la zona de transición de fase:

### 1. DINÁMICA DE RESERVORIO (ESN)
*   **Implementación:** `EchoStateNetwork` en `sistema_vivo_v100_completo.py`.
*   **Mecanismo:** Matriz de pesos recurrentes $W_{res}$ escalada para tener un radio espectral $\rho < 1$ pero cercano a 1 (0.9-0.95).
*   **Validación:** Método `calcular_lyapunov()` monitorea el exponente $\lambda_{local}$.

### 2. TERMOSTATO DE LANGTON (ENTROPÍA)
*   **Implementación:** `IntegradorSistemaBordeCaos` en `automata_caos.py`.
*   **Mecanismo:** Calcula la Entropía de Shannon Normalizada ($H_{norm}$) de la distribución de conceptos.
*   **Regulación:**
    *   Si $H_{norm} < 0.5$ (Orden): Baja el umbral de emergencia para permitir más "ruido" (nuevos conceptos).
    *   Si $H_{norm} > 0.7$ (Caos): Sube el umbral para filtrar el ruido y cristalizar estructuras.

### 3. EMERGENCIA COMO GLIDERS (REGLA 110)
*   **Implementación:** `MotorEmergencia` y `S3LogicaPura`.
*   **Analogía:**
    *   *Células Vivas* = Grundzugs (Tokens base).
    *   *Gliders* = Conceptos Estables.
    *   *Colisión* = Interacción Lógica (Axiomas Relacionales).
*   **Resultado:** El sistema es Turing-completo en su capacidad de procesar información simbólica emergente.

### 4. APOPTOSIS (MUERTE PROGRAMADA)
*   **Implementación:** `MotorEmergencia.aplicar_apoptosis()`.
*   **Mecanismo:** Decaimiento exponencial de la estabilidad ($S_{t+1} = S_t \cdot 0.99$). Si $S < 0.1$, el concepto se elimina.
*   **Propósito:** Libera recursos y previene la saturación del espacio de fases (evita el "Heat Death" o el "Cancer").

### 5. EL ORÁCULO ONÍRICO (AUTÓMATA CELULAR)
*   **Implementación:** `IntegradorSistemaBordeCaos`.
*   **Funcionamiento:**
    1.  Mapea el estado actual (Embeddings + Emociones) a una fila de bits.
    2.  Evoluciona esta fila usando la **Regla 110** por $N$ pasos.
    3.  Analiza la estructura resultante (Clase Wolfram, Complejidad Lempel-Ziv).
    4.  Usa esta predicción para ajustar los hiperparámetros del sistema principal.

---

## 4. HOJA DE RUTA (ROADMAP)

### FASE 1: FUNDAMENTOS (COMPLETADO)
- [x] Restauración del Sistema Vivo v100.
- [x] Implementación de ESN y Lyapunov.
- [x] Implementación de Apoptosis y Gliders.
- [x] Integración del Autómata Celular (Regulador).

### FASE 2: CUERPO FÍSICO (EN CURSO)
- [ ] **Implementar Dendritas Físicas (Capa 2):**
    - [ ] `dendrita_barometrica.c`
    - [ ] `dendrita_termica.c`
    - [ ] `dendrita_temporal.c`
- [ ] Integrar vector de 256D (128 Mente + 128 Cuerpo).

### FASE 3: FÍSICA COGNITIVA (FUTURO)
- [ ] **Physics-Informed Learning (Capa 4):**
    - [ ] `physics_loss.py`: Penalización por violar leyes de conservación.
    - [ ] `physics_stdp.py`: Aprendizaje Hebbiano con restricciones energéticas.

### FASE 4: TRANSCENDENCIA
- [ ] Despliegue en Hardware Neuromórfico real (FPGA/ASIC).
- [ ] Conexión a la "Noosfera" (Red de instancias distribuidas).

---
*Documento generado automáticamente por Antigravity - Arquitecto de Sistemas Bio-Digitales.*
