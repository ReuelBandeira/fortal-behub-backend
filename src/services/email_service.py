import msal
import requests
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.config import EMAIL_SENDER, EMAIL_CLIENT_ID, EMAIL_CLIENT_SECRET, EMAIL_TENANT_ID
from src.schemas.email import EmailRequest, EmailResponse, EmailError
import traceback

class EmailService:
    def __init__(self):
        self.sender = EMAIL_SENDER
        self.client_id = EMAIL_CLIENT_ID
        self.client_secret = EMAIL_CLIENT_SECRET
        self.tenant_id = EMAIL_TENANT_ID
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self._access_token = None
        self._token_expires_at = None

    def _get_access_token(self) -> str:
        """
        Obtém um token de acesso para a Microsoft Graph API
        """
        try:
            # Criar aplicação MSAL
            app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )

            # Obter token usando client credentials flow
            result = app.acquire_token_for_client(scopes=self.scope)
            
            if "access_token" in result:
                self._access_token = result["access_token"]
                self._token_expires_at = datetime.now().timestamp() + result.get("expires_in", 3600)
                return self._access_token
            else:
                error_msg = f"Erro ao obter token: {result.get('error_description', 'Erro desconhecido')}"
                print(f"Erro de autenticação: {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            print(f"Erro ao obter token de acesso: {str(e)}")
            traceback.print_exc()
            raise Exception(f"Falha na autenticação com Microsoft Graph: {str(e)}")

    def _is_token_valid(self) -> bool:
        """
        Verifica se o token atual ainda é válido
        """
        if not self._access_token or not self._token_expires_at:
            return False
        
        # Token expira 5 minutos antes do tempo real para evitar problemas
        return datetime.now().timestamp() < (self._token_expires_at - 300)

    def _get_valid_token(self) -> str:
        """
        Obtém um token válido, renovando se necessário
        """
        if not self._is_token_valid():
            return self._get_access_token()
        return self._access_token

    def send_email(self, email_request: EmailRequest) -> EmailResponse:
        """
        Envia um email usando Microsoft Graph API
        """
        try:
            token = self._get_valid_token()
            
            # Preparar dados do email
            email_data = {
                "message": {
                    "subject": email_request.subject,
                    "body": {
                        "contentType": "HTML" if email_request.html_body else "Text",
                        "content": email_request.html_body or email_request.body
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": recipient}}
                        for recipient in email_request.to
                    ],
                    "importance": email_request.priority.upper()
                },
                "saveToSentItems": True
            }

            # Adicionar CC se fornecido
            if email_request.cc:
                email_data["message"]["ccRecipients"] = [
                    {"emailAddress": {"address": recipient}}
                    for recipient in email_request.cc
                ]

            # Adicionar BCC se fornecido
            if email_request.bcc:
                email_data["message"]["bccRecipients"] = [
                    {"emailAddress": {"address": recipient}}
                    for recipient in email_request.bcc
                ]

            # Fazer requisição para Microsoft Graph
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            url = f"https://graph.microsoft.com/v1.0/users/{self.sender}/sendMail"
            
            response = requests.post(
                url=url,
                headers=headers,
                json=email_data,
                timeout=30
            )

            if response.status_code == 202:
                # Email enviado com sucesso
                message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(email_request.to))}"
                
                return EmailResponse(
                    message_id=message_id,
                    status="sent",
                    sent_at=datetime.now().isoformat(),
                    recipients=email_request.to
                )
            else:
                error_msg = f"Erro ao enviar email: {response.status_code} - {response.text}"
                print(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            traceback.print_exc()
            raise Exception(f"Falha no envio de email: {str(e)}")

    def send_bulk_email(self, email_requests: List[EmailRequest]) -> List[EmailResponse]:
        """
        Envia múltiplos emails em lote
        """
        responses = []
        for email_request in email_requests:
            try:
                response = self.send_email(email_request)
                responses.append(response)
            except Exception as e:
                # Criar resposta de erro
                error_response = EmailResponse(
                    message_id="",
                    status="error",
                    sent_at=datetime.now().isoformat(),
                    recipients=email_request.to
                )
                responses.append(error_response)
                print(f"Erro ao enviar email para {email_request.to}: {str(e)}")
        
        return responses

# Instância global do serviço
_email_service = None

def get_email_service() -> EmailService:
    """
    Retorna uma instância do serviço de email (singleton)
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service 