<template>
  <div class="app-layout">
    <!-- 1. HEADER TOPO-A-TOPO (FULL WIDTH) -->
    <header class="top-header-full">
      <div class="header-left">
        <img src="../assets/mtilab_logo.jpg" alt="Logo MTILab" class="header-logo" v-if="logoExiste" @error="logoExiste = false" />
        <span v-else class="brand-logo-fallback">🩺</span>
        
        <div class="header-brand-title">
          <span class="badge-prototipo">PROTÓTIPO DE VALIDAÇÃO CIENTÍFICA</span>
        </div>
      </div>

      <div class="header-right">
        <span class="sub-title">Copiloto de Apoio à Triagem Clínica</span>
        
        <!-- MENU SUSPENSO (DROPDOWN) -->
        <div class="header-dropdown">
          <button class="dropdown-btn" @click.stop="menuHeaderAberto = !menuHeaderAberto">
            ⚙️ Opções ▾
          </button>
          <ul v-if="menuHeaderAberto" class="dropdown-menu">
            <li @click="$emit('abrir-sobre')">Sobre</li>
          </ul>
        </div>
      </div>
    </header>

    <!-- 2. CORPO PRINCIPAL (SIDEBAR + WORKSPACE) -->
    <div class="main-body">
      <!-- SIDEBAR LATERAL ESTILO CHATGPT -->
      <aside class="sidebar-gpt">
        <!-- ATALHOS / NAVEGAÇÃO -->
        <div class="sidebar-navigation">
          <button class="nav-item btn-novo-chat" @click="iniciarNovoChat" :disabled="carregando">
            <span class="icon">✏️</span>
            <span>Novo atendimento</span>
          </button>
        </div>

        <!-- LISTA DE ATENDIMENTOS (RECENTES) -->
        <div class="sidebar-recentes">
          <span class="secao-label">Recentes</span>
          <ul class="lista-chats" :key="chats.length">
            <li 
              v-for="chat in chats" 
              :key="chat.ate_id"
              :class="['chat-item', { active: chatAtual?.ate_id === chat.ate_id }]"
              @click="selecionarChat(chat)"
            >
              <span class="chat-nome" :title="obterNomeExibicao(chat)">
                {{ obterNomeExibicao(chat) }}
              </span>
              <span class="chat-sep">—</span>
              <span 
                v-if="chat.ate_classificacao_final" 
                :class="['chat-status', chat.ate_classificacao_final.toLowerCase()]"
              >
                {{ chat.ate_classificacao_final }}
              </span>
              <span v-else class="chat-status em-andamento">
                Em Triagem
              </span>
            </li>
          </ul>
        </div>

        <!-- RODAPÉ DA SIDEBAR: TEMA + PERFIL DO USUÁRIO -->
        <div class="sidebar-footer">
          <button class="btn-theme-toggle" @click="alternarTema">
            <span class="icon">{{ modoEscuro ? '☀️' : '🌙' }}</span>
            <span>{{ modoEscuro ? 'Modo Claro' : 'Modo Escuro' }}</span>
          </button>

          <div class="user-profile-wrapper">
            <div v-if="menuPerfilAberto" class="profile-popover">
              <button class="popover-item logout" @click="$emit('logout')">
                <span>🚪 Sair da conta</span>
              </button>
            </div>

            <div class="user-profile-card" @click="menuPerfilAberto = !menuPerfilAberto">
              <div class="user-avatar">
                {{ obterIniciais(enfermeiro.enf_nome) }}
              </div>
              <div class="user-details">
                <span class="user-name">{{ enfermeiro.enf_nome }}</span>
                <span class="user-role">Enfermeiro(a)</span>
              </div>
              <span class="user-menu-dots">•••</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- WORKSPACE PRINCIPAL -->
      <div class="main-workspace">
        <!-- GRID DOS PAINÉIS (CHAT + RESUMO) -->
        <div class="workspace-grid">
          <!-- PAINEL CENTRAL: CHAT -->
          <section class="panel-chat">
            <div class="panel-header">
              <span>• Histórico de Conversas ({{ mensagens.length }} Interações)</span>
              <span class="chat-id" v-if="chatAtual">ID: CF-{{ chatAtual.ate_id }}</span>
            </div>

            <div class="messages-scroll" ref="messagesBox">
              <div v-if="!chatAtual" class="empty-state">
                <p>Selecione ou crie um novo atendimento para começar.</p>
              </div>

              <template v-else>
                <div 
                  v-for="msg in mensagens" 
                  :key="msg.msg_id"
                  :class="['chat-bubble-row', msg.msg_remetente === 'enfermeiro' ? 'row-profissional' : 'row-ia']"
                >
                  <div class="chat-bubble">
                    <span class="bubble-tag">
                      {{ msg.msg_remetente === 'enfermeiro' ? `👤 ${enfermeiro.enf_nome.toUpperCase()}` : '🤖 SUSANE (COPILOTO IA)' }}
                    </span>
                    <div class="bubble-content" v-html="formatarMensagem(msg.msg_conteudo)"></div>
                  </div>
                </div>

                <div v-if="enviando" class="chat-bubble-row row-ia">
                  <div class="chat-bubble loading">
                    <span class="bubble-tag">🤖 SUSANE (COPILOTO IA)</span>
                    <p class="anim-pulse">Analisando sinais clínicos e consultando diretrizes...</p>
                  </div>
                </div>
              </template>
            </div>

            <!-- INPUT DE MENSAGEM -->
            <div class="chat-input-area" v-if="chatAtual && chatAtual.ate_status !== 'Concluído'">
              <form @submit.prevent="enviarMensagem">
                <input 
                  v-model="novaMensagem" 
                  type="text" 
                  placeholder="Informe os sintomas, queixas ou sinais vitais..." 
                  :disabled="enviando"
                />
                <button type="submit" :disabled="!novaMensagem.trim() || enviando">Enviar</button>
              </form>
            </div>
          </section>

          <!-- PAINEL DA DIREITA: RESUMO E CLASSIFICAÇÃO -->
          <section class="panel-summary" v-if="chatAtual">
            <div :class="['card-classificacao', classifCor.toLowerCase().replace(' ', '-')]">
              <span class="card-label">CLASSIFICAÇÃO DE RISCO</span>
              <h2 class="card-status-title">{{ classifCor }}</h2>
              <p class="card-status-sub">{{ classifTempo }}</p>
            </div>

            <div class="card-prontuario">
              <div class="card-header-prontuario">
                <span>📄 RESUMO ESTRUTURADO PARA PRONTUÁRIO</span>
              </div>
              <div class="prontuario-content">
                <div class="paciente-info-strip" v-if="paciente.pac_nome">
                  <div><strong>Nome:</strong> {{ paciente.pac_nome }}</div>
                  <div><strong>Sexo:</strong> {{ paciente.pac_sexo || 'N/I' }}</div>
                </div>
                <div class="prontuario-texto bubble-content" v-html="resumoFormatado"></div>
              </div>
            </div>

            <button 
              v-if="chatAtual.ate_status !== 'Concluído'" 
              class="btn-concluir-triagem" 
              @click="modalConclusaoAberto = true"
            >
              ✓ Encerramento da Triagem e Classificação
            </button>
          </section>
        </div>
      </div>
    </div>

    <!-- MODAL DE CONCLUSÃO DE TRIAGEM -->
    <div v-if="modalConclusaoAberto" class="modal-overlay">
      <div class="modal-card">
        <h3>Confirmar Classificação Final</h3>
        <p>Selecione a classificação de risco definitiva:</p>
        <div class="color-options">
          <button 
            v-for="cor in coresSesab" 
            :key="cor.nome"
            :class="['btn-cor', cor.classe, { selected: corSelecionada === cor.nome }]"
            @click="corSelecionada = cor.nome"
          >
            {{ cor.nome }}
          </button>
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="modalConclusaoAberto = false">Cancelar</button>
          <button class="btn-confirm" :disabled="!corSelecionada" @click="concluirAtendimento">Confirmar</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { marked } from 'marked';
