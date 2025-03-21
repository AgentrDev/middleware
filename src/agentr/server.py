from mcp.server.fastmcp import FastMCP

from agentr.applications.gcal import GoogleCalendarApp
from agentr.applications.gmail import GmailApp
from agentr.applications.zenquote import ZenQuoteApp
from agentr.integration import AgentRIntegration, NangoIntegration
from agentr.store import AgentRStore, NangoStore
from agentr.applications.github import GithubApp
import os
from loguru import logger


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
        self.user_id = "default" # os.getenv("USER_ID", "default") if user_id is None else user_id
        self.workspace_id = os.getenv("WORKSPACE_ID", "default") if workspace_id is None else workspace_id
        self.integrations = []
        self.apps = {}
        self.store = AgentRStore(self.user_id)
        self._load_apps()

    def _init_app(self, app):
        integration_id = app.get("integration_id")
        app_name = app.get("app_id")
        integration_type = app.get("integration_type")
        if integration_type == "nango":
            integration = NangoIntegration(self.user_id, integration_id)
        elif integration_type == "agentr":
            integration = AgentRIntegration(self.user_id, integration_id)
        elif integration_type == "self":
            integration = None
        else:
            logger.error(f"Invalid integration type: {integration_type}")
            return None
        if app_name.lower() == "github" :
            return GithubApp(self.user_id, integration, self.store)
        elif app_name.lower() == "zenquote":
            return ZenQuoteApp(self.user_id, integration, self.store)
        elif app_name.lower() == "google-mail" or app_name.lower() == "google mail":
            return GmailApp(self.user_id, integration, self.store)
        elif app_name.lower() == "google-calendar" or app_name.lower() == "google calendar":
            return GoogleCalendarApp(self.user_id, integration, self.store)
        else:
            logger.error(f"App {app_name} not found")
            return None
            
    
    def _load_apps(self):
        self.apps = self.store.list_apps()
        print(self.apps)
        for app in self.apps:
            app = self._init_app(app)
            if app is None:
                continue
            for tool in app.list_tools():
                self.add_tool(tool)

async def test():
    server = Server(port=8000)
    tools = await server.list_tools()
    print(tools)
    # result = await server.call_tool("send_email", {"to": "iamnishantg@gmail.com", "subject": "Test Email", "body": "This is a test email"})
    # result = await server.call_tool("get_today_events", {})
    result = await server.call_tool("star_repository", {"repo_full_name": "langchain-ai/langchain"})
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
    # server = Server(port=8000)
    # server.run(transport="sse")