# Script PowerShell para iniciar o ambiente de desenvolvimento do Beehub
# Inclui Keycloak, PostgreSQL e API

Write-Host "Iniciando ambiente de desenvolvimento do Beehub..." -ForegroundColor Green

# Verificar se o Docker está rodando
try {
    docker info | Out-Null
    Write-Host "Docker está rodando" -ForegroundColor Green
} catch {
    Write-Host "Docker não está rodando. Por favor, inicie o Docker e tente novamente." -ForegroundColor Red
    exit 1
}

# Parar containers existentes
Write-Host "Parando containers existentes..." -ForegroundColor Yellow
docker-compose down

# Construir e iniciar os serviços
Write-Host "Construindo e iniciando serviços..." -ForegroundColor Yellow
docker-compose up -d

# Aguardar Keycloak estar pronto
Write-Host "Aguardando Keycloak estar pronto..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Executar script de configuração do Keycloak
Write-Host "Configurando Keycloak..." -ForegroundColor Yellow
python scripts/setup-keycloak.py

Write-Host ""
Write-Host "Ambiente de desenvolvimento iniciado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Serviços disponíveis:" -ForegroundColor Cyan
Write-Host "  • API Beehub: http://localhost:3000" -ForegroundColor White
Write-Host "  • Keycloak Admin: http://localhost:8080" -ForegroundColor White
Write-Host "  • PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host ""
Write-Host "Documentação da API: http://localhost:3000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usuários de teste:" -ForegroundColor Cyan
Write-Host "  • admin/admin123 (admin)" -ForegroundColor White
Write-Host "  • user/user123 (user)" -ForegroundColor White
Write-Host "  • moderator/mod123 (moderator)" -ForegroundColor White
Write-Host ""
Write-Host "Keycloak Admin:" -ForegroundColor Cyan
Write-Host "  • Username: admin" -ForegroundColor White
Write-Host "  • Password: admin" -ForegroundColor White
Write-Host ""
Write-Host "Para parar os serviços: docker-compose down" -ForegroundColor Yellow
Write-Host "Para ver logs: docker-compose logs -f" -ForegroundColor Yellow 