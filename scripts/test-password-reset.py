#!/usr/bin/env python3
"""
Script de teste para o sistema de reset de senha
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configurações
API_BASE_URL = "http://localhost:3000"
KEYCLOAK_URL = "http://localhost:8080"

def get_access_token(username, password):
    """Obtém token de acesso do Keycloak"""
    try:
        token_url = f"{KEYCLOAK_URL}/realms/beehub-realm/protocol/openid-connect/token"
        
        data = {
            "username": username,
            "password": password,
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

def test_request_password_reset(email):
    """Testa a solicitação de reset de senha"""
    try:
        headers = {"Content-Type": "application/json"}
        
        data = {
            "email": email
        }
        
        print(f"📤 Solicitando reset de senha para: {email}")
        
        response = requests.post(
            f"{API_BASE_URL}/auth/request-password-reset",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Reset solicitado com sucesso: {result}")
            return True
        else:
            print(f"❌ Erro ao solicitar reset: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao solicitar reset: {str(e)}")
        return False

def test_validate_reset_code(email, code):
    """Testa a validação de código de reset"""
    try:
        headers = {"Content-Type": "application/json"}
        
        data = {
            "email": email,
            "code": code
        }
        
        print(f"📤 Validando código: {code} para {email}")
        
        response = requests.post(
            f"{API_BASE_URL}/auth/validate-reset-code",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validação concluída: {result}")
            return result.get("valid", False)
        else:
            print(f"❌ Erro na validação: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na validação: {str(e)}")
        return False

def test_reset_password(email, code, new_password):
    """Testa o reset de senha"""
    try:
        headers = {"Content-Type": "application/json"}
        
        data = {
            "email": email,
            "code": code,
            "new_password": new_password
        }
        
        print(f"📤 Resetando senha para: {email}")
        
        response = requests.post(
            f"{API_BASE_URL}/auth/reset-password",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Senha resetada com sucesso: {result}")
            return True
        else:
            print(f"❌ Erro ao resetar senha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao resetar senha: {str(e)}")
        return False

def test_clear_expired_codes(token):
    """Testa a limpeza de códigos expirados"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("📤 Limpando códigos expirados...")
        
        response = requests.post(
            f"{API_BASE_URL}/auth/clear-expired-codes",
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Códigos limpos com sucesso: {result}")
            return True
        else:
            print(f"❌ Erro ao limpar códigos: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao limpar códigos: {str(e)}")
        return False

def test_user_sync(token):
    """Testa a sincronização de usuário"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print("📤 Testando sincronização de usuário...")
        
        # Fazer uma requisição autenticada para triggerar a sincronização
        response = requests.get(
            f"{API_BASE_URL}/enterprise",
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Sincronização de usuário funcionando")
            return True
        else:
            print(f"❌ Erro na sincronização: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na sincronização: {str(e)}")
        return False

def main():
    print("🧪 Testando Sistema de Reset de Senha - Beehub API")
    print("=" * 60)
    
    # Verificar se a API está rodando
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ API não está respondendo")
            sys.exit(1)
        print("✅ API está respondendo")
    except Exception as e:
        print(f"❌ Não foi possível conectar com a API: {str(e)}")
        sys.exit(1)
    
    # Obter token de acesso
    print("\n🔑 Obtendo token de acesso...")
    token = get_access_token("admin", "admin123")
    
    if not token:
        print("❌ Falha ao obter token de acesso")
        sys.exit(1)
    
    print("✅ Token obtido com sucesso")
    
    # Testar sincronização de usuário
    print("\n🔄 Testando sincronização de usuário...")
    if not test_user_sync(token):
        print("❌ Sincronização de usuário falhou")
        sys.exit(1)
    
    # Testar solicitação de reset de senha
    print("\n📧 Testando solicitação de reset de senha...")
    test_email = "admin@beehub.com"
    if not test_request_password_reset(test_email):
        print("❌ Solicitação de reset falhou")
        sys.exit(1)
    
    # Testar validação de código (com código inválido)
    print("\n🔍 Testando validação de código inválido...")
    if test_validate_reset_code(test_email, "000000"):
        print("❌ Código inválido foi aceito")
        sys.exit(1)
    else:
        print("✅ Código inválido rejeitado corretamente")
    
    # Testar limpeza de códigos expirados
    print("\n🧹 Testando limpeza de códigos expirados...")
    if not test_clear_expired_codes(token):
        print("❌ Limpeza de códigos falhou")
        sys.exit(1)
    
    print("\n🎉 Todos os testes passaram com sucesso!")
    print("✅ Sistema de reset de senha está funcionando corretamente")
    print("\n📝 Notas:")
    print("- Para testar o reset completo, verifique o email enviado")
    print("- Use o código recebido para testar a validação e reset")
    print("- O sistema está configurado para sincronizar usuários automaticamente")

if __name__ == "__main__":
    main() 