import api from '../services/api';

const props = defineProps({ enfermeiro: Object });
defineEmits(['logout']);

const modoEscuro = ref(false);
const menuPerfilAberto = ref(false);
const menuHeaderAberto = ref(false);
const logoExiste = ref(true);

const chats = ref([]);
const chatAtual = ref(null);
const paciente = ref({});
const mensagens = ref([]);
const novaMensagem = ref('');
const carregando = ref(false);
const enviando = ref(false);
const messagesBox = ref(null);

const modalConclusaoAberto = ref(false);
const corSelecionada = ref('');

const coresSesab = [
  { nome: 'Vermelho', classe: 'vermelho' },
  { nome: 'Amarelo', classe: 'amarelo' },
  { nome: 'Verde', classe: 'verde' },
  { nome: 'Azul', classe: 'azul' }
];

const alternarTema = () => {
  modoEscuro.value = !modoEscuro.value;
  document.documentElement.setAttribute('data-theme', modoEscuro.value ? 'dark' : 'light');
};

const obterIniciais = (nome) => {
  if (!nome) return 'EN';
  const partes = nome.trim().split(' ');
  if (partes.length === 1) return partes[0].substring(0, 2).toUpperCase();
  return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
};

const obterNomeExibicao = (chat) => {
  const nome = chat.paciente?.pac_nome || chat.paciente_nome || '';
  const nomeLimpo = nome.toLowerCase();
  const estaPendente = !nome || 
                        nomeLimpo.includes('identifica') || 
                        nomeLimpo.includes('identificap');

  if (!estaPendente) {
    return nome;
  }
  return `Atendimento #${chat.ate_id}`;
};

