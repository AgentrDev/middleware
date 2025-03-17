from mcp.server.fastmcp import FastMCP
from loguru import logger
from abc import abstractmethod, ABC
import httpx

class NangoStore:
    def __init__(self) -> None:
        self.user_id = "1234567890"
        self.organization_id = "1234567890"
        self.nango_secret_key = "7261c2fd-91aa-4ba1-9657-a34b2a0e4272"
    
    def list_integrations(self):
        url = "https://api.nango.dev/integrations"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"})
        if response.status_code == 200:
            return response.json()["data"]
        logger.error(f"Failed to list integrations: {response.text}")
        return []
    
    def retrieve_default_connection(self, integration_id):
        url = "https://api.nango.dev/connection"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"})
        if response.status_code == 200:
            connections = response.json()["connections"]
            for connection in connections:
                if connection["provider_config_key"] == integration_id:
                    return connection["connection_id"]
        logger.error(f"Failed to retrieve default credential: {response.text}")
        return None
    
    def retrieve_credential(self, integration_id, connection_id):
        url = f"https://api.nango.dev/connection/{connection_id}?provider_config_key={integration_id}"
        logger.info(url)
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"})
        data = response.json()
        logger.info(data)
        return data["credentials"]
    
    def create_session_token(self, integration_id):
        url = "https://api.nango.dev/connect/sessions"
        body = {
            "end_user": {
                "id": self.user_id,
            },
            "allowed_integrations": [integration_id]
        }
        response = httpx.post(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"}, json=body)
        data = response.json()
        return data["data"]["token"]
    

class Application(ABC):
    """ An Application is an collection of tools"""
    def __init__(self, name, store) -> None:
        self.name = name
        self.store = store
        self.connection_id = None
        self.integration_id = None
    
    @abstractmethod
    def _get_headers(self):
        pass

    def _get(self, url):
        headers = self._get_headers()
        response = httpx.get(url, headers=headers)
        return response
    
    def _post(self, url, data):
        headers = self._get_headers()
        response = httpx.post(url, headers=headers, data=data)
        return response

    def _put(self, url, data):
        headers = self._get_headers()
        response = httpx.put(url, headers=headers, data=data)
        return response

    def _delete(self, url):
        headers = self._get_headers()
        response = httpx.delete(url, headers=headers)
        return response

    def set_integration_id(self, integration_id):
        self.integration_id = integration_id

    def set_connection_id(self, connection_id):
        self.connection_id = connection_id

    def validate(self):
        # Check if the integration is Valid
        if not self.integration_id:
            raise Exception("Integration ID is not set. Improperly Configured")
        if not self.connection_id:
            connection_id = self.store.retrieve_default_connection(self.integration_id)
            if not connection_id:
                return False
            self.connection_id = connection_id
        return True
    
    def authorize(self):
        # Authorize the integration, only do if it is not valid
        session_token = self.store.create_session_token(self.integration_id)
        url = 'https://api.nango.dev' + f'/oauth/connect/{self.integration_id}?connect_session_token={session_token}'
        return f"You need an active connection to use this app. Please connect at {url}"

    @abstractmethod
    def list_tools(self):
        # Iterate over all tools available in the app
       pass

# class Integration:
#     """
#     An integration is an app with different config.
#     Eg, GMAIL app with only send scope & GMAIL with read and send are treated separate integrations.
#     """
#     def __init__(self, name) -> None:
#         self.name = name


class GithubApp(Application):
    def __init__(self, store) -> None:
        super().__init__(name="github", store=store)

    def _get_headers(self):
        credentials = self.store.retrieve_credential(self.integration_id, self.connection_id)
        logger.info(credentials)
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
        if not self.validate():
            logger.warning("Connection not configured correctly")
            return self.authorize()
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
    
    def list_tools(self):
        return [self.star_repository]
    

class Server(FastMCP):
    def __init__(self, user_id, workspace_id, **settings) -> None:
        super().__init__(name="AgentR", **settings)
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.integrations = []
        self.apps = {}
        self.store = NangoStore()
        self._load_integrations()
        self._load_tools()


    def _app_from_id(self, app_id):
        if app_id == "github":
            return GithubApp(self.store)
        else:
            raise Exception(f"App {app_id} not found")
    
    def _load_integrations(self):
        self.integrations = self.store.list_integrations()
        for integration in self.integrations:
            integration_id = integration.get("unique_key")
            app_name = integration.get("provider")
            app = self._app_from_id(app_name)
            app.set_integration_id(integration_id)
            self.apps[app_name] = app
    
    def _load_tools(self):
        for app_name, app in self.apps.items():
            for tool in app.list_tools():
                self.add_tool(tool)

    

mcp = Server(user_id="123", workspace_id="345", port=8001)

async def test():
    tools = await mcp.list_tools()  
    print(tools)
    result = await mcp.call_tool("star_repository", {"repo_full_name": "manojbajaj95/config"})
    print(result)
    # mcp.run(transport='sse')

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())