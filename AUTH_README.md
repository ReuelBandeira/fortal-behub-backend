# Autenticação Keycloak - Beehub API

Este documento explica como configurar e usar a autenticação com Keycloak implementada no backend Flask/FastAPI.

## Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/beehub

# Keycloak Configuration
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM_NAME=seu-realm
KEYCLOAK_CLIENT_ID=seu-client-id
KEYCLOAK_CLIENT_SECRET=seu-client-secret

# Debug
ENABLE_DEBUGPY=false
```

### 2. Configuração do Keycloak

1. **Criar um Realm**: No Keycloak Admin Console, crie um novo realm
2. **Criar um Client**: 
   - Client ID: `seu-client-id`
   - Client Protocol: `openid-connect`
   - Access Type: `confidential`
   - Valid Redirect URIs: `http://localhost:5173/*` (seu frontend)
3. **Obter Client Secret**: Na aba Credentials do client
4. **Configurar Roles**: Crie roles conforme necessário (ex: `admin`, `user`)

## Endpoints de Autenticação

### 1. Obter Informações do Usuário
```http
GET /auth/user
Authorization: Bearer <access_token>
```

**Resposta:**
```json
{
  "sub": "user-id",
  "preferred_username": "john.doe",
  "email": "john@example.com",
  "name": "John Doe",
  "roles": ["user", "admin"],
  "token_data": {...},
  "user_info": {...}
}
```

### 2. Renovar Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "your-refresh-token"
}
```

**Resposta:**
```json
{
  "access_token": "new-access-token",
  "refresh_token": "new-refresh-token",
  "token_type": "Bearer",
  "expires_in": 300
}
```

### 3. Logout
```http
POST /auth/logout
Content-Type: application/json

{
  "refresh_token": "your-refresh-token"
}
```

### 4. Validar Token
```http
POST /auth/validate
Authorization: Bearer <access_token>
```

### 5. Informações do Usuário (Alternativo)
```http
GET /auth/me
Authorization: Bearer <access_token>
```

## Protegendo Rotas

### 1. Autenticação Obrigatória

```python
from src.utils.auth_decorator import require_auth

@router.get("/protected")
def protected_route(user_data: Dict[str, Any] = Depends(require_auth())):
    return {"message": "Rota protegida", "user": user_data}
```

### 2. Autenticação Opcional

```python
from src.utils.auth_decorator import optional_auth

@router.get("/optional")
def optional_route(user_data: Optional[Dict[str, Any]] = Depends(optional_auth())):
    if user_data:
        return {"message": "Usuário autenticado", "user": user_data}
    return {"message": "Usuário não autenticado"}
```

### 3. Verificação de Roles

```python
from src.utils.auth_decorator import require_role, require_any_role

# Role específica
@router.get("/admin-only")
def admin_route(user_data: Dict[str, Any] = Depends(require_role("admin"))):
    return {"message": "Apenas admins"}

# Qualquer uma das roles
@router.get("/moderator-or-admin")
def moderator_route(user_data: Dict[str, Any] = Depends(require_any_role(["moderator", "admin"]))):
    return {"message": "Moderador ou admin"}
```

## Estrutura de Dados do Usuário

O `user_data` retornado pelo decorator contém:

```python
{
    "sub": "user-id",                    # ID único do usuário
    "preferred_username": "john.doe",    # Nome de usuário
    "email": "john@example.com",         # Email
    "name": "John Doe",                  # Nome completo
    "roles": ["user", "admin"],          # Roles do usuário
    "token_data": {...},                 # Dados do token JWT
    "user_info": {...}                   # Informações do usuário do Keycloak
}
```

## Tratamento de Erros

A API retorna códigos de erro padronizados:

- **401 Unauthorized**: Token inválido ou não fornecido
- **403 Forbidden**: Usuário não tem permissão (role)
- **422 Unprocessable Entity**: Erro de validação
- **500 Internal Server Error**: Erro interno

### Exemplo de Resposta de Erro:
```json
{
  "detail": "Token expirado",
  "error_code": "AUTH_ERROR",
  "path": "/api/protected-route"
}
```

## Exemplo de Uso no Frontend

### JavaScript/TypeScript
```javascript
// Fazer requisição autenticada
const response = await fetch('/api/enterprise', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});

// Renovar token
const refreshResponse = await fetch('/api/auth/refresh', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    refresh_token: refreshToken
  })
});

// Logout
await fetch('/api/auth/logout', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    refresh_token: refreshToken
  })
});
```

## Logs e Monitoramento

A API registra automaticamente:
- Tentativas de autenticação
- Erros de autenticação
- Requisições para endpoints de auth
- IPs dos clientes

Os logs são exibidos no console da aplicação.

## Segurança

- Tokens JWT são validados com a chave pública do Keycloak
- Refresh tokens são invalidados no logout
- Headers de segurança apropriados são retornados
- Validação de audience e expiração de tokens
- Logs de auditoria para tentativas de acesso

## Troubleshooting

### Erro: "Erro ao obter chave pública do Keycloak"
- Verifique se o Keycloak está rodando
- Confirme a URL e realm name
- Verifique conectividade de rede

### Erro: "Token inválido"
- Token pode estar expirado
- Verifique se o token é válido no Keycloak
- Confirme se o client ID está correto

### Erro: "Role necessária"
- Verifique se o usuário tem a role necessária no Keycloak
- Confirme se a role está sendo mapeada corretamente 