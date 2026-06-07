"""
Integración de Google Gemini con el Generador de Rutas Fenomenológicas
Permite usar Gemini para enriquecimiento semántico y análisis de convergencia
"""

import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-generativeai no instalado. Instalar con: pip install google-generativeai")

load_dotenv()


class GeminiEnriquecedor:
    """Enriquece rutas fenomenológicas usando Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai no está instalado")
        
        self.api_key = api_key or os.getenv('GOOGLE_GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY no configurada")
        
        genai.configure(api_key=self.api_key)
        
        # Configuración del modelo
        self.generation_config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
    
    def analizar_convergencia(self, concepto: str, rutas: List[Dict]) -> Dict:
        """
        Usa Gemini para analizar si las 5 rutas convergen hacia una definición unificada
        
        Args:
            concepto: El concepto analizado (ej: "SOPORTE")
            rutas: Lista de 5 diccionarios con las rutas generadas
        
        Returns:
            Dict con análisis de convergencia:
            {
                "convergen": bool,
                "razon": str,
                "definicion_unificada": str,
                "confianza": float,
                "recomendaciones": List[str]
            }
        """
        prompt = f"""Eres un experto en análisis fenomenológico y semántico. 

Analiza las siguientes 5 rutas fenomenológicas del concepto "{concepto}":

{json.dumps(rutas, indent=2, ensure_ascii=False)}

INSTRUCCIONES:
1. Determina si las 5 rutas CONVERGEN hacia una definición unificada del concepto
2. Una convergencia válida significa:
   - Las 5 rutas apuntan al mismo núcleo semántico
   - No hay contradicciones fundamentales entre rutas
   - La similitud coseno entre rutas es > 0.95
   - El concepto alcanza el "máximo relacional" (99%+ de certeza)

3. Responde SOLO en formato JSON válido:
{{
  "convergen": true/false,
  "razon": "Explicación breve (máx 100 palabras)",
  "definicion_unificada": "Definición del concepto si convergen, o null",
  "confianza": 0.0-1.0,
  "recomendaciones": ["Sugerencia 1", "Sugerencia 2"]
}}

NO agregues texto fuera del JSON. SOLO responde el JSON.
"""
        
        try:
            response = self.model.generate_content(prompt)
            texto_respuesta = response.text.strip()
            
            # Limpiar markdown code blocks si existen
            if texto_respuesta.startswith("```json"):
                texto_respuesta = texto_respuesta[7:]
            if texto_respuesta.startswith("```"):
                texto_respuesta = texto_respuesta[3:]
            if texto_respuesta.endswith("```"):
                texto_respuesta = texto_respuesta[:-3]
            
            resultado = json.loads(texto_respuesta.strip())
            
            # Validar estructura
            campos_requeridos = ["convergen", "razon", "definicion_unificada", "confianza", "recomendaciones"]
            if not all(campo in resultado for campo in campos_requeridos):
                raise ValueError(f"Respuesta incompleta de Gemini: {resultado}")
            
            return resultado
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON de Gemini: {e}")
            print(f"Respuesta cruda: {response.text}")
            return {
                "convergen": False,
                "razon": f"Error al parsear respuesta de Gemini: {str(e)}",
                "definicion_unificada": None,
                "confianza": 0.0,
                "recomendaciones": ["Revisar prompt de Gemini", "Validar formato JSON"]
            }
        except Exception as e:
            print(f"❌ Error en Gemini API: {e}")
            return {
                "convergen": False,
                "razon": f"Error en API de Gemini: {str(e)}",
                "definicion_unificada": None,
                "confianza": 0.0,
                "recomendaciones": ["Verificar API key", "Revisar conectividad"]
            }
    
    def enriquecer_ruta(self, concepto: str, ruta: Dict) -> Dict:
        """
        Enriquece una ruta individual con análisis semántico de Gemini
        
        Args:
            concepto: El concepto de la ruta
            ruta: Dict con la ruta a enriquecer
        
        Returns:
            Ruta enriquecida con campo "gemini_analisis"
        """
        prompt = f"""Analiza esta ruta fenomenológica del concepto "{concepto}":

