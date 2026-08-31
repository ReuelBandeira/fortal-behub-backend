from sqlalchemy.orm import Session
from src.repositories.keycloak_user import KeycloakUserRepository
from src.services.email_service import get_email_service
from src.models.keycloak_user import KeycloakUserModel
from typing import Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import secrets
import requests
import json


class PasswordResetService:
    def __init__(self, db: Session):
        self.repository = KeycloakUserRepository(db)
        self.email_service = get_email_service()
        # Configurações do Keycloak
        self.keycloak_url = "http://keycloak:8080"  # Usar nome do serviço Docker
        self.realm = "beehub-realm"
        self.client_id = "beehub-client"
        self.client_secret = "mdwpKGM4w6HBAy0AY8lVA2HHDR3jNPr1"
        self.admin_username = "admin"
        self.admin_password = "admin123"

    def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """
        Solicita reset de senha para um email
        
        Args:
            email: Email do usuário
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Buscar usuário pelo email
            user = self.repository.get_by_email(email.lower())
            if not user:
                return False, "Email não encontrado"
            
            # Gerar código de reset
            reset_code = user.generate_reset_code()
            
            # Salvar código no banco
            self.repository.db.commit()
            
            # Enviar email com código
            self._send_reset_email(user, reset_code)
            
            return True, "Código de verificação enviado com sucesso"
            
        except Exception as e:
            print(f"Erro ao solicitar reset de senha: {str(e)}")
            return False, "Erro interno, tente novamente"

    def validate_reset_code(self, email: str, code: str) -> Tuple[bool, str]:
        """
        Valida código de reset
        
        Args:
            email: Email do usuário
            code: Código de verificação
            
        Returns:
            Tuple[bool, str]: (válido, mensagem)
        """
        try:
            user = self.repository.get_by_email(email.lower())
            if not user:
                return False, "Email não encontrado"
            
            if user.validate_reset_code(code):
                return True, "Código válido"
            else:
                if user.is_reset_code_expired():
                    return False, "Código expirado"
                else:
                    return False, "Código inválido"
                    
        except Exception as e:
            print(f"Erro ao validar código: {str(e)}")
            return False, "Erro interno"

    def _get_keycloak_admin_token(self) -> Optional[str]:
        """
        Obtém token de administrador do Keycloak
        
        Returns:
            str: Token de acesso ou None se falhar
        """
        try:
            token_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
            
            data = {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.admin_username,
                "password": self.admin_password
            }
            
            response = requests.post(token_url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            else:
                print(f"Erro ao obter token admin: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao conectar com Keycloak: {str(e)}")
            return None

    def _reset_password_in_keycloak(self, keycloak_user_id: str, new_password: str) -> bool:
        """
        Reseta senha do usuário no Keycloak
        
        Args:
            keycloak_user_id: ID do usuário no Keycloak
            new_password: Nova senha
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            # Obter token de administrador
            admin_token = self._get_keycloak_admin_token()
            if not admin_token:
                print("Falha ao obter token de administrador")
                return False
            
            # URL para reset de senha
            reset_url = f"{self.keycloak_url}/admin/realms/{self.realm}/users/{keycloak_user_id}/reset-password"
            
            # Headers com token de administrador
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            # Body da requisição
            payload = {
                "temporary": False,
                "type": "password",
                "value": new_password
            }
            
            # Fazer requisição PUT para resetar senha
            response = requests.put(reset_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 204:
                print(f"Senha resetada com sucesso no Keycloak para usuário {keycloak_user_id}")
                return True
            else:
                print(f"Erro ao resetar senha no Keycloak: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Erro ao resetar senha no Keycloak: {str(e)}")
            return False

    def reset_password_with_code(self, email: str, code: str, new_password: str) -> Tuple[bool, str]:
        """
        Reseta senha usando código de verificação
        
        Args:
            email: Email do usuário
            code: Código de verificação
            new_password: Nova senha
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Buscar usuário por email e código de reset válido
            user = self.repository.get_by_reset_code(email.lower(), code)
            if not user:
                return False, "Código inválido ou expirado"
            
            # Resetar senha no Keycloak usando o keycloak_user_id obtido
            keycloak_success = self._reset_password_in_keycloak(user.keycloak_user_id, new_password)
            
            if not keycloak_success:
                return False, "Erro ao alterar senha no sistema de autenticação"
            
            # Limpar código de reset após sucesso
            user.clear_reset_code()
            self.repository.db.commit()
            
            return True, "Senha alterada com sucesso"
            
        except Exception as e:
            print(f"Erro ao resetar senha: {str(e)}")
            return False, "Erro interno, tente novamente"

    def _send_reset_email(self, user: KeycloakUserModel, reset_code: str):
        """
        Envia email com código de reset
        """
        try:
            # Template HTML do email
            html_content = self._generate_reset_email_html(user, reset_code)
            
            # Preparar dados do email
            from src.schemas.email import EmailRequest
            
            email_request = EmailRequest(
                to=[user.email],
                subject="Código de Verificação - Reset de Senha",
                body=f"Código de verificação: {reset_code}\nVálido por: 20 minutos\nSe você não solicitou, ignore este email.",
                html_body=html_content,
                priority="high"
            )
            
            # Enviar email
            self.email_service.send_email(email_request)
            
        except Exception as e:
            print(f"Erro ao enviar email de reset: {str(e)}")
            raise

    def _generate_reset_email_html(self, user: KeycloakUserModel, reset_code: str) -> str:
        """
        Gera template HTML para email de reset
        """
        user_name = user.first_name or user.username
        
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Código de Verificação</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .code {{
                    background-color: #3498db;
                    color: white;
                    padding: 15px;
                    font-size: 24px;
                    font-weight: bold;
                    text-align: center;
                    border-radius: 5px;
                    margin: 20px 0;
                    letter-spacing: 5px;
                }}
                .warning {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Beehub</div>
                    <h2>Código de Verificação</h2>
                </div>
                
                <p>Olá {user_name},</p>
                
                <p>Você solicitou a redefinição da sua senha. Use o código abaixo para continuar:</p>
                
                <div class="code">{reset_code}</div>
                
                <p><strong>Este código é válido por 20 minutos.</strong></p>
                
                <div class="warning">
                    <strong>⚠️ Importante:</strong> Se você não solicitou esta redefinição de senha, 
                    ignore este email. Sua senha permanecerá inalterada.
                </div>
                
                <p>Se você tiver alguma dúvida, entre em contato conosco.</p>
                
                <div class="footer">
                    <p>Este é um email automático, não responda a esta mensagem.</p>
                    <p>© 2025 Beehub. Todos os direitos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def clear_expired_codes(self):
        """
        Limpa códigos de reset expirados
        """
        try:
            # Buscar usuários com códigos expirados
            expired_users = self.repository.db.query(KeycloakUserModel).filter(
                KeycloakUserModel.reset_code_expires_at < datetime.utcnow(),
                KeycloakUserModel.reset_code.isnot(None)
            ).all()
            
            for user in expired_users:
                user.clear_reset_code()
            
            self.repository.db.commit()
            print(f"Limpos {len(expired_users)} códigos expirados")
            
        except Exception as e:
            print(f"Erro ao limpar códigos expirados: {str(e)}")
            self.repository.db.rollback() 