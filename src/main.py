from fastapi import FastAPI
from src.config import engine, SessionLocal, Base
from fastapi.middleware.cors import CORSMiddleware
from src.controllers import enterprise, auth, email, password_reset
from src.utils.error_handler import setup_exception_handlers
from src.utils.user_sync_middleware import UserSyncMiddleware
import debugpy
import os

if os.getenv("ENABLE_DEBUGPY", "false").lower() == "true":
    debugpy.listen(("0.0.0.0", 5678))

app = FastAPI(
    title="Beehub API",
    version="1.0.0",
    description="API do Beehub com autenticação Keycloak"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middleware de sincronização de usuários
app.add_middleware(UserSyncMiddleware)

# Configurar handlers de exceção
setup_exception_handlers(app)

Base.metadata.create_all(bind=engine)

# Incluir routers
app.include_router(auth.router)
app.include_router(enterprise.router)
app.include_router(email.router)
app.include_router(password_reset.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Beehub API is running!", "status": "healthy"}