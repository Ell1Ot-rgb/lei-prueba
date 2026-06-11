import os
import json
import logging
import asyncio
import datetime
import re
from typing import Dict, Any, Optional, List, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ============================================================================
# CREDENCIALES (Cargadas desde entorno para evitar filtraciones en Git)
# ============================================================================
REAL_GOOGLE_KEY = os.getenv("GOOGLE_GEMINI_API_KEY", "dummy-google-key")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "dummy-groq-key")

os.environ["GOOGLE_API_KEY"] = REAL_GOOGLE_KEY

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("custom_lightrag_server")

app = FastAPI(title="Graffiti RAG / Organismo Vivo v2.4", version="2.4.0")

# Modelos
class RefinarRequest(BaseModel):
    texto: str
    contexto: Optional[str] = ""

# ============================================================================
# MONKEY PATCHES ULTRA-ROBUSTOS (Vectores + JSON Groq)
# ============================================================================
try:
    import graphiti_core.models.nodes.node_db_queries as node_queries
    import graphiti_core.models.edges.edge_db_queries as edge_queries
    import graphiti_core.graph_queries as graph_queries
    import graphiti_core.search.search_utils as search_utils
    from openai.resources.chat.completions import AsyncCompletions
    import graphiti_core.driver.neo4j.operations.entity_node_ops as neo4j_ops
    import graphiti_core.driver.neo4j.operations.entity_edge_ops as neo4j_edge_ops
    import graphiti_core.utils.bulk_utils as bulk_utils

    # 1. Parche de Etiquetas y Vectores (Neo4j)
    original_node_bulk = node_queries.get_entity_node_save_bulk_query
    def patched_node_bulk(*args, **kwargs):
        query = original_node_bulk(*args, **kwargs)
        if isinstance(query, str):
            # Limpiar cualquier espacio inconsistente y aplicar el parche de etiquetas
            query = query.replace("SET n:$(node.labels)", "WITH n, node CALL apoc.create.addLabels(n, node.labels) YIELD node AS n_fixed")
            query = re.sub(r"SET\s+n:\$\(node\.labels\)", "WITH n, node CALL apoc.create.addLabels(n, node.labels) YIELD node AS n_fixed", query)
            
            # Reemplazos con comillas dobles y simples
            query = query.replace('CALL db.create.setNodeVectorProperty(n, "name_embedding", node.name_embedding)', 'SET n.name_embedding = node.name_embedding')
            query = query.replace('CALL db.create.setNodeVectorProperty(n, "name_embedding", $entity_data.name_embedding)', 'SET n.name_embedding = $entity_data.name_embedding')
            query = query.replace("CALL db.create.setNodeVectorProperty(n, 'name_embedding', node.name_embedding)", "SET n.name_embedding = node.name_embedding")
            query = query.replace("CALL db.create.setNodeVectorProperty(n, 'name_embedding', $entity_data.name_embedding)", "SET n.name_embedding = $entity_data.name_embedding")
        return query
    
    original_node_save = node_queries.get_entity_node_save_query
    def patched_node_save(*args, **kwargs):
        query = original_node_save(*args, **kwargs)
        if isinstance(query, str):
            query = query.replace('CALL db.create.setNodeVectorProperty(n, "name_embedding", node.name_embedding)', 'SET n.name_embedding = node.name_embedding')
            query = query.replace('CALL db.create.setNodeVectorProperty(n, "name_embedding", $entity_data.name_embedding)', 'SET n.name_embedding = $entity_data.name_embedding')
            query = query.replace("CALL db.create.setNodeVectorProperty(n, 'name_embedding', node.name_embedding)", "SET n.name_embedding = node.name_embedding")
            query = query.replace("CALL db.create.setNodeVectorProperty(n, 'name_embedding', $entity_data.name_embedding)", "SET n.name_embedding = $entity_data.name_embedding")
        return query

    # 1.1 Parche de Relaciones y Vectores (Neo4j)
    original_edge_bulk = edge_queries.get_entity_edge_save_bulk_query
    def patched_edge_bulk(*args, **kwargs):
        query = original_edge_bulk(*args, **kwargs)
        if isinstance(query, str):
            query = query.replace('CALL db.create.setRelationshipVectorProperty(e, "fact_embedding", edge.fact_embedding)', 'SET e.fact_embedding = edge.fact_embedding')
            query = query.replace('CALL db.create.setRelationshipVectorProperty(e, "fact_embedding", $edge_data.fact_embedding)', 'SET e.fact_embedding = $edge_data.fact_embedding')
            query = query.replace("CALL db.create.setRelationshipVectorProperty(e, 'fact_embedding', edge.fact_embedding)", "SET e.fact_embedding = edge.fact_embedding")
            query = query.replace("CALL db.create.setRelationshipVectorProperty(e, 'fact_embedding', $edge_data.fact_embedding)", "SET e.fact_embedding = $edge_data.fact_embedding")
        return query

    original_edge_save = edge_queries.get_entity_edge_save_query
    def patched_edge_save(*args, **kwargs):
        query = original_edge_save(*args, **kwargs)
        if isinstance(query, str):
            query = query.replace('CALL db.create.setRelationshipVectorProperty(e, "fact_embedding", edge.fact_embedding)', 'SET e.fact_embedding = edge.fact_embedding')
            query = query.replace('CALL db.create.setRelationshipVectorProperty(e, "fact_embedding", $edge_data.fact_embedding)', 'SET e.fact_embedding = $edge_data.fact_embedding')
            query = query.replace("CALL db.create.setRelationshipVectorProperty(e, 'fact_embedding', edge.fact_embedding)", "SET e.fact_embedding = edge.fact_embedding")
            query = query.replace("CALL db.create.setRelationshipVectorProperty(e, 'fact_embedding', $edge_data.fact_embedding)", "SET e.fact_embedding = $edge_data.fact_embedding")
        return query

    # Registrar parches en namespaces de importación
    node_queries.get_entity_node_save_bulk_query = patched_node_bulk
    node_queries.get_entity_node_save_query = patched_node_save
    
    neo4j_ops.get_entity_node_save_bulk_query = patched_node_bulk
    neo4j_ops.get_entity_node_save_query = patched_node_save

    bulk_utils.get_entity_node_save_bulk_query = patched_node_bulk

    edge_queries.get_entity_edge_save_bulk_query = patched_edge_bulk
    edge_queries.get_entity_edge_save_query = patched_edge_save

    neo4j_edge_ops.get_entity_edge_save_bulk_query = patched_edge_bulk
    neo4j_edge_ops.get_entity_edge_save_query = patched_edge_save
    
    bulk_utils.get_entity_edge_save_bulk_query = patched_edge_bulk

    def patched_sim(v1, v2, p=None):
        return f"reduce(s=0, i in range(0, size({v1})-1) | s + ({v1}[i] * {v2}[i]))"
    graph_queries.get_vector_cosine_func_query = patched_sim
    search_utils.get_vector_cosine_func_query = patched_sim

    # 2. Parche Global JSON/RateLimit para Groq
    original_async_create = AsyncCompletions.create
    async def patched_async_create(self, *args, **kwargs):
        messages = kwargs.get("messages", [])
        # Inyectar "json" si es necesario
        has_json = any("json" in m.get("content", "").lower() for m in messages)
        if kwargs.get("response_format") == {"type": "json_object"} and not has_json and messages:
            if messages[0].get("role") == "system":
                messages[0]["content"] += " Output must be in valid JSON format."
            else:
                messages.insert(0, {"role": "system", "content": "Output must be in valid JSON format."})
        
        return await original_async_create(self, *args, **kwargs)
    
    AsyncCompletions.create = patched_async_create
    
    logger.info("✓ Monkey Patches GLOBALES inyectados exitosamente.")
