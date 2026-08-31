# 🚀 Guia Rápido - Beehub API

## ⚡ Inicialização Rápida

### 1. Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11+ (para scripts)

### 2. Iniciar o projeto

**Windows (PowerShell):**

```powershell
.\scripts\start-dev.ps1
```

**Linux/Mac:**

```bash
bash scripts/start-dev.sh
```

**Manual:**

```bash
docker-compose up -d
```

### 3. Aguardar inicialização

Os serviços levam alguns minutos para inicializar completamente:

- PostgreSQL: ~30 segundos
- Keycloak: ~2-3 minutos
- API: ~1 minuto

### 4. Testar se está funcionando

```bash
python scripts/test-api.py
```

## 📋 Serviços Disponíveis

| Serviço    | URL                        | Descrição            |
| ---------- | -------------------------- | -------------------- |
| API        | http://localhost:3000      | API principal        |
| Docs       | http://localhost:3000/docs | Documentação Swagger |
| Keycloak   | http://localhost:8080      | Admin do Keycloak    |
| PostgreSQL | localhost:5432             | Banco de dados       |

## 🔑 Credenciais

### Keycloak Admin

- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

### Usuários de Teste

- **admin/admin123** (admin)
- **user/user123** (user)
- **moderator/mod123** (moderator)

## 🛠️ Comandos Úteis

```bash
# Ver status dos containers
docker-compose ps

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Reconstruir
docker-compose build --no-cache

# Testar API
python scripts/test-api.py
```

## 🐛 Problemas Comuns

### Keycloak não inicia

- Aguarde mais tempo (pode levar 3-5 minutos)
- Verifique logs: `docker-compose logs keycloak`

### API não responde

- Verifique se o banco está pronto
- Verifique logs: `docker-compose logs beehub-api`

### Porta ocupada

- Pare outros serviços que usem as portas 3000, 8080, 5432
- Ou altere as portas no `docker-compose.yml`

## 📚 Próximos Passos

1. Acesse a documentação: http://localhost:3000/docs
2. Configure o Keycloak: http://localhost:8080
3. Teste a autenticação com os usuários de teste
4. Explore os endpoints da API

---

**🎉 Pronto! Seu ambiente está funcionando!**
