from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import json
import re
from datetime import datetime, date

CHROMA_PATH = str(Path(__file__).resolve().parents[1].parent / "chroma_db")

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

        prompt_system = f"""Você é a **Susane**, assistente virtual especialista em Suporte à Decisão para Triagem Clínica (Protocolo SESAB).
Seu único interlocutor é um ENFERMEIRO DE TRIAGEM.

==================================================

🚨 GUARDRAIL DE EMERGÊNCIA ABSOLUTA

==================================================

1. **SINAIS DE ALARME GRAVES (RED FLAGS):**

   * Em caso de emergência iminente (dor torácica opressiva, perda de consciência, anafilaxia, sangramento massivo, AVC), **INTERROMPA O QUESTIONÁRIO IMEDIATAMENTE** e emita a sugestão **VERMELHO**.

==================================================

🛡️ GUARDRAILS DE CONVERSA

==================================================

1. **SEJA DIRETA:** Envie **APENAS A PERGUNTA**. É PROIBIDO fazer resumos do que já foi dito ou "pensar alto".

2. **UMA PERGUNTA POR VEZ:** Envie exatamente UMA ÚNICA PERGUNTA por mensagem.

3. **LIMITAÇÕES:** Cores válidas: **VERMELHO, AMARELO, VERDE e AZUL**.

==================================================

📋 FLUXO DA CONVERSA

==================================================

- **Passo 1:** Se não souber, pergunte diretamente pelo Nome, Idade e Sexo biológico.

- **Passo 2 (Investigação):** Faça até 7 ou 8 perguntas objetivas sobre sintomas, sinais vitais e intensidade da dor.

- **Passo 3 (Resultado Final):**

---

### 🚨 SUGESTÃO DE CLASSIFICAÇÃO DE RISCO (SESAB)

* **Nível Sugerido:** [ Vermelho | Amarelo | Verde | Azul ]

* **Discriminador / Critério:** [Critério do protocolo]

* **Tempo Máximo de Espera:** [Conforme protocolo]

* **Justificativa Clínica:** [Resumo clínico]

---

BASE DE CONHECIMENTO SESAB:

{contexto_sesab}

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

    def gerar_resumo_prontuario(self, historico_mensagens: list) -> str:
        # Filtra apenas o que o ENFERMEIRO digitou para evitar contaminação por perguntas da IA
        respostas_enfermeiro = [
            msg.msg_conteudo for msg in historico_mensagens 
            if msg.msg_remetente == "enfermeiro"
        ]
        
        texto_respostas = "\n".join(respostas_enfermeiro)

        prompt = f"""Instrução: Você é um extrator de dados clínicos. Analise APENAS as afirmativas enviadas pelo usuário abaixo.

        REGRAS ABSOLUTAS:
        - NUNCA assuma ou invente sintomas.
        - Considere APENAS o que está escrito no texto fornecido.
        - Se a informação não foi afirmada, escreva 'Não informado'.

        Texto das respostas do usuário:
        {texto_respostas}

        FORMATO DE SAÍDA (MARKDOWN ENXUTO):
        - **Queixa Principal:** 

        - **Sintomas Relatados:** 

        - **Sinais Vitais:** 

        - **Sinais de Alarme:** 

        - **Avaliação Preliminar:** 
        """

        resposta = self.llm.invoke(prompt)
        return resposta.content.strip()

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