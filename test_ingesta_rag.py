
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

URL_INDEXAR = "http://localhost:7688/indexar"

def procesar_archivos():
    resultados = []
    print(f"--- Iniciando Ingesta de 10 Textos de Prueba ---\n")
    
    for i, texto in enumerate(TEXTOS_PRUEBA):
        print(f"Procesando archivo {i+1}/10...")
        payload = {
            "texto": texto,
            "fuente": f"test_file_{i+1}.txt",
            "metadata": {"categoria": "biologia", "iteracion": 1}
        }
        
        try:
            response = requests.post(URL_INDEXAR, json=payload, timeout=30)
            if response.status_code == 200:
                res_data = response.json()
                resultados.append(res_data)
                print(f"✓ Éxito: {res_data.get('estadisticas', {}).get('hechos_extraidos', 0)} hechos extraídos.")
            else:
                print(f"✗ Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"✗ Excepción: {e}")
        
        time.sleep(1)  # Pequeña pausa entre envíos

    print(f"\n--- Ingesta Finalizada ---")
    
    # Resumen final
    total_hechos = sum(r.get('estadisticas', {}).get('hechos_extraidos', 0) for r in resultados)
    total_entidades = sum(r.get('estadisticas', {}).get('entidades_detectadas', 0) for r in resultados)
    
    print(f"Total Hechos Extraídos: {total_hechos}")
    print(f"Total Entidades Detectadas: {total_entidades}")

if __name__ == "__main__":
    procesar_archivos()
