#!/usr/bin/env python3
"""
verify_pipeline_connections.py — Script de Diagnóstico del Sistema de Sincronización
===================================================================================
Verifica las conexiones a las bases de datos de grafos, las APIs REST de los RAG,
el estado del Vault de Obsidian, y valida el flujo completo.
"""

import os
import sys
import json
import pathlib
import requests
from pathlib import Path
from dotenv import load_dotenv

# Configurar path raíz
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

def color_text(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "bold": "\033[1m",
        "end": "\033[0m"
    }
    return f"{colors.get(color, '')}{text}{colors.get('end', '')}"

def print_section(title):
    print("\n" + "=" * 80)
    print(color_text(f" {title} ", "bold"))
    print("=" * 80)

def test_neo4j():
    print(color_text("1. Verificando conexión a Neo4j (LightRAG / Graphiti)...", "bold"))
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7690")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "fenomenologia2024")
    
    print(f"  URI: {uri}")
    print(f"  User: {user}")
    
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print(color_text("  [✅ OK] Conexión directa a Neo4j exitosa.", "green"))
                driver.close()
                return True
            else:
                print(color_text("  [❌ ERROR] Neo4j retornó un resultado inesperado.", "red"))
        driver.close()
    except Exception as e:
        print(color_text(f"  [❌ ERROR] No se pudo conectar a Neo4j: {e}", "red"))
    return False

def test_memgraph():
    print(color_text("2. Verificando conexión a Memgraph (MemGraphRAG)...", "bold"))
    host = os.getenv("MEMGRAPH_HOST", "localhost")
    port = int(os.getenv("MEMGRAPH_PORT", "7687"))
    uri = f"bolt://{host}:{port}"
    user = ""
    password = ""
    
    print(f"  URI: {uri}")
    
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print(color_text("  [✅ OK] Conexión directa a Memgraph exitosa.", "green"))
                driver.close()
                return True
            else:
                print(color_text("  [❌ ERROR] Memgraph retornó un resultado inesperado.", "red"))
        driver.close()
    except Exception as e:
        print(color_text(f"  [❌ ERROR] No se pudo conectar a Memgraph: {e}", "red"))
    return False

def test_lightrag_api():
    print(color_text("3. Verificando API REST de LightRAG / Graphiti (puerto 8000)...", "bold"))
    url = os.getenv("LIGHTRAG_API_URL", "http://localhost:8000")
    health_url = f"{url}/health"
    print(f"  Endpoint: {health_url}")
    
    try:
        r = requests.get(health_url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(color_text("  [✅ OK] API REST LightRAG en línea.", "green"))
            print(f"    Status: {data.get('status')}")
            print(f"    Provider: {data.get('provider')}")
            print(f"    Graphiti Activo (Neo4j Temporal Context): {data.get('graphiti_active')}")
            return True
        else:
            print(color_text(f"  [❌ ERROR] Retornó código HTTP {r.status_code}", "red"))
    except Exception as e:
        print(color_text(f"  [❌ ERROR] Falló conexión a API de LightRAG: {e}", "red"))
    return False

def test_memgraph_rag_api():
    print(color_text("4. Verificando API REST de Memgraph RAG (puerto 7688)...", "bold"))
    url = os.getenv("MEMGRAPH_RAG_API_URL", "http://localhost:7688")
    health_url = f"{url}/health"
    print(f"  Endpoint: {health_url}")
    
    try:
        r = requests.get(health_url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(color_text("  [✅ OK] API REST MemGraphRAG en línea.", "green"))
            print(f"    Estado: {data.get('estado')}")
            print(f"    Servicio: {data.get('servicio')}")
            print(f"    Memgraph Activo (Conectado a DB): {data.get('memgraph_activo')}")
            print(f"    Paper: {data.get('paper')}")
            return True
        else:
            print(color_text(f"  [❌ ERROR] Retornó código HTTP {r.status_code}", "red"))
    except Exception as e:
        print(color_text(f"  [❌ ERROR] Falló conexión a API de MemGraphRAG: {e}", "red"))
    return False

def test_obsidian_vault():
    print(color_text("5. Verificando Vault de Obsidian...", "bold"))
    vault_path = os.getenv("VAULT_PATH", "")
    print(f"  Path: {vault_path}")
    
    if not vault_path:
        print(color_text("  [❌ ERROR] VAULT_PATH no está configurado en .env", "red"))
        return False
        
    p = Path(vault_path)
    if not p.exists():
        print(color_text("  [❌ ERROR] El directorio del Vault no existe en el sistema.", "red"))
        return False
        
    required_dirs = ["00_MOC", "01_PreInstancias", "02_Instancias", "05_Fenomenos", "09_YO", "12_Logica"]
    missing = []
    for rd in required_dirs:
        if not (p / rd).exists():
            missing.append(rd)
            
    if not missing:
        print(color_text("  [✅ OK] La estructura del Vault está completa y validada.", "green"))
        # Mostrar cuántas notas hay
        for rd in required_dirs[:5]:
            n = len(list((p / rd).glob("*.md")))
            print(f"    - {rd}: {n} nota(s)")
        return True
    else:
        print(color_text(f"  [❌ ERROR] Faltan directorios requeridos en el Vault: {', '.join(missing)}", "red"))
        return False

def main():
    print_section("DIAGNÓSTICO COMPLETO DE CONEXIONES Y SERVICIOS")
    
    results = {}
    results["neo4j"] = test_neo4j()
    print()
    results["memgraph"] = test_memgraph()
    print()
    results["lightrag"] = test_lightrag_api()
    print()
    results["memgraph_rag"] = test_memgraph_rag_api()
    print()
    results["obsidian"] = test_obsidian_vault()
    
    print_section("RESUMEN DE DIAGNÓSTICO")
    
    all_ok = True
    for key, ok in results.items():
        name = key.upper()
        if key == "lightrag":
            name = "LIGHTRAG / GRAPHITI API"
        elif key == "memgraph_rag":
            name = "MEMGRAPH RAG API"
        
        status = color_text("🟢 CONECTADO / OK", "green") if ok else color_text("🔴 ERROR / DESCONECTADO", "red")
        print(f"  {name:<30}: {status}")
        if not ok:
            all_ok = False
            
    print("\n" + "=" * 80)
    if all_ok:
        print(color_text("  EL SISTEMA ESTÁ TOTALMENTE CONECTADO Y LISTO PARA OPERAR.", "green"))
    else:
        print(color_text("  EL SISTEMA REQUIERE INTERVENCIÓN. REVISA LAS CONEXIONES CON ERROR.", "red"))
    print("=" * 80)

if __name__ == "__main__":
    main()
