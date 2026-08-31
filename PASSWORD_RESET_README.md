# 🔐 Sistema de Reset de Senha - Beehub API

## Visão Geral

O sistema de reset de senha da Beehub API oferece uma solução completa e segura para redefinição de senhas, integrado com Keycloak e Microsoft Graph API para envio de emails. O sistema inclui sincronização automática de usuários, códigos de verificação seguros e templates de email profissionais.

## 🏗️ Arquitetura

### Componentes Principais

1. **Tabela `keycloak_users`** - Armazena dados dos usuários sincronizados
2. **Middleware de Sincronização** - Sincroniza automaticamente usuários no login
3. **Serviço de Reset** - Gerencia códigos de verificação e envio de emails
4. **Endpoints REST** - API para solicitação e validação de reset

### Fluxo de Funcionamento

```
1. Usuário faz login → Middleware sincroniza dados
2. Usuário solicita reset → Sistema gera código de 6 dígitos
3. Email é enviado → Usuário recebe código por email
4. Usuário valida código → Sistema verifica e permite reset
5. Senha é alterada → Código é invalidado automaticamente
```

## 📋 Endpoints Disponíveis

### 1. Solicitar Reset de Senha

**POST** `/auth/request-password-reset`

Solicita o envio de um código de verificação por email.

**Request Body:**
```json
{
  "email": "usuario@exemplo.com"
}
```

**Response:**
```json
{
  "message": "Se o email fornecido estiver cadastrado, você receberá um código de verificação em breve.",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. Validar Código de Reset

**POST** `/auth/validate-reset-code`

Valida se um código de reset é válido.

**Request Body:**
```json
{
  "email": "usuario@exemplo.com",
  "code": "123456"
}
```

**Response:**
```json
{
  "valid": true,
  "message": "Código válido"
}
```

### 3. Resetar Senha

**POST** `/auth/reset-password`

Reseta a senha usando código de verificação.

**Request Body:**
```json
{
  "email": "usuario@exemplo.com",
  "code": "123456",
  "new_password": "nova_senha123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Senha alterada com sucesso"
}
```

### 4. Limpar Códigos Expirados

**POST** `/auth/clear-expired-codes`

Limpa códigos de reset expirados (requer autenticação).

**Response:**
```json
{
  "message": "Códigos expirados limpos com sucesso"
}
```

## 🗄️ Estrutura do Banco de Dados

### Tabela `keycloak_users`

```sql
CREATE TABLE keycloak_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keycloak_user_id VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    reset_code VARCHAR,
    reset_code_expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**Campos:**
- `id` - Identificador único (UUID)
- `keycloak_user_id` - ID do usuário no Keycloak
- `email` - Email do usuário (único)
- `username` - Nome de usuário (único)
- `first_name` - Primeiro nome
- `last_name` - Sobrenome
- `reset_code` - Hash do código de reset
- `reset_code_expires_at` - Data de expiração do código
- `created_at` - Data de criação
- `updated_at` - Data de atualização
- `last_login` - Último login

## 🔄 Sincronização Automática

### Middleware de Sincronização

O sistema inclui um middleware que sincroniza automaticamente os dados dos usuários:

- **Primeiro login**: Cria novo registro na tabela `keycloak_users`
- **Logins subsequentes**: Apenas atualiza `last_login`
- **Prevenção de duplicatas**: Usa `keycloak_user_id` como chave única

### Endpoints Excluídos da Sincronização

Para evitar loops infinitos, os seguintes endpoints são excluídos:
- `/auth/login`
- `/auth/request-password-reset`
- `/auth/reset-password`
- `/docs`
- `/openapi.json`

## 🔐 Segurança

### Códigos de Verificação

- **6 dígitos numéricos** (100000-999999)
- **Expiração**: 20 minutos após geração
- **Armazenamento**: Hash SHA-256 (não texto plano)
- **Único por usuário**: Novo código invalida o anterior

### Medidas de Segurança

1. **Não exposição de informações**: Mesmo response para emails válidos/inválidos
2. **Rate limiting**: Implementado no nível da aplicação
3. **Logs de auditoria**: Todas as tentativas são registradas
4. **Validação robusta**: Verificação de formato e expiração
5. **Hash seguro**: Códigos armazenados como hash

