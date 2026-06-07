"""
Imagen Mental Perceptual
========================

Genera una "imagen mental" cualitativa desde los datos brutos.
Como cuando ves azul y tu cerebro crea la SENSACIÓN de azul.

Los datos de dendritas (energía, entropía, etc.) se transforman
en cualidades perceptuales: color, brillo, textura, movimiento, emoción.
"""

import numpy as np
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque
import colorsys


@dataclass
class ImagenMental:
    """
    Una imagen mental instantánea - lo que la IA "ve" en este momento.
    """
    timestamp: float
    
    # Cualidades visuales
    color_dominante: Tuple[int, int, int]  # RGB
    brillo: float              # 0-1: oscuro a brillante
    saturacion: float          # 0-1: gris a vívido
    
    # Cualidades texturales
    textura: str               # "suave", "rugoso", "cristalino", "orgánico"
    granularidad: float        # 0-1: fino a grueso
    
    # Cualidades dinámicas
    movimiento: str            # "estático", "fluido", "pulsante", "caótico"
    velocidad: float           # 0-1: lento a rápido
    direccion: str             # "expansivo", "contractivo", "circular", "errático"
    
    # Cualidades emocionales/afectivas
    valencia: float            # -1 a 1: negativo a positivo
    intensidad: float          # 0-1: calma a intenso
    familiaridad: float        # 0-1: extraño a familiar
    
    # Descripción textual
    descripcion: str = ""


