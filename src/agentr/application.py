from abc import abstractmethod, ABC
import httpx
from agentr.integration import Integration
from agentr.store import Store

class Application(ABC):
    """ An Application is an collection of tools"""
    def __init__(self, name, user_id, integration: Integration = None, store: Store = None) -> None:
        self.name = name
        self.user_id = user_id
        self.integration = integration
        self.store = store
        self.connection_id = None

    def _get_headers(self):
        return {}
    
    def _get(self, url, params=None):
        headers = self._get_headers()
        response = httpx.get(url, headers=headers, params=params)
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

    def set_connection_id(self, connection_id):
        self.connection_id = connection_id

    def validate(self):
        # Check if the integration is Valid
        if not self.integration:
            raise Exception("Integration is not set. Improperly Configured")
        if not self.connection_id:
            connection_id = self.integration.get_connection_by_owner(self.user_id)
            if not connection_id:
                return False
            self.connection_id = connection_id
        return True
    
    def authorize(self):
        # Authorize the integration, only do if it is not valid
        url = self.integration.get_authorize_url()
        return f"You need an active connection to use this app. Please connect at {url}"

    @abstractmethod
    def list_tools(self):
        # Iterate over all tools available in the app
       pass

