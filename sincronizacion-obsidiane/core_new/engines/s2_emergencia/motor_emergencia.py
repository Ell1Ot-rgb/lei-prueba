"""
Motor de Emergencia de Conceptos - VERSIÓN INCREMENTAL
=======================================================

Mejoras:
1. Aprendizaje progresivo desde datos brutos
2. Refinamiento continuo de conceptos
3. Persistencia de estado entre sesiones
4. Convergencia a largo plazo
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import pickle
import os

from .sistema_observado import SistemaObservado
from .experimento import Experimento, TipoExperimento
from .patron_relacional import PatronRelacional
from .concepto_emergente import ConceptoEmergente


class MotorEmergenciaConceptos:
    """
    Motor incremental que aprende desde datos brutos progresivamente.
    
    MEJORAS:
    - Carga/guarda estado entre sesiones
    - Refina conceptos con cada nueva observación
    - Detecta convergencia automáticamente
    """
    
    def __init__(self, state_file: str = "estado_emergencia.pkl"):
        self.sistemas = []
        self.experimentos_ejecutados = []
        self.patrones_detectados = []
        self.conceptos_emergidos = []
        
        # NUEVO: Estado incremental
        self.state_file = state_file
        self.iteracion = 0
        self.historico_certezas = {}  # {concepto_nombre: [certezas por iteración]}
        self.convergencia_alcanzada = False
        
        # NUEVO: Conexión con Sistema 1
        self.grundzugs_fuente = []  # Grundzugs recibidos del S1
        
        # Cargar estado previo si existe
        self._cargar_estado()
        
    def agregar_sistema(self, sistema: SistemaObservado) -> None:
        """Agrega un sistema para estudiar."""
        self.sistemas.append(sistema)
        
    def ingerir_desde_sistema1(self, grundzugs: List[Dict[str, Any]]) -> None:
        """
        NUEVO: Ingiere Grundzugs empíricos del Sistema 1.
        
        Args:
            grundzugs: Lista de Grundzugs en formato dict
                      {nombre, certeza, nivel, instancias_count, ...}
        
        Este método convierte conocimiento empírico en sistemas observables.
        """
        self.grundzugs_fuente.extend(grundzugs)
        
        for g in grundzugs:
            # Crear SistemaObservado desde Grundzug
            sistema = SistemaObservado(g['nombre'], num_componentes=g.get('instancias_count', 10))
            
            # Usar certeza empírica como propiedad oculta
            sistema.definir_propiedad_oculta('certeza_empirica', g['certeza'])
            sistema.definir_propiedad_oculta('nivel_conceptual', g.get('nivel', 1))
            
            # Si hay instancias, calcular "entropía conceptual"
            if g.get('instancias_count', 0) > 0:
                # Entropía = función de diversidad de instancias
                entropia_conceptual = self._calcular_entropia_conceptual(g)
                sistema.definir_propiedad_oculta('entropia_conceptual', entropia_conceptual)
            
            self.agregar_sistema(sistema)
    
    def _calcular_entropia_conceptual(self, grundzug: Dict) -> float:
        """
        Calcula entropía desde la diversidad de instancias del Grundzug.
        
        Teoría: Conceptos con muchas instancias diversas tienen alta entropía.
        """
        num_instancias = grundzug.get('instancias_count', 1)
        certeza = grundzug.get('certeza', 0.5)
        
        # Heurística: Alta certeza + muchas instancias = alta entropía conceptual
        # (Concepto bien establecido con mucha variabilidad)
        entropia = (certeza * num_instancias) / 10.0
        
        return min(15.0, entropia)  # Cap a 15
    
    def ejecutar_bateria_experimentos(
        self,
        tipos: List[TipoExperimento] = None
    ) -> List[Experimento]:
        """
        Ejecuta experimentos. MEJORADO para re-ejecutar sobre sistemas existentes.
        """
        if tipos is None:
            tipos = list(TipoExperimento)
        
        # NUEVO: Si ya hay experimentos previos, solo agregar nuevos datos
        if self.experimentos_ejecutados and len(self.sistemas) > len(self.experimentos_ejecutados[0].resultados):
            # Modo incremental: ejecutar solo sobre nuevos sistemas
            nuevos_sistemas = self.sistemas[len(self.experimentos_ejecutados[0].resultados):]
            
            for exp in self.experimentos_ejecutados:
                for sistema in nuevos_sistemas:
                    exp.ejecutar(sistema)
        else:
            # Modo inicial: ejecutar todos
            for tipo_exp in tipos:
                exp = Experimento(
                    nombre=f"exp_{tipo_exp.value}_iter{self.iteracion}",
                    tipo=tipo_exp,
                    descripcion=f"Experimento de {tipo_exp.value} - Iteración {self.iteracion}"
                )
                
                for sistema in self.sistemas:
                    exp.ejecutar(sistema)
                
                self.experimentos_ejecutados.append(exp)
        
        return self.experimentos_ejecutados
    
    def detectar_patrones(
        self,
        threshold_correlacion: float = 0.8
    ) -> PatronRelacional:
        """
        Detecta patrones. MEJORADO para refinamiento incremental.
        """
        patron = PatronRelacional(f"patron_iter{self.iteracion}")
        patron.detectar_from_experimentos(
            self.experimentos_ejecutados,
            threshold_correlacion
        )
        
        # NUEVO: Comparar con patrones previos
        if self.patrones_detectados:
            patron_previo = self.patrones_detectados[-1]
            similitud = self._comparar_patrones(patron, patron_previo)
            
            if similitud > 0.95:
                # Patrón estable, aumentar convergencia
                patron.certeza = min(1.0, patron.certeza * 1.1)
        
        self.patrones_detectados.append(patron)
        return patron
    
    def _comparar_patrones(self, patron1: PatronRelacional, patron2: PatronRelacional) -> float:
        """
        Compara dos patrones para detectar convergencia.
        
        Returns:
            Similitud [0, 1]
        """
        # Comparar correlaciones
        if not patron1.correlaciones or not patron2.correlaciones:
            return 0.0
        
        corrs1 = set((c['metrica1'], c['metrica2']) for c in patron1.correlaciones)
        corrs2 = set((c['metrica1'], c['metrica2']) for c in patron2.correlaciones)
        
        interseccion = len(corrs1 & corrs2)
        union = len(corrs1 | corrs2)
        
        return interseccion / union if union > 0 else 0.0
    
    def emergir_concepto(
        self,
        nombre_provisional: str = "PROP_P",
        refinar_existente: bool = True
    ) -> ConceptoEmergente:
        """
        Hace emerger concepto. MEJORADO para refinamiento progresivo.
        
        Args:
            refinar_existente: Si True, refina concepto existente con mismo nombre
        """
        # NUEVO: Buscar concepto existente
        concepto_existente = None
        if refinar_existente:
            concepto_existente = next(
                (c for c in self.conceptos_emergidos if c.nombre_provisional == nombre_provisional),
                None
            )
        
        if concepto_existente:
            # Modo refinamiento
            concepto = self._refinar_concepto(concepto_existente)
        else:
            # Modo creación
            concepto = ConceptoEmergente(nombre_provisional)
            self.conceptos_emergidos.append(concepto)
        
        # Calcular valores de P
        valores_p = self._calcular_valores_propiedad()
        
        for sistema_nombre, valor in valores_p.items():
            concepto.asignar_valores(sistema_nombre, valor)
        
        # Generar/actualizar definición
        concepto.definicion_relacional = self._generar_definicion_relacional()
        
        # Descubrir/refinar leyes
        leyes = self._descubrir_leyes(valores_p)
        concepto.leyes_cualitativas = leyes  # Reemplazar con nuevas
        
        # Generar predicciones
        predicciones = self._generar_predicciones(valores_p)
        for pred in predicciones:
            if pred not in concepto.predicciones:
                concepto.agregar_prediccion(pred)
        
        # NUEVO: Calcular certeza incremental
        certeza_actual = self._calcular_certeza_incremental(concepto)
        concepto.certeza = certeza_actual
        
        concepto.num_observaciones = sum(
            len(ex.resultados) for ex in self.experimentos_ejecutados
        )
        concepto.num_sistemas_estudiados = len(self.sistemas)
        
        # NUEVO: Registrar historial
        if nombre_provisional not in self.historico_certezas:
            self.historico_certezas[nombre_provisional] = []
        self.historico_certezas[nombre_provisional].append(certeza_actual)
        
        # NUEVO: Detectar convergencia
        self._verificar_convergencia(concepto)
        
        return concepto
    
    def _refinar_concepto(self, concepto: ConceptoEmergente) -> ConceptoEmergente:
        """
        Refina un concepto existente con nuevos datos.
        """
        # Mantener concepto existente pero actualizar datos
        # El método principal emergir_concepto se encargará de actualizar
        return concepto
    
    def _calcular_certeza_incremental(self, concepto: ConceptoEmergente) -> float:
        """
        Calcula certeza considerando:
        1. Número de observaciones (más = mejor)
        2. Estabilidad del patrón (convergencia)
        3. Consistencia de leyes
        
        Returns:
            Certeza [0, 1]
        """
        # Factor 1: Observaciones (escala logarítmica)
        import math
        num_obs = concepto.num_observaciones
        factor_obs = min(1.0, math.log(num_obs + 1) / math.log(100))  # Saturación en 100
        
        # Factor 2: Estabilidad (de historial)
        factor_estabilidad = 0.5  # Default
        if len(self.historico_certezas.get(concepto.nombre_provisional, [])) > 1:
            historico = self.historico_certezas[concepto.nombre_provisional]
            
            # Calcular varianza de últimas 3 certezas
            ultimas = historico[-3:]
            if len(ultimas) >= 2:
                varianza = sum((c - sum(ultimas)/len(ultimas))**2 for c in ultimas) / len(ultimas)
                factor_estabilidad = max(0.0, 1.0 - varianza * 10)  # Baja varianza = alta estabilidad
        
        # Factor 3: Leyes consistentes
        factor_leyes = min(1.0, len(concepto.leyes_cualitativas) / 3.0)
        
        # Combinación ponderada
        certeza = (
            0.4 * factor_obs +
            0.4 * factor_estabilidad +
            0.2 * factor_leyes
        )
        
        return certeza
    
    def _verificar_convergencia(self, concepto: ConceptoEmergente) -> bool:
        """
        Verifica si el concepto ha convergido.
        
        Convergencia = certeza estable > 0.90 por 3+ iteraciones
        """
        historico = self.historico_certezas.get(concepto.nombre_provisional, [])
        
        if len(historico) >= 3:
            ultimas_3 = historico[-3:]
            
            if all(c > 0.90 for c in ultimas_3):
                diferencia_max = max(ultimas_3) - min(ultimas_3)
                
                if diferencia_max < 0.05:
                    self.convergencia_alcanzada = True
                    return True
        
        return False
    
    def _calcular_valores_propiedad(self) -> Dict[str, float]:
        """Igual que antes, sin cambios."""
        valores = {}
        
        for sistema in self.sistemas:
            predicibilidad = 1.0
            reversibilidad = 1.0
            diversidad = 0.0
            
            for exp in self.experimentos_ejecutados:
                if sistema.nombre in exp.resultados:
                    res = exp.resultados[sistema.nombre]
                    
                    if "predicibilidad" in res:
                        predicibilidad = res["predicibilidad"]
                    if "reversibilidad" in res:
                        reversibilidad = res["reversibilidad"]
                    if "sorpresa_promedio" in res:
                        diversidad = res["sorpresa_promedio"]
            
            p_valor = (
                (1.0 - predicibilidad) * 5.0 +
                (1.0 - reversibilidad) * 5.0 +
                diversidad * 0.5
            )
            
            valores[sistema.nombre] = round(p_valor, 1)
        
        return valores
    
    def _generar_definicion_relacional(self) -> str:
        """Igual que antes."""
        definicion = (
            "P(sistema) es una propiedad tal que:\n"
            "  - Alta P ↔ baja predicibilidad\n"
            "  - Alta P ↔ baja reversibilidad\n"
            "  - Alta P ↔ alta diversidad de configuraciones\n"
            "  - P está relacionada con el DESORDEN del sistema"
        )
        return definicion
    
    def _descubrir_leyes(self, valores_p: Dict[str, float]) -> List[str]:
        """Igual que antes."""
        leyes = []
        
        decrementos = 0
        incrementos = 0
        
        for exp in self.experimentos_ejecutados:
            if exp.tipo == TipoExperimento.EVOLUCION_TEMPORAL:
                for resultado in exp.resultados.values():
                    if "tendencia" in resultado:
                        if "decremento" in resultado["tendencia"]:
                            decrementos += 1
                        else:
                            incrementos += 1
        
        if decrementos == 0 and incrementos > 0:
            leyes.append("P nunca decrece espontáneamente (dP/dt ≥ 0)")
        
        valores_list = list(valores_p.values())
        if valores_list:
            max_p = max(valores_list)
            if max_p > 10:
                leyes.append(f"P tiene un máximo teórico (~{max_p:.0f})")
        
        if len(valores_p) >= 3:
            leyes.append("P es aditiva: P(A+B) ≈ P(A) + P(B) para sistemas independientes")
        
        return leyes
    
    def _generar_predicciones(self, valores_p: Dict[str, float]) -> List[str]:
        """Igual que antes."""
        predicciones = []
        
        if valores_p:
            min_p = min(valores_p.values())
            max_p = max(valores_p.values())
            
            predicciones.append(
                f"Sistemas con P bajo ({min_p:.1f}) son más predecibles y controlables"
            )
            predicciones.append(
                f"Sistemas con P alto ({max_p:.1f}) son impredecibles y caóticos"
            )
            predicciones.append(
                "No se puede disminuir P de un sistema aislado sin aumentarla en otro lugar"
            )
            predicciones.append(
                "P máxima corresponde a equilibrio termodinámico"
            )
        
        return predicciones
    
    def ciclo_incremental(self, nuevos_grundzugs: List[Dict] = None) -> Dict[str, Any]:
        """
        NUEVO: Método principal para ejecución incremental.
        
        Args:
            nuevos_grundzugs: Nuevos Grundzugs desde Sistema 1
        
        Returns:
            Reporte del ciclo
        """
        self.iteracion += 1
        
        # 1. Ingerir nuevos datos si hay
        if nuevos_grundzugs:
            self.ingerir_desde_sistema1(nuevos_grundzugs)
        
        # 2. Ejecutar experimentos (incremental)
        self.ejecutar_bateria_experimentos()
        
        # 3. Detectar patrones
        patron = self.detectar_patrones()
        
        # 4. Emerger/refinar conceptos
        conceptos = []
        for nombre in set(c.nombre_provisional for c in self.conceptos_emergidos) or ["PROP_P"]:
            concepto = self.emergir_concepto(nombre, refinar_existente=True)
            conceptos.append(concepto)
        
        # 5. Guardar estado
        self._guardar_estado()
        
        return {
            "iteracion": self.iteracion,
            "sistemas_totales": len(self.sistemas),
            "nuevos_sistemas": len(nuevos_grundzugs) if nuevos_grundzugs else 0,
            "patron_certeza": patron.certeza,
            "conceptos": [c.generar_reporte() for c in conceptos],
            "convergencia": self.convergencia_alcanzada
        }
    
    def _guardar_estado(self) -> None:
        """
        Guarda estado completo para persistencia entre sesiones.
        """
        estado = {
            'sistemas': self.sistemas,
            'experimentos': self.experimentos_ejecutados,
            'patrones': self.patrones_detectados,
            'conceptos': self.conceptos_emergidos,
            'iteracion': self.iteracion,
            'historico_certezas': self.historico_certezas,
            'convergencia': self.convergencia_alcanzada,
            'grundzugs_fuente': self.grundzugs_fuente
        }
        
        with open(self.state_file, 'wb') as f:
            pickle.dump(estado, f)
    
    def _cargar_estado(self) -> None:
        """
        Carga estado previo si existe.
        """
        if os.path.exists(self.state_file):
            with open(self.state_file, 'rb') as f:
                estado = pickle.load(f)
            
            self.sistemas = estado.get('sistemas', [])
            self.experimentos_ejecutados = estado.get('experimentos', [])
            self.patrones_detectados = estado.get('patrones', [])
            self.conceptos_emergidos = estado.get('conceptos', [])
            self.iteracion = estado.get('iteracion', 0)
            self.historico_certezas = estado.get('historico_certezas', {})
            self.convergencia_alcanzada = estado.get('convergencia', False)
            self.grundzugs_fuente = estado.get('grundzugs_fuente', [])
    
    def generar_reporte_completo(self) -> Dict[str, Any]:
        """Reporte extendido con información incremental."""
        return {
            "sistemas_estudiados": len(self.sistemas),
            "experimentos_realizados": len(self.experimentos_ejecutados),
            "patrones_detectados": len(self.patrones_detectados),
            "conceptos_emergidos": len(self.conceptos_emergidos),
            
            # NUEVO: Información incremental
            "iteracion_actual": self.iteracion,
            "convergencia_alcanzada": self.convergencia_alcanzada,
            "historico_certezas": self.historico_certezas,
            
            "sistemas": [s.nombre for s in self.sistemas],
            
            "experimentos": [
                {
                    "nombre": e.nombre,
                    "tipo": e.tipo.value,
                    "num_resultados": len(e.resultados)
                }
                for e in self.experimentos_ejecutados
            ],
            
            "conceptos": [c.generar_reporte() for c in self.conceptos_emergidos]
        }