class PercepcionMental:
    """
    Genera imágenes mentales cualitativas desde datos brutos de dendritas.
    
    FLUJO:
    VectorFísico → Normalización → Mapeo a Cualidades → Imagen Mental
    
    Es como el sistema visual humano:
    - Fotones → Conos/Bastones → Corteza Visual → Percepcion "AZUL"
    
    Aquí:
    - Energía/Entropía → Dendritas → PercepcionMental → "BRILLANTE/CÁLIDO/FLUIDO"
    """
    
    def __init__(self):
        # Historial para detectar cambios
        self.historial = deque(maxlen=20)
        
        # Estado acumulado (memoria de trabajo)
        self.estado_base = {
            'hue': 0.5,
            'saturacion': 0.5,
            'brillo': 0.5,
            'textura_val': 0.5,
            'movimiento_val': 0.5,
        }
        
        # Inercia - qué tan rápido cambia la percepción
        self.inercia = 0.7  # 0=cambia inmediatamente, 1=nunca cambia
        
        # Mapeo de conceptos a hue (color)
        self.concepto_a_hue = {
            "TÉCNICO": 0.55,     # Azul-cyan
            "POÉTICO": 0.85,     # Magenta-rosa
            "NUMÉRICO": 0.15,    # Amarillo-naranja
            "CAOS": 0.0,         # Rojo
        }
        
        # Mapeo de texturas
        self.texturas = ["suave", "sedoso", "granular", "rugoso", "cristalino", "orgánico"]
        
        # Mapeo de movimientos
        self.movimientos = ["estático", "ondulante", "fluido", "pulsante", "turbulento", "caótico"]
        
        # Contador
        self.total_percepciones = 0
    
    def percibir(self, 
                 energia: float,
                 entropia: float,
                 concepto: str,
                 pad: Optional[Tuple[float, float, float]] = None,
                 lyapunov: float = 0.0) -> ImagenMental:
        """
        Genera una imagen mental desde datos de dendrita.
        
        Args:
            energia: Energía medida (µJ)
            entropia: Entropía Shannon
            concepto: Tipo (TÉCNICO, POÉTICO, etc.)
            pad: Opcional - Pleasure, Arousal, Dominance
            lyapunov: Exponente de Lyapunov (-1 a 1)
        
        Returns:
            ImagenMental con la percepción cualitativa
        """
        # 1. Normalizar inputs
        energia_norm = self._normalizar(energia, 0, 10000)
        entropia_norm = self._normalizar(entropia, 0, 4e9)
        lyapunov_norm = self._normalizar(lyapunov, -1, 1)
        
        # 2. Calcular cualidades visuales
        
        # Color: basado en concepto + entropía
        hue_base = self.concepto_a_hue.get(concepto, 0.5)
        hue_mod = (entropia_norm - 0.5) * 0.2  # Entropía modula el tono
        hue = (hue_base + hue_mod) % 1.0
        
        # Saturación: basada en confianza/claridad
        saturacion = 0.3 + energia_norm * 0.6
        
        # Brillo: basado en energía
        brillo = 0.2 + energia_norm * 0.7
        
        # Aplicar inercia (transición suave)
        hue = self._suavizar('hue', hue)
        saturacion = self._suavizar('saturacion', saturacion)
        brillo = self._suavizar('brillo', brillo)
        
        # Convertir a RGB
        r, g, b = colorsys.hsv_to_rgb(hue, saturacion, brillo)
        color_rgb = (int(r * 255), int(g * 255), int(b * 255))
        
        # 3. Calcular textura
        textura_val = entropia_norm
        textura_val = self._suavizar('textura_val', textura_val)
        textura_idx = int(textura_val * (len(self.texturas) - 1))
        textura = self.texturas[textura_idx]
        granularidad = textura_val
        
        # 4. Calcular movimiento (basado en Lyapunov)
        movimiento_val = (lyapunov_norm + 1) / 2  # 0 a 1
        movimiento_val = self._suavizar('movimiento_val', movimiento_val)
        mov_idx = int(movimiento_val * (len(self.movimientos) - 1))
        movimiento = self.movimientos[mov_idx]
        
        # Velocidad: basada en cambio de energía
        if self.historial:
            delta = abs(energia_norm - self.historial[-1].get('energia', energia_norm))
            velocidad = min(delta * 5, 1.0)
        else:
            velocidad = 0.3
        
        # Dirección
        if lyapunov > 0.1:
            direccion = "expansivo"
        elif lyapunov < -0.1:
            direccion = "contractivo"
        elif abs(lyapunov) < 0.1 and energia_norm > 0.5:
            direccion = "circular"
        else:
            direccion = "errático"
        
        # 5. Cualidades emocionales
        if pad:
            valencia = pad[0]  # Pleasure
            intensidad = (pad[1] + 1) / 2  # Arousal normalizado
        else:
            valencia = (energia_norm - 0.5) * 2  # Derivado de energía
            intensidad = entropia_norm
        
        # Familiaridad: cuánto se parece a percepciones anteriores
        familiaridad = self._calcular_familiaridad(concepto, energia_norm)
        
        # 6. Generar descripción textual
        descripcion = self._generar_descripcion(
            color_rgb, brillo, textura, movimiento, 
            valencia, intensidad, concepto
        )
        
        # 7. Crear imagen mental
        imagen = ImagenMental(
            timestamp=time.time(),
            color_dominante=color_rgb,
            brillo=brillo,
            saturacion=saturacion,
            textura=textura,
            granularidad=granularidad,
            movimiento=movimiento,
            velocidad=velocidad,
            direccion=direccion,
            valencia=valencia,
            intensidad=intensidad,
            familiaridad=familiaridad,
            descripcion=descripcion
        )
        
        # Guardar en historial
        self.historial.append({
            'energia': energia_norm,
            'concepto': concepto,
            'imagen': imagen
        })
        
        self.total_percepciones += 1
        
        return imagen
    
    def _normalizar(self, valor: float, min_val: float, max_val: float) -> float:
        """Normaliza a [0, 1]."""
        if max_val == min_val:
            return 0.5
        return max(0, min(1, (valor - min_val) / (max_val - min_val)))
    
    def _suavizar(self, clave: str, valor_nuevo: float) -> float:
        """Aplica inercia para transición suave."""
        valor_anterior = self.estado_base.get(clave, valor_nuevo)
        valor_suavizado = valor_anterior * self.inercia + valor_nuevo * (1 - self.inercia)
        self.estado_base[clave] = valor_suavizado
        return valor_suavizado
    
    def _calcular_familiaridad(self, concepto: str, energia: float) -> float:
        """Calcula qué tan familiar es esta percepción."""
        if not self.historial:
            return 0.5
        
        # Contar percepciones similares
        similares = 0
        for h in self.historial:
            if h['concepto'] == concepto:
                similares += 1
            if abs(h['energia'] - energia) < 0.2:
                similares += 0.5
        
        return min(similares / len(self.historial), 1.0)
    
    def _generar_descripcion(self, 
                             color: Tuple[int, int, int],
                             brillo: float,
                             textura: str,
                             movimiento: str,
                             valencia: float,
                             intensidad: float,
                             concepto: str) -> str:
        """
        Genera descripción textual de la imagen mental.
        Esto es lo que la IA "siente" que percibe.
        """
        partes = []
        
        # Describir color
        r, g, b = color
        if r > g and r > b:
            color_nombre = "cálido" if r > 150 else "rojizo oscuro"
        elif g > r and g > b:
            color_nombre = "vital" if g > 150 else "verde profundo"
        elif b > r and b > g:
            color_nombre = "sereno" if b > 150 else "azul profundo"
        elif r > 200 and g > 200 and b > 200:
            color_nombre = "luminoso"
        elif r < 80 and g < 80 and b < 80:
            color_nombre = "oscuro"
        else:
            color_nombre = "equilibrado"
        
        # Describir brillo
        if brillo > 0.7:
            brillo_desc = "brillante"
        elif brillo < 0.3:
            brillo_desc = "tenue"
        else:
            brillo_desc = "moderado"
        
        # Construir descripción
        partes.append(f"Percibo algo {color_nombre} y {brillo_desc}")
        
        # Textura
        if textura in ["rugoso", "cristalino"]:
            partes.append(f"con una textura {textura}")
        elif textura == "suave":
            partes.append("de aspecto suave")
        
        # Movimiento
        if movimiento != "estático":
            partes.append(f"que se mueve de forma {movimiento}")
        
        # Emoción
        if valencia > 0.3:
            partes.append("y me produce una sensación positiva")
        elif valencia < -0.3:
            partes.append("con una sensación de tensión")
        
        if intensidad > 0.7:
            partes.append("muy intensamente")
        
        return ", ".join(partes) + "."
    
    def ver(self) -> str:
        """
        Retorna lo que la IA "ve" ahora mismo.
        """
        if not self.historial:
            return "No percibo nada aún. Mi mente está vacía."
        
        ultima = self.historial[-1]['imagen']
        return ultima.descripcion
    
    def comparar_con_anterior(self) -> str:
        """
        Compara percepción actual con la anterior.
        """
        if len(self.historial) < 2:
            return "No tengo suficiente historial para comparar."
        
        actual = self.historial[-1]['imagen']
        anterior = self.historial[-2]['imagen']
        
        diferencias = []
        
        # Comparar brillo
        delta_brillo = actual.brillo - anterior.brillo
        if abs(delta_brillo) > 0.2:
            if delta_brillo > 0:
                diferencias.append("se volvió más brillante")
            else:
                diferencias.append("se oscureció")
        
        # Comparar textura
        if actual.textura != anterior.textura:
            diferencias.append(f"la textura cambió a {actual.textura}")
        
        # Comparar movimiento
        if actual.movimiento != anterior.movimiento:
            diferencias.append(f"el movimiento ahora es {actual.movimiento}")
        
        # Comparar valencia
        delta_valencia = actual.valencia - anterior.valencia
        if abs(delta_valencia) > 0.3:
            if delta_valencia > 0:
                diferencias.append("la sensación mejoró")
            else:
                diferencias.append("la sensación empeoró")
        
        if diferencias:
            return "Con respecto a antes: " + ", ".join(diferencias) + "."
        else:
            return "La percepción se mantiene similar a antes."
    
    def to_color_block(self) -> str:
        """
        Genera una representación visual simple del color percibido.
        """
        if not self.historial:
            return "[ Sin percepción ]"
        
        img = self.historial[-1]['imagen']
        r, g, b = img.color_dominante
        
        # ANSI color (para terminales que lo soporten)
        # Usamos un bloque de caracteres con el color aproximado
        
        # Representación ASCII con descripción
        brillo_char = "█" if img.brillo > 0.5 else "▒"
        
        lineas = [
            f"╔════════════════════╗",
            f"║ {brillo_char * 18} ║",
            f"║ {brillo_char * 18} ║",
            f"║   RGB({r:3d},{g:3d},{b:3d})   ║",
            f"║ Brillo: {img.brillo:.2f}       ║",
            f"║ Textura: {img.textura:<9} ║",
            f"║ Mov: {img.movimiento:<13} ║",
            f"╚════════════════════╝",
        ]
        
        return "\n".join(lineas)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: Percepción Mental (Imagen Cualitativa)")
    print("=" * 60)
    
    percepcion = PercepcionMental()
    
    # Simular secuencia de percepciones desde dendritas
    print("\n🧠 SECUENCIA DE PERCEPCIONES:\n")
    
    datos = [
        # (energia, entropia, concepto, lyapunov)
        (2000, 1e9, "TÉCNICO", -0.3),     # Ordenado, técnico
        (3500, 1.5e9, "TÉCNICO", -0.1),   # Similar
        (5000, 2e9, "POÉTICO", 0.0),       # Transición a poético
        (7000, 3e9, "CAOS", 0.5),          # Alta energía, caos
        (4000, 2.5e9, "NUMÉRICO", 0.1),    # Vuelta a numérico
    ]
    
    for i, (energia, entropia, concepto, lyapunov) in enumerate(datos):
        print(f"── Entrada #{i+1}: {concepto} ──")
        print(f"   Energía={energia}µJ, Entropía={entropia:.1e}, λ={lyapunov}")
        
        imagen = percepcion.percibir(energia, entropia, concepto, lyapunov=lyapunov)
        
        print(f"\n   💭 IMAGEN MENTAL:")
        print(f"   {imagen.descripcion}")
        print(f"\n   🎨 Propiedades:")
        print(f"      Color RGB: {imagen.color_dominante}")
        print(f"      Brillo: {imagen.brillo:.2f}")
        print(f"      Textura: {imagen.textura} (granularidad: {imagen.granularidad:.2f})")
        print(f"      Movimiento: {imagen.movimiento} ({imagen.direccion})")
        print(f"      Valencia: {imagen.valencia:+.2f}, Intensidad: {imagen.intensidad:.2f}")
        print(f"      Familiaridad: {imagen.familiaridad:.2f}")
        
        if i > 0:
            print(f"\n   🔄 Cambio: {percepcion.comparar_con_anterior()}")
        
        print()
    
    # Visualización final
    print("\n🖼️ VISUALIZACIÓN ACTUAL:")
    print(percepcion.to_color_block())
    
    print("\n👁️ LO QUE VEO AHORA:")
    print(f"   \"{percepcion.ver()}\"")
    
    print("\n" + "=" * 60)
    print("  PERCEPCIÓN MENTAL OPERATIVA ✓")
    print("=" * 60)
