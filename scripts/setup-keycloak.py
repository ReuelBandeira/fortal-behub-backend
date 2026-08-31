#!/usr/bin/env python3
"""
Script para configurar automaticamente o Keycloak para o projeto Beehub
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configurações do Keycloak
KEYCLOAK_URL = "http://keycloak:8080"  # Usando o nome do serviço Docker
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"
REALM_NAME = "beehub-realm"
CLIENT_ID = "beehub-client"
CLIENT_SECRET = "your-client-secret"

def get_admin_token() -> str:
    """Obtém o token de administrador do Keycloak"""
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "grant_type": "password",
        "client_id": "admin-cli"
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.RequestException as e:
        print(f"❌ Erro ao obter token de admin: {e}")
        sys.exit(1)

def create_realm(admin_token: str) -> bool:
    """Cria o realm do Beehub"""
    url = f"{KEYCLOAK_URL}/admin/realms"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    realm_data = {
        "realm": REALM_NAME,
        "enabled": True,
        "displayName": "Beehub Realm",
        "displayNameHtml": "<div class=\"kc-logo-text\"><span>Beehub</span></div>"
    }
    
    try:
        response = requests.post(url, headers=headers, json=realm_data)
        if response.status_code == 201:
            print(f"✅ Realm '{REALM_NAME}' criado com sucesso")
            return True
        elif response.status_code == 409:
            print(f"ℹ️ Realm '{REALM_NAME}' já existe")
            return True
        else:
            print(f"❌ Erro ao criar realm: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Erro ao criar realm: {e}")
        return False

def create_client(admin_token: str) -> bool:
    """Cria o client do Beehub"""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    client_data = {
        "clientId": CLIENT_ID,
        "enabled": True,
        "protocol": "openid-connect",
        "publicClient": True,  # Client authentication: OFF (para public client)
        "standardFlowEnabled": True,  # Standard flow: ON
        "directAccessGrantsEnabled": True,  # Direct access grants: ON
        "serviceAccountsEnabled": False,  # Service accounts roles: OFF
        "authorizationServicesEnabled": False,  # Authorization: OFF
        "redirectUris": [
            "http://localhost:5173/*",
            "http://localhost:3000/*"
        ],
        "webOrigins": [
            "http://localhost:5173",
            "http://localhost:3000"
        ],
        "attributes": {
            "saml.assertion.signature": "false",
            "saml.force.post.binding": "false",
            "saml.multivalued.roles": "false",
            "saml.encrypt": "false",
            "saml.server.signature": "false",
            "saml.server.signature.keyinfo.ext": "false",
            "exclude.session.state.from.auth.response": "false",
            "saml_force_name_id_format": "false",
            "saml.client.signature": "false",
            "tls.client.certificate.bound.access.tokens": "false",
            "saml.authnstatement": "false",
            "display.on.consent.screen": "false",
            "saml.onetimeuse.condition": "false"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=client_data)
        if response.status_code == 201:
            print(f"✅ Client '{CLIENT_ID}' criado com sucesso")
            return True
        elif response.status_code == 409:
            print(f"ℹ️ Client '{CLIENT_ID}' já existe")
            # Atualizar o client existente
            return update_existing_client(admin_token)
        else:
            print(f"❌ Erro ao criar client: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Erro ao criar client: {e}")
        return False

def update_existing_client(admin_token: str) -> bool:
    """Atualiza o client existente com as configurações corretas"""
    print("🔄 Atualizando client existente...")
    
    # Primeiro, obter o client existente
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        clients = response.json()
        client = next((c for c in clients if c["clientId"] == CLIENT_ID), None)
        
        if not client:
            print("❌ Client não encontrado para atualização")
            return False
        
        client_id = client["id"]
        
        # Atualizar o client
        update_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients/{client_id}"
        update_data = {
            "id": client_id,
            "clientId": CLIENT_ID,
            "enabled": True,
            "protocol": "openid-connect",
            "publicClient": False,
            "standardFlowEnabled": True,
            "directAccessGrantsEnabled": True,
            "serviceAccountsEnabled": True,
            "authorizationServicesEnabled": False,  # Authorization: OFF
            "redirectUris": [
                "http://localhost:5173/*",
                "http://localhost:3000/*"
            ],
            "webOrigins": [
                "http://localhost:5173",
                "http://localhost:3000"
            ],
            "attributes": {
                "saml.assertion.signature": "false",
                "saml.force.post.binding": "false",
                "saml.multivalued.roles": "false",
                "saml.encrypt": "false",
                "saml.server.signature": "false",
                "saml.server.signature.keyinfo.ext": "false",
                "exclude.session.state.from.auth.response": "false",
                "saml_force_name_id_format": "false",
                "saml.client.signature": "false",
                "tls.client.certificate.bound.access.tokens": "false",
                "saml.authnstatement": "false",
                "display.on.consent.screen": "false",
                "saml.onetimeuse.condition": "false"
            },
            "defaultClientScopes": ["profile", "email", "roles"],
            "optionalClientScopes": ["address", "phone", "offline_access"]
        }
        
        update_response = requests.put(update_url, headers=headers, json=update_data)
        if update_response.status_code == 204:
            print("✅ Client atualizado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao atualizar client: {update_response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Erro ao atualizar client: {e}")
        return False

def get_client_secret(admin_token: str) -> str:
    """Obtém o client secret"""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        clients = response.json()
        client = next((c for c in clients if c["clientId"] == CLIENT_ID), None)
        
        if client:
            client_id = client["id"]
            secret_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients/{client_id}/client-secret"
            secret_response = requests.get(secret_url, headers=headers)
            secret_response.raise_for_status()
            return secret_response.json()["value"]
        else:
            print("❌ Client não encontrado")
            return ""
    except requests.RequestException as e:
        print(f"❌ Erro ao obter client secret: {e}")
        return ""

def create_roles(admin_token: str) -> bool:
    """Cria as roles básicas"""
    roles = ["admin", "user", "moderator"]
    
    for role in roles:
        url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles"
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        role_data = {
            "name": role,
            "description": f"Role {role} para o Beehub"
        }
        
        try:
            response = requests.post(url, headers=headers, json=role_data)
            if response.status_code == 201:
                print(f"✅ Role '{role}' criada com sucesso")
            elif response.status_code == 409:
                print(f"ℹ️ Role '{role}' já existe")
            else:
                print(f"❌ Erro ao criar role '{role}': {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Erro ao criar role '{role}': {e}")
    
    return True

def create_test_users(admin_token: str) -> bool:
    """Cria usuários de teste"""
    users = [
        {
            "username": "admin",
            "email": "admin@beehub.com",
            "firstName": "Admin",
            "lastName": "User",
            "enabled": True,
            "credentials": [{"type": "password", "value": "admin123", "temporary": False}],
            "roles": ["admin"]
        },
        {
            "username": "user",
            "email": "user@beehub.com",
            "firstName": "Regular",
            "lastName": "User",
            "enabled": True,
            "credentials": [{"type": "password", "value": "user123", "temporary": False}],
            "roles": ["user"]
        },
        {
            "username": "moderator",
            "email": "moderator@beehub.com",
            "firstName": "Moderator",
            "lastName": "User",
            "enabled": True,
            "credentials": [{"type": "password", "value": "mod123", "temporary": False}],
            "roles": ["moderator"]
        }
    ]
    
    for user_data in users:
        url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        user_payload = {
            "username": user_data["username"],
            "email": user_data["email"],
            "firstName": user_data["firstName"],
            "lastName": user_data["lastName"],
            "enabled": user_data["enabled"],
            "credentials": user_data["credentials"]
        }
        
        try:
            response = requests.post(url, headers=headers, json=user_payload)
            if response.status_code == 201:
                print(f"✅ Usuário '{user_data['username']}' criado com sucesso")
                
                # Adicionar roles ao usuário
                user_id = response.headers["Location"].split("/")[-1]
                for role in user_data["roles"]:
                    role_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles/{role}"
                    role_response = requests.get(role_url, headers=headers)
                    if role_response.status_code == 200:
                        role_data = role_response.json()
                        user_roles_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/realm"
                        requests.post(user_roles_url, headers=headers, json=[role_data])
                        print(f"  ✅ Role '{role}' atribuída ao usuário '{user_data['username']}'")
                
            elif response.status_code == 409:
                print(f"ℹ️ Usuário '{user_data['username']}' já existe")
            else:
                print(f"❌ Erro ao criar usuário '{user_data['username']}': {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Erro ao criar usuário '{user_data['username']}': {e}")
    
    return True

def wait_for_keycloak():
    """Aguarda o Keycloak estar disponível"""
    print("⏳ Aguardando Keycloak estar disponível...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{KEYCLOAK_URL}/", timeout=5)
            if response.status_code == 200:
                print("✅ Keycloak está disponível!")
                return True
        except requests.RequestException:
            pass
        
        attempt += 1
        time.sleep(2)
        print(f"  Tentativa {attempt}/{max_attempts}...")
    
    print("❌ Timeout aguardando Keycloak")
    return False

def main():
    """Função principal"""
    print("🚀 Configurando Keycloak para o Beehub...")
    
    # Aguarda Keycloak estar disponível
    if not wait_for_keycloak():
        sys.exit(1)
    
    # Obtém token de admin
    print("🔑 Obtendo token de administrador...")
    admin_token = get_admin_token()
    
    # Cria realm
    print("🏛️ Criando realm...")
    if not create_realm(admin_token):
        sys.exit(1)
    
    # Cria client
    print("🔧 Criando client...")
    if not create_client(admin_token):
        sys.exit(1)
    
    # Obtém client secret
    print("🔐 Obtendo client secret...")
    client_secret = get_client_secret(admin_token)
    if client_secret:
        print(f"✅ Client Secret: {client_secret}")
        print("⚠️  IMPORTANTE: Atualize o CLIENT_SECRET no docker-compose.yml!")
    
    # Cria roles
    print("👥 Criando roles...")
    create_roles(admin_token)
    
    # Cria usuários de teste
    print("👤 Criando usuários de teste...")
    create_test_users(admin_token)
    
    print("\n🎉 Configuração do Keycloak concluída!")
    print("\n📋 Informações de acesso:")
    print(f"  • Keycloak Admin Console: http://localhost:8080")
    print(f"  • Admin Username: admin")
    print(f"  • Admin Password: admin")
    print(f"  • Realm: {REALM_NAME}")
    print(f"  • Client ID: {CLIENT_ID}")
    print(f"  • Client Secret: {client_secret}")
    print("\n👤 Usuários de teste criados:")
    print(f"  • admin/admin123 (roles: admin)")
    print(f"  • user/user123 (roles: user)")
    print(f"  • moderator/mod123 (roles: moderator)")

if __name__ == "__main__":
    main() 