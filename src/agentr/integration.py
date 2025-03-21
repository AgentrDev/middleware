from abc import abstractmethod, ABC
import httpx
import os

from loguru import logger
class Integration(ABC):
    def __init__(self, user_id, integration_id):
        self.integration_id = integration_id
        self.user_id = user_id

    @abstractmethod
    def get_authorize_url(self):
        pass

    @abstractmethod
    def get_connection_by_owner(self, user_id):
        pass

class NangoIntegration(Integration):
    def __init__(self, user_id, integration_id):
        self.integration_id = integration_id
        self.user_id = user_id
        self.nango_secret_key = os.getenv("NANGO_SECRET_KEY")

    def _create_session_token(self):
        url = "https://api.nango.dev/connect/sessions"
        body = {
            "end_user": {
                "id": self.user_id,
            },
            "allowed_integrations": [self.integration_id]
        }
        response = httpx.post(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"}, json=body)
        data = response.json()
        return data["data"]["token"]
    
    def get_authorize_url(self):
        session_token = self._create_session_token()
        return f"https://api.nango.dev/oauth/connect/{self.integration_id}?connect_session_token={session_token}"

    def get_connection_by_owner(self, user_id):
        url = f"https://api.nango.dev/connection?endUserId={user_id}"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.nango_secret_key}"})
        if response.status_code == 200:
            connections = response.json()["connections"]
            for connection in connections:
                if connection["provider_config_key"] == self.integration_id:
                    return connection["connection_id"]
        return None
    
class AgentRIntegration(Integration):
    def __init__(self, user_id, integration_id):
        self.base_url = "https://agentr.info/api"
        self.integration_id = integration_id
        self.user_id = user_id
        self.api_key = "41c23144-c779-4458-8edb-3607bc3a92d4"

    def _create_session_token(self):
        url = f"{self.base_url}/integrations/{self.integration_id}/fetch_nango_session/"
        body = {
            "owner": self.user_id
        }
        response = httpx.post(url, headers={"Authorization": f"Bearer {self.api_key}"}, json=body)
        response.raise_for_status()
        data = response.json()
        return data["data"]["token"]

    def get_authorize_url(self):
        session_token = self._create_session_token()
        return f"https://api.nango.dev/oauth/connect/{self.integration_id}?connect_session_token={session_token}"
    
    def get_connection_by_owner(self, user_id):
        url = f"{self.base_url}/integrations/{self.integration_id}/connections_from_owner/?owner={user_id}"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        connections = data.get("connection_ids", [])
        if len(connections) > 0:
            return connections[0]
        return None

