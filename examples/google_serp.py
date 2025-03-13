import os
from mcp.server.fastmcp import FastMCP
import httpx


class GoogleSERP(FastMCP):
    def __init__(self):
        super().__init__("Google SERP", port=8004)
        self.serp_api_key = os.getenv("SERP_API_KEY")
        self.add_tool(self.search)
    
    def validate(self):
        if "SERP_API_KEY" not in os.environ:
            raise ValueError("SERP_API_KEY is not set")

    def get_headers(self):
        return {
            "X-API-KEY": self.serp_api_key,
            "Content-Type": "application/json",
        }
    
    def call_api(self, url, params):
        self.validate()
        response = httpx.get(url, headers=self.get_headers(), params=params)
        return response.json()

    def search(self, query: str) -> str:
        url = "https://api.serpapi.com/search"
        return self.call_api(url, {"q": query})

mcp = GoogleSERP()

if __name__ == "__main__":
    mcp.run(transport='sse')