const carregarChats = async () => {
  try {
    const res = await api.get(`/atendimentos/enfermeiro/${props.enfermeiro.enf_id}`);
    // Força a substituição do valor criando uma nova referência do Array
    chats.value = [...res.data];
    console.log("Chats carregados do banco:", chats.value);
  } catch (err) {
    console.error("Erro ao carregar chats:", err);
  }
};

const iniciarNovoChat = async () => {
  if (carregando.value) return;
  carregando.value = true;

  try {
    // 1. Cria no backend
    const res = await api.post(`/atendimentos/novo/${props.enfermeiro.enf_id}`);
    console.log("Resposta do POST /novo:", res.data);
    
    // 2. Monta o objeto completo
    const novoChat = {
      ...res.data,
      paciente: res.data.paciente || { pac_nome: 'Em identificação' }
    };

    // 3. Força a criação de um NOVO ARRAY para o Vue detectar a mudança na interface
    chats.value = [novoChat, ...chats.value];

    // 4. Seleciona o chat e busca mensagens
    chatAtual.value = novoChat;
    paciente.value = novoChat.paciente;
    await carregarMensagens(novoChat.ate_id);

    // 5. Re-busca do banco para garantir integridade
    await carregarChats();
  } catch (err) {
    console.error("Erro ao iniciar chat:", err);
    alert("Erro ao iniciar novo atendimento.");
  } finally {
    carregando.value = false;
  }
};

const selecionarChat = async (chat) => {
  chatAtual.value = chat;
  await carregarMensagens(chat.ate_id);
};

const carregarMensagens = async (ateId) => {
  try {
    const res = await api.get(`/atendimentos/${ateId}/mensagens`);
    mensagens.value = res.data;
    if (chatAtual.value && chatAtual.value.paciente) {
      paciente.value = chatAtual.value.paciente;
    }
    scrollToBottom();
  } catch (err) {
    console.error("Erro ao carregar mensagens:", err);
  }
};