### Validações

- Email deve ser válido
- Código deve ter exatamente 6 dígitos
- Nova senha deve ter pelo menos 8 caracteres
- Código não pode estar expirado

## 📧 Template de Email

O sistema envia emails com template HTML profissional:

- **Design responsivo** e moderno
- **Código destacado** em caixa azul
- **Aviso de segurança** sobre não solicitação
- **Informações de expiração** (20 minutos)
- **Logo e branding** da Beehub

## 🧪 Testes

### Script de Teste

Execute o script de teste para verificar o funcionamento:

```bash
python scripts/test-password-reset.py
```

### Testes Incluídos

1. **Sincronização de usuário** - Verifica se usuários são sincronizados
2. **Solicitação de reset** - Testa envio de código por email
3. **Validação de código** - Testa rejeição de códigos inválidos
4. **Limpeza de códigos** - Testa limpeza de códigos expirados

## 🔧 Configuração

### Variáveis de Ambiente

O sistema utiliza as mesmas variáveis do sistema de email:

```env
# Email Configuration (Microsoft Graph API)
EMAIL_SENDER=noreply@irede.org.br
EMAIL_CLIENT_ID=5850e39a-1be6-405d-b7e6-baddf90f5113
EMAIL_CLIENT_SECRET=seu-email-client-secret
EMAIL_TENANT_ID=6635641d-db4a-45e4-8fd0-a0b32a2214c2
```

### Dependências

O sistema utiliza as seguintes dependências:
- `msal==1.26.0` - Para Microsoft Graph API
- `python-keycloak` - Para integração com Keycloak
- `psycopg2-binary` - Para PostgreSQL

## 📝 Logs e Monitoramento

### Logs Registrados

- Tentativas de reset de senha
- Sincronização de usuários
- Envio de emails
- Validação de códigos
- Limpeza de códigos expirados

### Comandos Úteis

```bash
# Verificar logs do container
docker-compose logs beehub-api

# Executar limpeza manual de códigos
curl -X POST "http://localhost:3000/auth/clear-expired-codes" \
  -H "Authorization: Bearer SEU_TOKEN"

# Testar sincronização
curl -X GET "http://localhost:3000/enterprise" \
  -H "Authorization: Bearer SEU_TOKEN"
```

## 🚨 Tratamento de Erros

### Códigos de Status

- **200 OK** - Operação realizada com sucesso
- **400 Bad Request** - Dados inválidos ou código expirado
- **401 Unauthorized** - Token inválido ou não fornecido
- **500 Internal Server Error** - Erro interno do servidor

### Mensagens de Erro

- "Email não encontrado" - Email não cadastrado no sistema
- "Código inválido" - Código incorreto ou mal formatado
- "Código expirado" - Código expirou (20 minutos)
- "Erro interno, tente novamente" - Erro no servidor

## 🔄 Manutenção

### Limpeza Automática

O sistema inclui funcionalidade para limpar códigos expirados:

```python
# Executar limpeza
password_reset_service.clear_expired_codes()
```

### Monitoramento

- Verificar logs regularmente
- Monitorar tentativas de reset
- Acompanhar taxa de sucesso de emails
- Verificar integridade da tabela

## 📚 Recursos Adicionais

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## ✅ Critérios de Aceitação

- [x] Tabela criada e migrada
- [x] Usuários sincronizam no primeiro login
- [x] Não há duplicatas de usuários
- [x] Códigos são gerados corretamente
- [x] Códigos expiram em 20 minutos
- [x] Emails são enviados com sucesso
- [x] Endpoint retorna responses adequados
- [x] Sistema é seguro contra ataques
- [x] Código está bem documentado

## 🎯 Próximos Passos

1. **Implementar reset de senha no Keycloak** - Integração completa
2. **Rate limiting** - Limitar tentativas por IP
3. **Notificações push** - Alertas em tempo real
4. **Dashboard de monitoramento** - Interface administrativa
5. **Backup de códigos** - Recuperação em caso de falha 