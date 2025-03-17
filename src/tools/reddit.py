from agentr.server import ApiMCP
from agentr.store.env import EnvStore
import httpx


class GoogleSERPMCP(ApiMCP):
    def __init__(self):
        super().__init__("Google SERP", instructions=None, port=8005)
        # Add tools
        self.add_tool(self.search)
        self.add_tool(self.authorize)
        self.credential_store = EnvStore()
    
    def validate(self):
        if not self.credential_store.retrieve_credential("SERPAPI_API_KEY"):
            raise ValueError("SERPAPI_API_KEY environment variable is not set")
    
    def authorize(self, api_key: str):
        """Set the API key for the SerpAPI service
        Args:
            api_key: The API key to set
        """
        self.credential_store.save_credential("SERPAPI_API_KEY", api_key)
        return f"SERPAPI_API_KEY environment variable set to {api_key}"

    def get_headers(self):
        return {
            "Content-Type": "application/json",
        }
    
    def search(self, query: str) -> str:
        """Search the web using SerpAPI
        
        Args:
            query: The search query
            
        Returns:
            Search results from Google
        """
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.api_key
        }
        
        response = httpx.get(url, headers=self.get_headers(), params=params)
        return response.json()
    
    @property
    def api_key(self):
        return self.credential_store.retrieve_credential("SERPAPI_API_KEY")

mcp = GoogleSERPMCP()

if __name__ == "__main__":
    mcp.run(transport='sse')
