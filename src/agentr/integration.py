from abc import abstractmethod, ABC
import httpx

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
        self.nango_secret_key = "7261c2fd-91aa-4ba1-9657-a34b2a0e4272"

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
        self.integration_id = integration_id
        self.user_id = user_id
        self.api_key = "7261c2fd-91aa-4ba1-9657-a34b2a0e4272"
        
    def get_authorize_url(self):
        return f"https://api.agentr.ai/oauth/connect/{self.integration_id}"
    
    def get_connection_by_owner(self, user_id):
        url = f"https://api.agentr.dev/v1/credentials/{self.integration_id}?endUserId={user_id}"
        response = httpx.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
        if response.status_code == 200:
            return response.json()["data"]
        return None

