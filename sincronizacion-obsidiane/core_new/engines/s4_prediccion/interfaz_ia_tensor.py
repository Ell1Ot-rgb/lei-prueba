"""
Interfaz IA-Tensor: Permite a LLMs interactuar directamente con S4
===================================================================

Esta interfaz permite que una IA (LLM como Gemini, GPT, etc.) pueda:
1. Leer el estado tensorial actual
2. Modificar tensores en tiempo real
3. Consultar predicciones
4. Ajustar hiperparámetros
5. Analizar dinámica de Koopman

Diseñado para integrarse con:
- n8n function calling
- LangChain tools
- Gemini/GPT function calling
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

# Import condicional para standalone o módulo
try:
    from .motor_s4 import MotorS4, PrediccionS4
except ImportError:
    from motor_s4 import MotorS4, PrediccionS4


@dataclass
class ToolDefinition:
    """Definición de herramienta para LLM."""
    name: str
    description: str
    parameters: Dict[str, str]
    returns: str


class InterfazIATensor:
    """
    Interfaz bidireccional entre una IA (LLM) y los tensores de S4.
    
    CAPACIDADES:
    ============
    
    LECTURA:
    - leer_estado_tensor(): Estado completo actual
    - leer_modos_dinamicos(): Análisis de Koopman
    - leer_historial(): Historial de tensores
    - leer_patrones_spa(): Patrones detectados
    
    ESCRITURA:
    - modificar_pad_emotions(): Ajustar estado emocional
    - inyectar_patron(): Inyectar patrón al reservoir
    - ajustar_memoria_rmn(): Modificar decay de memoria
    - reset_sistema(): Reiniciar S4
    
    PREDICCIÓN:
    - pedir_prediccion(): Predicción numérica
    - pedir_prediccion_textual(): Predicción interpretable
    - analizar_tendencia(): Análisis de tendencias
    
    INTEGRACIÓN LLM:
    - get_tools_for_llm(): Definiciones para function calling
    - ejecutar_tool(): Ejecutar herramienta por nombre
    """
    
    def __init__(self, motor_s4: MotorS4):
        self.motor = motor_s4
        self._tools = self._registrar_tools()
    
    # =========================================================================
    # LECTURA
    # =========================================================================
    
    def leer_estado_tensor(self) -> Dict[str, Any]:
        """
        Lee el estado tensorial actual del sistema.
        
        Returns:
            Diccionario con todos los tensores actuales:
            - embedding: Vector semántico [64]
            - esn_state: Estado del reservoir [100]
            - pad_emotions: Pleasure/Arousal/Dominance [3]
            - grundzug_freq: Top-10 frecuencias [10]
            - lyapunov_features: Métricas de caos [5]
            - flat: Vector concatenado [182]
        """
        if len(self.motor.historial) == 0:
            return {"error": "Sin historial", "tensores": {}}
        
        ultimo = self.motor.historial.buffer[-1]
        
        return {
            "timestamp": ultimo.timestamp,
            "tensores": {
                "embedding": ultimo.embedding.tolist(),
                "esn_state": ultimo.esn_state.tolist(),
                "pad_emotions": {
                    "pleasure": float(ultimo.pad_emotions[0]),
                    "arousal": float(ultimo.pad_emotions[1]),
                    "dominance": float(ultimo.pad_emotions[2])
                },
                "grundzug_freq": ultimo.grundzug_freq.tolist(),
                "lyapunov_features": ultimo.lyapunov_features.tolist()
            },
            "dimensiones": {
                "embedding": 64,
                "esn_state": 100,
                "pad": 3,
                "grundzug": 10,
                "lyapunov": 5,
                "total": 182
            }
        }
    
    def leer_modos_dinamicos(self) -> Dict[str, Any]:
        """
        Analiza los modos de Koopman/DMD del sistema.
        
        Returns:
            Diccionario con:
            - eigenvalues: Valores propios dominantes
            - frequencies: Frecuencias de oscilación
            - growth_rates: Tasas de crecimiento/decaimiento
            - interpretation: Interpretación textual
        """
        if not self.motor.dmd.fitted:
            return {"error": "DMD no entrenado", "fitted": False}
        
        try:
            modes, eigenvalues = self.motor.dmd.get_dominant_modes(k=5)
            freqs, growth = self.motor.dmd.get_frequencies_and_growth()
            
            return {
                "fitted": True,
                "eigenvalues": {
                    "magnitudes": np.abs(eigenvalues).tolist(),
                    "phases": np.angle(eigenvalues).tolist()
                },
                "frequencies_hz": freqs[:5].tolist() if len(freqs) >= 5 else freqs.tolist(),
                "growth_rates": growth[:5].tolist() if len(growth) >= 5 else growth.tolist(),
                "modes_shape": list(modes.shape),
                "interpretation": self._interpretar_modos(freqs, growth),
                "regimen": self._clasificar_regimen(self.motor.rmn.compute_lyapunov_estimate())
            }
        except Exception as e:
            return {"error": str(e), "fitted": False}
    
    def leer_historial(self, ultimos_n: int = 10) -> Dict[str, Any]:
        """
        Lee el historial de tensores.
        
        Args:
            ultimos_n: Número de tensores a retornar
        
        Returns:
            Lista de tensores con timestamps
        """
        if len(self.motor.historial) == 0:
            return {"error": "Sin historial", "tensores": []}
        
        historial = []
        buffer = list(self.motor.historial.buffer)[-ultimos_n:]
        
        for tf in buffer:
            historial.append({
                "timestamp": tf.timestamp,
                "pad": tf.pad_emotions.tolist(),
                "lyapunov": tf.lyapunov_features[0].item() if tf.lyapunov_features.size > 0 else 0
            })
        
        return {
            "total_en_buffer": len(self.motor.historial),
            "retornados": len(historial),
            "tensores": historial
        }
    
    def leer_patrones_spa(self) -> Dict[str, Any]:
        """
        Lee los patrones detectados por SPA.
        
        Returns:
            Información sobre patrones y transiciones
        """
        if not self.motor.spa.fitted:
            return {"error": "SPA no entrenado", "fitted": False}
        
        stats = self.motor.spa.get_pattern_statistics()
        
        return {
            "fitted": True,
            "n_patrones": len(stats['centroides']),
            "distribucion_estacionaria": stats['distribucion_estacionaria'][:10].tolist(),
            "entropia_transicion_media": float(stats['entropia_transicion'].mean()),
            "patrones_activos": int((stats['conteo_patrones'] > 0).sum())
        }
    
    # =========================================================================
    # ESCRITURA
    # =========================================================================
    
    def modificar_pad_emotions(self, 
                               pleasure: float, 
                               arousal: float, 
                               dominance: float) -> Dict[str, Any]:
        """
        Modifica directamente el estado emocional PAD.
        
        Args:
            pleasure: -1.0 a 1.0 (displacer → placer)
            arousal: -1.0 a 1.0 (calma → excitación)
            dominance: -1.0 a 1.0 (sumisión → dominancia)
        
        Returns:
            Confirmación con valores anteriores y nuevos
        """
        if len(self.motor.historial) == 0:
            return {"error": "Sin historial para modificar"}
        
        ultimo = self.motor.historial.buffer[-1]
        anterior = ultimo.pad_emotions.copy()
        
        # Clamp valores
        nuevo = np.array([
            np.clip(pleasure, -1.0, 1.0),
            np.clip(arousal, -1.0, 1.0),
            np.clip(dominance, -1.0, 1.0)
        ], dtype=np.float32)
        
        ultimo.pad_emotions = nuevo
        
        return {
            "success": True,
            "anterior": {
                "pleasure": float(anterior[0]),
                "arousal": float(anterior[1]),
                "dominance": float(anterior[2])
            },
            "nuevo": {
                "pleasure": float(nuevo[0]),
                "arousal": float(nuevo[1]),
                "dominance": float(nuevo[2])
            }
        }
    
    def inyectar_patron(self, patron: List[float]) -> Dict[str, Any]:
        """
        Inyecta un patrón directamente al Reservoir Memory Network.
        
        Args:
            patron: Vector de 182 dimensiones
        
        Returns:
            Confirmación con nuevo estado
        """
        patron_array = np.array(patron, dtype=np.float32)
        
        if patron_array.shape[0] != 182:
            return {
                "error": f"Patrón debe tener 182 dimensiones, recibido: {patron_array.shape[0]}"
            }
        
        # Inyectar al RMN
        nuevo_estado = self.motor.rmn.step(patron_array)
        
        return {
            "success": True,
            "patron_inyectado_dim": len(patron),
            "nuevo_estado_shape": nuevo_estado.shape,
            "nuevo_estado_norma": float(np.linalg.norm(nuevo_estado)),
            "lyapunov_despues": float(self.motor.rmn.compute_lyapunov_estimate())
        }
    
    def ajustar_memoria_rmn(self, decay: float) -> Dict[str, Any]:
        """
        Ajusta el decay de la memoria del RMN.
        
        Args:
            decay: 0.9 a 0.999 (mayor = memoria más larga)
        
        Returns:
            Confirmación con valor anterior y nuevo
        """
        anterior = self.motor.rmn.config.memory_decay
        nuevo = float(np.clip(decay, 0.9, 0.999))
        
        self.motor.rmn.config.memory_decay = nuevo
        
        # Reconstruir matriz de memoria
        self.motor.rmn.W_mem = np.eye(self.motor.rmn.config.memory_size) * nuevo
        self.motor.rmn.W_mem += np.random.randn(
            self.motor.rmn.config.memory_size,
            self.motor.rmn.config.memory_size
        ) * 0.01
        
        return {
            "success": True,
            "decay_anterior": anterior,
            "decay_nuevo": nuevo,
            "memoria_size": self.motor.rmn.config.memory_size
        }
    
    def reset_sistema(self) -> Dict[str, Any]:
        """
        Reinicia el motor S4 completamente.
        
        Returns:
            Confirmación
        """
        historial_anterior = len(self.motor.historial)
        self.motor.reset()
        
        return {
            "success": True,
            "historial_eliminado": historial_anterior,
            "entrenado": self.motor.entrenado
        }
    
    # =========================================================================
    # PREDICCIÓN
    # =========================================================================
    
    def pedir_prediccion(self, horizonte: int = 10) -> Dict[str, Any]:
        """
        Genera predicción numérica.
        
        Args:
            horizonte: Pasos a predecir
        
        Returns:
            Predicción con estadísticas
        """
        pred = self.motor.predecir(horizonte)
        
        return {
            "horizonte": horizonte,
            "prediccion_shape": list(pred.prediccion.shape),
            "incertidumbre_media": float(pred.incertidumbre.mean()),
            "incertidumbre_max": float(pred.incertidumbre.max()),
            "lyapunov": float(pred.lyapunov),
            "regimen": self._clasificar_regimen(pred.lyapunov),
            "patrones_spa": pred.patrones_spa,
            "timestamp": pred.timestamp
        }
    
    def pedir_prediccion_textual(self, horizonte: int = 5) -> str:
        """
        Genera predicción en formato textual interpretable.
        
        Args:
            horizonte: Pasos a predecir
        
        Returns:
            Texto con análisis de predicción
        """
        pred = self.motor.predecir(horizonte)
        
        # Analizar tendencias
        if pred.prediccion.shape[0] > 1:
            emb_trend = "↑" if pred.prediccion[-1, :64].mean() > pred.prediccion[0, :64].mean() else "↓"
            esn_trend = "↑" if pred.prediccion[-1, 64:164].mean() > pred.prediccion[0, 64:164].mean() else "↓"
            pad_final = pred.prediccion[-1, 164:167]
        else:
            emb_trend = "→"
            esn_trend = "→"
            pad_final = np.zeros(3)
        
        texto = f"""
