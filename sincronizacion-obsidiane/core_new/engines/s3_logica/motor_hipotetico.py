"""
Motor Hipotético - VERSIÓN INCREMENTAL
=======================================

Mejoras:
1. Expansión progresiva de mundos
2. Refinamiento de axiomas basado en observaciones
3. Integración con conocimiento empírico
4. Validación cruzada con Sistema 1
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import pickle
import os

from .mundo_hipotetico import MundoHipotetico
from .instancia_abstracta import InstanciaAbstracta

# Importar FCAProcessor del sistema principal si existe
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from procesadores.fca_processor import FCAProcessor
except ImportError:
    # Mock simple si no está disponible
    class FCAProcessor:
        def generate_concepts(self, objetos, atributos, relacion):
            return []


class MotorHipotetico:
    """
    Motor que procesa mundos hipotéticos con aprendizaje incremental.
    
    MEJORAS:
    - Expansión progresiva de mundos
    - Aprendizaje de axiomas desde observaciones empíricas
    - Vvalidación cruzada con Sistema 1
    - Persistencia de estado
    """
    
    def __init__(self, state_file: str = "estado_logica_pura.pkl"):
        self.mundos = {}
        self.fca = FCAProcessor()
        
        # NUEVO: Estado incremental
        self.state_file = state_file
        self.iteracion = 0
        self.axiomas_aprendidos = []  # Axiomas descubiertos desde datos
        self.validaciones_empiricas = []  # Validaciones con S1
        
        # NUEVO: Conexión con Sistema 1
        self.grundzugs_referencia = {}  # {nombre: grundzug_dict}
        
        # Cargar estado previo
        self._cargar_estado()
        
    def ingestar_mundo(self, mundo: MundoHipotetico) -> Dict[str, Any]:
        """
        Procesa un mundo hipotético completo.
        """
        self.mundos[mundo.nombre] = mundo
        
        # 1. Generar instancias
        instancias = mundo.instanciar()
        
        # 2. Extraer conceptos mediante FCA
        conceptos_formales = self._aplicar_fca(instancias)
        
        return {
            "mundo": mundo.nombre,
            "num_instancias": len(instancias),
            "conceptos_generados": conceptos_formales,
            "instancias": [i.to_dict() for i in instancias]
        }
    
    def expandir_mundo_desde_grundzugs(
        self,
        mundo_base: MundoHipotetico,
        grundzugs: List[Dict[str, Any]]
    ) -> MundoHipotetico:
        """
        NUEVO: Expande un mundo con conocimiento del Sistema 1.
        
        Args:
            mundo_base: Mundo existente
            grund zugs: Grundzugs empíricos del S1
        
        Returns:
            Mundo expandido con nuevos objetos y relaciones inferidas
        """
        self.grundzugs_referencia.update({g['nombre']: g for g in grundzugs})
        
        for grund in grundzugs:
            # Agregar como objeto al mundo si no existe
            if grund['nombre'] not in mundo_base.objetos_def:
                # Extraer propiedades simbólicas desde qualia
                props_simbolicas = self._grundzug_to_props_simbolicas(grund)
                mundo_base.agregar_objeto(grund['nombre'], props_simbolicas)
        
        # NUEVO: Inferir relaciones entre Grundzugs
        relaciones_inferidas = self._inferir_relaciones_empiricas(grundzugs)
        for rel in relaciones_inferidas:
            try:
                mundo_base.agregar_relacion(rel['sujeto'], rel['tipo'], rel['objeto'])
            except ValueError:
                pass  # Objetos no existen, ignorar
        
        return mundo_base
    
    def _grundzug_to_props_simbolicas(self, grundzug: Dict) -> Dict[str, Any]:
        """
        Convierte Grundzug empírico a propiedades lógicas simbólicas.
        
        Estrategia:
        - Certeza alta → propiedad "establecido"
        - Nivel alto → propiedad "abstracto"
        - Tipo de qualia → propiedades específicas
        """
        props = {}
        
        # Certeza
        certeza = grundzug.get('certeza', 0.5)
        if certeza > 0.9:
            props['bien_establecido'] = True
        elif certeza > 0.7:
            props['parcialmente_establecido'] = True
        else:
            props['hipotetico'] = True
        
        # Nivel conceptual
        nivel = grundzug.get('nivel', 1)
        if nivel >= 3:
            props['meta_concepto'] = True
        elif nivel == 2:
            props['concepto_medio'] = True
        else:
            props['concepto_basico'] = True
        
        # Qualia dominante (si existe)
        qualia_dom = grundzug.get('qualia_dominante', None)
        if qualia_dom:
            props[f'origen_{qualia_dom}'] = True
        
        return props
    
    def _inferir_relaciones_empiricas(self, grundzugs: List[Dict]) -> List[Dict]:
        """
        Infiere relaciones lógicas desde co-ocurrencias empíricas.
        
        Ejemplo:
          Si "lluvia" y "agua" co-ocurren frecuentemente
          → Inferir relación "lluvia es_forma_de agua"
        """
        relaciones = []
        
        # Estrategia simple: buscar inclusiones jerárquicas
        for i, g1 in enumerate(grundzugs):
            for g2 in grundzugs[i+1:]:
                # Si g1 tiene nivel menor que g2, posible "es_tipo_de"
                if g1.get('nivel', 1) < g2.get('nivel', 1):
                    relaciones.append({
                        'sujeto': g1['nombre'],
                        'tipo': 'es_tipo_de',
                        'objeto': g2['nombre']
                    })
                
                # Si ambos tienen alta certeza y mismo tipo qualia, posible "similar_a"
                if (g1.get('certeza', 0) > 0.8 and 
                    g2.get('certeza', 0) > 0.8 and
                    g1.get('qualia_dominante') == g2.get('qualia_dominante')):
                    relaciones.append({
                        'sujeto': g1['nombre'],
                        'tipo': 'similar_a',
                        'objeto': g2['nombre']
                    })
        
        return relaciones
    
    def aprender_axiomas_desde_observaciones(
        self,
        mundo: MundoHipotetico,
        observaciones_empiricas: List[Dict]
    ) -> List[str]:
        """
        NUEVO: Descubre axiomas desde observaciones empíricas.
        
        Args:
            observaciones: Lista de hechos empíricos
                          [{sujeto, predicado, objeto, certeza}, ...]
        
        Returns:
            Lista de axiomas descubiertos en forma "P → Q"
        
        Ejemplo:
          Observaciones: {"lluvia", "es_liquido"} con certeza 0.95
          Axioma: "∀x (lluvia(x) → liquido(x))"
        """
        axiomas_nuevos = []
        
        # Agrupar observaciones por sujeto
        por_sujeto = {}
        for obs in observaciones_empiricas:
            suj = obs.get('sujeto')
            if suj not in por_sujeto:
                por_sujeto[suj] = []
            por_sujeto[suj].append(obs)
        
        # Buscar patrones comunes
        for sujeto, obs_list in por_sujeto.items():
            # Si TODAS las observaciones de un sujeto tienen cierta propiedad
            propiedades_comunes = set(obs['predicado'] for obs in obs_list)
            
            for prop in propiedades_comunes:
                # Contar cuántas veces aparece
                count = sum(1 for o in obs_list if o['predicado'] == prop)
                certeza_prom = sum(o.get('certeza', 1.0) for o in obs_list if o['predicado'] == prop) / count
                
                if count >= 3 and certeza_prom > 0.85:
                    # Axioma: sujeto implica propiedad
                    axioma = f"{sujeto} → {prop}"
                    
                    if axioma not in self.axiomas_aprendidos:
                        axiomas_nuevos.append(axioma)
                        self.axiomas_aprendidos.append(axioma)
                        
                        # Agregar al mundo
                        mundo.agregar_axioma(axioma)
        
        return axiomas_nuevos
    
    def validar_con_sistema1(
        self,
        instancias_abstractas: List[InstanciaAbstracta],
        grundzugs_s1: List[Dict]
    ) -> Dict[str, Any]:
        """
        NUEVO: Valida instancias lógicas con conocimiento empírico del S1.
        
        Returns:
            {
                'consistentes': [...],
                'inconsistentes': [...],
                'certeza_validacion': float
            }
        """
        consistentes = []
        inconsistentes = []
        
        # Crear mapa de grundzugs por nombre
        grund_map = {g['nombre']: g for g in grundzugs_s1}
        
        for inst in instancias_abstractas:
            if inst.concepto in grund_map:
                grund = grund_map[inst.concepto]
                
                # Comparar propiedades lógicas vs empíricas
                props_logicas = inst.propiedades
                props_empiricas = self._grundzug_to_props_simbolicas(grund)
                
                # Verificar consistencia
                conflictos = []
                for prop_log, val_log in props_logicas.items():
                    if prop_log in props_empiricas:
                        if props_empiricas[prop_log] != val_log:
                            conflictos.append(prop_log)
                
                if conflictos:
                    inconsistentes.append({
                        'concepto': inst.concepto,
                        'conflictos': conflictos
                    })
                else:
                    consistentes.append(inst.concepto)
        
        certeza = len(consistentes) / len(instancias_abstractas) if instancias_abstractas else 1.0
        
        validacion = {
            'consistentes': consistentes,
            'inconsistentes': inconsistentes,
            'certeza_validacion': certeza,
            'timestamp': datetime.now().isoformat()
        }
        
        self.validaciones_empiricas.append(validacion)
        
        return validacion
    
    def ciclo_incremental(
        self,
        mundo_nombre: str,
        nuevos_grundzugs: List[Dict] = None,
        observaciones: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        NUEVO: Método principal para ejecución incremental.
        
        Args:
            mundo_nombre: Nombre del mundo a procesar/expandir
            nuevos_grundzugs: Nuevos Grundzugs desde Sistema 1
            observaciones: Observaciones empíricas para aprender axiomas
        
        Returns:
            Reporte del ciclo
        """
        self.iteracion += 1
        
        # 1. Obtener o crear mundo
        if mundo_nombre in self.mundos:
            mundo = self.mundos[mundo_nombre]
        else:
            mundo = MundoHipotetico(mundo_nombre)
            self.mundos[mundo_nombre] = mundo
        
        # 2. Expandir con nuevos grundzugs
        if nuevos_grundzugs:
            mundo = self.expandir_mundo_desde_grundzugs(mundo, nuevos_grundzugs)
        
        # 3. Aprender axiomas desde observaciones
        axiomas_nuevos = []
        if observaciones:
            axiomas_nuevos = self.aprender_axiomas_desde_observaciones(mundo, observaciones)
        
        # 4. Procesar mundo
        resultado = self.ingestar_mundo(mundo)
        
        # 5. Validar con S1
        validacion = None
        if nuevos_grundzugs:
            instancias = [InstanciaAbstracta(
                concepto=i['concepto'],
                propiedades=i['propiedades'],
                mundo_origen=mundo_nombre
            ) for i in resultado['instancias'] if not i['propiedades'].get('es_relacion')]
            
            validacion = self.validar_con_sistema1(instancias, nuevos_grundzugs)
        
        # 6. Guardar estado
        self._guardar_estado()
        
        return {
            'iteracion': self.iteracion,
            'mundo': mundo_nombre,
            'objetos_totales': len(mundo.objetos_def),
            'axiomas_totales': len(mundo.motor_axiomas.axiomas),
            'axiomas_nuevos_aprendidos': len(axiomas_nuevos),
            'conceptos_formales': resultado['conceptos_generados'],
            'validacion': validacion,
            'resultado_completo': resultado
        }
    
    def _aplicar_fca(self, instancias: List[InstanciaAbstracta]) -> List[Dict]:
        """Igual que antes, sin cambios."""
        objetos = [inst.concepto for inst in instancias]
        
        atributos = set()
        for inst in instancias:
            for k, v in inst.propiedades.items():
                if v is True:
                    atributos.add(k)
                elif isinstance(v, str):
                    atributos.add(f"{k}:{v}")
                    
        atributos = list(atributos)
        
        relacion = []
        for inst in instancias:
            for attr in atributos:
                tiene = False
                if ":" in attr:
                    k, v = attr.split(":", 1)
                    if str(inst.propiedades.get(k)) == v:
                        tiene = True
                else:
                    if inst.propiedades.get(attr) is True:
                        tiene = True
                
                if tiene:
                    relacion.append((inst.concepto, attr))
        
        # FCA simple
        conceptos = []
        
        attr_counts = {}
        for obj, attr in relacion:
            attr_counts[attr] = attr_counts.get(attr, 0) + 1
            
        attrs_compartidos = [a for a, c in attr_counts.items() if c > 1]
        
        for attr in attrs_compartidos:
            extension = [obj for obj, a in relacion if a == attr]
            conceptos.append({
                "nombre": f"GRUPO_{attr.upper()}",
                "intension": [attr],
                "extension": extension,
                "certeza": 1.0,
                "tipo": "abstracto"
            })
            
        return conceptos
    
    def _guardar_estado(self) -> None:
        """Guarda estado completo."""
        estado = {
            'mundos': self.mundos,
            'iteracion': self.iteracion,
            'axiomas_aprendidos': self.axiomas_aprendidos,
            'validaciones': self.validaciones_empiricas,
            'grundzugs_ref': self.grundzugs_referencia
        }
        
        with open(self.state_file, 'wb') as f:
            pickle.dump(estado, f)
    
    def _cargar_estado(self) -> None:
        """Carga estado previo si existe."""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'rb') as f:
                estado = pickle.load(f)
            
            self.mundos = estado.get('mundos', {})
            self.iteracion = estado.get('iteracion', 0)
            self.axiomas_aprendidos = estado.get('axiomas_aprendidos', [])
            self.validaciones_empiricas = estado.get('validaciones', [])
            self.grundzugs_referencia = estado.get('grundzugs_ref', {})
    
    def generar_reporte_completo(self) -> Dict[str, Any]:
        """Reporte extendido."""
        return {
            'num_mundos': len(self.mundos),
            'iteracion_actual': self.iteracion,
            'axiomas_aprendidos': len(self.axiomas_aprendidos),
            'validaciones_realizadas': len(self.validaciones_empiricas),
            
            'mundos': {
                nombre: {
                    'objetos': len(m.objetos_def),
                    'relaciones': len(m.relaciones_def),
                    'axiomas': len(m.motor_axiomas.axiomas)
                }
                for nombre, m in self.mundos.items()
            },
            
            'certeza_validacion_promedio': (
                sum(v['certeza_validacion'] for v in self.validaciones_empiricas) / 
                len(self.validaciones_empiricas)
            ) if self.validaciones_empiricas else 0.0
        }
