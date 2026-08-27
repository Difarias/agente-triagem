from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Date
from sqlalchemy.orm import relationship
from .database import Base

class Enfermeiro(Base):
    __tablename__ = "tri_enfermeiros"

    enf_id = Column(Integer, primary_key=True, autoincrement=True)
    enf_nome = Column(String(150), nullable=False)
    enf_email = Column(String(150), unique=True, nullable=False)
    enf_senha = Column(String(255), nullable=False)
    enf_coren = Column(String(30), unique=True, nullable=False)
    enf_data_criacao = Column(DateTime, default=datetime.utcnow)

    atendimentos = relationship("Atendimento", back_populates="enfermeiro")


class Paciente(Base):
    __tablename__ = "tri_pacientes"

    pac_id = Column(Integer, primary_key=True, autoincrement=True)
    pac_nome = Column(String(150), nullable=True, default="Em identificação")
    pac_data_nascimento = Column(Date, nullable=True)
    pac_sexo = Column(String(10), nullable=True)
    pac_data_criacao = Column(DateTime, default=datetime.utcnow)

    atendimentos = relationship("Atendimento", back_populates="paciente")


class Atendimento(Base):
    __tablename__ = "tri_atendimentos"

    ate_id = Column(Integer, primary_key=True, autoincrement=True)
    ate_enf_id = Column(Integer, ForeignKey("tri_enfermeiros.enf_id"), nullable=False)
    ate_pac_id = Column(Integer, ForeignKey("tri_pacientes.pac_id"), nullable=False)
    ate_dados_iniciais = Column(Text, nullable=True)
    ate_status = Column(String(20), default="Em Andamento")
    ate_classificacao_final = Column(String(20), nullable=True)
    ate_criado_em = Column(DateTime, default=datetime.utcnow)
    ate_concluido_em = Column(DateTime, nullable=True)

    enfermeiro = relationship("Enfermeiro", back_populates="atendimentos")
    paciente = relationship("Paciente", back_populates="atendimentos")
    mensagens = relationship("MensagemChat", back_populates="atendimento")


class MensagemChat(Base):
    __tablename__ = "tri_mensagens_chat"

    msg_id = Column(Integer, primary_key=True, autoincrement=True)
    msg_ate_id = Column(Integer, ForeignKey("tri_atendimentos.ate_id"), nullable=False)
    msg_remetente = Column(String(15), nullable=False)
    msg_conteudo = Column(Text, nullable=False)
    msg_criado_em = Column(DateTime, default=datetime.utcnow)

    atendimento = relationship("Atendimento", back_populates="mensagens")