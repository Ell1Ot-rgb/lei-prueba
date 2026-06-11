import asyncio
import os
import traceback
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def main():
    try:
        url = "http://localhost:8005/sse"
        print(f"Connecting to MCP SSE at {url}...")
        
        # Connect to the SSE stream
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Initialized session!")

                # List available tools
                tools = await session.list_tools()
                print("\nAvailable tools:")
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description}")

                # Execute tool to get node count
                query = "MATCH (n) RETURN count(n) as count"
                print(f"\nExecuting tool 'execute_cypher_memgraph' with query: {query}")
                result = await session.call_tool("execute_cypher_memgraph", arguments={"query": query})
                print("Result:")
                for content in result.content:
                    print(content.text)

                # Get nodes
                query2 = "MATCH (n) RETURN n.name as name, labels(n) as labels LIMIT 5"
                print(f"\nExecuting tool 'execute_cypher_memgraph' with query: {query2}")
                result2 = await session.call_tool("execute_cypher_memgraph", arguments={"query": query2})
                print("Result:")
                for content in result2.content:
                    print(content.text)

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