═══════════════════════════════════════
 PREDICCIÓN S4 (horizonte={horizonte})
═══════════════════════════════════════

📊 MÉTRICAS GLOBALES
   • Lyapunov: {pred.lyapunov:.4f}
   • Régimen: {self._clasificar_regimen(pred.lyapunov)}
   • Incertidumbre: {pred.incertidumbre.mean():.4f} ± {pred.incertidumbre.std():.4f}

📈 TENDENCIAS
   • Embedding: {emb_trend} (semántica {'expansiva' if emb_trend == '↑' else 'contractiva'})
   • ESN State: {esn_trend} (dinámica {'activa' if esn_trend == '↑' else 'estable'})
   • PAD Final: P={pad_final[0]:.2f}, A={pad_final[1]:.2f}, D={pad_final[2]:.2f}

🔮 PATRONES SPA
   {pred.patrones_spa if pred.patrones_spa else 'No detectados'}

═══════════════════════════════════════
"""
        return texto.strip()
    
    def analizar_tendencia(self, variable: str = "embedding") -> Dict[str, Any]:
        """
        Analiza la tendencia de una variable específica.
        
        Args:
            variable: 'embedding', 'esn_state', 'pad', 'lyapunov'
        
        Returns:
            Análisis de tendencia
        """
        historial = self.motor.historial.get_component_history(variable)
        
        if historial is None or len(historial) < 3:
            return {"error": "Historial insuficiente"}
        
        # Calcular tendencia lineal
        t = np.arange(len(historial))
        medias = historial.mean(axis=1) if historial.ndim > 1 else historial
        
        slope, intercept = np.polyfit(t, medias, 1)
        
        # Proyección
        proyeccion_5 = slope * (len(historial) + 5) + intercept
        
        return {
            "variable": variable,
            "n_muestras": len(historial),
            "media_actual": float(medias[-1]),
            "media_inicial": float(medias[0]),
            "slope": float(slope),
            "tendencia": "creciente" if slope > 0.01 else ("decreciente" if slope < -0.01 else "estable"),
            "proyeccion_5_pasos": float(proyeccion_5)
        }
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _interpretar_modos(self, freqs: np.ndarray, growth: np.ndarray) -> str:
        """Genera interpretación textual de los modos."""
        if len(freqs) == 0:
            return "Sin modos detectados"
        
        dominant_freq = np.abs(freqs[0])
        dominant_growth = growth[0]
        
        if dominant_growth > 0.1:
            return f"Sistema INESTABLE - expansión exponencial (λ={dominant_growth:.3f}), oscilación a {dominant_freq:.3f} Hz"
        elif dominant_growth < -0.1:
            return f"Sistema ESTABLE - convergencia (λ={dominant_growth:.3f}), amortiguamiento a {dominant_freq:.3f} Hz"
        else:
            period = 1/max(dominant_freq, 0.001)
            return f"Sistema en BORDE DEL CAOS - oscilación cuasi-periódica, periodo ≈ {period:.1f}s"
    
    def _clasificar_regimen(self, lyapunov: float) -> str:
        """Clasifica el régimen dinámico según Lyapunov."""
        if lyapunov > 0.1:
            return "CAÓTICO"
        elif lyapunov < -0.1:
            return "ORDENADO"
        else:
            return "BORDE_DEL_CAOS"
    
    # =========================================================================
    # INTEGRACIÓN LLM
    # =========================================================================
    
    def _registrar_tools(self) -> Dict[str, ToolDefinition]:
        """Registra las herramientas disponibles."""
        return {
            "leer_estado_tensor": ToolDefinition(
                name="leer_estado_tensor",
                description="Lee el estado tensorial actual del sistema S4 incluyendo embedding, ESN, PAD, grundzug y lyapunov",
                parameters={},
                returns="Dict con todos los tensores actuales"
            ),
            "leer_modos_dinamicos": ToolDefinition(
                name="leer_modos_dinamicos",
                description="Analiza los modos de Koopman/DMD del sistema para entender la dinámica",
                parameters={},
                returns="Dict con eigenvalores, frecuencias, tasas de crecimiento e interpretación"
            ),
            "leer_historial": ToolDefinition(
                name="leer_historial",
                description="Lee el historial de tensores recientes",
                parameters={"ultimos_n": "int, número de tensores a retornar (default: 10)"},
                returns="Lista de tensores con timestamps"
            ),
            "leer_patrones_spa": ToolDefinition(
                name="leer_patrones_spa",
                description="Lee los patrones detectados por el algoritmo SPA",
                parameters={},
                returns="Info sobre patrones y distribución estacionaria"
            ),
            "modificar_pad_emotions": ToolDefinition(
                name="modificar_pad_emotions",
                description="Modifica el estado emocional PAD directamente",
                parameters={
                    "pleasure": "float [-1, 1] - nivel de placer",
                    "arousal": "float [-1, 1] - nivel de excitación",
                    "dominance": "float [-1, 1] - nivel de dominancia"
                },
                returns="Confirmación con valores anterior y nuevo"
            ),
            "inyectar_patron": ToolDefinition(
                name="inyectar_patron",
                description="Inyecta un patrón de 182 dimensiones al reservoir",
                parameters={"patron": "List[float] de 182 elementos"},
                returns="Confirmación y nuevo estado"
            ),
            "ajustar_memoria_rmn": ToolDefinition(
                name="ajustar_memoria_rmn",
                description="Ajusta el decay de la memoria del RMN (mayor = memoria más larga)",
                parameters={"decay": "float [0.9, 0.999]"},
                returns="Confirmación con valores"
            ),
            "pedir_prediccion": ToolDefinition(
                name="pedir_prediccion",
                description="Genera predicción numérica para N pasos",
                parameters={"horizonte": "int, pasos a predecir (default: 10)"},
                returns="Dict con predicción y métricas"
            ),
            "pedir_prediccion_textual": ToolDefinition(
                name="pedir_prediccion_textual",
                description="Genera predicción en formato textual interpretable",
                parameters={"horizonte": "int, pasos a predecir (default: 5)"},
                returns="Texto con análisis completo"
            ),
            "analizar_tendencia": ToolDefinition(
                name="analizar_tendencia",
                description="Analiza la tendencia de una variable específica",
                parameters={"variable": "str - 'embedding', 'esn_state', 'pad_emotions', 'lyapunov_features'"},
                returns="Dict con análisis de tendencia"
            ),
            "reset_sistema": ToolDefinition(
                name="reset_sistema",
                description="Reinicia completamente el motor S4",
                parameters={},
                returns="Confirmación"
            )
        }
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Retorna definiciones de herramientas para LLM function calling.
        
        Compatible con:
        - OpenAI function calling
        - Google Gemini function calling
        - LangChain tools
        - n8n AI nodes
        
        Returns:
            Lista de definiciones de herramientas
        """
        tools = []
        for name, tool in self._tools.items():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        k: {"type": "number" if "float" in v else ("integer" if "int" in v else "string"), 
                            "description": v}
                        for k, v in tool.parameters.items()
                    },
                    "required": []
                }
            })
        return tools
    
    def get_tools_openai_format(self) -> List[Dict[str, Any]]:
        """Formato específico para OpenAI function calling."""
        return [
            {
                "type": "function",
                "function": tool
            }
            for tool in self.get_tools_for_llm()
        ]
    
    def ejecutar_tool(self, nombre: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una herramienta por nombre.
        
        Args:
            nombre: Nombre de la herramienta
            **kwargs: Argumentos para la herramienta
        
        Returns:
            Resultado de la herramienta
        """
        method_map = {
            "leer_estado_tensor": self.leer_estado_tensor,
            "leer_modos_dinamicos": self.leer_modos_dinamicos,
            "leer_historial": self.leer_historial,
            "leer_patrones_spa": self.leer_patrones_spa,
            "modificar_pad_emotions": self.modificar_pad_emotions,
            "inyectar_patron": self.inyectar_patron,
            "ajustar_memoria_rmn": self.ajustar_memoria_rmn,
            "pedir_prediccion": self.pedir_prediccion,
            "pedir_prediccion_textual": self.pedir_prediccion_textual,
            "analizar_tendencia": self.analizar_tendencia,
            "reset_sistema": self.reset_sistema
        }
        
        if nombre not in method_map:
            return {"error": f"Herramienta '{nombre}' no encontrada"}
        
        try:
            return method_map[nombre](**kwargs)
        except Exception as e:
            return {"error": str(e)}


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  TEST: Interfaz IA-Tensor")
    print("=" * 70)
    
    # Crear motor S4
    motor = MotorS4()
    
    # Simular datos
    for i in range(30):
        motor.actualizar(
            embedding=np.random.randn(64).astype(np.float32),
            esn_state=np.random.randn(100).astype(np.float32),
            pad_emotions=np.random.rand(3).astype(np.float32)
        )
    
    # Crear interfaz
    interfaz = InterfazIATensor(motor)
    
    print("\n📖 LECTURA")
    print("-" * 40)
    
    estado = interfaz.leer_estado_tensor()
    print(f"  Estado tensor: timestamp={estado.get('timestamp', 0):.2f}")
    print(f"  PAD: {estado['tensores']['pad_emotions']}")
    
    modos = interfaz.leer_modos_dinamicos()
    print(f"\n  Modos DMD: {modos.get('interpretation', 'N/A')}")
    
    patrones = interfaz.leer_patrones_spa()
    print(f"  Patrones SPA: {patrones.get('n_patrones', 0)}")
    
    print("\n✏️ ESCRITURA")
    print("-" * 40)
    
    resultado = interfaz.modificar_pad_emotions(0.8, 0.5, 0.9)
    print(f"  PAD modificado: {resultado['nuevo']}")
    
    resultado = interfaz.ajustar_memoria_rmn(0.95)
    print(f"  Memoria RMN: decay={resultado['decay_nuevo']}")
    
    print("\n🔮 PREDICCIÓN")
    print("-" * 40)
    
    pred = interfaz.pedir_prediccion(horizonte=5)
    print(f"  Lyapunov: {pred['lyapunov']:.4f}")
    print(f"  Régimen: {pred['regimen']}")
    print(f"  Incertidumbre: {pred['incertidumbre_media']:.4f}")
    
    print("\n📄 PREDICCIÓN TEXTUAL")
    print(interfaz.pedir_prediccion_textual(horizonte=5))
    
    print("\n🔧 HERRAMIENTAS LLM")
    print("-" * 40)
    
    tools = interfaz.get_tools_for_llm()
    print(f"  Herramientas disponibles: {len(tools)}")
    for t in tools:
        print(f"    • {t['name']}")
    
    # Ejecutar via nombre
    print("\n🎯 EJECUCIÓN VIA NOMBRE")
    resultado = interfaz.ejecutar_tool("leer_historial", ultimos_n=3)
    print(f"  Historial: {resultado['retornados']} tensores")
    
    print("\n" + "=" * 70)
    print("  INTERFAZ IA-TENSOR OPERATIVA ✓")
    print("=" * 70)
