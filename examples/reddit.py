import os
from mcp.server.fastmcp import FastMCP
import httpx


class GoogleSERP(FastMCP):
    def __init__(self):
        super().__init__("Reddit", port=8005)
        self.reddit_api_key = os.getenv("REDDIT_API_KEY")

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.reddit_api_key}",
            "Content-Type": "application/json",
        }
    
    def call_api(self, url, params):
        response = httpx.get(url, headers=self.get_headers(), params=params)
        return response.json()

    def search(self, query: str) -> str:
        url = "https://api.serpapi.com/search"
        return self.call_api(url, {"q": query})
    
if __name__ == "__main__":
    mcp = GoogleSERP()
    mcp.run(transport='sse')



