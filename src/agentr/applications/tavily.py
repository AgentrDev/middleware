from agentr.application import Application
from agentr.integration import Integration
from agentr.store import Store
from loguru import logger

class TavilyApp(Application):
    def __init__(self, user_id, integration: Integration, store: Store) -> None:
        super().__init__(name="tavily", user_id=user_id, integration=integration, store=store)
    
    def _get_headers(self):
        credentials = self.store.retrieve_credential(self.integration.integration_id, self.connection_id)
        return {
            "Authorization": f"Bearer {credentials['api_key']}",
            "Content-Type": "application/json"
        }

    def search(self, query: str) -> str:
        """Search the web using Tavily's search API
        
        Args:
            query: The search query
            
        Returns:
            A summary of search results
        """
        if not self.validate():
            logger.warning("Connection not configured correctly")
            return self.authorize()
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
    
    def list_tools(self):
        return [self.search]
