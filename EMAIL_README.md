# 📧 Sistema de Email - Beehub API

## Visão Geral

O sistema de email da Beehub API utiliza a **Microsoft Graph API** para envio de emails através do Microsoft 365. O sistema oferece endpoints para envio de emails individuais, em lote e notificações.

## 🔧 Configuração

### Variáveis de Ambiente

Adicione as seguintes variáveis ao seu arquivo `.env`:

```env
# Email Configuration (Microsoft Graph API)
EMAIL_SENDER=noreply@irede.org.br
EMAIL_CLIENT_ID=5850e39a-1be6-405d-b7e6-baddf90f5113
EMAIL_CLIENT_SECRET=seu-email-client-secret
EMAIL_TENANT_ID=6635641d-db4a-45e4-8fd0-a0b32a2214c2
```

### Configuração Microsoft Graph

1. **Registrar aplicação** no Azure Active Directory
2. **Configurar permissões** para Microsoft Graph API:
   - `Mail.Send` - Para envio de emails
   - `Mail.ReadWrite` - Para leitura e escrita de emails
3. **Gerar Client Secret** e configurar as variáveis de ambiente

## 📋 Endpoints Disponíveis

### 1. Enviar Email Individual

**POST** `/email/send`

Envia um email individual com suporte a HTML, CC, BCC e prioridades.

**Autenticação:** Obrigatória

**Request Body:**

```json
{
  "to": ["destinatario@exemplo.com"],
  "cc": ["copia@exemplo.com"],
  "bcc": ["copia-oculta@exemplo.com"],
  "subject": "Assunto do Email",
  "body": "Corpo do email em texto simples",
  "html_body": "<h1>Corpo do email em HTML</h1>",
  "priority": "normal",
  "attachments": ["caminho/para/arquivo.pdf"]
}
```

**Response:**

```json
{
  "message_id": "msg_20240101_120000_123456",
  "status": "sent",
  "sent_at": "2024-01-01T12:00:00",
  "recipients": ["destinatario@exemplo.com"]
}
```

### 2. Enviar Emails em Lote

**POST** `/email/send-bulk`

Envia múltiplos emails em lote (máximo 100 por requisição).

**Autenticação:** Obrigatória (role: admin)

**Request Body:**

```json
[
  {
    "to": ["destinatario1@exemplo.com"],
    "subject": "Email 1",
    "body": "Corpo do email 1"
  },
  {
    "to": ["destinatario2@exemplo.com"],
    "subject": "Email 2",
    "body": "Corpo do email 2"
  }
]
```

**Response:**

```json
[
  {
    "message_id": "msg_20240101_120000_123456",
    "status": "sent",
    "sent_at": "2024-01-01T12:00:00",
    "recipients": ["destinatario1@exemplo.com"]
  },
  {
    "message_id": "msg_20240101_120001_789012",
    "status": "sent",
    "sent_at": "2024-01-01T12:00:01",
    "recipients": ["destinatario2@exemplo.com"]
  }
]
```

### 3. Health Check

**GET** `/email/health`

Verifica a saúde do serviço de email.

**Autenticação:** Obrigatória

**Response:**

```json
{
  "status": "healthy",
  "service": "email",
  "message": "Serviço de email funcionando corretamente",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔐 Autenticação

Todos os endpoints de email requerem autenticação via **Bearer Token** do Keycloak.

### Exemplo de Uso com cURL

```bash
# 1. Obter token de acesso
curl -X POST "http://localhost:8080/realms/beehub-realm/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123&grant_type=password&client_id=beehub-client&client_secret=mdwpKGM4w6HBAy0AY8lVA2HHDR3jNPr1"

# 2. Enviar email usando o token
curl -X POST "http://localhost:3000/email/send" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["reuel.bandeira30@gmail.com"],
    "subject": "Teste de Email",
    "body": "Este é um email de teste.",
    "priority": "normal"
  }'
```

## 🧪 Testes

Execute o script de teste para verificar se o sistema está funcionando:

```bash
python scripts/test-email.py
```

O script irá:

1. Verificar se a API está respondendo
2. Obter token de acesso do Keycloak
3. Testar o health check do email
4. Enviar emails de teste com diferentes formatos

## 📊 Prioridades de Email

- `low` - Baixa prioridade
- `normal` - Prioridade normal (padrão)
- `high` - Alta prioridade

## 🚨 Tratamento de Erros

O sistema inclui tratamento robusto de erros:

- **400 Bad Request** - Dados inválidos (emails inválidos, assunto vazio, etc.)
- **401 Unauthorized** - Token inválido ou não fornecido
- **403 Forbidden** - Sem permissão (role admin necessário para bulk)
- **500 Internal Server Error** - Erro interno do servidor

## 📝 Logs

O sistema registra logs detalhados para:

- Tentativas de autenticação com Microsoft Graph
- Envios de email (sucesso e falha)
- Erros de configuração
- Problemas de conectividade

## 🔧 Troubleshooting

### Problemas Comuns

1. **Erro de autenticação Microsoft Graph**

   - Verificar se as credenciais estão corretas
   - Confirmar se a aplicação tem as permissões necessárias

2. **Email não enviado**

   - Verificar se o remetente está configurado corretamente
   - Confirmar se os destinatários são válidos

3. **Timeout na requisição**
   - Aumentar o timeout se necessário
   - Verificar conectividade com Microsoft Graph

### Comandos Úteis

```bash
# Verificar logs do container
docker-compose logs beehub-api

# Reiniciar apenas o serviço da API
docker-compose restart beehub-api

# Testar conectividade com Microsoft Graph
curl -H "Authorization: Bearer TOKEN" https://graph.microsoft.com/v1.0/me
```

## 📚 Recursos Adicionais

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [FastAPI Email Documentation](https://fastapi.tiangolo.com/tutorial/security/)
