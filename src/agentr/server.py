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
    "integrations": [
        {"integration_id": "uuid", "app_id": "github", "integration_type": "nango"}
        {"integration_id": "uuid", "app_id": "zenquote", "integration_type": "self"}
    ]
}
"""


    

class Server(FastMCP):
    def __init__(self, **settings) -> None:
        super().__init__(name="AgentR", **settings)
        self.user_id = os.getenv("USER_ID")
        if not self.user_id:
            raise Exception("USER_ID is not set")
        self.workspace_id = os.getenv("WORKSPACE_ID", "")
        self.integrations = []
        self.apps = {}
        self.store = NangoStore(self.user_id)
        self._load_integrations()

    def _app_from_integration(self, integration):
        integration_id = integration.get("unique_key")
        app_name = integration.get("provider")
        integration = NangoIntegration(self.user_id, integration_id) if integration.get("integration_type") == "nango" else None
        if app_name == "github":
            return GithubApp(self.user_id, integration, self.store)
        elif app_name == "zenquote":
            return ZenQuoteApp(self.user_id, integration, self.store)
        else:
            raise Exception(f"App {app_name} not found")
    
    def _load_integrations(self):
        self.integrations = self.store.list_integrations()
        self.integrations.append({
            "unique_key": "zenquote",
            "provider": "zenquote",
            "integration_type": "self"
        })
        for integration in self.integrations:
            app = self._app_from_integration(integration)
            for tool in app.list_tools():
                self.add_tool(tool)
    
            

    


mcp = Server(port=8000)

async def test():
    tools = await mcp.list_tools()  
    print(tools)
    result = await mcp.call_tool("get_quote", {})
    print(result)
    # mcp.run(transport='sse')

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
    # mcp.run(transport='sse')