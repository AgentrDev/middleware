from agentr.application import Application
from agentr.integration import Integration
from agentr.store import Store
from loguru import logger

class ZenQuoteApp(Application):
    def __init__(self, user_id, integration: Integration = None, store: Store = None) -> None:
        super().__init__(name="zenquote", user_id=user_id, integration=integration, store=store)

    def get_quote(self) -> str:
        """Get an inspirational quote from the Zen Quotes API
        
        Returns:
            A random inspirational quote
        """
        url = "https://zenquotes.io/api/random"
        data = self._get(url)
        quote_data = data[0]
        return f"{quote_data['q']} - {quote_data['a']}"

    def list_tools(self):
        return [self.get_quote]