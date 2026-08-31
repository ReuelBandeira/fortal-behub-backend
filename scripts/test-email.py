#!/usr/bin/env python3
"""
Script para testar validação de email
"""

import requests
import json

API_BASE_URL = "http://localhost:3000"
KEYCLOAK_URL = "http://localhost:8080"

def get_access_token():
    """Obtém token de acesso do Keycloak"""
    try:
        token_url = f"{KEYCLOAK_URL}/realms/beehub-realm/protocol/openid-connect/token"
        
        data = {
            "username": "admin",
            "password": "admin123",
            "grant_type": "password",
            "client_id": "beehub-client",
            "client_secret": "mdwpKGM4w6HBAy0AY8lVA2HHDR3jNPr1"
        }
        
        response = requests.post(token_url, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"❌ Erro ao obter token: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao conectar com Keycloak: {str(e)}")
        return None

def test_email_endpoint(token, email):
    """Testa o endpoint /send com um email"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "to": [email],
            "subject": "Teste de Email - Beehub API",
            "body": "Este é um email de teste.",
            "priority": "normal"
        }
        
        print(f"\n🧪 Testando send com email: {email}")
        print(f"📤 Enviando dados: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            f"{API_BASE_URL}/email/send",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Resposta: {response.text}")
        
        if response.status_code == 200:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        return False

def main():
    print("🧪 Testando Validação de Email - Beehub API")
    print("=" * 50)
    
    # Obter token
    token = get_access_token()
    if not token:
        print("❌ Falha ao obter token")
        return
    
    # Lista de emails para testar
    emails_teste = [
        "reuel.bandeira30@gmail.com",
        "teste@exemplo.com",
        "admin@beehub.com",
        "test@test.com",
        "invalid-email",
        "test@",
        "@test.com",
        "test.email@domain.co.uk"
    ]
    
    # Testar cada email no endpoint /send
    for email in emails_teste:
        print(f"\n{'='*60}")
        print(f"🔍 TESTANDO EMAIL: {email}")
        print(f"{'='*60}")
        
        # Testar endpoint /send
        success_send = test_email_endpoint(token, email)
        
        print(f"\n📊 RESULTADO PARA {email}:")
        print(f"   /send: {'✅' if success_send else '❌'}")

if __name__ == "__main__":
    main()