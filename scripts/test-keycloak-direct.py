#!/usr/bin/env python3
"""
Script para testar diretamente a autenticação no Keycloak
"""

import requests
import json

# Configurações
KEYCLOAK_URL = "http://localhost:8080"
REALM_NAME = "beehub-realm"
CLIENT_ID = "beehub-client"
CLIENT_SECRET = "mdwpKGM4w6HBAy0AY8lVA2HHDR3jNPr1"

def test_keycloak_direct():
    """Testa autenticação diretamente no Keycloak"""
    print("🔍 Testando Keycloak diretamente...")
    
    # 1. Testar se o realm existe
    print("\n1️⃣ Verificando se o realm existe...")
    try:
        response = requests.get(f"{KEYCLOAK_URL}/realms/{REALM_NAME}")
        if response.status_code == 200:
            print("✅ Realm encontrado!")
            realm_info = response.json()
            print(f"   Nome: {realm_info.get('realm')}")
        else:
            print(f"❌ Realm não encontrado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar realm: {e}")
        return False
    
    # 2. Testar se o client existe
    print("\n2️⃣ Verificando se o client existe...")
    try:
        # Primeiro obter token de admin
        admin_token_url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
        admin_data = {
            "username": "admin",
            "password": "admin",
            "grant_type": "password",
            "client_id": "admin-cli"
        }
        
        admin_response = requests.post(admin_token_url, data=admin_data)
        if admin_response.status_code != 200:
            print(f"❌ Erro ao obter token de admin: {admin_response.status_code}")
            return False
        
        admin_token = admin_response.json()["access_token"]
        
        # Agora verificar o client
        client_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients"
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        client_response = requests.get(client_url, headers=headers)
        if client_response.status_code == 200:
            clients = client_response.json()
            client = next((c for c in clients if c["clientId"] == CLIENT_ID), None)
            if client:
                print("✅ Client encontrado!")
                print(f"   ID: {client['id']}")
                print(f"   Client ID: {client['clientId']}")
                print(f"   Enabled: {client.get('enabled', False)}")
            else:
                print("❌ Client não encontrado!")
                return False
        else:
            print(f"❌ Erro ao verificar client: {client_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar client: {e}")
        return False
    
    # 3. Testar autenticação de usuário
    print("\n3️⃣ Testando autenticação de usuário...")
    try:
        token_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
        data = {
            "username": "admin",
            "password": "admin123",
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        
        response = requests.post(token_url, data=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Autenticação bem-sucedida!")
            print(f"   Access Token: {token_data.get('access_token', '')[:50]}...")
            print(f"   Token Type: {token_data.get('token_type', '')}")
            print(f"   Expires In: {token_data.get('expires_in', '')}")
            
            # 4. Testar userinfo
            print("\n4️⃣ Testando userinfo...")
            access_token = token_data["access_token"]
            userinfo_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            userinfo_response = requests.get(userinfo_url, headers=headers)
            print(f"   Status: {userinfo_response.status_code}")
            print(f"   Response: {userinfo_response.text}")
            
            if userinfo_response.status_code == 200:
                user_info = userinfo_response.json()
                print("✅ Userinfo bem-sucedido!")
                print(f"   Username: {user_info.get('preferred_username', '')}")
                print(f"   Email: {user_info.get('email', '')}")
                return True
            else:
                print("❌ Erro no userinfo")
                return False
        else:
            print("❌ Erro na autenticação")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar autenticação: {e}")
        return False

if __name__ == "__main__":
    test_keycloak_direct()