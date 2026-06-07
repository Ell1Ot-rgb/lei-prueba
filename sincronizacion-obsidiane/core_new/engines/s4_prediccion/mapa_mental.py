"""
Mapa Mental Interno (Mental Map)
================================

Crea un "mapa" interno del entorno a partir de los datos brutos
de las dendritas. Como una imagen mental o recuerdo del mundo.

Simple y ligero - no usa frameworks pesados.
"""

import numpy as np
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque
import json


@dataclass
class Punto:
    """Un punto en el mapa mental."""
    x: float              # Posición en eje energía
    y: float              # Posición en eje entropía
    intensidad: float     # Qué tan "fuerte" es
    tipo: str             # Concepto asociado
    timestamp: float      # Cuándo se creó
    decaimiento: float = 1.0  # Se desvanece con el tiempo


@dataclass
class Zona:
    """Una zona del mapa (cluster de puntos similares)."""
    centro_x: float
    centro_y: float
    radio: float
    nombre: str
    puntos: List[int] = field(default_factory=list)  # IDs de puntos
    color: str = "#888888"


@dataclass  
class Conexion:
    """Conexión entre dos puntos (asociación)."""
    origen: int
    destino: int
    fuerza: float
    tipo: str  # "temporal", "conceptual", "causal"


class MapaMental:
    """
    Mapa interno del entorno construido desde datos de dendritas.
    
    Imagina un espacio 2D donde:
    - Eje X = Energía (actividad)
    - Eje Y = Entropía (complejidad/caos)
    
    Los puntos aparecen cuando llegan datos,
    se conectan si son similares,
    y se desvanecen con el tiempo (como recuerdos).
    """
    
    def __init__(self, 
                 max_puntos: int = 500,
                 decay_rate: float = 0.995,
                 umbral_conexion: float = 0.3):
        
        self.max_puntos = max_puntos
        self.decay_rate = decay_rate
        self.umbral_conexion = umbral_conexion
        
        # Estado del mapa
        self.puntos: Dict[int, Punto] = {}
        self.conexiones: List[Conexion] = []
        self.zonas: Dict[str, Zona] = {}
        
        # Contador de IDs
        self.next_id = 0
        
        # Historial para detectar patrones
        self.historial_reciente = deque(maxlen=50)
        
        # Calibración (rangos observados)
        self.rango_energia = [0, 10000]  # µJ
        self.rango_entropia = [0, 4e9]   # Shannon
        
        # Estadísticas
        self.total_percepciones = 0
        
        # Zonas predefinidas del mapa
        self._inicializar_zonas()
    
    def _inicializar_zonas(self):
        """Define las zonas del mapa mental."""
        self.zonas = {
            "caos": Zona(0.8, 0.8, 0.2, "CAOS", color="#ff4444"),
            "orden": Zona(0.2, 0.2, 0.2, "ORDEN", color="#4444ff"),
            "tecnico": Zona(0.5, 0.3, 0.15, "TÉCNICO", color="#44ff44"),
            "poetico": Zona(0.3, 0.7, 0.15, "POÉTICO", color="#ff44ff"),
            "numerico": Zona(0.7, 0.4, 0.15, "NUMÉRICO", color="#ffff44"),
            "borde": Zona(0.5, 0.5, 0.1, "BORDE_CAOS", color="#ffffff"),
        }
    
    def percibir(self, 
                 energia: float, 
                 entropia: float, 
                 concepto: str,
                 confianza: float = 1.0) -> int:
        """
        Recibe datos de una dendrita y crea un punto en el mapa.
        
        Args:
            energia: Energía medida (µJ)
            entropia: Entropía Shannon
            concepto: Tipo de concepto (TÉCNICO, POÉTICO, etc.)
            confianza: Qué tan confiable es el dato
        
        Returns:
            ID del punto creado
        """
        # Normalizar a [0, 1]
        x = self._normalizar(energia, self.rango_energia)
        y = self._normalizar(entropia, self.rango_entropia)
        
        # Actualizar rangos si es necesario
        self._actualizar_rangos(energia, entropia)
        
        # Crear punto
        punto = Punto(
            x=x,
            y=y,
            intensidad=confianza,
            tipo=concepto,
            timestamp=time.time(),
            decaimiento=1.0
        )
        
        # Agregar al mapa
        punto_id = self.next_id
        self.puntos[punto_id] = punto
        self.next_id += 1
        
        # Agregar a zona correspondiente
        self._asignar_a_zona(punto_id, punto)
        
        # Crear conexiones con puntos cercanos
        self._crear_conexiones(punto_id, punto)
        
        # Registrar en historial
        self.historial_reciente.append({
            'id': punto_id,
            'x': x,
            'y': y,
            'tipo': concepto,
            't': time.time()
        })
        
        self.total_percepciones += 1
        
        # Limpiar puntos antiguos si hay demasiados
        if len(self.puntos) > self.max_puntos:
            self._limpiar_puntos_debiles()
        
        return punto_id
    
    def tick(self):
        """
        Actualiza el mapa (decaimiento de puntos).
        Llamar periódicamente.
        """
        puntos_a_eliminar = []
        
        for pid, punto in self.puntos.items():
            # Aplicar decaimiento
            punto.decaimiento *= self.decay_rate
            
            # Marcar para eliminar si muy débil
            if punto.decaimiento < 0.1:
                puntos_a_eliminar.append(pid)
        
        # Eliminar puntos débiles
        for pid in puntos_a_eliminar:
            self._eliminar_punto(pid)
    
    def get_vista(self) -> Dict:
        """
        Retorna una vista del mapa mental actual.
        Útil para visualización o para que la IA "vea" su mapa.
        """
        # Calcular centro de masa
        if self.puntos:
            centro_x = np.mean([p.x for p in self.puntos.values()])
            centro_y = np.mean([p.y for p in self.puntos.values()])
        else:
            centro_x, centro_y = 0.5, 0.5
        
        # Zona dominante
        zona_dominante = self._zona_con_mas_puntos()
        
        # Puntos más recientes
        recientes = sorted(
            self.puntos.items(),
            key=lambda x: x[1].timestamp,
            reverse=True
        )[:10]
        
        return {
            'total_puntos': len(self.puntos),
            'total_conexiones': len(self.conexiones),
            'centro': {'x': centro_x, 'y': centro_y},
            'zona_dominante': zona_dominante,
            'puntos_recientes': [
                {
                    'id': pid,
                    'x': p.x,
                    'y': p.y,
                    'tipo': p.tipo,
                    'intensidad': p.decaimiento
                }
                for pid, p in recientes
            ],
            'zonas': {
                nombre: {
                    'centro': (z.centro_x, z.centro_y),
                    'n_puntos': len(z.puntos),
                    'color': z.color
                }
                for nombre, z in self.zonas.items()
            }
        }
    
    def describir(self) -> str:
        """
        Genera una descripción textual del mapa mental.
        Esta es la "percepción" de la IA de su entorno.
        """
        vista = self.get_vista()
        
        if vista['total_puntos'] == 0:
            return "Mi mapa mental está vacío. No he percibido nada aún."
        
        # Construir descripción
        partes = []
        
        # Zona dominante
        if vista['zona_dominante']:
            partes.append(f"Me encuentro principalmente en la zona {vista['zona_dominante']}.")
        
        # Centro de actividad
        cx, cy = vista['centro']['x'], vista['centro']['y']
        if cx > 0.6:
            partes.append("Hay mucha energía en mi percepción.")
        elif cx < 0.4:
            partes.append("La energía es baja.")
        
        if cy > 0.6:
            partes.append("Percibo alta complejidad/caos.")
        elif cy < 0.4:
            partes.append("Todo parece ordenado.")
        
        # Densidad
        if vista['total_puntos'] > 100:
            partes.append(f"Mi mapa está denso ({vista['total_puntos']} puntos).")
        elif vista['total_puntos'] < 20:
            partes.append("Mi mapa tiene pocos puntos aún.")
        
        # Últimas percepciones
        if vista['puntos_recientes']:
            tipos = [p['tipo'] for p in vista['puntos_recientes'][:5]]
            tipo_comun = max(set(tipos), key=tipos.count)
            partes.append(f"Últimamente percibo mucho tipo {tipo_comun}.")
        
        return " ".join(partes)
    
    def buscar_patron(self) -> Optional[Dict]:
        """
        Busca patrones en el historial reciente.
        Detecta si hay repeticiones o tendencias.
        """
        if len(self.historial_reciente) < 10:
            return None
        
        # Analizar tipos
        tipos = [h['tipo'] for h in self.historial_reciente]
        tipo_dominante = max(set(tipos), key=tipos.count)
        frecuencia = tipos.count(tipo_dominante) / len(tipos)
        
        # Analizar movimiento en el mapa
        xs = [h['x'] for h in self.historial_reciente]
        ys = [h['y'] for h in self.historial_reciente]
        
        # Tendencia
        if len(xs) >= 2:
            dx = xs[-1] - xs[0]
            dy = ys[-1] - ys[0]
            
            if abs(dx) > 0.2:
                tendencia_x = "subiendo" if dx > 0 else "bajando"
            else:
                tendencia_x = "estable"
            
            if abs(dy) > 0.2:
                tendencia_y = "aumentando" if dy > 0 else "disminuyendo"
            else:
                tendencia_y = "estable"
        else:
            tendencia_x = tendencia_y = "desconocida"
        
        return {
            'tipo_dominante': tipo_dominante,
            'frecuencia': frecuencia,
            'tendencia_energia': tendencia_x,
            'tendencia_entropia': tendencia_y
        }
    
    def recordar(self, tipo: str = None, limite: int = 10) -> List[Dict]:
        """
        Recupera "recuerdos" (puntos pasados) del mapa.
        """
        resultados = []
        
        for pid, punto in sorted(
            self.puntos.items(),
            key=lambda x: x[1].decaimiento,
            reverse=True
        ):
            if tipo and punto.tipo != tipo:
                continue
            
            resultados.append({
                'id': pid,
                'posicion': (punto.x, punto.y),
                'tipo': punto.tipo,
                'intensidad': punto.intensidad,
                'fuerza_recuerdo': punto.decaimiento,
                'edad': time.time() - punto.timestamp
            })
            
            if len(resultados) >= limite:
                break
        
        return resultados
    
    def to_grid(self, resolucion: int = 10) -> np.ndarray:
        """
        Convierte el mapa a una matriz 2D (imagen mental).
        """
        grid = np.zeros((resolucion, resolucion))
        
        for punto in self.puntos.values():
            # Posición en grid
            gx = min(int(punto.x * resolucion), resolucion - 1)
            gy = min(int(punto.y * resolucion), resolucion - 1)
            
            # Acumular intensidad
            grid[gy, gx] += punto.intensidad * punto.decaimiento
        
        # Normalizar
        if grid.max() > 0:
            grid = grid / grid.max()
        
        return grid
    
    def to_ascii(self, resolucion: int = 20) -> str:
        """
        Genera una representación ASCII del mapa mental.
        """
        grid = self.to_grid(resolucion)
        
        chars = " .:-=+*#%@"
        
        lineas = []
        lineas.append("+" + "-" * resolucion + "+")
        
        for fila in grid:
            linea = "|"
            for val in fila:
                idx = min(int(val * (len(chars) - 1)), len(chars) - 1)
                linea += chars[idx]
            linea += "|"
            lineas.append(linea)
        
        lineas.append("+" + "-" * resolucion + "+")
        lineas.append(" Energía →")
        
        return "\n".join(lineas)
    
    # === Métodos internos ===
    
    def _normalizar(self, valor: float, rango: List[float]) -> float:
        """Normaliza valor a [0, 1]."""
        if rango[1] == rango[0]:
            return 0.5
        return max(0, min(1, (valor - rango[0]) / (rango[1] - rango[0])))
    
    def _actualizar_rangos(self, energia: float, entropia: float):
        """Actualiza rangos observados."""
        self.rango_energia[0] = min(self.rango_energia[0], energia)
        self.rango_energia[1] = max(self.rango_energia[1], energia)
        self.rango_entropia[0] = min(self.rango_entropia[0], entropia)
        self.rango_entropia[1] = max(self.rango_entropia[1], entropia)
    
    def _asignar_a_zona(self, punto_id: int, punto: Punto):
        """Asigna un punto a su zona correspondiente."""
        for nombre, zona in self.zonas.items():
            dist = np.sqrt((punto.x - zona.centro_x)**2 + 
                          (punto.y - zona.centro_y)**2)
            if dist < zona.radio:
                zona.puntos.append(punto_id)
                break
    
    def _crear_conexiones(self, punto_id: int, punto: Punto):
        """Crea conexiones con puntos cercanos."""
        for pid, p in self.puntos.items():
            if pid == punto_id:
                continue
            
            # Distancia euclidiana
            dist = np.sqrt((punto.x - p.x)**2 + (punto.y - p.y)**2)
            
            if dist < self.umbral_conexion:
                # Tipo de conexión
                if punto.tipo == p.tipo:
                    tipo_conexion = "conceptual"
                elif abs(punto.timestamp - p.timestamp) < 1.0:
                    tipo_conexion = "temporal"
                else:
                    tipo_conexion = "espacial"
                
                self.conexiones.append(Conexion(
                    origen=pid,
                    destino=punto_id,
                    fuerza=1.0 - dist,
                    tipo=tipo_conexion
                ))
    
    def _zona_con_mas_puntos(self) -> Optional[str]:
        """Retorna la zona con más puntos."""
        max_puntos = 0
        zona_max = None
        
        for nombre, zona in self.zonas.items():
            # Contar puntos que aún existen
            puntos_vivos = [p for p in zona.puntos if p in self.puntos]
            zona.puntos = puntos_vivos  # Limpiar
            
            if len(puntos_vivos) > max_puntos:
                max_puntos = len(puntos_vivos)
                zona_max = nombre
        
        return zona_max
    
    def _limpiar_puntos_debiles(self):
        """Elimina los puntos más débiles."""
        # Ordenar por decaimiento
        ordenados = sorted(
            self.puntos.items(),
            key=lambda x: x[1].decaimiento
        )
        
        # Eliminar el 20% más débil
        n_eliminar = len(ordenados) // 5
        for pid, _ in ordenados[:n_eliminar]:
            self._eliminar_punto(pid)
    
    def _eliminar_punto(self, punto_id: int):
        """Elimina un punto y sus conexiones."""
        if punto_id in self.puntos:
            del self.puntos[punto_id]
        
        # Eliminar conexiones
        self.conexiones = [
            c for c in self.conexiones 
            if c.origen != punto_id and c.destino != punto_id
        ]


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: Mapa Mental Interno")
    print("=" * 60)
    
    mapa = MapaMental()
    
    # Simular percepciones de dendritas
    print("\n📡 Simulando percepciones...")
    
    conceptos = ["TÉCNICO", "POÉTICO", "NUMÉRICO", "CAOS"]
    
    for i in range(100):
        energia = np.random.uniform(1000, 8000)
        entropia = np.random.uniform(1e9, 3e9)
        concepto = np.random.choice(conceptos)
        
        mapa.percibir(energia, entropia, concepto, confianza=0.9)
        
        # Aplicar decaimiento cada 10 percepciones
        if i % 10 == 0:
            mapa.tick()
    
    # Mostrar estado del mapa
    print("\n🗺️ ESTADO DEL MAPA:")
    print(f"   Puntos: {len(mapa.puntos)}")
    print(f"   Conexiones: {len(mapa.conexiones)}")
    
    # Obtener vista
    vista = mapa.get_vista()
    print(f"   Centro: ({vista['centro']['x']:.2f}, {vista['centro']['y']:.2f})")
    print(f"   Zona dominante: {vista['zona_dominante']}")
    
    # Descripción
    print("\n📝 PERCEPCIÓN DE LA IA:")
    print(f"   \"{mapa.describir()}\"")
    
    # Patrón detectado
    patron = mapa.buscar_patron()
    if patron:
        print(f"\n🔍 PATRÓN DETECTADO:")
        print(f"   Tipo dominante: {patron['tipo_dominante']} ({patron['frecuencia']:.0%})")
        print(f"   Tendencia energía: {patron['tendencia_energia']}")
        print(f"   Tendencia entropía: {patron['tendencia_entropia']}")
    
    # Visualización ASCII
    print("\n🖼️ MAPA VISUAL (ASCII):")
    print(mapa.to_ascii(15))
    
    # Recuerdos
    print("\n💭 RECUERDOS MÁS FUERTES:")
    for rec in mapa.recordar(limite=5):
        print(f"   - {rec['tipo']} en ({rec['posicion'][0]:.2f}, {rec['posicion'][1]:.2f})")
        print(f"     fuerza: {rec['fuerza_recuerdo']:.2f}, edad: {rec['edad']:.1f}s")
    
    print("\n" + "=" * 60)
    print("  MAPA MENTAL OPERATIVO ✓")
    print("=" * 60)
