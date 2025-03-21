import httpx
from loguru import logger
from abc import abstractmethod, ABC
import os

class Store(ABC):
    def __init__(self, user_id, organization_id = None) -> None:
        self.user_id = user_id
        self.organization_id = organization_id

    @abstractmethod
    def list_apps(self) -> list:
        """
        Returns a list of apps with the following structure:
        [
            {"integration_id": "uuid", "app_id": "github", "integration_type": "nango"},
            {"integration_id": "uuid", "app_id": "zenquote", "integration_type": "self"}
        ]

        Should not return duplicate apps.
        """
        pass

    @abstractmethod
    def retrieve_credential(self, integration_id, connection_id):
        pass

class NangoStore(Store):
    def __init__(self, user_id, organization_id = None) -> None:
        self.user_id = user_id
        self.organization_id = organization_id
        self.nango_secret_key = os.getenv("NANGO_SECRET_KEY")
    
    def list_apps(self):
        url = "https://api.nango.dev/integrations"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"})
        response.raise_for_status()
        apps = {}
        integrations = response.json()["data"]
        for i in integrations:
            app_id = i["provider"]
            integration_id = i["unique_key"]
            if app_id not in apps:
                apps[app_id] = {"integration_id": integration_id, "app_id": app_id, "integration_type": "nango"}
        return list(apps.values())
    
    def retrieve_credential(self, integration_id, connection_id):
        url = f"https://api.nango.dev/connection/{connection_id}?provider_config_key={integration_id}"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"})
        data = response.json()
        return data["credentials"]
    
class AgentRStore(Store):
    def __init__(self, user_id, organization_id = None) -> None:
        super().__init__(user_id, organization_id)
        self.base_url = "https://agentr.info/api"
        self.api_key = "41c23144-c779-4458-8edb-3607bc3a92d4"

        
    def list_apps(self):
        url = f"{self.base_url}/apps/list_apps_with_default_integration/"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
        response.raise_for_status()
        apps = response.json()
        logger.info(f"Apps: {apps}")
        return [{"integration_id": a["default_integration"].strip("/").split("/")[-1], "app_id": a["name"], "integration_type": "agentr"} for a in apps]
        
    def retrieve_credential(self, integration_id, connection_id):
        url = f"{self.base_url}/connections/{connection_id}/auth_headers/"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return {"headers": data}
    
class TestStore(Store):
    def __init__(self, user_id, organization_id = None) -> None:
        super().__init__(user_id, organization_id)
        self.integrations = [{"integration_id": "uuid", "app_id": "github", "integration_type": "nango"},
                             {"integration_id": "uuid", "app_id": "zenquote", "integration_type": "self"}]

    def list_integrations(self):
        return self.integrations
    
    def retrieve_credential(self, integration_id, connection_id):
        return {"credentials": {"access_token": "1234567890"}}