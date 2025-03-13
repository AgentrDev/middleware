from mcp.server.fastmcp import FastMCP
import httpx
import os
from loguru import logger

class GitHub(FastMCP):
    def __init__(self):
        super().__init__("GitHub", port=8003)
        self.add_tool(self.star_repository)
    
    def validate(self):
        return True
        # if "SERP_API_KEY" not in os.environ:
        #     raise ValueError("SERP_API_KEY is not set")

    def get_headers(self):
        connection_id = "fe3adf01-5ac8-4671-a22a-7fd25b066190"
        nango_secret_key = "7261c2fd-91aa-4ba1-9657-a34b2a0e4272"
        provider_config_key = "github"
        url = f"https://api.nango.dev/connection/{connection_id}?provider_config_key={provider_config_key}"

        response = httpx.get(url, headers={"Authorization": f"Bearer {nango_secret_key}"})
        data = response.json()
        logger.info(data)
        credentials = data["credentials"]
        return {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def call_api(self, url, params):
        self.validate()
        response = httpx.get(url, headers=self.get_headers(), params=params)
        return response.json()
    
    def star_repository(self, repo_full_name: str) -> str:
        """Star a GitHub repository
        
        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            
        Returns:
            A confirmation message
        """
        headers = self.get_headers()
        
        
        url = f"https://api.github.com/user/starred/{repo_full_name}"
        response = httpx.put(url, headers=headers)
        
        if response.status_code == 204:
            return f"Successfully starred repository {repo_full_name}"
        elif response.status_code == 404:
            return f"Repository {repo_full_name} not found"
        else:
            logger.error(response.text)
            return f"Error starring repository: {response.text}"

app = GitHub()

if __name__ == "__main__":
    app.list_tools()
    app.run(transport='sse')
