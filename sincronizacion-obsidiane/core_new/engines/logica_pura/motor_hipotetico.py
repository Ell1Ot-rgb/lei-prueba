"""
Motor Hipotético - VERSIÓN HEXAGONAL
Integra aprendizaje FCA y escenarios contingentes (Mundos).
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import pickle
import os

from .mundo_hipotetico import MundoHipotetico
from .instancia_abstracta import InstanciaAbstracta

class MotorHipotetico:
    def __init__(self, state_file: str = "estado_logica_pura.pkl"):
        self.mundos = {}
        self.state_file = state_file
        self.iteracion = 0
        self.axiomas_aprendidos = []  
        self.validaciones_empiricas = []  
        self.grundzugs_referencia = {}  
        self._cargar_estado()
        
    def ingestar_mundo(self, mundo: MundoHipotetico) -> Dict[str, Any]:
        self.mundos[mundo.nombre] = mundo
        instancias = mundo.instanciar()
        conceptos_formales = self._aplicar_fca(instancias)
        
        return {
            "mundo": mundo.nombre,
            "num_instancias": len(instancias),
            "conceptos_generados": conceptos_formales,
            "instancias": [i.to_dict() for i in instancias]
        }
    
    def expandir_mundo_desde_grundzugs(self, mundo_base: MundoHipotetico, grundzugs: List[Dict[str, Any]]) -> MundoHipotetico:
        self.grundzugs_referencia.update({g.get('nombre', 'unknown'): g for g in grundzugs})
        
        for grund in grundzugs:
            nombre = grund.get('nombre', f"g_{len(self.grundzugs_referencia)}")
            if nombre not in mundo_base.objetos_def:
                props_simbolicas = self._grundzug_to_props_simbolicas(grund)
                mundo_base.agregar_objeto(nombre, props_simbolicas)
        
        relaciones_inferidas = self._inferir_relaciones_empiricas(grundzugs)
        for rel in relaciones_inferidas:
            try:
                mundo_base.agregar_relacion(rel['sujeto'], rel['tipo'], rel['objeto'])
            except ValueError:
                pass
        
        return mundo_base
    
    def _grundzug_to_props_simbolicas(self, grundzug: Dict) -> Dict[str, Any]:
        props = {}
        certeza = grundzug.get('certeza', 0.5)
        if certeza > 0.9: props['bien_establecido'] = True
        elif certeza > 0.7: props['parcialmente_establecido'] = True
        else: props['hipotetico'] = True
        
        nivel = grundzug.get('nivel', 1)
        if nivel >= 3: props['meta_concepto'] = True
        elif nivel == 2: props['concepto_medio'] = True
        else: props['concepto_basico'] = True
        
        qualia_dom = grundzug.get('qualia_dominante')
        if qualia_dom: props[f'origen_{qualia_dom}'] = True
        return props
    
    def _inferir_relaciones_empiricas(self, grundzugs: List[Dict]) -> List[Dict]:
        relaciones = []
        for i, g1 in enumerate(grundzugs):
            for g2 in grundzugs[i+1:]:
                n1, n2 = g1.get('nombre'), g2.get('nombre')
                if not n1 or not n2: continue
                
                if g1.get('nivel', 1) < g2.get('nivel', 1):
                    relaciones.append({'sujeto': n1, 'tipo': 'es_tipo_de', 'objeto': n2})
                if (g1.get('certeza', 0) > 0.8 and g2.get('certeza', 0) > 0.8 and
                    g1.get('qualia_dominante') == g2.get('qualia_dominante') and g1.get('qualia_dominante')):
                    relaciones.append({'sujeto': n1, 'tipo': 'similar_a', 'objeto': n2})
        return relaciones
    
    def _aplicar_fca(self, instancias: List[InstanciaAbstracta]) -> List[Dict]:
        conceptos = []
        atributos = set()
        for inst in instancias:
            for k, v in inst.propiedades.items():
                if v is True: atributos.add(k)
                elif isinstance(v, str): atributos.add(f"{k}:{v}")
                    
        atributos = list(atributos)
        relacion = []
        attr_counts = {}
        
        for inst in instancias:
            for attr in atributos:
                tiene = False
                if ":" in attr:
                    k, v = attr.split(":", 1)
                    if str(inst.propiedades.get(k)) == v: tiene = True
                else:
                    if inst.propiedades.get(attr) is True: tiene = True
                
                if tiene:
                    relacion.append((inst.concepto, attr))
                    attr_counts[attr] = attr_counts.get(attr, 0) + 1
        
        attrs_compartidos = [a for a, c in attr_counts.items() if c > 1]
        for attr in attrs_compartidos:
            extension = [obj for obj, a in relacion if a == attr]
            conceptos.append({
                "nombre": f"GRUPO_{attr.upper().replace(':','_')}",
                "intension": [attr],
                "extension": extension,
                "certeza": 1.0,
                "tipo": "abstracto"
            })
        return conceptos
    
    def _guardar_estado(self) -> None:
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
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'rb') as f:
                    estado = pickle.load(f)
                self.mundos = estado.get('mundos', {})
                self.iteracion = estado.get('iteracion', 0)
                self.axiomas_aprendidos = estado.get('axiomas_aprendidos', [])
                self.validaciones_empiricas = estado.get('validaciones', [])
                self.grundzugs_referencia = estado.get('grundzugs_ref', {})
            except Exception:
                # Archivo corrupto o incompatible: comenzar desde cero
                self.mundos = {}
                self.iteracion = 0
                self.axiomas_aprendidos = []
                self.validaciones_empiricas = []
                self.grundzugs_referencia = {}
