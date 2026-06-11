# ☁️ Guía de Transición y Configuración — AWS Bedrock RAG Backend

Este documento detalla cómo migrar el motor cognitivo (LLM) de nuestro sistema RAG (actualmente en **Groq**) hacia **Amazon Bedrock**. Esto nos permitirá eliminar los estrictos límites de tasa (*Rate Limits*) del Tier gratuito y beneficiarnos de la escalabilidad y fiabilidad de nivel empresarial de AWS.

---

## 🎯 1. Modelos Óptimos en AWS Bedrock

Para tareas de RAG (extracción semántica estructurada de entidades y relaciones), los modelos más eficientes en AWS Bedrock son:

### ⚡ Opción A: Anthropic Claude 3 Haiku (Recomendado por Velocidad y Coste)
* **ID de Modelo**: `anthropic.claude-3-haiku-20240307-v1:0`
* **Coste por 1M Tokens**: ~$0.25 (Input) / ~$1.25 (Output).
* **Ventajas**: Es extremadamente veloz, consume muy poco presupuesto y posee una ventana de contexto de 200,000 tokens. Su precisión en tareas de extracción de datos estructurados es soberbia.

### 🧠 Opción B: Meta Llama 3.1 70B Instruct (Recomendado por Capacidad Abierta)
* **ID de Modelo**: `meta.llama3-1-70b-instruct-v1:0`
* **Coste por 1M Tokens**: ~$2.65 (Input) / ~$3.50 (Output).
* **Ventajas**: Equivalente al modelo actual que usamos en Groq. Su razonamiento lógico de grado 70B es óptimo para la consolidación de esquemas y deduplicación compleja de grafos.

### 🏆 Opción C: Claude 3.5 Sonnet v2 (Recomendado por Inteligencia Suprema)
* **ID de Modelo**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
* **Coste por 1M Tokens**: ~$3.00 (Input) / ~$15.00 (Output).
* **Ventajas**: El modelo más inteligente del mercado para agentes. Ideal si tu bóveda requiere razonamiento filosófico, fenomenológico o técnico avanzado, pero con mayor latencia y coste.

---

## 🔑 2. Requisitos de Credenciales (Variables de Entorno)

Para que el servidor se conecte a AWS Bedrock, debemos añadir las siguientes variables al archivo `.env` (tanto local como remoto):

```env
# --- CONFIGURACIÓN DE AWS BEDROCK ---
AWS_ACCESS_KEY_ID=tu_aws_access_key_id
AWS_SECRET_ACCESS_KEY=tu_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1           # o us-west-2 (donde habilites los modelos)
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

> [!CAUTION]
> Asegúrate de que el usuario de IAM asociado a las credenciales tenga políticas de acceso asignadas para invocar modelos en Bedrock: `bedrock:InvokeModel`.
> Asimismo, debes **solicitar acceso al modelo** (Model Access) en la consola de AWS Bedrock de la región configurada antes de realizar las llamadas de API.

---

## 🛠️ 3. Implementación de Código (Patrón Converse API)

Para integrar Bedrock de forma asíncrona dentro de la API FastAPI del RAG sin bloquear el bucle de eventos, usaremos el método unificado `converse` envuelto con `asyncio.to_thread` de Python.

A continuación se presenta el patrón de diseño para sustituir el mock extractor en [lightrag_custom_server.py](file:///workspaces/lei-prueba/sincronizacion-obsidiane/lightrag_custom_server.py):

```python
import boto3
import asyncio
import json
import logging

logger = logging.getLogger("custom_lightrag_server")

async def call_bedrock_converse(model_id: str, messages: list, region: str = "us-east-1"):
    """
    Invoca un modelo en AWS Bedrock usando la Converse API de forma asíncrona.
    """
    # 1. Separar System Prompt de los mensajes principales
    system_prompts = []
    bedrock_messages = []
    
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        
        if role == "system":
            system_prompts.append({"text": content})
        else:
            # Bedrock Converse solo admite 'user' y 'assistant'
            if role not in ["user", "assistant"]:
                role = "user"
            bedrock_messages.append({
                "role": role,
                "content": [{"text": content}]
            })
            
    # 2. Definir llamada síncrona para Boto3
    def _invoke():
        # Usa las credenciales inyectadas por variables de entorno automáticamente
        client = boto3.client("bedrock-runtime", region_name=region)
        return client.converse(
            modelId=model_id,
            messages=bedrock_messages,
            system=system_prompts,
            inferenceConfig={
                "temperature": 0.1,
                "maxTokens": 4000
            }
        )

    # 3. Ejecutar la llamada bloqueante en un hilo de trabajo secundario para no congelar FastAPI
    response = await asyncio.to_thread(_invoke)
    
    # 4. Extraer el texto de respuesta
    output_text = response["output"]["message"]["content"][0]["text"]
    return output_text
```

### Inyección de la respuesta estructurada en Graphiti:
Reemplazaremos la llamada de Groq dentro de `mock_p` con una llamada a `call_bedrock_converse`:
```python
        async def mock_p(**kwargs):
            input_messages = kwargs.get("input")
            model_to_use = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
            aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            
            # Llamar a Bedrock
            response_text = await call_bedrock_converse(model_to_use, input_messages, region=aws_region)
            
            # Procesar el JSON estructurado devuelto por el modelo...
            d = json.loads(response_text)
            # (El resto del procesador robusto de entidades/relaciones se mantiene igual)
```

---

## 📋 4. Pasos para Activar AWS Bedrock

1. **Requisitos de Dependencia**:
   - Asegurarnos de que `boto3` esté en la lista de dependencias del contenedor RAG. Añadiremos `boto3` a `/workspaces/lei-prueba/sincronizacion-obsidiane/requirements.txt` si es necesario.
2. **Habilitación en Consola**:
   - Entra en tu consola de AWS.
   - Ve a **Amazon Bedrock** -> **Model Access** y solicita acceso para Claude 3 Haiku y/o Llama 3.1.
3. **Configuración de Variables**:
   - Edita el archivo `.env` del host local y del VPS remoto con las nuevas variables.
4. **Implementación de Parche**:
   - Reemplazar el bloque LLM de `lightrag_custom_server.py`.
