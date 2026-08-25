from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.database import get_db
from app.models import Enfermeiro
from app.schemas import EnfermeiroCreate, EnfermeiroResponse, LoginSchema

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Inicializa o gerenciador moderno de senhas com Bcrypt
password_hash = PasswordHash((BcryptHasher(),))

def gerar_hash_senha(senha_plana: str) -> str:
    """Gera o hash unidirecional seguro da senha."""
    return password_hash.hash(senha_plana)

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Valida a senha digitada contra o hash do banco."""
    return password_hash.verify(senha_plana, senha_hash)


@router.post("/cadastro", response_model=EnfermeiroResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_enfermeiro(enfermeiro_data: EnfermeiroCreate, db: Session = Depends(get_db)):
    if db.query(Enfermeiro).filter(Enfermeiro.enf_email == enfermeiro_data.enf_email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    if db.query(Enfermeiro).filter(Enfermeiro.enf_coren == enfermeiro_data.enf_coren).first():
        raise HTTPException(status_code=400, detail="COREN já cadastrado.")

    # Criptografa a senha com o novo hasher
    senha_criptografada = gerar_hash_senha(enfermeiro_data.enf_senha)

    novo_enfermeiro = Enfermeiro(
        enf_nome=enfermeiro_data.enf_nome,
        enf_email=enfermeiro_data.enf_email,
        enf_senha=senha_criptografada,
        enf_coren=enfermeiro_data.enf_coren
    )
    db.add(novo_enfermeiro)
    db.commit()
    db.refresh(novo_enfermeiro)
    return novo_enfermeiro


@router.post("/login")
def login(login_data: LoginSchema, db: Session = Depends(get_db)):
    enfermeiro = db.query(Enfermeiro).filter(Enfermeiro.enf_email == login_data.enf_email).first()
    
    if not enfermeiro or not verificar_senha(login_data.enf_senha, enfermeiro.enf_senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    return {
        "status": "sucesso",
        "enf_id": enfermeiro.enf_id,
        "enf_nome": enfermeiro.enf_nome,
        "mensagem": "Login efetuado com sucesso"
    }