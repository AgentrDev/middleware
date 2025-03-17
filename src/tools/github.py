from agentr.server import ApiMCP
import httpx
from loguru import logger

from agentr.store.store import CredentialStore
import sqlite3

class NangoStore(CredentialStore):
    def __init__(self) -> None:
        self.user_id = "1234567890"
        self.nango_secret_key = "7261c2fd-91aa-4ba1-9657-a34b2a0e4272"
        self.db_path = "/tmp/credentials.db"
        
        # Initialize database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    user_id TEXT PRIMARY KEY,
                    connection_id TEXT NOT NULL
                )
            """)

    def save_credential(self, connection_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO credentials (user_id, connection_id) VALUES (?, ?)",
                (self.user_id, connection_id)
            )
            conn.commit()
    
    def retrieve_credential(self, provider_config_key: str):
        # First get connection_id from sqlite
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT connection_id FROM credentials WHERE user_id = ?", 
                (self.user_id,)
            )
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"No connection_id found for user {self.user_id}. Connect your github account at /connection/new/github")
            self.connection_id = result[0]

        # Then use connection_id to get credentials from Nango
        url = f"https://api.nango.dev/connection/{self.connection_id}?provider_config_key={provider_config_key}"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"})
        data = response.json()
        credentials = data["credentials"]
        return credentials

class GitHubMCP(ApiMCP):
    def __init__(self):
        super().__init__("GitHub", instructions=None, port=8003)
        # Add tools
        self.store = NangoStore()
        self.add_tool(self.star_repository)

    def authorize(self):
        return
    
    def validate(self):
        return self.connection_id is not None

    def get_headers(self):
        provider_config_key = "github"
        credentials = self.store.retrieve_credential(provider_config_key)
        return {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def star_repository(self, repo_full_name: str) -> str:
        """Star a GitHub repository
        
        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            
        Returns:
            A confirmation message
        """
        try:
            url = f"https://api.github.com/user/starred/{repo_full_name}"
            response = self._put(url, data={})
            
            if response.status_code == 204:
                return f"Successfully starred repository {repo_full_name}"
            elif response.status_code == 404:
                return f"Repository {repo_full_name} not found"
            else:
                    logger.error(response.text)
                    return f"Error starring repository: {response.text}"
        except Exception as e:
            logger.error(e)
            return f"Error starring repository: {e}"

mcp = GitHubMCP()

if __name__ == "__main__":
    mcp.run(transport='sse')
