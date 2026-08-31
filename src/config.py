import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Keycloak Configuration
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
KEYCLOAK_REALM_NAME = os.getenv("KEYCLOAK_REALM_NAME", "seu-realm")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "seu-client-id")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "seu-client-secret")

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "noreply@irede.org.br")
EMAIL_CLIENT_ID = os.getenv("EMAIL_CLIENT_ID", "5850e39a-1be6-405d-b7e6-baddf90f5113")
EMAIL_CLIENT_SECRET = os.getenv("EMAIL_CLIENT_SECRET", "seu-email-client-secret")
EMAIL_TENANT_ID = os.getenv("EMAIL_TENANT_ID", "6635641d-db4a-45e4-8fd0-a0b32a2214c2")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