const enviarMensagem = async () => {
  if (!novaMensagem.value.trim() || enviando.value) return;

  const texto = novaMensagem.value;
  novaMensagem.value = '';
  enviando.value = true;

  mensagens.value.push({ msg_id: Date.now(), msg_remetente: 'enfermeiro', msg_conteudo: texto });
  scrollToBottom();

  try {
    const res = await api.post(`/atendimentos/${chatAtual.value.ate_id}/mensagens`, { msg_conteudo: texto });
    mensagens.value.push(res.data);
    
    // 1. Recarrega a lista do banco
    await carregarChats();
    
    // 2. Garante a reatividade forçada criando um novo objeto atualizado
    const chatEncontrado = chats.value.find(c => c.ate_id === chatAtual.value.ate_id);
    if (chatEncontrado) {
      chatAtual.value = { ...chatEncontrado };
      if (chatEncontrado.paciente) {
        paciente.value = chatEncontrado.paciente;
      }
    }
  } catch (err) {
    alert("Erro ao enviar mensagem.");
  } finally {
    enviando.value = false;
    scrollToBottom();
  }
};

const concluirAtendimento = async () => {
  if (!corSelecionada.value) return;

  try {
    const res = await api.patch(`/atendimentos/${chatAtual.value.ate_id}/concluir`, {
      ate_classificacao_final: corSelecionada.value
    });

    // Atualiza o objeto do chat ativo com todos os dados retornados pelo backend
    chatAtual.value = {
      ...chatAtual.value,
      ...res.data
    };

    modalConclusaoAberto.value = false;
    await carregarChats();
  } catch (err) {
    console.error("Erro ao concluir atendimento:", err);
    alert("Erro ao concluir atendimento.");
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesBox.value) messagesBox.value.scrollTop = messagesBox.value.scrollHeight;
  });
};

const formatarMensagem = (texto) => texto ? marked.parse(texto, { breaks: true }) : '';

const classifCor = computed(() => chatAtual.value?.ate_classificacao_final || 'EM ANÁLISE');

const classifTempo = computed(() => {
  const cor = classifCor.value.toLowerCase();
  if (cor === 'vermelho') return 'Emergência - Atendimento Imediato (0 min)';
  if (cor === 'amarelo') return 'Urgência - Atendimento em até 60 minutos';
  if (cor === 'verde') return 'Pouco Urgente - Atendimento em até 120 minutos';
  if (cor === 'azul') return 'Não Urgente - Atendimento em até 240 minutos';
  return 'Coletando sintomas para classificação...';
});


const resumoFormatado = computed(() => {
  if (!chatAtual.value) return 'Selecione um atendimento.';
  
  // Pega o campo exato onde seu backend salva o resumo da IA
  const texto = chatAtual.value.ate_dados_iniciais;

  if (texto && texto.trim() !== '') {
    return marked.parse(texto);
  }
  
  return 'Aguardando informações do atendimento...';
});

const fecharMenusFora = (e) => {
  if (!e.target.closest('.header-dropdown')) menuHeaderAberto.value = false;
  if (!e.target.closest('.user-profile-wrapper')) menuPerfilAberto.value = false;
};

onMounted(() => {
  document.documentElement.setAttribute('data-theme', 'light');
  window.addEventListener('click', fecharMenusFora);
  carregarChats();
});

onMounted(() => {
  document.documentElement.setAttribute('data-theme', 'light');
  window.addEventListener('click', fecharMenusFora);
  carregarChats();
});

onUnmounted(() => {
  window.removeEventListener('click', fecharMenusFora);
});
</script>

<style scoped>
/* CONTAINER GLOBAL DA TELA */
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background-color: var(--bg-primary);
  overflow: hidden;
}

/* ==================================================
   1. HEADER SUPERIOR FULL-WIDTH (TOPO A TOPO)
================================================== */
.top-header-full {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1.2rem;
  background-color: #1e40af;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
  z-index: 100;
  height: 58px;
  flex-shrink: 0;
}

