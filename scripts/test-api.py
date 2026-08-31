#!/usr/bin/env python3
"""
Script para testar se a API está funcionando corretamente
"""

import requests
import time
import sys

def test_health_check():
    """Testa o endpoint de health check"""
    try:
        response = requests.get("http://localhost:3000/", timeout=10)
        if response.status_code == 200:
            print("✅ Health check: OK")
            return True
        else:
            print(f"❌ Health check: Erro {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Health check: {e}")
        return False

def test_docs():
    """Testa se a documentação está disponível"""
    try:
        response = requests.get("http://localhost:3000/docs", timeout=10)
        if response.status_code == 200:
            print("✅ Documentação: OK")
            return True
        else:
            print(f"❌ Documentação: Erro {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Documentação: {e}")
        return False

def test_keycloak():
    """Testa se o Keycloak está disponível"""
    try:
        response = requests.get("http://localhost:8080/", timeout=10)
        if response.status_code == 200:
            print("✅ Keycloak: OK")
            return True
        else:
            print(f"❌ Keycloak: Erro {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Keycloak: {e}")
        return False

def test_database():
    """Testa se o banco de dados está acessível"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="beehub",
            user="beehubuser",
            password="beehubpassword"
        )
        conn.close()
        print("✅ Database: OK")
        return True
    except Exception as e:
        print(f"❌ Database: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Testando serviços do Beehub...")
    print("=" * 50)
    
    # Aguarda um pouco para os serviços inicializarem
    print("⏳ Aguardando serviços inicializarem...")
    time.sleep(5)
    
    tests = [
        ("Health Check", test_health_check),
        ("Documentação", test_docs),
        ("Keycloak", test_keycloak),
        ("Database", test_database)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testando {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Resultados dos testes:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os serviços estão funcionando corretamente!")
        print("\n📋 Próximos passos:")
        print("  • Acesse a documentação: http://localhost:3000/docs")
        print("  • Configure o Keycloak: http://localhost:8080")
        print("  • Use os usuários de teste para autenticação")
        return 0
    else:
        print("⚠️  Alguns serviços não estão funcionando.")
        print("\n🔧 Verifique:")
        print("  • Se todos os containers estão rodando: docker-compose ps")
        print("  • Logs dos serviços: docker-compose logs")
        print("  • Se as portas estão livres")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 