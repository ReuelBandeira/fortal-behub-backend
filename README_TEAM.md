# 🚀 Beehub API - Guia para Equipe

## 📋 Pré-requisitos

- ✅ Docker Desktop
- ✅ Docker Compose

## 🚀 Iniciar o Projeto

### **1. Clone o repositório**

```bash
git clone <url-do-repositorio>
cd beehub-api
```

### **2. Iniciar com Docker Compose**

```bash
docker-compose up -d
```

### **3. Configurar Keycloak (Primeira vez apenas)**

```bash
# Aguardar os serviços estarem prontos (2-3 minutos)
# Depois executar:
python scripts/setup-keycloak.py
```

**Pronto!** 🎉 O projeto estará funcionando.

## ⏱️ Tempo de Inicialização

- **Primeira execução**: 2-3 minutos (inclui configuração automática)
- **Execuções subsequentes**: 30-60 segundos

## 🔗 URLs de Acesso

| Serviço            | URL                        | Descrição                |
| ------------------ | -------------------------- | ------------------------ |
| **API**            | http://localhost:3000      | API principal            |
| **Documentação**   | http://localhost:3000/docs | Swagger UI               |
| **Keycloak Admin** | http://localhost:8080      | Console de administração |

## 👤 Usuários de Teste

Após a inicialização, você terá acesso aos seguintes usuários:

| Usuário     | Senha      | Role      |
| ----------- | ---------- | --------- |
| `admin`     | `admin123` | admin     |
| `user`      | `user123`  | user      |
| `moderator` | `mod123`   | moderator |

## 🛠️ Comandos Úteis

### **Gerenciar Serviços**

```bash
# Parar todos os serviços
docker-compose down

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f beehub-api

# Reiniciar apenas a API
docker-compose restart beehub-api
```

### **Verificar Status**

```bash
# Ver status dos containers
docker-compose ps

# Ver uso de recursos
docker stats
```

### **Limpeza**

```bash
# Parar e remover containers
docker-compose down

# Parar e remover containers + volumes (cuidado!)
docker-compose down -v

# Limpar imagens não utilizadas
docker system prune
```

## 🔧 Configuração Automática

O projeto inclui configuração automática que:

1. **Aguarda** PostgreSQL e Keycloak estarem prontos
2. **Executa** migrações do banco de dados
3. **Configura** Keycloak com realm, client e usuários
4. **Inicia** a API automaticamente

## 🐛 Troubleshooting

### **Se a API não carregar:**

```bash
# Verificar logs da API
docker-compose logs beehub-api

# Verificar se todos os serviços estão rodando
docker-compose ps
```

### **Se o Keycloak não carregar:**

```bash
# Verificar logs do Keycloak
docker-compose logs keycloak

# Aguardar mais tempo (às vezes demora na primeira execução)
docker-compose restart keycloak
```

### **Se precisar reconfigurar tudo:**

```bash
# Parar tudo
docker-compose down

# Remover volumes (isso apaga dados)
docker-compose down -v

# Iniciar novamente
docker-compose up -d
```

## 📁 Estrutura do Projeto

```
beehub-api/
├── src/                    # Código fonte da API
├── alembic/               # Migrações do banco
├── scripts/               # Scripts de configuração
├── docker-compose.yml     # Configuração Docker
├── dockerfile            # Imagem da API
└── docker-entrypoint.sh  # Script de inicialização automática
```

## 🔐 Variáveis de Ambiente

As variáveis estão configuradas no `docker-compose.yml`:

- `DATABASE_URL`: Conexão com PostgreSQL
- `SECRET_KEY`: Chave secreta da API
- `KEYCLOAK_*`: Configurações do Keycloak (Public Client - sem client secret)

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `docker-compose logs -f`
2. Reinicie os serviços: `docker-compose restart`
3. Se necessário, recrie tudo: `docker-compose down -v && docker-compose up -d`

---

**🎯 Objetivo**: Zero configuração manual! Apenas `docker-compose up -d` e está pronto para usar.