[data-theme="dark"] .top-header-full {
  background-color: #0f172a;
  border-bottom: 1px solid #334155;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

/* LOGO MTILAB MAIOR E COM BORDAS ARREDONDADAS */
.header-logo {
  height: 42px;
  width: auto;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.brand-logo-fallback {
  font-size: 1.4rem;
}

.header-brand-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.header-brand-title h1 {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  color: #ffffff;
}

.badge-prototipo {
  font-size: 0.6rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.2);
  color: #e0f2fe;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.sub-title {
  font-size: 0.85rem;
  color: #dbeafe;
  font-weight: 500;
}

/* DROPDOWN NO HEADER */
.header-dropdown {
  position: relative;
}

.dropdown-btn {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  padding: 0.35rem 0.8rem;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.dropdown-btn:hover {
  background: rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 120%;
  background-color: #ffffff;
  color: #253b1e;
  list-style: none;
  padding: 0.3rem;
  margin: 0;
  border-radius: 15px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  min-width: 140px;
  z-index: 200;
  border: 1px solid #e2e8f0;
}

[data-theme="dark"] .dropdown-menu {
  background-color: #1e293b;
  color: #f8fafc;
  border-color: #334155;
}

.dropdown-menu li {
  padding: 0.5rem 0.8rem;
  font-size: 0.85rem;
  cursor: pointer;
  border-radius: 16px;
  border: 1px solid transparent;
  transition: all 0.15s ease;
}

.dropdown-menu li:hover {
  background-color: rgba(0, 0, 0, 0.06);
  border-color: rgba(0, 0, 0, 0.1);
  color: #1e40af;
}

[data-theme="dark"] .dropdown-menu li:hover {
  background-color: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
  color: #38bdf8;
}

/* ==================================================
   2. CORPO DA APLICAÇÃO (SIDEBAR + WORKSPACE)
================================================== */
.main-body {
  display: flex;
  flex: 1;
  height: calc(100vh - 58px);
  overflow: hidden;
}

/* SIDEBAR ESTILO CHATGPT (250px) */
.sidebar-gpt {
  width: 250px;
  min-width: 250px;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 0.8rem 0.6rem;
  user-select: none;
}

.sidebar-navigation { display: flex; flex-direction: column; gap: 0.2rem; margin-bottom: 1rem; }

/* BOTAO NOVO ATENDIMENTO */
.nav-item {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.55rem 0.7rem; 
  border-radius: 15px; 
  border: 1px solid var(--border-color);
  font-size: 0.85rem;
  font-weight: 500; 
  color: var(--text-main); 
  cursor: pointer; 
  transition: all 0.2s ease;
}

.nav-item:hover { 
  background-color: rgba(0, 0, 0, 0.06);
  border-color: rgba(0, 0, 0, 0.15);
}

[data-theme="dark"] .nav-item:hover {
  background-color: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-novo-chat { background: transparent; width: 100%; text-align: left; }

.sidebar-recentes { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }
.secao-label { font-size: 0.7rem; font-weight: 700; color: var(--text-muted); padding: 0.4rem 0.7rem; margin-bottom: 0.2rem; }
.lista-chats { list-style: none; }

/* BLOCOS DOS ATENDIMENTOS RECENTES */
.chat-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.7rem;
  border-radius: 15px;
  border: 1px solid transparent;
  font-size: 0.8rem;
  cursor: pointer;
  margin-bottom: 0.25rem;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.chat-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] .chat-item:hover {
  background-color: rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.1);
}

.chat-item.active {
  background-color: var(--bg-card);
  border-color: var(--border-color);
  font-weight: 600;
}

.chat-nome {
  font-weight: 500;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.chat-sep {
  color: var(--text-muted);
  font-size: 0.7rem;
  flex-shrink: 0;
}

.chat-status {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
}

.chat-status.em-andamento { color: var(--text-muted); }
.chat-status.vermelho { color: var(--vermelho); }
.chat-status.amarelo { color: var(--amarelo); }
.chat-status.verde { color: var(--verde); }
.chat-status.azul { color: var(--azul); }

.sidebar-footer {
  padding-top: 0.6rem; border-top: 1px solid var(--border-color);
  display: flex; flex-direction: column; gap: 0.5rem;
}

.btn-theme-toggle {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.5rem 0.7rem; border-radius: 15px; border: 1px solid transparent;
  background: transparent; color: var(--text-main); font-size: 0.85rem;
  cursor: pointer; width: 100%; transition: all 0.2s ease;
}

.btn-theme-toggle:hover { 
  background-color: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] .btn-theme-toggle:hover {
  background-color: rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.1);
}

/* CARD DO PERFIL DO USUÁRIO */
.user-profile-wrapper { position: relative; }
.user-profile-card {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.5rem 0.6rem; 
  border-radius: 15px; 
  border: 1px solid transparent;
  cursor: pointer; 
  transition: all 0.2s ease;
}

.user-profile-card:hover { 
  background-color: rgba(0, 0, 0, 0.06);
  border-color: rgba(0, 0, 0, 0.12);
}

[data-theme="dark"] .user-profile-card:hover {
  background-color: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.12);
}

