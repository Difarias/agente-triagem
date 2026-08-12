from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Enfermeiro
from app.schemas import EnfermeiroCreate, EnfermeiroResponse, LoginSchema

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/cadastro", response_model=EnfermeiroResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_enfermeiro(enfermeiro_data: EnfermeiroCreate, db: Session = Depends(get_db)):
    if db.query(Enfermeiro).filter(Enfermeiro.enf_email == enfermeiro_data.enf_email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    if db.query(Enfermeiro).filter(Enfermeiro.enf_coren == enfermeiro_data.enf_coren).first():
        raise HTTPException(status_code=400, detail="COREN já cadastrado.")

    novo_enfermeiro = Enfermeiro(
        enf_nome=enfermeiro_data.enf_nome,
        enf_email=enfermeiro_data.enf_email,
        enf_senha=enfermeiro_data.enf_senha, 
        enf_coren=enfermeiro_data.enf_coren
    )
    db.add(novo_enfermeiro)
    db.commit()
    db.refresh(novo_enfermeiro)
    return novo_enfermeiro

@router.post("/login")
def login(login_data: LoginSchema, db: Session = Depends(get_db)):
    enfermeiro = db.query(Enfermeiro).filter(Enfermeiro.enf_email == login_data.enf_email).first()
    if not enfermeiro or enfermeiro.enf_senha != login_data.enf_senha:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    return {
        "status": "sucesso",
        "enf_id": enfermeiro.enf_id,
        "enf_nome": enfermeiro.enf_nome,
        "mensagem": "Login efetuado com sucesso"
    }