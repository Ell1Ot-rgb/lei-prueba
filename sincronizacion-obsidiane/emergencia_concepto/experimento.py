"""
Experimentos para Revelar Propiedades Ocultas
==============================================

Define los tipos de experimentos que se pueden realizar sobre sistemas
para descubrir sus propiedades relacionalmente.
"""

from enum import Enum
from typing import Dict, Any, List, Callable
from datetime import datetime
import uuid


class TipoExperimento(Enum):
    """Tipos de experimentos para revelar propiedades."""
    PREDICIBILIDAD = "predicibilidad"
    REVERSIBILIDAD = "reversibilidad"
    DIVERSIDAD = "diversidad"
    EVOLUCION_TEMPORAL = "evolucion_temporal"
    INTERACCION_AGENTE = "interaccion_agente"
    RESPUESTA_PERTURBACION = "respuesta_perturbacion"


class Experimento:
    """
    Experimento que se realiza sobre uno o más sistemas para
    observar comportamientos y revelar propiedades.
    """
    
    def __init__(
        self,
        nombre: str,
        tipo: TipoExperimento,
        descripcion: str = ""
    ):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.tipo = tipo
        self.descripcion = descripcion
        self.resultados = {}
        self.creado_en = datetime.now()
        
    def ejecutar(
        self,
        sistema,
        parametros: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el experimento sobre un sistema.
        
        Args:
            sistema: SistemaObservado a experimentar
            parametros: Parámetros específicos del experimento
            
        Returns:
            Resultados observables
        """
        parametros = parametros or {}
        
        # Seleccionar método según tipo
        metodos = {
            TipoExperimento.PREDICIBILIDAD: self._medir_predicibilidad,
            TipoExperimento.REVERSIBILIDAD: self._medir_reversibilidad,
            TipoExperimento.DIVERSIDAD: self._medir_diversidad,
            TipoExperimento.EVOLUCION_TEMPORAL: self._medir_evolucion,
            TipoExperimento.INTERACCION_AGENTE: self._medir_interaccion,
            TipoExperimento.RESPUESTA_PERTURBACION: self._medir_perturbacion
        }
        
        metodo = metodos.get(self.tipo)
        if metodo:
            resultado = metodo(sistema, parametros)
        else:
            resultado = {"error": "Tipo de experimento no implementado"}
        
        # Guardar resultado
        self.resultados[sistema.nombre] = resultado
        sistema.registrar_experimento(self.id, resultado)
        
        return resultado
    
    def _medir_predicibilidad(self, sistema, params) -> Dict[str, Any]:
        """
        Mide qué tan predecible es el sistema.
        
        Método: Observar estados en t, t+1, t+2... y medir similitud.
        """
        num_pasos = params.get("num_pasos", 10)
        
        estados = []
        cambios = 0
        
        for t in range(num_pasos):
            estado = sistema.registrar_estado(
                f"predicibilidad_t{t}",
                {"paso": t}
            )
            estados.append(estado)
            
            # Simular evolución basada en propiedad oculta
            entropia = sistema._verificar_propiedad_oculta("entropia") or 0
            
            # Alta entropía → más cambios
            if entropia > 5 and t > 0:
                cambios += int(entropia / 2)
        
        predicibilidad = max(0.0, 1.0 - (cambios / (num_pasos * 10)))
        
        return {
            "predicibilidad": round(predicibilidad, 2),
            "cambios_observados": cambios,
            "num_pasos": num_pasos
        }
    
    def _medir_reversibilidad(self, sistema, params) -> Dict[str, Any]:
        """
        Mide si los cambios en el sistema son reversibles.
        """
        entropia = sistema._verificar_propiedad_oculta("entropia") or 0
        
        # Alta entropía → baja reversibilidad
        reversibilidad = max(0.0, 1.0 - (entropia / 15.0))
        
        return {
            "reversibilidad": round(reversibilidad, 2),
            "accion": "perturbar_sistema",
            "revertir": "aplicar_accion_inversa",
            "estado_final": "similar" if reversibilidad > 0.5 else "diferente"
        }
    
    def _medir_diversidad(self, sistema, params) -> Dict[str, Any]:
        """
        Mide cuántas configuraciones diferentes puede tener el sistema.
        """
        num_observaciones = params.get("num_observaciones", 1000)
        entropia = sistema._verificar_propiedad_oculta("entropia") or 0
        
        # Alta entropía → muchas configuraciones
        configs_unicas = int(num_observaciones * min(1.0, entropia / 13.0))
        
        # Evitar 0 configuraciones
        if configs_unicas == 0 and entropia > 0:
            configs_unicas = 1
        
        return {
            "observaciones": num_observaciones,
            "configuraciones_unicas": configs_unicas,
            "sorpresa_promedio": round(entropia, 1)
        }
    
    def _medir_evolucion(self, sistema, params) -> Dict[str, Any]:
        """
        Mide cómo evoluciona una propiedad con el tiempo.
        """
        tiempos = params.get("tiempos", [0, 100, 1000])
        entropia_inicial = sistema._verificar_propiedad_oculta("entropia") or 0
        
        # La entropía puede aumentar pero nunca decrece
        valores = []
        for t in tiempos:
            incremento = (t / 1000) * min(2.0, 13 - entropia_inicial)
            valor = entropia_inicial + incremento
            valores.append(round(valor, 1))
        
        # Determinar tendencia
        if valores[0] == valores[-1]:
            tendencia = "constante"
        elif valores[-1] - valores[0] < 1.0:
            tendencia = "incremento_lento"
        elif valores[-1] - valores[0] < 3.0:
            tendencia = "incremento_moderado"
        else:
            tendencia = "incremento_notable"
        
        return {
            "P_inicial": valores[0],
            f"P_t={tiempos[1]}": valores[1],
            f"P_t={tiempos[2]}": valores[2],
            "tendencia": tendencia
        }
    
    def _medir_interaccion(self, sistema, params) -> Dict[str, Any]:
        """
        Mide cómo un agente externo interactúa con el sistema.
        """
        agente = params.get("agente", "humano")
        accion = params.get("accion", "observar")
        
        entropia = sistema._verificar_propiedad_oculta("entropia") or 0
        
        # Simular respuesta basada en entropía
        if entropia < 3:
            reaccion = "neutral"
            tiempo_atencion = 0.5
        elif entropia < 6:
            reaccion = "interes_moderado"
            tiempo_atencion = 2.0
        else:
            reaccion = "fascinacion"
            tiempo_atencion = 3.5
        
        return {
            "agente": agente,
            "accion": accion,
            "reaccion": reaccion,
            "tiempo_atencion": tiempo_atencion
        }
    
    def _medir_perturbacion(self, sistema, params) -> Dict[str, Any]:
        """
        Mide cómo responde el sistema a perturbaciones.
        """
        intensidad = params.get("intensidad", 1.0)
        entropia = sistema._verificar_propiedad_oculta("entropia") or 0
        
        # Alta entropía → gran respuesta a perturbaciones
        amplificacion = 1.0 + (entropia / 10.0)
        
        return {
            "perturbacion_aplicada": intensidad,
            "respuesta_observada": round(intensidad * amplificacion, 2),
            "amplificacion": round(amplificacion, 2)
        }
    
    def comparar_sistemas(self, sistemas: List) -> Dict[str, Any]:
        """
        Compara los resultados del experimento en múltiples sistemas.
        
        Returns:
            Ranking y análisis comparativo
        """
        if not self.resultados:
            return {"error": "No hay resultados para comparar"}
        
        # Extraer métrica principal según tipo
        metricas = {
            TipoExperimento.PREDICIBILIDAD: "predicibilidad",
            TipoExperimento.REVERSIBILIDAD: "reversibilidad",
            TipoExperimento.DIVERSIDAD: "configuraciones_unicas"
        }
        
        metrica_clave = metricas.get(self.tipo, "valor")
        
        # Ordenar sistemas
        ranking = sorted(
            self.resultados.items(),
            key=lambda x: x[1].get(metrica_clave, 0),
            reverse=True
        )
        
        return {
            "experimento": self.nombre,
            "tipo": self.tipo.value,
            "ranking": ranking,
            "metrica": metrica_clave
        }
    
    def __repr__(self):
        return f"Experimento('{self.nombre}', tipo={self.tipo.value}, resultados={len(self.resultados)})"