.user-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background-color: #d97706; color: white; font-weight: bold;
  font-size: 0.75rem; display: flex; align-items: center; justify-content: center;
}

.user-details { flex: 1; display: flex; flex-direction: column; line-height: 1.2; }
.user-name { font-size: 0.85rem; font-weight: 600; color: var(--text-main); }
.user-role { font-size: 0.7rem; color: var(--text-muted); }
.user-menu-dots { color: var(--text-muted); font-size: 0.8rem; }

.profile-popover {
  position: absolute; bottom: 110%; left: 0; width: 100%;
  background-color: var(--bg-secondary); border: 1px solid var(--border-color);
  border-radius: 15px; padding: 0.3rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); z-index: 50;
}

.popover-item {
  width: 100%; padding: 0.5rem 0.7rem; border: 1px solid transparent; background: transparent;
  color: var(--vermelho); font-weight: 600; font-size: 0.8rem; text-align: left;
  border-radius: 15px; cursor: pointer; transition: all 0.2s ease;
}

.popover-item:hover { 
  background-color: rgba(239, 68, 68, 0.1); 
  border-color: rgba(239, 68, 68, 0.2);
}

/* WORKSPACE */
.main-workspace { flex: 1; display: flex; flex-direction: column; min-width: 0; }

.workspace-grid {
  flex: 1; display: grid; grid-template-columns: 1fr 320px;
  gap: 0.8rem; padding: 0.8rem; overflow: hidden;
}

/* CHAT REFINADO */
.panel-chat {
  background-color: var(--bg-secondary); border-radius: 8px;
  border: 1px solid var(--border-color); display: flex; flex-direction: column; overflow: hidden;
}

.panel-header {
  padding: 0.6rem 1rem; border-bottom: 1px solid var(--border-color);
  display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; color: var(--text-muted);
}

