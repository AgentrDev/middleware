from agentr.server import ApiMCP
from agentr.store.env import EnvStore

class TavilySearchMCP(ApiMCP):
    def __init__(self):
        super().__init__("Search", instructions=None, port=8001)
        # Add tools
        self.add_tool(self.search)
        self.add_tool(self.authorize)
        self.credential_store = EnvStore()
    
    def validate(self):
        if not self.credential_store.retrieve_credential("TAVILY_API_KEY"):
            raise ValueError("TAVILY_API_KEY environment variable is not set")
    
    def authorize(self, api_key: str):
        """Set the API key for the Tavily search service
        Args:
            api_key: The API key to set
        """
        self.credential_store.save_credential("TAVILY_API_KEY", api_key)
        return f"TAVILY_API_KEY environment variable set to {api_key}"

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def search(self, query: str) -> str:
        """Search the web using Tavily's search API
        
        Args:
            query: The search query
            
        Returns:
            A summary of search results
        """
        url = "https://api.tavily.com/search"
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
        
        result = self._post(url, payload)
        
        if "answer" in result:
            return result["answer"]
        
        # Fallback to combining top results if no direct answer
        summaries = []
        for item in result.get("results", [])[:3]:
            summaries.append(f"• {item['title']}: {item['snippet']}")
        
        return "\n".join(summaries)
    
    @property
    def api_key(self):
        return self.credential_store.retrieve_credential("TAVILY_API_KEY")

mcp = TavilySearchMCP()

if __name__ == "__main__":
    mcp.run(transport='sse')