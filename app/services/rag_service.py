from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Optional
import json
import re
from datetime import datetime, date

CHROMA_PATH = "chroma_db"

# Schema de Extração de Dados do Paciente via IA
class DadosPacienteExtraidos(BaseModel):
    pac_nome: Optional[str] = Field(None, description="Nome do paciente se mencionado no texto, caso contrário None")
    pac_sexo: Optional[str] = Field(None, description="Sexo do paciente (Masculino/Feminino) se mencionado, caso contrário None")
    pac_data_nascimento: Optional[str] = Field(None, description="Data de nascimento no formato YYYY-MM-DD se mencionada/calculada, caso contrário None")


class AgenteSusane:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vector_store = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=self.embeddings
        )
        self.llm = ChatOllama(model="llama3.1", temperature=0.1)

    def gerar_resposta(self, historico_mensagens: list, mensagem_usuario: str) -> str:
        docs = self.vector_store.similarity_search(mensagem_usuario, k=4)
        contexto_sesab = "\n\n".join([doc.page_content for doc in docs])

        chat_history = []
        for msg in historico_mensagens:
            if msg.msg_remetente == "enfermeiro":
                chat_history.append(HumanMessage(content=msg.msg_conteudo))
            elif msg.msg_remetente == "ia":
                chat_history.append(AIMessage(content=msg.msg_conteudo))

        prompt_system = f"""Você é a **Susane**, assistente virtual de inteligência artificial especialista em Suporte à Decisão para Triagem Clínica, baseada estritamente no Protocolo de Triagem da SESAB (Secretaria de Saúde do Estado da Bahia).

Seu único interlocutor é um ENFERMEIRO DE TRIAGEM.

==================================================
🛡️ GUARDRAILS E REGRAS INVIOLÁVEIS (LIMITES DE ATUAÇÃO)
==================================================
1. **ESCOPO EXCLUSIVO:**
   * Você deve responder APENAS a questões relacionadas à triagem clínica hospitalar, classificação de risco e aplicação do Protocolo SESAB.
   * Se o usuário fizer perguntas fora desse contexto, recuse gentilmente dizendo: *"Desculpe, meu escopo de atuação é estritamente voltado ao suporte à decisão na triagem clínica com base no Protocolo SESAB. Como posso ajudar em relação ao atendimento atual?"*

2. **PRESCRIÇÃO E DIAGNÓSTICO PROIBIDOS:**
   * Você NUNCA deve prescrever medicamentos, sugerir doses ou emitir diagnósticos médicos finais.

3. **CORDIALIDADE E TOM DE VOZ:**
   * Seja sempre cordial, empática, calma e profissional.

4. **FIDELIDADE AO PROTOCOLO SESAB:**
   * NUNCA invente cores ou critérios de triagem fora do documento oficial.

==================================================
📋 FLUXO DE ATENDIMENTO
==================================================
1. Analise as mensagens do enfermeiro comparando com as DIRETRIZES DA SESAB fornecidas abaixo.
2. Se faltarem dados essenciais para determinar o risco (sinais vitais, tempo de início, dor, comorbidades), faça de **1 a 2 perguntas curtas e diretas** por vez.
3. Quando possuir dados suficientes, emita a sugestão final neste formato:

---
### 🚨 SUGESTÃO DE CLASSIFICAÇÃO DE RISCO (SESAB)

* **Nível Sugerido:** [ Vermelho | Laranja | Amarelo | Verde | Azul ]
* **Discriminador / Critério:** [Critério exato do protocolo SESAB]
* **Tempo Máximo de Espera:** [Conforme protocolo SESAB]
* **Justificativa Clínica:** [Breve resumo cruzando os dados do paciente com o protocolo]
---

---
**DIRETRIZES TÉCNICAS DO PROTOCOLO SESAB (BASE VETORIAL):**
{contexto_sesab}
---
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_system),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        chain = prompt | self.llm
        resposta = chain.invoke({
            "chat_history": chat_history,
            "input": mensagem_usuario
        })

        return resposta.content

    def extrair_dados_paciente(self, texto_usuario: str) -> DadosPacienteExtraidos:
        """ Analisa a mensagem do enfermeiro e extrai Nome, Sexo e Data de Nascimento / Idade. """
        ano_atual = datetime.now().year

        prompt = f"""Extraia as informações do paciente da mensagem abaixo e responda APENAS em formato JSON válido, sem nenhum texto adicional.

Campos requeridos no JSON:
- "pac_nome": nome do paciente se citado (senão null)
- "pac_sexo": "Masculino" ou "Feminino" se citado/subentendido (senão null)
- "pac_data_nascimento": se a data exata for informada, use "YYYY-MM-DD". Se apenas a idade for informada (ex: 55 anos), calcule o ano aproximado de nascimento mantendo "YYYY-01-01" considerando o ano atual de {ano_atual} (senão null).

Mensagem: "{texto_usuario}"

Exemplo de resposta:
{{"pac_nome": "Carlos Eduardo", "pac_sexo": "Masculino", "pac_data_nascimento": "1971-01-01"}}
"""
        try:
            resposta = self.llm.invoke(prompt)
            conteudo = resposta.content.strip()
            
            match = re.search(r'\{.*\}', conteudo, re.DOTALL)
            if match:
                dados_json = json.loads(match.group(0))
                return DadosPacienteExtraidos(
                    pac_nome=dados_json.get("pac_nome"),
                    pac_sexo=dados_json.get("pac_sexo"),
                    pac_data_nascimento=dados_json.get("pac_data_nascimento")
                )
        except Exception as e:
            print(f"Erro ao extrair dados do paciente: {e}")
        
        return DadosPacienteExtraidos()