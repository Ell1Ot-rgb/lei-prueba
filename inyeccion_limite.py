import time
import sys
import os
import random

# Rutas para el contenedor
sys.path.insert(0, "/app/antigravity-connect/sistema biologico/sistema_terminado/interfaces")

from neural_ports import (
    ConfiguracionSistema, GrundzugTracker, 
    MotorEmergencia, S3LogicaPura
)

def inyeccion_masiva_conceptos():
    print("=" * 80)
    print("INYECCIÓN MASIVA DE ONTOLOGÍA (HACIA EL LÍMITE DE 500)")
    print("=" * 80)
    
    config = ConfiguracionSistema()
    tracker = GrundzugTracker(config)
    emergencia = MotorEmergencia(config)
    
    # 1. Restaurar los 63 conceptos previos para mantener continuidad
    filosoficos = ["Ser", "Tiempo", "Mundo", "Fenómeno", "Angustia", "Consciencia", "Muerte", "Técnica", "Dasein", "Epojé", "Ereignis", "Gestell", "Habitar"]
    cientificos = [
        "Entropía", "Cuántico", "Relatividad", "Genética", "Neurona", "Agujero_Negro", "Superposición", "ADN", "Átomo", "Bit",
        "Algoritmo", "Cifrado", "Sintaxis", "Red_Neuronal", "Energía", "Materia_Oscura", "Evolución", "Célula", "Proteína", "Gravedad",
        "Termodinámica", "Fisión", "Fusión", "Capa_Ozono", "Biodiversidad", "Ecosistema", "Quarks", "Fotón", "Láser", "Fibra_Óptica",
        "Supercomputación", "Blockchain", "Ciberseguridad", "Robot", "Nanotecnología", "Hidrógeno", "Isótopo", "Teoría_Caos", "Fractal", "Big_Bang",
        "Radiación", "Magnetismo", "Electrón", "Protón", "Neutrón", "Genoma", "Clonación", "Sintético", "Interferencia", "Resonancia"
    ]
    
    for f in filosoficos: emergencia.inyectar_concepto(f, certeza=0.99)
    for c in cientificos: emergencia.inyectar_concepto(c, certeza=0.95)
    
    print(f"Estado inicial: {len(emergencia.conceptos)} conceptos vivos.")

    # 2. Diccionario de expansión (Arte, Historia, Geografía, Matemáticas)
    arte = ["Barroco", "Pintura", "Escultura", "Sinfonía", "Ópera", "Cine", "Fotografía", "Surrealismo", "Cubismo", "Poesía"]
    historia = ["Renacimiento", "Revolución", "Imperio", "Colonia", "Antigüedad", "Edad_Media", "Democracia", "Feudalismo", "Guerra", "Tratado"]
    geo = ["Océano", "Continente", "Cordillera", "Desierto", "Selva", "Glaciar", "Volcán", "Archipiélago", "Atmósfera", "Biosfera"]
    math = ["Cálculo", "Integral", "Derivada", "Geometría", "Álgebra", "Matriz", "Infinito", "Lógica", "Probabilidad", "Estadística"]
    otros = [f"Variable_{i}" for i in range(400)] # Relleno para llegar al límite

    megalista = arte + historia + geo + math + otros
    
    print(f"Iniciando inyección de {len(megalista)} conceptos adicionales...")
    
    contador = 0
    for c_name in megalista:
        if len(emergencia.conceptos) >= 500:
            print(f"\n⚠️ ¡LÍMITE DE 500 ALCANZADO! Deteniendo inyección para evitar saturación física.")
            break
            
        emergencia.inyectar_concepto(c_name, certeza=random.uniform(0.7, 0.9))
        contador += 1
        
        if contador % 50 == 0:
            print(f"  > {len(emergencia.conceptos)}/500 conceptos anclados...")

    print("\n" + "=" * 80)
    print("INVENTARIO FINAL TRAS EXPANSIÓN MÁXIMA")
    print("=" * 80)
    print(f"Total de conceptos en el 'Cerebro': {len(emergencia.conceptos)}")
    
    # Muestra aleatoria de la diversidad
    vivos = list(emergencia.conceptos.values())
    muestra = random.sample(vivos, 15)
    
    print("\n[MUESTRA DE DIVERSIDAD CONCEPTUAL]")
    for c in muestra:
        print(f"  - {c.nombre:<20} | Certeza: {c.certeza:.2f}")

    print("\n[ANÁLISIS DE CAPACIDAD]")
    print(f"Espacio libre en el Grafo Conceptual: {500 - len(emergencia.conceptos)} slots.")
    print("El sistema está ahora en su LÍMITE OPERATIVO v100.")
    print("=" * 80)

if __name__ == "__main__":
    inyeccion_masiva_conceptos()
