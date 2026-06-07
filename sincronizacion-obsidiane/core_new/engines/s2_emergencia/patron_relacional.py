"""
Patrón Relacional - Emergencia de Conceptos
============================================

Detecta patrones en los comportamientos observados de sistemas
para inferir propiedades ocultas.
"""

from typing import Dict, List, Any
from sklearn.cluster import DBSCAN
import numpy as np


class PatronRelacional:
    """
    Representa un patrón detectado en las relaciones entre sistemas.
    """
    
    def __init__(self, nombre: str = "patron_sin_nombre"):
        self.nombre = nombre
        self.sistemas_con_patron = []
        self.sistemas_sin_patron = []
        self.caracteristicas = {}
        self.correlaciones = []
        self.certeza = 0.0
        
    def detectar_from_experimentos(
        self,
        experimentos: List,
        threshold_correlacion: float = 0.8
    ):
        """
        Detecta patrones a partir de resultados de experimentos.
        
        Args:
            experimentos: Lista de objetos Experimento ejecutados
            threshold_correlacion: Umbral para considerar correlación
            
        Returns:
            Self para permitir method chaining
        """
        # Recolectar todos los resultados
        todos_resultados = {}
        
        for exp in experimentos:
            for sistema_nombre, resultado in exp.resultados.items():
                if sistema_nombre not in todos_resultados:
                    todos_resultados[sistema_nombre] = {}
                
                # Guardar resultados por tipo de experimento
                todos_resultados[sistema_nombre][exp.tipo.value] = resultado
        
        # Detectar correlaciones entre métricas
        self._analizar_correlaciones(todos_resultados, threshold_correlacion)
        
        return self
    
    def _analizar_correlaciones(
        self,
        resultados: Dict[str, Dict],
        threshold: float
    ):
        """
        Analiza correlaciones entre diferentes métricas experimentales.
        """
        # Extraer métricas numéricas
        metricas = {}
        sistemas = list(resultados.keys())
        
        for sistema in sistemas:
            metricas[sistema] = {}
            for tipo_exp, datos in resultados[sistema].items():
                for clave, valor in datos.items():
                    if isinstance(valor, (int, float)):
                        nombre_metrica = f"{tipo_exp}_{clave}"
                        metricas[sistema][nombre_metrica] = valor
        
        # Calcular correlaciones
        nombres_metricas = set()
        for sistema_metrics in metricas.values():
            nombres_metricas.update(sistema_metrics.keys())
        
        nombres_metricas = list(nombres_metricas)
        
        # Matriz de correlación
        for i, metrica1 in enumerate(nombres_metricas):
            for metrica2 in nombres_metricas[i+1:]:
                valores1 = []
                valores2 = []
                
                for sistema in sistemas:
                    if metrica1 in metricas[sistema] and metrica2 in metricas[sistema]:
                        valores1.append(metricas[sistema][metrica1])
                        valores2.append(metricas[sistema][metrica2])
                
                if len(valores1) >= 3:  # Mínimo 3 puntos
                    corr = np.corrcoef(valores1, valores2)[0, 1]
                    
                    if abs(corr) > threshold:
                        self.correlaciones.append({
                            "metrica1": metrica1,
                            "metrica2": metrica2,
                            "correlacion": round(float(corr), 3)
                        })
        
        # Calcular certeza basada en número de correlaciones
        self.certeza = min(1.0, len(self.correlaciones) / 5.0)
    
    def cluster_sistemas(
        self,
        experimentos: List,
        eps: float = 0.5,
        min_samples: int = 2
    ) -> Dict[str, List[str]]:
        """
        Agrupa sistemas con comportamientos similares usando DBSCAN.
        
        Returns:
            Diccionario con clusters detectados
        """
        # Extraer features para clustering
        sistemas = []
        features = []
        
        if not experimentos or not experimentos[0].resultados:
            return {"cluster_0": []}
        
        for exp in experimentos:
            for sistema_nombre, resultado in exp.resultados.items():
                if sistema_nombre not in sistemas:
                    sistemas.append(sistema_nombre)
                    
                    # Extraer valores numéricos
                    feat = []
                    for valor in resultado.values():
                        if isinstance(valor, (int, float)):
                            feat.append(valor)
                    
                    if feat:
                        features.append(feat)
        
        if not features or len(features) < min_samples:
            return {"cluster_0": sistemas}
        
        # Normalizar features
        features_array = np.array(features)
        features_norm = (features_array - features_array.min(axis=0)) / (features_array.max(axis=0) - features_array.min(axis=0) + 1e-10)
        
        # Clustering
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(features_norm)
        
        # Organizar por clusters
        clusters = {}
        for idx, label in enumerate(clustering.labels_):
            cluster_name = f"cluster_{label}"
            if cluster_name not in clusters:
                clusters[cluster_name] = []
            clusters[cluster_name].append(sistemas[idx])
        
        return clusters
    
    def generar_hipotesis(self) -> str:
        """
        Genera una hipótesis sobre la propiedad que causa el patrón.
        
        Returns:
            Texto descriptivo de la hipótesis
        """
        if not self.correlaciones:
            return "Insuficientes datos para generar hipótesis"
        
        # Analizar correlaciones
        predicibilidad_correlaciones = [
            c for c in self.correlaciones
            if "predicibilidad" in c["metrica1"] or "predicibilidad" in c["metrica2"]
        ]
        
        reversibilidad_correlaciones = [
            c for c in self.correlaciones
            if "reversibilidad" in c["metrica1"] or "reversibilidad" in c["metrica2"]
        ]
        
        diversidad_correlaciones = [
            c for c in self.correlaciones
            if "diversidad" in c["metrica1"] or "configuraciones" in c["metrica1"]
        ]
        
        hipotesis = "Existe una propiedad P del sistema tal que:\n"
        
        if predicibilidad_correlaciones:
            hipotesis += "  - Alta P correlaciona con baja predicibilidad\n"
        
        if reversibilidad_correlaciones:
            hipotesis += "  - Alta P correlaciona con baja reversibilidad\n"
        
        if diversidad_correlaciones:
            hipotesis += "  - Alta P correlaciona con alta diversidad de configuraciones\n"
        
        hipotesis += "\nInterpretación: P parece medir el DESORDEN o ALEATORIEDAD del sistema."
        
        return hipotesis
    
    def __repr__(self):
        return f"PatronRelacional('{self.nombre}', correlaciones={len(self.correlaciones)}, certeza={self.certeza:.2f})"
