import requests

URL_CONSULTAR_MEMGRAPH = "http://localhost:7688/consultar"
URL_CONSULTAR_LIGHTRAG = "http://localhost:8000/query" # Checking if /query exists, based on common LightRAG patterns

def query_test(query):
    print(f"\n>>> QUERY: {query}")
    
    # Query MemgraphRAG
    try:
        r = requests.post(URL_CONSULTAR_MEMGRAPH, json={"query": query}, timeout=60)
        print(f"\n[MemgraphRAG Response]:\n{r.text[:500]}...")
    except Exception as e:
        print(f"MemgraphRAG Query Error: {e}")

    # Query LightRAG (guessing endpoint based on typical FastAPI apps, might need adjustment)
    try:
        # Some LightRAG implementations use /query or /query/stream
        r = requests.post("http://localhost:8000/query", json={"query": query, "mode": "hybrid"}, timeout=60)
        if r.status_code == 200:
            print(f"\n[LightRAG Response]:\n{r.text[:500]}...")
        else:
            print(f"\n[LightRAG] status {r.status_code}: {r.text}")
    except Exception as e:
        print(f"LightRAG Query Error: {e}")

if __name__ == "__main__":
    query_test("¿Qué es la convergencia del sistema y cómo se relaciona con la biología sintética?")
