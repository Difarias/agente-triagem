from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

# --- SCHEMAS DE ENFERMEIRO ---
class EnfermeiroCreate(BaseModel):
    enf_nome: str
    enf_email: EmailStr
    enf_senha: str
    enf_coren: str

class EnfermeiroResponse(BaseModel):
    enf_id: int
    enf_nome: str
    enf_email: EmailStr
    enf_coren: str
    enf_data_criacao: datetime

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    enf_email: EmailStr
    enf_senha: str


# --- SCHEMAS DE MENSAGENS E ATENDIMENTO ---
class MensagemCreate(BaseModel):
    msg_conteudo: str

class MensagemResponse(BaseModel):
    msg_id: int
    msg_remetente: str
    msg_conteudo: str
    msg_criado_em: datetime

    class Config:
        from_attributes = True

class AtendimentoCreate(BaseModel):
    pac_nome: str
    pac_data_nascimento: date
    pac_sexo: str
    ate_dados_iniciais: str

class AtendimentoConcluir(BaseModel):
    ate_classificacao_final: str # Ex: "Vermelho", "Laranja", "Amarelo", "Verde", "Azul"

# Schema do Paciente
class PacienteResponse(BaseModel):
    pac_id: int
    pac_nome: str
    pac_sexo: Optional[str] = None
    pac_data_nascimento: Optional[date] = None

    class Config:
        from_attributes = True

# SCHEMA ÚNICO E CORRIGIDO DE ATENDIMENTO
class AtendimentoResponse(BaseModel):
    ate_id: int
    ate_enf_id: int
    ate_pac_id: int
    ate_status: Optional[str] = "Em Triagem"
    ate_dados_iniciais: Optional[str] = None  # <--- CAMPO LIBERADO PARA O FRONT-END
    ate_classificacao_final: Optional[str] = None
    ate_criado_em: datetime
    ate_concluido_em: Optional[datetime] = None
    paciente: Optional[PacienteResponse] = None

    class Config:
        from_attributes = True