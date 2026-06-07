import os
import sys

# Mocking environment for Graphiti
os.environ["NEO4J_URI"] = "bolt://neo4j:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "fenomenologia2024"

try:
    import graphiti_core
    from graphiti_core import Graphiti
    
    print("Modules found in graphiti_core:")
    print(dir(graphiti_core))
    
    if hasattr(graphiti_core, 'llm_client'):
        print("\nContent of graphiti_core.llm_client:")
        print(dir(graphiti_core.llm_client))
        
        # Intentar encontrar la clase cliente de OpenAI
        import graphiti_core.llm_client
        for name in dir(graphiti_core.llm_client):
            if "OpenAI" in name or "Client" in name:
                cls = getattr(graphiti_core.llm_client, name)
                print(f"\nAnalyzing class: {name}")
                try:
                    # Ver atributos de clase (posible modelo hardcoded)
                    print(f"  - Attributes: {[a for a in dir(cls) if not a.startswith('_')]}")
                except:
                    pass

except Exception as e:
    print(f"Error: {e}")
