from fastapi import FastAPI
from app.database import engine, Base
import app.models as models
from app.routers import auth, atendimentos

# Cria as tabelas automaticamente no PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Triagem Clínica - SESAB",
    description="API do projeto de tese para suporte à decisão em triagem com LLM.",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(atendimentos.router)

@app.get("/")
def home():
    return {
        "status": "online",
        "mensagem": "API de Triagem rodando e conectada ao PostgreSQL!"
    }