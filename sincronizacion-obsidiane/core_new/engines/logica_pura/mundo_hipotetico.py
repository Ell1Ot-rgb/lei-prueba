"""
Mundo Hipotético - Lógica Pura
"""
from typing import Dict, List, Any
from .instancia_abstracta import InstanciaAbstracta
from .motor_axiomas import MotorAxiomas

class ObjetoDefinicion:
    def __init__(self, nombre: str, propiedades: Dict[str, Any]):
        self.nombre = nombre
        self.propiedades = propiedades

class RelacionDefinicion:
    def __init__(self, sujeto: str, predicado: str, objeto: str):
        self.sujeto = sujeto
        self.predicado = predicado
        self.objeto = objeto

class MundoHipotetico:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.objetos_def = {}
        self.relaciones_def = []
        self.motor_axiomas = MotorAxiomas()
        
    def agregar_objeto(self, nombre: str, propiedades: Dict[str, Any]):
        self.objetos_def[nombre] = ObjetoDefinicion(nombre, propiedades)
        
    def agregar_relacion(self, obj1: str, tipo_rel: str, obj2: str):
        if obj1 not in self.objetos_def or obj2 not in self.objetos_def:
            raise ValueError(f"Objetos no existen: {obj1}, {obj2}")
        self.relaciones_def.append(RelacionDefinicion(obj1, tipo_rel, obj2))
        
    def agregar_axioma(self, regla: str):
        self.motor_axiomas.agregar_axioma(regla)
    
    def instanciar(self) -> List[InstanciaAbstracta]:
        instancias = []
        mapa_instancias = {}
        
        for nombre, obj_def in self.objetos_def.items():
            inst = InstanciaAbstracta(
                concepto=nombre,
                propiedades=obj_def.propiedades.copy(),
                mundo_origen=self.nombre
            )
            instancias.append(inst)
            mapa_instancias[nombre] = inst
            
        for rel in self.relaciones_def:
            sujeto = mapa_instancias[rel.sujeto]
            objeto = mapa_instancias[rel.objeto]
            sujeto.agregar_relacion(rel.predicado, objeto.id)
            
            nombre_rel = f"{rel.sujeto}_{rel.predicado}_{rel.objeto}"
            props_rel = {
                "tipo_relacion": rel.predicado,
                "sujeto": rel.sujeto,
                "objeto": rel.objeto,
                "es_relacion": True
            }
            inst_rel = InstanciaAbstracta(
                concepto=nombre_rel,
                propiedades=props_rel,
                mundo_origen=self.nombre
            )
            instancias.append(inst_rel)
            
        for inst in instancias:
            nuevas_props = self.motor_axiomas.inferir_propiedades(inst)
            inst.propiedades.update(nuevas_props)
            
        return instancias
