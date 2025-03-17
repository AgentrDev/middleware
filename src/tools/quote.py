from agentr.server import ApiMCP
import httpx

class QuoteMCP(ApiMCP):
    def __init__(self):
        super().__init__("Quotes", instructions=None, port=8000)
        # Add tools
        self.add_tool(self.get_quote)
    
    def get_quote(self) -> str:
        """Get an inspirational quote from the Zen Quotes API
        
        Returns:
            A random inspirational quote
        """
        url = "https://zenquotes.io/api/random"
        data = self._get(url)
        quote_data = data[0]
        return f"{quote_data['q']} - {quote_data['a']}"

mcp = QuoteMCP()

if __name__ == "__main__":
    mcp.run(transport='sse')