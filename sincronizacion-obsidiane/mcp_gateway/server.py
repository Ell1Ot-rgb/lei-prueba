import os
import httpx
from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase

# Configuración
LIGHTRAG_URL = os.getenv("LIGHTRAG_URL", "http://lightrag:8000")
MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://memgraph:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# Crear el servidor MCP
mcp = FastMCP("GraphGateway", dependencies=["httpx", "neo4j"])

@mcp.tool()
async def query_knowledge_graph(query: str, modo: str = "global") -> str:
    """
    Busca información en el sistema RAG (Graphiti/LightRAG).
    Usa esta herramienta cuando necesites buscar conceptos fenomenológicos, notas o contexto.
    Modos permitidos: 'local', 'global', 'hybrid'.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"query": query, "mode": modo}
            response = await client.post(f"{LIGHTRAG_URL}/query", json=payload)
            response.raise_for_status()
            data = response.json()
            return str(data.get("respuesta", data))
    except Exception as e:
        return f"Error consultando LightRAG: {str(e)}"

@mcp.tool()
def execute_cypher_memgraph(query: str) -> str:
    """
    Ejecuta una consulta Cypher directamente en Memgraph (Grafo en memoria).
    Útil para explorar conexiones directas entre nodos y relaciones en tiempo real.
    """
    try:
        driver = GraphDatabase.driver(MEMGRAPH_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run(query)
            records = [record.data() for record in result]
        driver.close()
        return str(records) if records else "Consulta exitosa pero sin resultados."
    except Exception as e:
        return f"Error ejecutando Cypher: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    # Use standard uvicorn to host the SSE app exposed by FastMCP
    # FastMCP creates an SSE app via mcp._mcp_server
    # Actually, the simplest is to just use standard command line or the native mcp.run
    # Let's try mcp.run(transport="sse") and if it fails, fallback to uvicorn
    # In FastMCP (version 0.1), run with SSE might just be mcp.run(transport="sse")
    app = mcp._mcp_server if hasattr(mcp, '_mcp_server') else None
    
    # FastMCP exposes 'run' or you can just use settings. FastMCP uses starlette under the hood.
    try:
        from mcp.server.fastmcp import FastMCP
        # mcp._create_starlette_app() is often available
        app = mcp._app if hasattr(mcp, '_app') else mcp
        
        # We can just start it with SSE transport directly without host keyword if not supported
        import sys
        sys.argv = ["server.py"] # override to prevent parsing docker cmd
        # To make it listen on 0.0.0.0 we should perhaps use mcp settings or environment variables
        os.environ["HOST"] = "0.0.0.0"
        os.environ["PORT"] = "8005"
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = 8005
    except Exception:
        pass
        
    mcp.run(transport="sse")
