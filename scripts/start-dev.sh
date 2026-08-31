#!/bin/bash

# Script para iniciar o ambiente de desenvolvimento do Beehub
# Inclui Keycloak, PostgreSQL e API

set -e

echo "🚀 Iniciando ambiente de desenvolvimento do Beehub..."

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker e tente novamente."
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e iniciar os serviços
echo "🔨 Construindo e iniciando serviços..."
docker-compose up -d

# Aguardar Keycloak estar pronto
echo "⏳ Aguardando Keycloak estar pronto..."
sleep 30

# Executar script de configuração do Keycloak
echo "🔧 Configurando Keycloak..."
python scripts/setup-keycloak.py

echo ""
echo "🎉 Ambiente de desenvolvimento iniciado com sucesso!"
echo ""
echo "📋 Serviços disponíveis:"
echo "  • API Beehub: http://localhost:3000"
echo "  • Keycloak Admin: http://localhost:8080"
echo "  • PostgreSQL: localhost:5432"
echo ""
echo "📚 Documentação da API: http://localhost:3000/docs"
echo ""
echo "👤 Usuários de teste:"
echo "  • admin/admin123 (admin)"
echo "  • user/user123 (user)"
echo "  • moderator/mod123 (moderator)"
echo ""
echo "🔑 Keycloak Admin:"
echo "  • Username: admin"
echo "  • Password: admin"
echo ""
echo "🔧 Para parar os serviços: docker-compose down"
echo "🔍 Para ver logs: docker-compose logs -f" 