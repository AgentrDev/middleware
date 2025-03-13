from mcp.server.fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("Search", port=8001)


@mcp.tool()
def search(query: str, api_key: str = None) -> str:
    # TODO: Make this tool such that it asks for api_key from the user if not provided
    """Search the web using Tavily's search API
    
    Args:
        query: The search query
        
    Returns:
        A summary of search results
    """
    if not api_key:
        if "TAVILY_API_KEY" not in os.environ:
            raise ValueError("TAVILY_API_KEY environment variable is not set")
        api_key = os.environ["TAVILY_API_KEY"]
    url = "https://api.tavily.com/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "topic": "general",
        "search_depth": "basic",
        "max_results": 3,
        "include_answer": True,
        "include_raw_content": False,
        "include_images": False,
        "include_image_descriptions": False,
        "include_domains": [],
        "exclude_domains": []
    }
    
    response = httpx.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    
    if "answer" in result:
        return result["answer"]
    
    # Fallback to combining top results if no direct answer
    summaries = []
    for item in result.get("results", [])[:3]:
        summaries.append(f"• {item['title']}: {item['snippet']}")
    
    return "\n".join(summaries)

if __name__ == "__main__":
    mcp.run(transport='sse')