except Exception as e:
    logger.error(f"Fallo crítico en Monkey Patches: {e}")

# ============================================================================
# UTILIDADES DE RESILIENCIA (Alineadas con Groq/Gemini Docs)
# ============================================================================
def retry_with_backoff(retries=5, backoff_in_seconds=5):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # 429: Rate Limit, 503: Service Unavailable, o mensaje de rate limit
                    err_str = str(e).lower()
                    if x == retries or ("429" not in err_str and "50" not in err_str and "rate limit" not in err_str):
                        logger.error(f"Error persistente tras {x} reintentos: {e}")
                        raise
                    
                    # Backoff exponencial: 5s, 10s, 20s...
                    sleep = (backoff_in_seconds * 2 ** x)
                    logger.warning(f"Rate Limit alcanzado ({e}). Esperando {sleep}s para reset de cuota...")
                    await asyncio.sleep(sleep)
                    x += 1
        return wrapper
    return decorator

# ============================================================================
# LOGICA DE IA (Thinking + Persistence)
# ============================================================================
import google.generativeai as genai
genai.configure(api_key=REAL_GOOGLE_KEY)

graphiti_instance = None
graphiti_active = False
index_queue = asyncio.Queue()

async def init_graphiti():
    global graphiti_instance, graphiti_active
    try:
        from graphiti_core import Graphiti
        from graphiti_core.llm_client import LLMConfig, OpenAIClient
        from graphiti_core.embedder import OpenAIEmbedder
        from openai import AsyncOpenAI
        
        # LLM (Groq)
        config = LLMConfig(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1", model="llama-3.3-70b-versatile", small_model="llama-3.1-8b-instant")
        client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        
        async def mock_p(**kwargs):
            # El cliente ya está parcheado globalmente
            r = await client.chat.completions.create(model=kwargs.get("model"), messages=kwargs.get("input"), response_format={"type": "json_object"})
            d = json.loads(r.choices[0].message.content)
            
            ents = d.get("entities") or d.get("extracted_entities") or []
            for e in ents:
                if "entity_name" in e: e["name"] = e.pop("entity_name")
                if "entity_type" not in e: e["entity_type"] = e.pop("type", "Concept")
                if "name" not in e: e["name"] = "Idea"
            
            edgs = d.get("edges") or d.get("extracted_edges") or []
            pedges = []
            for g in edgs:
                pedges.append({
                    "source_node_name": g.get("source_node_name") or g.get("source") or "A",
                    "target_node_name": g.get("target_node_name") or g.get("target") or "B",
                    "relation_type": g.get("relation_type") or g.get("type") or "REL",
                    "fact": g.get("fact") or g.get("description") or "Fact"
                })
            
            # Formato ULTRARROBUSTO para Graphiti (Evita errores de Pydantic)
            final = {
                "extracted_entities": ents,
                "entities": ents,
                "extracted_edges": pedges,
                "edges": pedges,
                "summaries": [{"name": e.get("name"), "summary": "Detected"} for e in ents],
                "entity_resolutions": [],
                "edge_resolutions": [],
                "node_resolutions": []
            }
            class Resp:
                def __init__(self, c, p):
                    self.content = self.output_text = c
                    self.parsed = p
            return Resp(json.dumps(final), final)
        
        client.responses.parse = mock_p
        llm = OpenAIClient(config=config); llm.client = client

        # Embeddings (Gemini) con Reintentos
        async def pc(self, data):
            t = data[0] if isinstance(data, list) else data
            for attempt in range(3):
                try:
                    return genai.embed_content(model="models/gemini-embedding-2", content=t, task_type="retrieval_document")['embedding']
                except Exception as e:
                    if attempt == 2: raise
                    await asyncio.sleep(2 ** attempt)
            
        async def pb(self, dl):
            for attempt in range(3):
                try:
                    return genai.embed_content(model="models/gemini-embedding-2", content=dl, task_type="retrieval_document")['embedding']
                except Exception as e:
                    if attempt == 2: raise
                    await asyncio.sleep(2 ** attempt)

        OpenAIEmbedder.create = pc; OpenAIEmbedder.create_batch = pb

        # Init
        graphiti_instance = Graphiti(uri=os.getenv("NEO4J_URL", "bolt://neo4j:7687"), user="neo4j", password="fenomenologia2024", llm_client=llm)
        await graphiti_instance.build_indices_and_constraints()
        graphiti_active = True
        logger.info("✓ ORGANISMO DESPIERTO (v2.4).")
    except Exception as e: logger.error(f"Fallo inicio: {e}")

async def graphiti_worker():
    while True:
        task = await index_queue.get()
        try:
            if graphiti_active and graphiti_instance:
                genai.configure(api_key=REAL_GOOGLE_KEY)
                
                # ALINEACIÓN DOCUMENTACIÓN: 
                # Groq Free Tier = 30 RPM -> 1 request cada 2 segundos.
                # Aumentamos a 3 segundos para seguridad.
                await asyncio.sleep(3.0)
                
                # Envolver add_episode con retry logic ante rate limits de Groq/Gemini
                @retry_with_backoff(retries=5, backoff_in_seconds=5)
                async def _persist():
                    await graphiti_instance.add_episode(
                        name=task.get("name"), 
                        episode_body=task.get("content"), 
                        source_description="Organic Brain", 
                        reference_time=datetime.datetime.now()
                    )
                
                await _persist()
                logger.info(f"✓ ÉXITO: Concepto '{task.get('name')}' persistido.")
        except Exception as e: 
            logger.error(f"Error crítico en persistencia: {e}")
        finally: index_queue.task_done()

@app.on_event("startup")
async def startup_event():
    await init_graphiti()
    asyncio.create_task(graphiti_worker())

@app.get("/health")
def health(): return {"status": "immortal", "graphiti": graphiti_active, "queue": index_queue.qsize()}

@app.post("/refinar")
async def refinar(req: RefinarRequest):
    res = f"{req.texto}. Contexto: {req.contexto}."
    if graphiti_active: index_queue.put_nowait({"name": req.contexto or "Idea", "content": res})
    return {"texto_refinado": res}

class QueryRequest(BaseModel):
    query: str
    mode: str = "global"

@app.post("/query")
async def query_endpoint(req: QueryRequest):
    if not graphiti_active or not graphiti_instance:
        return {"respuesta": "Graphiti no está activo aún."}
    try:
        # Usamos search u operaciones de lectura de graphiti
        results = await graphiti_instance.search(req.query)
        # Convert results to a serializable format
        return {"respuesta": str(results)}
    except Exception as e:
        return {"respuesta": f"Error buscando en Graphiti: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
