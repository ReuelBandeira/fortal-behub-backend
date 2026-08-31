#!/usr/bin/env python3
"""
Script de teste específico para o endpoint de reset de senha
"""

import requests
import json
import sys

# Configurações
API_BASE_URL = "http://localhost:3000"

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
        print(f"📤 Código: {code}")
        print(f"📤 Nova senha: {new_password}")
        
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

def test_validate_code(email, code):
    """Testa a validação de código"""
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

def main():
    print("🧪 Testando Reset de Senha - Beehub API")
    print("=" * 50)
    
    # Dados de teste
    test_email = "reuel.bandeira30@gmail.com"
    test_code = "123456"  # Código de teste
    test_new_password = "Rsb123456!"
    
    # Primeiro, testar validação de código
    print("\n🔍 Testando validação de código...")
    is_valid = test_validate_code(test_email, test_code)
    
    if is_valid:
        print("\n🔄 Código válido, testando reset de senha...")
        success = test_reset_password(test_email, test_code, test_new_password)
        
        if success:
            print("\n🎉 Reset de senha realizado com sucesso!")
            print("✅ A senha foi alterada no Keycloak")
        else:
            print("\n❌ Falha no reset de senha")
    else:
        print("\n❌ Código inválido ou expirado")
        print("💡 Para testar com um código válido:")
        print("1. Solicite um novo código: POST /auth/request-password-reset")
        print("2. Verifique o email recebido")
        print("3. Use o código recebido no teste")

if __name__ == "__main__":
    main() 