import os
import sys

# Mocking environment for Graphiti
os.environ["NEO4J_URI"] = "bolt://neo4j:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "fenomenologia2024"

try:
    from graphiti_core import Graphiti
    import inspect
    
    print(f"Signature of Graphiti.add_episode:")
    sig = inspect.signature(Graphiti.add_episode)
    print(sig)
    for name, param in sig.parameters.items():
        print(f"  - {name}: {param.kind}")

except Exception as e:
    print(f"Error: {e}")