.messages-scroll {
  flex: 1; overflow-y: auto; padding: 1rem; display: flex; flex-direction: column; gap: 0.75rem;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.chat-bubble-row { display: flex; width: 100%; }

.row-profissional { justify-content: flex-end; }
.row-ia { justify-content: flex-start; }

.chat-bubble {
  max-width: 75%; padding: 0.65rem 0.85rem; border-radius: 8px;
  border: 1px solid var(--border-color); font-size: 0.85rem; line-height: 1.4;
}

.row-profissional .chat-bubble {
  background-color: var(--bg-chat-user); color: var(--text-main); text-align: right;
}

.row-ia .chat-bubble {
  background-color: var(--bg-chat-ia); color: var(--text-main); text-align: left;
}

.bubble-tag {
  font-size: 0.65rem; font-weight: 700; color: var(--text-muted); display: block; margin-bottom: 0.25rem;
}

.row-profissional .bubble-tag { text-align: right; }
.row-ia .bubble-tag { text-align: left; }

.bubble-content {
  line-height: 1.5;
  font-size: 0.85rem;
}

.bubble-content :deep(p) {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.bubble-content :deep(p:last-child) {
  margin-bottom: 0;
}

.bubble-content :deep(h1),
.bubble-content :deep(h2),
.bubble-content :deep(h3),
.bubble-content :deep(h4) {
  font-size: 0.9rem;
  font-weight: 700;
  margin-top: 0.6rem;
  margin-bottom: 0.3rem;
  color: var(--accent-color, #2563eb);
}

.bubble-content :deep(ul), 
.bubble-content :deep(ol) {
  padding-left: 1.2rem;
  margin-top: 0.2rem;
  margin-bottom: 0.5rem;
}

.bubble-content :deep(li) {
  margin-bottom: 0.2rem;
}

.bubble-content :deep(strong) {
  font-weight: 700;
}

.chat-input-area { padding: 0.6rem 0.8rem; border-top: 1px solid var(--border-color); background: var(--bg-secondary); }
.chat-input-area form { display: flex; gap: 0.5rem; }

.chat-input-area input {
  flex: 1; padding: 0.5rem 0.8rem; border-radius: 15px; border: 1px solid var(--border-color);
  background: var(--bg-primary); color: var(--text-main); font-size: 0.85rem;
}

.chat-input-area button {
  padding: 0 1rem; background: var(--accent-color); color: white;
  border: none; border-radius: 15px; font-weight: 600; font-size: 0.85rem; cursor: pointer;
  transition: opacity 0.2s;
}

.chat-input-area button:hover {
  opacity: 0.9;
}

/* PAINEL DIREITO */
.panel-summary { display: flex; flex-direction: column; gap: 0.8rem; }

.card-classificacao {
  padding: 1rem; border-radius: 8px; text-align: center;
  border: 1px solid var(--border-color); background-color: var(--bg-card);
}

.card-classificacao.em-análise { background-color: var(--bg-card); border: 1px dashed var(--border-color); }
.card-classificacao.em-análise .card-status-title { color: var(--text-muted); }
.card-classificacao.vermelho { background-color: var(--vermelho); color: white; }
.card-classificacao.laranja { background-color: var(--laranja); color: white; }
.card-classificacao.amarelo { background-color: var(--amarelo); color: #000; }
.card-classificacao.verde { background-color: var(--verde); color: white; }
.card-classificacao.azul { background-color: var(--azul); color: white; }

.card-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.5px; display: block; opacity: 0.9; }
.card-status-title { font-size: 1.4rem; font-weight: 800; margin: 0.2rem 0; }
.card-status-sub { font-size: 0.75rem; opacity: 0.95; }

.card-prontuario {
  flex: 1; background-color: var(--bg-secondary); border: 1px solid var(--border-color);
  border-radius: 15px; display: flex; flex-direction: column; overflow: hidden;
}

.card-header-prontuario { padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--border-color); font-size: 0.7rem; font-weight: 700; color: var(--text-muted); }
.prontuario-content { padding: 0.8rem; font-size: 0.8rem; overflow-y: auto; color: var(--text-main); }

.paciente-info-strip {
  display: flex; gap: 1rem; padding-bottom: 0.5rem; margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color); font-size: 0.75rem; color: var(--text-muted);
}

.btn-concluir-triagem {
  padding: 0.7rem; background-color: var(--verde); color: white; border: none;
  border-radius: 15px; font-weight: bold; font-size: 0.8rem; cursor: pointer; transition: opacity 0.2s;
}

.btn-concluir-triagem:hover {
  opacity: 0.9;
}

/* MODAIS */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal-card {
  background: var(--bg-secondary); padding: 1.2rem; border-radius: 15px; width: 380px;
  border: 1px solid var(--border-color); color: var(--text-main); box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
.color-options { display: flex; flex-direction: column; gap: 0.4rem; margin: 1rem 0; }
.btn-cor { padding: 0.5rem; border-radius: 15px; border: none; color: white; font-weight: bold; cursor: pointer; }
.btn-cor.vermelho { background: var(--vermelho); }
.btn-cor.laranja { background: var(--laranja); }
.btn-cor.amarelo { background: var(--amarelo); color: black; }
.btn-cor.verde { background: var(--verde); }
.btn-cor.azul { background: var(--azul); }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
.btn-cancel, .btn-confirm { padding: 0.4rem 0.8rem; border-radius: 15px; border: none; cursor: pointer; font-size: 0.8rem; }
.btn-confirm { background: var(--accent-color, #1e40af); color: white; }
</style>