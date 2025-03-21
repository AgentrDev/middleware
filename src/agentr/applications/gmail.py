from agentr.application import Application
from agentr.integration import Integration
from agentr.store import Store
from loguru import logger
import httpx
import base64
from email.message import EmailMessage

class GmailApp(Application):
    def __init__(self, user_id, integration: Integration, store: Store) -> None:
        super().__init__(name="gmail", user_id=user_id, integration=integration, store=store)

    def _get_headers(self):
        credentials = self.store.retrieve_credential(self.integration.integration_id, self.connection_id)
        if "headers" in credentials:
            return credentials["headers"]
        return {
            "Authorization": f"Bearer {credentials['access_token']}",
            'Content-Type': 'application/json'
        }

    def send_email(self, to: str, subject: str, body: str) -> str:
        """Send an email
        
        Args:
            to: The email address of the recipient
            subject: The subject of the email
            body: The body of the email
            
        Returns:
        
            A confirmation message
        """
        if not self.validate():
            logger.warning("Connection not configured correctly")
            return self.authorize()
        try:
            url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
            
            # Create email in base64 encoded format
            email_message = {
                "raw": self._create_message(to, subject, body)
            }
            logger.info(email_message)
            
            # Use json parameter instead of data to properly format JSON
            response = httpx.post(url, headers=self._get_headers(), json=email_message)
            
            if response.status_code == 200:
                return f"Successfully sent email to {to}"
            else:
                logger.error(response.text)
                return f"Error sending email: {response.text}"
        except Exception as e:
            logger.error(e)
            return f"Error sending email: {e}"
            
    def _create_message(self, to, subject, body):
        message = EmailMessage()
        message['to'] = to
        message['from'] = "manojbajaj95@gmail.com"
        message['subject'] = subject
        message.set_content(body)
        
        # Encode as base64 string
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return raw
    
    def list_tools(self):
        return [self.send_email]