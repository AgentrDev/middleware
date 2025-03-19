import httpx
from loguru import logger
from abc import abstractmethod, ABC


class Store(ABC):
    def __init__(self, user_id, organization_id = None) -> None:
        self.user_id = user_id
        self.organization_id = organization_id

    @abstractmethod
    def list_integrations(self):
        pass

    @abstractmethod
    def retrieve_credential(self, integration_id, connection_id):
        pass

class NangoStore(Store):
    def __init__(self, user_id, organization_id = None) -> None:
        self.user_id = user_id
        self.organization_id = organization_id
        self.nango_secret_key = "7261c2fd-91aa-4ba1-9657-a34b2a0e4272"
    
    def list_integrations(self):
        url = "https://api.nango.dev/integrations"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"})
        if response.status_code == 200:
            return response.json()["data"]
        logger.error(f"Failed to list integrations: {response.text}")
        return []
    
    def retrieve_credential(self, integration_id, connection_id):
        url = f"https://api.nango.dev/connection/{connection_id}?provider_config_key={integration_id}"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"})
        data = response.json()
        return data["credentials"]