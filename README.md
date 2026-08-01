# Processo de Acolhimento com Classificação de Risco no SUS

O processo de acolhimento com classificação de risco é um elemento crítico nas portas de entrada do Sistema Único de Saúde (SUS), exigindo decisões rápidas e assertivas.  

## Desafios
- **Condições adversas**: superlotação e fadiga mental.  
- **Equipe de enfermagem**: enfrenta exaustão cognitiva.  
- **Consequências**: variabilidade subjetiva de condutas e potenciais erros de triagem.  

## Limitações dos Sistemas Tradicionais
- **Sistemas de Apoio à Decisão Clínica (SADC)**: baseados em regras rígidas.  
- **Problema**: não processam linguagem natural dos pacientes de forma eficiente.  
- **Resultado**: exigem esforço manual para estruturação e codificação das queixas.  

## Potencial dos LLMs
- **Vantagem**: resolvem barreira da comunicação.  
- **Risco**: alucinações probabilísticas.  
- **Necessidade**: abordagem que garanta segurança assistencial e aderência às normas médicas.  

## Objetivo do Projeto
Desenvolver e validar um **agente conversacional inteligente** para apoiar o processo de triagem em serviços de saúde.  

### Funcionalidades
- Guiar coleta de informações.  
- Sugerir classificação de risco em tempo real.  
- Integrar **LLMs + RAG (Geração Aumentada por Recuperação)**.  
- Implementar **guardrails** para segurança computacional.  

## Metodologia
- **Tipo de pesquisa**: aplicada e exploratória.  
- **Base**: modelagem computacional e engenharia de software em saúde.  
- **Fonte de conhecimento (RAG)**: Protocolo Estadual de Classificação de Risco da SESAB.  
- **Modelo**: Mistral (código aberto).  
- **Orquestração**: LangGraph, estruturando interação como **Máquina de Estados Finitos**.  

## Segurança e Conformidade
- **Guardrails**: input e output rails para interceptar dados sensíveis.  
- **Bloqueio**: condutas exclusivas de médicos (diagnósticos definitivos, prescrições).  
- **Premissa HITL (Human-in-the-loop)**: decisão final permanece com o enfermeiro.  

## Validação
- **Testes de caixa preta**: casos sintéticos.  
- **Testes de estresse de segurança**: prompt injection/jailbreak.  

## Resultados Parciais
- **Provas de conceito (PoC)**: sucesso inicial da arquitetura híbrida.  
- **Capacidades demonstradas**:
  - Mapeamento preciso de sintomas.  
  - Identificação de sinais de alerta imediatos.  
  - Geração de resumos clínicos estruturados.  
- **Guardrails**: eficazes em recusar prescrições de medicamentos, mantendo neutralidade clínica.  

## Entregáveis
- Protótipo funcional, seguro e clinicamente auditável.  
- Transformação de formulários estáticos em **interfaces de IA proativas e confiáveis** para o SUS.  
