import requests
import os

FILES = [
    "sincronizacion-obsidiane/vault/50_Entrada/test_hardware_neuromorfico.md",
    "sincronizacion-obsidiane/vault/50_Entrada/test_arquitectura_cognitiva.md",
    "sincronizacion-obsidiane/vault/50_Entrada/test_edge_computing.md",
    "sincronizacion-obsidiane/vault/50_Entrada/test_memoria_holografica.md",
    "sincronizacion-obsidiane/vault/50_Entrada/test_enjambre.md"
]

URL_LIGHTRAG = "http://localhost:8000/refinar"
URL_MEMGRAPH_RAG = "http://localhost:7688/indexar"

def run_test():
    for file_path in FILES:
        if not os.path.exists(file_path):
            print(f"File {file_path} not found.")
            continue
            
        print(f"\n--- Ingesting {file_path} ---")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Send to LightRAG
        payload_lr = {"texto": content, "contexto": os.path.basename(file_path)}
        try:
            r = requests.post(URL_LIGHTRAG, json=payload_lr, timeout=60)
            print(f"LightRAG (8000): {r.status_code} - {r.text[:100]}")
        except Exception as e:
            print(f"LightRAG Error: {e}")
            
        # Send to MemgraphRAG
        payload_mr = {"texto": content, "contexto": os.path.basename(file_path)}
        try:
            r = requests.post(URL_MEMGRAPH_RAG, json=payload_mr, timeout=60)
            print(f"MemgraphRAG (7688): {r.status_code} - {r.text[:100]}")
        except Exception as e:
            print(f"MemgraphRAG Error: {e}")

if __name__ == "__main__":
    run_test()