Tipo de Ruta: {ruta['tipo_ruta']}
Definición: {ruta['definicion']}
Contexto: {ruta['contexto_fenomenologico']}

Proporciona:
1. Profundidad semántica: ¿Qué tan profunda es esta definición?
2. Coherencia interna: ¿Es coherente consigo misma?
3. Relaciones implícitas: ¿Qué otros conceptos implica?

Formato JSON:
{{
  "profundidad_semantica": 0.0-1.0,
  "coherencia_interna": 0.0-1.0,
  "relaciones_implicitas": ["concepto1", "concepto2"],
  "observaciones": "Breve análisis"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            texto = response.text.strip()
            
            # Limpiar markdown
            if texto.startswith("```json"):
                texto = texto[7:]
            if texto.startswith("```"):
                texto = texto[3:]
            if texto.endswith("```"):
                texto = texto[:-3]
            
            analisis = json.loads(texto.strip())
            ruta_enriquecida = ruta.copy()
            ruta_enriquecida["gemini_analisis"] = analisis
            
            return ruta_enriquecida
            
        except Exception as e:
            print(f"⚠️ Error enriqueciendo ruta con Gemini: {e}")
            ruta["gemini_analisis"] = {
                "error": str(e),
                "profundidad_semantica": 0.5,
                "coherencia_interna": 0.5,
                "relaciones_implicitas": [],
                "observaciones": "No se pudo analizar con Gemini"
            }
            return ruta
    
    def generar_embedding_texto(self, texto: str) -> Optional[List[float]]:
        """
        Genera embedding usando Gemini (alternativa a SentenceTransformer)
        
        NOTA: Gemini 1.5 Pro no tiene API de embeddings nativa.
        Esta función usa el modelo text-embedding-004.
        """
        try:
            # Usar modelo de embeddings de Google
            resultado = genai.embed_content(
                model="models/text-embedding-004",
                content=texto,
                task_type="semantic_similarity"
            )
            return resultado['embedding']
        except Exception as e:
            print(f"⚠️ Error generando embedding con Gemini: {e}")
            return None


def verificar_gemini_disponible() -> bool:
    """Verifica si Gemini está configurado y disponible"""
    if not GEMINI_AVAILABLE:
        return False
    
    api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
    if not api_key:
        return False
    
    try:
        enriquecedor = GeminiEnriquecedor(api_key)
        # Test simple
        test_response = enriquecedor.model.generate_content("Di 'OK'")
        return "OK" in test_response.text or "ok" in test_response.text.lower()
    except Exception as e:
        print(f"❌ Gemini no disponible: {e}")
        return False


if __name__ == "__main__":
    # Prueba de integración
    print("🧪 Probando integración con Gemini...")
    
    if verificar_gemini_disponible():
        print("✅ Gemini disponible y funcional")
        
        # Prueba de análisis de convergencia
        enriquecedor = GeminiEnriquecedor()
        
        rutas_ejemplo = [
            {
                "tipo_ruta": "etimologica",
                "definicion": "Del latín 'supportare': llevar por debajo, sostener",
                "contexto_fenomenologico": "Fundamento que sostiene algo desde abajo",
                "certeza": 0.98
            },
            {
                "tipo_ruta": "practica",
                "definicion": "Estructura física o conceptual que sostiene algo",
                "contexto_fenomenologico": "Elemento que permite que otro se mantenga",
                "certeza": 0.97
            }
        ]
        
        resultado = enriquecedor.analizar_convergencia("SOPORTE", rutas_ejemplo)
        print(f"\n📊 Resultado análisis:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print("❌ Gemini no está disponible")
        print("Asegúrate de:")
        print("1. Instalar: pip install google-generativeai")
        print("2. Configurar: export GOOGLE_GEMINI_API_KEY='tu-api-key'")
