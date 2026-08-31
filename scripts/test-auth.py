#!/usr/bin/env python3
"""
Script para testar a autenticação com os usuários criados no Keycloak
"""

import requests
import json
import sys
from typing import Dict, Any

# Configurações
KEYCLOAK_URL = "http://localhost:8080"
API_URL = "http://localhost:3000"
REALM_NAME = "beehub-realm"
CLIENT_ID = "beehub-client"
CLIENT_SECRET = "mdwpKGM4w6HBAy0AY8lVA2HHDR3jNPr1"

# Usuários de teste
TEST_USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "role": "admin"
    },
    {
        "username": "user", 
        "password": "user123",
        "role": "user"
    },
    {
        "username": "moderator",
        "password": "mod123", 
        "role": "moderator"
    }
]

def get_token(username: str, password: str) -> str:
    """Obtém token de acesso para um usuário"""
    url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    data = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except requests.RequestException as e:
        print(f"❌ Erro ao obter token para {username}: {e}")
        return None

def test_api_endpoint(token: str, endpoint: str, description: str) -> bool:
    """Testa um endpoint da API com token"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_URL}{endpoint}", headers=headers)
        if response.status_code == 200:
            print(f"  ✅ {description}: OK")
            return True
        else:
            print(f"  ❌ {description}: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"  ❌ {description}: Erro de conexão - {e}")
        return False

def test_user_authentication(user: Dict[str, str]):
    """Testa autenticação completa para um usuário"""
    print(f"\n🔐 Testando usuário: {user['username']} (role: {user['role']})")
    print("=" * 50)
    
    # 1. Obter token
    print("1️⃣ Obtendo token de acesso...")
    token = get_token(user['username'], user['password'])
    if not token:
        print("❌ Falha ao obter token")
        return False
    
    print("✅ Token obtido com sucesso!")
    
    # 2. Testar endpoint /auth/me
    print("\n2️⃣ Testando endpoint /auth/me...")
    success = test_api_endpoint(token, "/auth/me", "Informações do usuário")
    
    # 3. Testar UserInfo endpoint do Keycloak
    print("\n3️⃣ Testando UserInfo endpoint do Keycloak...")
    try:
        userinfo_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/userinfo"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(userinfo_url, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print("  ✅ UserInfo: OK")
            print(f"     Username: {user_info.get('preferred_username', 'N/A')}")
            print(f"     Email: {user_info.get('email', 'N/A')}")
            print(f"     Name: {user_info.get('name', 'N/A')}")
            print(f"     Sub: {user_info.get('sub', 'N/A')}")
            print(f"     Roles: {user_info.get('realm_access', {}).get('roles', [])}")
        elif response.status_code == 403:
            print("  ⚠️ UserInfo: 403 - Endpoint não configurado para este client")
            print("     (Isso é normal se o client não tiver permissão para UserInfo)")
        else:
            print(f"  ❌ UserInfo: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  ❌ UserInfo: Erro de conexão - {e}")
    
    # 4. Testar endpoint /enterprise (protegido)
    print("\n4️⃣ Testando endpoint /enterprise...")
    success &= test_api_endpoint(token, "/enterprise", "Lista de empresas")
    
    # 5. Testar endpoint raiz (não protegido)
    print("\n5️⃣ Testando endpoint raiz (sem autenticação)...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("  ✅ Endpoint raiz: OK")
        else:
            print(f"  ❌ Endpoint raiz: {response.status_code}")
    except requests.RequestException as e:
        print(f"  ❌ Endpoint raiz: Erro de conexão - {e}")
    
    return success

def test_invalid_token():
    """Testa comportamento com token inválido"""
    print(f"\n🚫 Testando com token inválido...")
    print("=" * 50)
    
    invalid_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.invalid"
    
    success = test_api_endpoint(invalid_token, "/auth/me", "Token inválido")
    if not success:
        print("✅ Comportamento correto: API rejeitou token inválido")
    else:
        print("❌ Problema: API aceitou token inválido")

def test_no_token():
    """Testa comportamento sem token"""
    print(f"\n🚫 Testando sem token...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_URL}/auth/me")
        if response.status_code == 401:
            print("✅ Comportamento correto: API rejeitou requisição sem token")
        else:
            print(f"❌ Problema: API aceitou requisição sem token - {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

def test_keycloak_openid_endpoints():
    """Testa os endpoints principais do Keycloak OpenID Connect"""
    print(f"\n🔗 Testando Endpoints OpenID Connect do Keycloak...")
    print("=" * 60)
    
    # 1. Obter token primeiro
    print("1️⃣ Obtendo token de acesso...")
    token = get_token("admin", "admin123")
    if not token:
        print("❌ Falha ao obter token para testar endpoints")
        return False
    
    print("✅ Token obtido com sucesso!")
    
    # 2. Testar UserInfo endpoint
    print("\n2️⃣ Testando UserInfo endpoint...")
    try:
        userinfo_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/userinfo"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(userinfo_url, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ UserInfo endpoint funcionando!")
            print(f"   Username: {user_info.get('preferred_username', 'N/A')}")
            print(f"   Email: {user_info.get('email', 'N/A')}")
            print(f"   Name: {user_info.get('name', 'N/A')}")
            print(f"   Sub: {user_info.get('sub', 'N/A')}")
        else:
            print(f"❌ UserInfo falhou: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro no UserInfo: {e}")
        return False
    
    # 3. Testar Logout endpoint (com refresh token)
    print("\n3️⃣ Testando Logout endpoint...")
    try:
        # Primeiro obter refresh token
        token_response = requests.post(f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token", data={
            "username": "admin",
            "password": "admin123",
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        })
        
        if token_response.status_code == 200:
            refresh_token = token_response.json().get("refresh_token")
            
            if refresh_token:
                logout_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/logout"
                logout_data = {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "refresh_token": refresh_token
                }
                
                logout_response = requests.post(logout_url, data=logout_data)
                print(f"   Status: {logout_response.status_code}")
                
                if logout_response.status_code in [200, 204]:
                    print("✅ Logout endpoint funcionando!")
                else:
                    print(f"⚠️ Logout retornou: {logout_response.status_code}")
            else:
                print("⚠️ Refresh token não disponível para teste de logout")
        else:
            print(f"❌ Erro ao obter refresh token: {token_response.status_code}")
    except Exception as e:
        print(f"❌ Erro no Logout: {e}")
    
    # 4. Testar Token endpoint (já testado, mas vamos mostrar detalhes)
    print("\n4️⃣ Detalhes do Token endpoint...")
    try:
        token_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
        token_data = {
            "username": "admin",
            "password": "admin123",
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        
        response = requests.post(token_url, data=token_data)
        if response.status_code == 200:
            token_info = response.json()
            print("✅ Token endpoint funcionando!")
            print(f"   Access Token: {token_info.get('access_token', '')[:50]}...")
            print(f"   Token Type: {token_info.get('token_type', 'N/A')}")
            print(f"   Expires In: {token_info.get('expires_in', 'N/A')}s")
            print(f"   Refresh Expires In: {token_info.get('refresh_expires_in', 'N/A')}s")
            print(f"   Scope: {token_info.get('scope', 'N/A')}")
            print(f"   Session State: {token_info.get('session_state', 'N/A')}")
        else:
            print(f"❌ Token endpoint falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no Token endpoint: {e}")
        return False
    
    print("\n✅ Todos os endpoints OpenID Connect testados!")
    return True

def main():
    """Função principal"""
    print("🚀 Testando Autenticação - Beehub API")
    print("=" * 60)
    
    # Verificar se a API está rodando
    print("🔍 Verificando se a API está rodando...")
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ API está rodando!")
        else:
            print(f"❌ API não está respondendo corretamente: {response.status_code}")
            sys.exit(1)
    except requests.RequestException:
        print("❌ API não está acessível. Verifique se está rodando em http://localhost:3000")
        sys.exit(1)
    
    # Verificar se o Keycloak está rodando
    print("\n🔍 Verificando se o Keycloak está rodando...")
    try:
        response = requests.get(f"{KEYCLOAK_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Keycloak está rodando!")
        else:
            print(f"❌ Keycloak não está respondendo corretamente: {response.status_code}")
            sys.exit(1)
    except requests.RequestException:
        print("❌ Keycloak não está acessível. Verifique se está rodando em http://localhost:8080")
        sys.exit(1)
    
    # Testar endpoints OpenID Connect do Keycloak
    test_keycloak_openid_endpoints()
    
    # Testar cada usuário
    total_success = 0
    for user in TEST_USERS:
        if test_user_authentication(user):
            total_success += 1
    
    # Testar casos de erro
    test_invalid_token()
    test_no_token()
    
    # Resumo
    print(f"\n📊 Resumo dos Testes")
    print("=" * 60)
    print(f"✅ Usuários testados com sucesso: {total_success}/{len(TEST_USERS)}")
    
    if total_success == len(TEST_USERS):
        print("🎉 Todos os testes de autenticação passaram!")
        print("\n🔗 Links úteis:")
        print(f"  • API: {API_URL}")
        print(f"  • Documentação da API: {API_URL}/docs")
        print(f"  • Keycloak Admin: {KEYCLOAK_URL}")
        print(f"  • Realm: {REALM_NAME}")
        print(f"\n🔗 Endpoints OpenID Connect testados:")
        print(f"  • Token: {KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token")
        print(f"  • UserInfo: {KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/userinfo")
        print(f"  • Logout: {KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/logout")
    else:
        print("⚠️ Alguns testes falharam. Verifique a configuração.")
        sys.exit(1)

if __name__ == "__main__":
    main() 