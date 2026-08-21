from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Atendimento, Paciente, MensagemChat
from app.schemas import AtendimentoResponse, MensagemCreate, MensagemResponse, AtendimentoConcluir
from app.services.rag_service import AgenteSusane

router = APIRouter(prefix="/atendimentos", tags=["Atendimentos (Chats)"])
agente = AgenteSusane()

@router.post("/novo/{enf_id}", response_model=AtendimentoResponse, status_code=status.HTTP_201_CREATED)
def iniciar_novo_atendimento(enf_id: int, db: Session = Depends(get_db)):
    novo_paciente = Paciente(pac_nome="Em identificação")
    db.add(novo_paciente)
    db.commit()
    db.refresh(novo_paciente)

    novo_atendimento = Atendimento(
        ate_enf_id=enf_id,
        ate_pac_id=novo_paciente.pac_id,
        ate_dados_iniciais="Atendimento iniciado via chat."
    )
    db.add(novo_atendimento)
    db.commit()
    db.refresh(novo_atendimento)

    saudacao_susane = (
        "Olá! Meu nome é Susane e sou sua assistente de suporte à decisão em triagem clínica. "
        "Estou aqui para te auxiliar! Para começarmos, qual é o nome, idade e o sexo do paciente?"
    )

    msg_inicial = MensagemChat(
        msg_ate_id=novo_atendimento.ate_id,
        msg_remetente="ia",
        msg_conteudo=saudacao_susane
    )
    db.add(msg_inicial)
    db.commit()

    return novo_atendimento


@router.post("/{ate_id}/mensagens", response_model=MensagemResponse)
def enviar_mensagem_chat(ate_id: int, dados: MensagemCreate, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.ate_id == ate_id).first()
    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado.")

    # 1. Salva a mensagem do enfermeiro no banco
    msg_enfermeiro = MensagemChat(
        msg_ate_id=ate_id,
        msg_remetente="enfermeiro",
        msg_conteudo=dados.msg_conteudo
    )
    db.add(msg_enfermeiro)
    db.commit()

    # 2. EXTRAÇÃO AUTOMÁTICA DOS DADOS DO PACIENTE
    paciente = db.query(Paciente).filter(Paciente.pac_id == atendimento.ate_pac_id).first()
    if paciente:
        dados_extraidos = agente.extrair_dados_paciente(dados.msg_conteudo)
        
        # Atualiza apenas se o dado foi encontrado e o registro ainda estava padrão
        if dados_extraidos.pac_nome and paciente.pac_nome == "Em identificação":
            paciente.pac_nome = dados_extraidos.pac_nome
        if dados_extraidos.pac_sexo and not paciente.pac_sexo:
            paciente.pac_sexo = dados_extraidos.pac_sexo
        if dados_extraidos.pac_data_nascimento and not paciente.pac_data_nascimento:
            try:
                paciente.pac_data_nascimento = datetime.strptime(dados_extraidos.pac_data_nascimento, "%Y-%m-%d").date()
            except ValueError:
                pass
        
        db.commit()

    # 3. Busca histórico e gera resposta da Susane
    historico = db.query(MensagemChat).filter(MensagemChat.msg_ate_id == ate_id).order_by(MensagemChat.msg_criado_em.asc()).all()

    resposta_ia = agente.gerar_resposta(
        historico_mensagens=historico[:-1],
        mensagem_usuario=dados.msg_conteudo
    )

    # 4. Salva resposta da IA
    msg_ia = MensagemChat(
        msg_ate_id=ate_id,
        msg_remetente="ia",
        msg_conteudo=resposta_ia
    )
    db.add(msg_ia)
    db.commit()
    db.refresh(msg_ia)

    return msg_ia


@router.get("/{ate_id}/mensagens", response_model=List[MensagemResponse])
def obter_historico_chat(ate_id: int, db: Session = Depends(get_db)):
    return db.query(MensagemChat).filter(MensagemChat.msg_ate_id == ate_id).order_by(MensagemChat.msg_criado_em.asc()).all()

@router.patch("/{ate_id}/concluir", response_model=AtendimentoResponse)
def concluir_atendimento(ate_id: int, dados: AtendimentoConcluir, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.ate_id == ate_id).first()
    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado.")

    atendimento.ate_status = "Concluído"
    atendimento.ate_classificacao_final = dados.ate_classificacao_final
    atendimento.ate_concluido_em = datetime.utcnow()

    db.commit()
    db.refresh(atendimento)

    return atendimento

@router.get("/enfermeiro/{enf_id}", response_model=List[AtendimentoResponse])
def listar_atendimentos_enfermeiro(enf_id: int, db: Session = Depends(get_db)):
    return db.query(Atendimento).filter(Atendimento.ate_enf_id == enf_id).order_by(Atendimento.ate_criado_em.desc()).all()