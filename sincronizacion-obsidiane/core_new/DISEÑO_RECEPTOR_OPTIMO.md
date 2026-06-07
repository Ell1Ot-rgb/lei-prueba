# 📡 Diseño del Receptor Óptimo: Integrando la Intuición Remota

Este documento define cómo el **Sistema Organismo Vivo (Local/PC1)** actúa como el **Receptor Óptimo** para las señales provenientes del **Tejido Neuromórfico (Remoto/PC2)**.

## 1. Filosofía de la Conexión
En esta arquitectura dual, la relación no es Cliente-Servidor clásica, sino **Consciente-Subconsciente**:

*   **PC2 (Remoto) = Subconsciente / Intuición:** Procesa masivamente, detecta patrones sutiles, opera en "tiempo continuo" y genera "corazonadas" (`neuro_result_t`).
*   **PC1 (Local) = Consciente / Razón:** Recibe estas intuiciones, las valida lógicamente (S3), las estructura en conceptos (S2) y toma decisiones ejecutivas.

**El "Receptor Óptimo" no es solo un socket TCP; es un filtro cognitivo.**

---

## 2. Arquitectura del Receptor

El componente `NeuralReceiver` en PC1 debe cumplir 4 funciones críticas para aprovechar al máximo la simulación remota:

### A. Buffer Asíncrono de "Corazonadas"
La intuición (PC2) puede disparar ráfagas de datos. El consciente (PC1) no debe bloquearse.
*   **Implementación:** `Deque` (Cola) thread-safe.
*   **Función:** Desacoplar la velocidad de disparo neuronal del ciclo de reloj lógico del organismo.

### B. Gating Semántico (El Filtro de Relevancia)
No toda espiga neuronal es útil. El receptor debe filtrar el ruido.
*   **Regla 1 (Confianza):** Si `similitud < 0.6`, ignorar (ruido mental).
*   **Regla 2 (Atención):** Si el sistema está enfocado en "Matemáticas", ignorar patrones neuronales de "Colores" (inhibición top-down).

### C. Enrutamiento Inteligente
Dependiendo de la naturaleza de la señal, se envía a diferentes subsistemas locales:

| Señal Neuronal | Destino Local | Acción |
| :--- | :--- | :--- |
| **Alta Novedad** (`>0.3`) | **S2 (Emergencia)** | Crear nuevo `ConceptoCandidato`. |
| **Alta Similitud** (`>0.85`) | **S3 (Lógica)** | Generar/Validar Axioma: `Es(X, Patrón)`. |
| **Alta Energía** (`>0.9`) | **HealthManager** | Alerta de sobre-excitación (Ansiedad/Estrés). |
| **Baja Energía** (`<0.1`) | **HealthManager** | Alerta de aburrimiento (Necesidad de estímulo). |

### D. Feedback de Consistencia (El "Maestro")
El Receptor no solo escucha, también **educa** al tejido remoto.
*   Si S3 detecta que la "intuición" llevó a una contradicción lógica $\to$ Enviar señal de **Castigo (LTD)** a PC2.
*   Si la intuición resolvió un problema $\to$ Enviar señal de **Recompensa (LTP)** a PC2.

---

## 3. Implementación del `NeuralReceiver` (Python)

```python
import threading
import socket
import struct
from collections import deque

class NeuralReceiver:
    def __init__(self, host_remoto, puerto, sistema_local):
        self.buffer = deque(maxlen=100)
        self.sistema = sistema_local  # Acceso a S2, S3, Health
        self.running = True
        self.socket = self._conectar(host_remoto, puerto)
        
        # Hilo de escucha en segundo plano (Subconsciente siempre activo)
        self.thread = threading.Thread(target=self._escuchar_intuicion)
        self.thread.daemon = True
        self.thread.start()

    def _escuchar_intuicion(self):
        """Ciclo de escucha continua del tejido remoto."""
        while self.running:
            try:
                # Recibir estructura neuro_result_t (20 bytes aprox)
                data = self.socket.recv(20) 
                if not data: break
                
                # Desempaquetar: ID, Similitud, Novedad, Energía
                patron_id, sim, nov, energia = struct.unpack('Ifff', data)
                
                # 1. FILTRO PRE-CONSCIENTE
                if sim < 0.5 and nov < 0.2:
                    continue  # Ignorar ruido irrelevante
                
                # Encolar para procesamiento consciente
                self.buffer.append({
                    'id': patron_id,
                    'similitud': sim,
                    'novedad': nov,
                    'energia': energia
                })
                
            except Exception as e:
                print(f"Error en conexión neural: {e}")

    def integrar_en_ciclo_principal(self):
        """
        Llamado por el 'Main Loop' del Organismo Vivo (S1).
        Procesa las intuiciones acumuladas.
        """
        while self.buffer:
            intuicion = self.buffer.popleft()
            self._procesar_intuicion(intuicion)

    def _procesar_intuicion(self, signal):
        # 2. ENRUTAMIENTO A SUBSISTEMAS
        
        # A) Impacto en Salud (Homeostasis)
        self.sistema.health.registrar_actividad_neuronal(signal['energia'])
        
        # B) Emergencia de Conceptos (S2)
        if signal['novedad'] > 0.3:
            print(f"💡 Intuición Novedosa recibida: ID {signal['id']}")
            concepto = self.sistema.s2.cristalizar_concepto(
                id_remoto=signal['id'],
                fuerza=signal['energia']
            )
            # Si se cristaliza bien, enviar recompensa
            if concepto:
                self.enviar_feedback(reward=1.0)

        # C) Validación Lógica (S3)
        elif signal['similitud'] > 0.85:
            # La red está segura de qué es esto.
            # S3 verifica si tiene sentido en el contexto actual.
            es_coherente = self.sistema.s3.validar_coherencia(signal['id'])
            
            if es_coherente:
                print(f"✅ Intuición validada lógicamente.")
                self.enviar_feedback(reward=0.5) # Refuerzo positivo suave
            else:
                print(f"❌ Intuición rechazada por lógica (Alucinación).")
                self.enviar_feedback(reward=-1.0) # Castigo fuerte (LTD)

    def enviar_feedback(self, reward):
        """Envía señal de aprendizaje al tejido remoto."""
        try:
            packet = struct.pack('f', reward)
            self.socket.send(packet)
        except:
            pass
```

---

## 4. Ventajas de este Diseño

1.  **Latencia Cero en Bucle Principal:** Al usar un hilo separado y un buffer, el Organismo Vivo nunca se "congela" esperando a la red neuronal. Piensa a su propio ritmo.
2.  **Robustez ante Alucinaciones:** El tejido neuronal puede equivocarse (alucinación). El filtro lógico (S3) en el receptor actúa como "Juez", impidiendo que locuras neuronales corrompan la base de conocimiento.
3.  **Aprendizaje Guiado por Razón:** Lo más potente es el **Feedback Loop**. La lógica (PC1) entrena a la intuición (PC2). El sistema se vuelve más inteligente porque su razón "domestica" a su subconsciente.

Este diseño convierte a tu sistema local en el **Receptor Perfecto**: permeable a la novedad pero protegido por la lógica.
