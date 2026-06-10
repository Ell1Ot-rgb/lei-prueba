
import requests
import json
import time

TEXTOS_PRUEBA = [
    "El metabolismo celular es el conjunto de reacciones químicas que ocurren en el interior de las células.",
    "La homeostasis permite a los organismos mantener un equilibrio interno estable frente a cambios externos.",
    "La evolución biológica es el proceso de cambio en los rasgos heredados de una población a través de las generaciones.",
    "La simbiosis es una relación estrecha y persistente entre organismos de distintas especies.",
    "La fotosíntesis convierte la energía lumínica en energía química en las plantas y otros organismos.",
    "El sistema inmune protege al organismo contra agentes patógenos como virus y bacterias.",
    "La plasticidad neuronal es la capacidad del sistema nervioso para cambiar su estructura y funcionamiento.",
    "La epigenética estudia los cambios hereditarios que no alteran la secuencia de ADN.",
    "El ciclo de Krebs es una ruta metabólica fundamental para la respiración celular en organismos aeróbicos.",
    "La apoptosis es el proceso de muerte celular programada fundamental para el desarrollo de tejidos."
]

URL_REFINAR = "http://localhost:8000/refinar"

def procesar_lightrag():
    print(f"--- Iniciando Ingesta en LightRAG (Port 8000) ---\n")
    
    for i, texto in enumerate(TEXTOS_PRUEBA):
        print(f"Procesando archivo {i+1}/10...")
        payload = {
            "texto": texto,
            "contexto": f"Bio_Concept_{i+1}"
        }
        
        try:
            response = requests.post(URL_REFINAR, json=payload, timeout=60)
            if response.status_code == 200:
                print(f"✓ Éxito: Procesado en LightRAG.")
            else:
                print(f"✗ Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"✗ Excepción: {e}")
        
        time.sleep(2)  # Pausa mayor para dejar que el worker procese con LLM

    print(f"\n--- Ingesta LightRAG Finalizada ---")

if __name__ == "__main__":
    procesar_lightrag()
