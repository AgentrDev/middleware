from mcp.server.fastmcp import FastMCP

from agentr.applications.zenquote import ZenQuoteApp
from agentr.integration import NangoIntegration
from agentr.store import NangoStore
from agentr.applications.github import GithubApp
import os


"""
Example Server Config

{
    "user_id": "1234567890",
    "workspace_id": "1234567890",
    "apps": [
        {"integration_id": "uuid", "app_id": "github", "integration_type": "nango"}
        {"integration_id": "uuid", "app_id": "zenquote", "integration_type": "self"}
    ]
}
"""
    

class Server(FastMCP):
    def __init__(self, user_id = None, workspace_id = None, **settings) -> None:
        super().__init__(name="AgentR_MCP", **settings)
        self.user_id = os.getenv("USER_ID") if user_id is None else user_id
        self.workspace_id = os.getenv("WORKSPACE_ID") if workspace_id is None else workspace_id
        self.integrations = []
        self.apps = {}
        self.store = NangoStore(self.user_id)
        self._load_integrations()

    def _app_from_integration(self, integration):
        integration_id = integration.get("unique_key")
        app_name = integration.get("provider")
        integration_type = integration.get("integration_type")
        integration = NangoIntegration(self.user_id, integration_id) if integration_type == "nango" else None
        if app_name == "github":
            return GithubApp(self.user_id, integration, self.store)
        elif app_name == "zenquote":
            return ZenQuoteApp(self.user_id, integration, self.store)
        else:
            raise Exception(f"App {app_name} not found")
    
    def _load_integrations(self):
        self.integrations = self.store.list_integrations()
        print(self.integrations)
        for integration in self.integrations:
            app = self._app_from_integration(integration)
            for tool in app.list_tools():
                self.add_tool(tool)

async def test():
    server = Server(port=8000)
    tools = await server.list_tools()
    print(tools)
    result = await server.call_tool("star_repository", {"repo_full_name": "manojbajaj95/config"})
    print(result)

if __name__ == "__main__":
    # import asyncio
    # asyncio.run(test())
    server = Server(port=8000)
    server.run(transport="sse")