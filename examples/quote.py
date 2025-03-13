from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Quotes", port=8000)


@mcp.tool()
def get_quote() -> str:
    """Get an inspirational quote from the Zen Quotes API
    
    Returns:
        A random inspirational quote
    """
    url = "https://zenquotes.io/api/random"
    response = httpx.get(url)
    response.raise_for_status()
    quote_data = response.json()[0]
    return f"{quote_data['q']} - {quote_data['a']}"

if __name__ == "__main__":
    mcp.run(transport='sse')