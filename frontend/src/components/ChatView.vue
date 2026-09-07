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
        <nav class="header-nav" aria-label="Navegação principal">
          <button class="header-nav-link active" type="button">Atendimento</button>
          <button class="header-nav-link" type="button" @click="$emit('abrir-sobre')">Sobre</button>
        </nav>
        <span class="sub-title">Copiloto de Apoio à Triagem Clínica</span>
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
          <div class="recentes-header">
            <span class="secao-label">Recentes</span>
            <span class="recentes-count">{{ filteredChats.length }}</span>
          </div>
          <div class="filtros-chats">
            <label class="busca-chats">
              <Search :size="14" aria-hidden="true" />
              <input v-model="filtroTexto" type="search" placeholder="Buscar atendimento" aria-label="Buscar atendimento" />
            </label>
            <select v-model="filtroStatus" class="filtro-status" aria-label="Filtrar por classificação">
              <option value="todos">Todos</option>
              <option value="em-andamento">Em Triagem</option>
              <option value="vermelho">Vermelho</option>
              <option value="amarelo">Amarelo</option>
              <option value="verde">Verde</option>
              <option value="azul">Azul</option>
            </select>
          </div>
          <ul class="lista-chats" :key="chats.length">
            <li 
              v-for="chat in filteredChats" 
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
              <button
                class="btn-excluir-chat"
                type="button"
                title="Excluir atendimento"
                :aria-label="`Excluir ${obterNomeExibicao(chat)}`"
                @click.stop="excluirChat(chat)"
              >
                <Trash2 :size="15" stroke-width="2" />
              </button>
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
                    <time v-if="formatarHorario(msg.msg_criado_em)" class="bubble-time" :datetime="msg.msg_criado_em">
                      {{ formatarHorario(msg.msg_criado_em) }}
                    </time>
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
                <small class="prontuario-fonte">Respostas ancoradas no protocolo da SESAB 2017</small>
              </div>
              <div class="prontuario-content">
                <div class="paciente-info-strip" v-if="paciente.pac_nome">
                  <div><strong>Nome:</strong> {{ paciente.pac_nome }}</div>
                  <div><strong>Sexo:</strong> {{ paciente.pac_sexo || 'N/I' }}</div>
                  <button
                    class="btn-copiar-prontuario"
                    type="button"
                    :title="prontuarioCopiado ? 'Prontuário copiado' : 'Copiar prontuário'"
                    :aria-label="prontuarioCopiado ? 'Prontuário copiado' : 'Copiar prontuário'"
                    @click="copiarProntuario"
                  >
                    <Check v-if="prontuarioCopiado" :size="14" />
                    <Copy v-else :size="14" />
                  </button>
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
            <Check v-if="corSelecionada === cor.nome" :size="15" stroke-width="3" />
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
import { Check, Copy, Search, Trash2 } from 'lucide-vue-next';
import api from '../services/api';

const props = defineProps({ enfermeiro: Object });
defineEmits(['logout']);

const modoEscuro = ref(false);
const menuPerfilAberto = ref(false);
const logoExiste = ref(true);

const chats = ref([]);
const chatAtual = ref(null);
const paciente = ref({});
const mensagens = ref([]);
const novaMensagem = ref('');
const carregando = ref(false);
const enviando = ref(false);
const messagesBox = ref(null);
const prontuarioCopiado = ref(false);
const filtroTexto = ref('');
const filtroStatus = ref('todos');

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

const filteredChats = computed(() => {
  const texto = filtroTexto.value.trim().toLowerCase();

  return chats.value.filter((chat) => {
    const nome = obterNomeExibicao(chat).toLowerCase();
    const titulo = `atendimento #${chat.ate_id}`;
    const status = chat.ate_classificacao_final?.toLowerCase() || 'em-andamento';
    const correspondeTexto = !texto || nome.includes(texto) || titulo.includes(texto);
    const correspondeStatus = filtroStatus.value === 'todos' || status === filtroStatus.value;

    return correspondeTexto && correspondeStatus;
  });
});

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

const excluirChat = async (chat) => {
  const nomeChat = obterNomeExibicao(chat);
  if (!window.confirm(`Deseja excluir o atendimento ${nomeChat}? Essa ação não pode ser desfeita.`)) return;

  try {
    await api.delete(`/atendimentos/${chat.ate_id}`);
    chats.value = chats.value.filter((item) => item.ate_id !== chat.ate_id);

    if (chatAtual.value?.ate_id === chat.ate_id) {
      chatAtual.value = null;
      paciente.value = {};
      mensagens.value = [];
    }
  } catch (err) {
    console.error('Erro ao excluir atendimento:', err);
    alert('Não foi possível excluir o atendimento.');
  }
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

const formatarHorario = (data) => {
  if (!data) return '';

  const dataMensagem = typeof data === 'number'
    ? new Date(data)
    : new Date(/(?:Z|[+-]\d{2}:?\d{2})$/.test(data) ? data : `${data}Z`);
  if (Number.isNaN(dataMensagem.getTime())) return '';

  return dataMensagem.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

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

const copiarProntuario = async () => {
  if (!chatAtual.value) return;

  const linhasPaciente = [];
  if (paciente.value.pac_nome) linhasPaciente.push(`Nome: ${paciente.value.pac_nome}`);
  if (paciente.value.pac_sexo) linhasPaciente.push(`Sexo: ${paciente.value.pac_sexo}`);

  const resumo = chatAtual.value.ate_dados_iniciais?.trim() || 'Aguardando informações do atendimento...';
  const texto = [
    'RESUMO ESTRUTURADO PARA PRONTUÁRIO',
    linhasPaciente.length ? linhasPaciente.join('\n') : '',
    resumo
  ].filter(Boolean).join('\n\n');

  try {
    await navigator.clipboard.writeText(texto);
    prontuarioCopiado.value = true;
    window.setTimeout(() => {
      prontuarioCopiado.value = false;
    }, 2000);
  } catch (err) {
    console.error('Erro ao copiar prontuário:', err);
    alert('Não foi possível copiar o prontuário.');
  }
};

const fecharMenusFora = (e) => {
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
  padding: 0.75rem 1.4rem;
  background-color: #0f172a;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
  z-index: 100;
  min-height: 64px;
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
  background: rgba(255, 255, 255, 0.12);
  color: #e0f2fe;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.18);
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
.header-nav { display: flex; align-items: center; gap: 1.15rem; }
.header-nav-link {
  position: relative; padding: 0.45rem 0.05rem; border: 0; background: transparent;
  color: #cbd5e1; font-size: 0.8rem; font-weight: 600; cursor: pointer;
  transition: color 0.2s ease;
}
.header-nav-link::after {
  content: ''; position: absolute; left: 0; right: 0; bottom: 0;
  height: 2px; border-radius: 999px; background: #93c5fd;
  transform: scaleX(0); transform-origin: center; transition: transform 0.2s ease;
}
.header-nav-link:hover, .header-nav-link.active { color: #ffffff; }
.header-nav-link:hover::after, .header-nav-link.active::after { transform: scaleX(1); }
.header-nav-link:focus-visible { outline: 2px solid #93c5fd; outline-offset: 4px; border-radius: 3px; }

/* ==================================================
   2. CORPO DA APLICAÇÃO (SIDEBAR + WORKSPACE)
================================================== */
.main-body {
  display: flex;
  flex: 1;
  height: calc(100vh - 64px);
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
  padding: 1rem 0.75rem;
  user-select: none;
}

.sidebar-navigation { display: flex; flex-direction: column; gap: 0.2rem; margin-bottom: 1rem; }

/* BOTAO NOVO ATENDIMENTO */
.nav-item {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.7rem 0.8rem; 
  border-radius: 10px; 
  border: 1px solid transparent;
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

.btn-novo-chat { background: var(--accent-color); color: #ffffff; width: 100%; text-align: left; box-shadow: 0 4px 10px rgba(30, 64, 175, 0.18); }
.btn-novo-chat:hover { background: #1d4ed8; border-color: transparent; transform: translateY(-1px); }

.sidebar-recentes { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }
.recentes-header { display: flex; align-items: center; justify-content: space-between; padding-right: 0.65rem; }
.secao-label { font-size: 0.7rem; font-weight: 700; color: var(--text-muted); padding: 0.4rem 0.7rem; margin-bottom: 0.2rem; }
.recentes-count { min-width: 1.25rem; padding: 0.12rem 0.35rem; border-radius: 999px; background: var(--bg-card); color: var(--text-muted); font-size: 0.62rem; text-align: center; }
.filtros-chats { display: flex; gap: 0.35rem; padding: 0 0.35rem 0.7rem; }
.busca-chats { min-width: 0; flex: 1; display: flex; align-items: center; gap: 0.35rem; padding: 0.4rem 0.5rem; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-primary); color: var(--text-muted); }
.busca-chats input { min-width: 0; width: 100%; border: 0; outline: 0; background: transparent; color: var(--text-main); font-size: 0.7rem; }
.busca-chats input::placeholder { color: var(--text-muted); }
.filtro-status { width: 5.2rem; padding: 0.4rem 0.25rem; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-primary); color: var(--text-main); font-size: 0.65rem; outline: 0; }
.busca-chats:focus-within, .filtro-status:focus-visible { border-color: var(--accent-color); box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12); }
.lista-chats { list-style: none; }

/* BLOCOS DOS ATENDIMENTOS RECENTES */
.chat-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.65rem 0.7rem;
  border-radius: 10px;
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
  background-color: #eaf0ff;
  border-color: #c7d2fe;
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
  padding: 0.18rem 0.42rem;
  border-radius: 999px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
}

.chat-status.em-andamento { background: #fef3c7; color: #92400e; }
.chat-status.vermelho { background: #fee2e2; color: #b91c1c; }
.chat-status.amarelo { background: #fef3c7; color: #92400e; }
.chat-status.verde { background: #dcfce7; color: #166534; }
.chat-status.azul { background: #dbeafe; color: #1d4ed8; }

[data-theme="dark"] .chat-item.active {
  background-color: #334155;
  border-color: #475569;
  color: #f8fafc;
}

[data-theme="dark"] .chat-item.active .chat-nome,
[data-theme="dark"] .chat-item.active .chat-sep {
  color: #f8fafc;
}

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
  flex: 1; display: grid; grid-template-columns: minmax(0, 1fr) 420px;
  gap: 1rem; padding: 1rem; overflow: hidden;
}

/* CHAT REFINADO */
.panel-chat {
  background-color: var(--bg-secondary); border-radius: 12px;
  border: 1px solid var(--border-color); display: flex; flex-direction: column; overflow: hidden;
}

.panel-header {
  padding: 0.85rem 1.1rem; border-bottom: 1px solid var(--border-color);
  display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; color: var(--text-muted);
}

.messages-scroll {
  flex: 1; overflow-y: auto; padding: 1.25rem; display: flex; flex-direction: column; gap: 0.9rem;
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
  max-width: 78%; padding: 0.85rem 1rem; border-radius: 14px;
  border: 1px solid transparent; font-size: 0.85rem; line-height: 1.5; position: relative;
}

.row-profissional .chat-bubble {
  background-color: var(--bg-chat-user); color: var(--text-main); text-align: right; border-bottom-right-radius: 5px;
}

.row-ia .chat-bubble {
  background-color: var(--bg-chat-ia); color: var(--text-main); text-align: left; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05); border-color: #eef2f7; border-bottom-left-radius: 5px;
}

.bubble-time { display: block; margin-top: 0.45rem; color: #64748b; font-size: 0.62rem; line-height: 1; text-align: right; }
[data-theme="dark"] .bubble-time { color: #94a3b8; }

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

.chat-input-area { padding: 0.85rem 1rem 1rem; border-top: 1px solid var(--border-color); background: var(--bg-secondary); }
.chat-input-area form { display: flex; gap: 0.5rem; }

.chat-input-area input {
  flex: 1; padding: 0.7rem 0.9rem; border-radius: 10px; border: 1px solid var(--border-color);
  background: var(--bg-primary); color: var(--text-main); font-size: 0.85rem;
}

.chat-input-area button {
  padding: 0 1.1rem; background: var(--accent-color); color: white;
  border: none; border-radius: 10px; font-weight: 600; font-size: 0.85rem; cursor: pointer;
  transition: opacity 0.2s;
}

.chat-input-area button:hover {
  opacity: 0.9;
}

/* PAINEL DIREITO */
.panel-summary { display: flex; flex-direction: column; gap: 0.8rem; }

.card-classificacao {
  padding: 1rem 1.1rem; border-radius: 10px; text-align: left;
  border: 1px solid var(--border-color); border-left: 5px solid #94a3b8; background-color: #f8fafc;
}

.card-classificacao.em-análise { background-color: #f8fafc; border-left-color: #94a3b8; }
.card-classificacao.em-análise .card-status-title { color: #475569; }
.card-classificacao.vermelho { background-color: #fef2f2; border-left-color: #dc2626; color: #991b1b; }
.card-classificacao.vermelho .card-status-title { color: #991b1b; }
.card-classificacao.laranja .card-status-title { color: #9a3412; }
.card-classificacao.amarelo { background-color: #fffbeb; border-left-color: #d97706; color: #92400e; }
.card-classificacao.amarelo .card-status-title { color: #92400e; }
.card-classificacao.verde { background-color: #f0fdf4; border-left-color: #16a34a; color: #166534; }
.card-classificacao.verde .card-status-title { color: #166534; }
.card-classificacao.azul { background-color: #eff6ff; border-left-color: #2563eb; color: #1e40af; }
.card-classificacao.azul .card-status-title { color: #1e40af; }

.card-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.5px; display: block; opacity: 0.9; }
.card-status-title { font-size: 1.35rem; font-weight: 800; margin: 0.2rem 0; }
.card-status-sub { font-size: 0.75rem; opacity: 0.95; }

.card-prontuario {
  flex: 1; background-color: var(--bg-secondary); border: 1px solid var(--border-color);
  border-radius: 10px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}

.card-header-prontuario { padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--border-color); display: flex; flex-direction: column; align-items: center; gap: 0.15rem; font-size: 0.7rem; font-weight: 700; color: var(--text-muted); }
.prontuario-fonte { font-size: 0.60rem; font-weight: 400; line-height: 1.2; text-align: center; white-space: nowrap; }
.btn-copiar-prontuario { flex-shrink: 0; width: 1.6rem; height: 1.6rem; padding: 0.25rem; display: inline-flex; align-items: center; justify-content: center; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-primary); color: var(--text-main); cursor: pointer; }
.btn-copiar-prontuario:hover { background: var(--bg-card); color: var(--accent-color, #2563eb); }
.prontuario-content { padding: 0.8rem; font-size: 0.8rem; overflow-y: auto; color: var(--text-main); }

.paciente-info-strip {
  display: flex; align-items: center; gap: 0.65rem; padding: 0.55rem 0; margin-bottom: 0.7rem;
  border-bottom: 1px solid var(--border-color); font-size: 0.75rem; color: var(--text-muted);
}

.paciente-info-strip > div { white-space: nowrap; }
.paciente-info-strip .btn-copiar-prontuario { margin-left: auto; }

.btn-excluir-chat {
  margin-left: auto; padding: 0.25rem; display: inline-flex; align-items: center; justify-content: center;
  border: 0; background: transparent; color: var(--text-muted); cursor: pointer; opacity: 0.65;
  transition: color 0.2s, opacity 0.2s;
}

.chat-item:hover .btn-excluir-chat,
.chat-item:focus-within .btn-excluir-chat { opacity: 1; }

.btn-excluir-chat:hover { color: #dc2626; }

.btn-concluir-triagem {
  padding: 0.75rem; background-color: #166534; color: white; border: none;
  border-radius: 10px; font-weight: bold; font-size: 0.8rem; cursor: pointer; transition: opacity 0.2s;
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
  background: var(--bg-secondary); padding: 1.2rem; border-radius: 12px; width: 380px;
  border: 1px solid var(--border-color); color: var(--text-main); box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
.color-options { display: flex; flex-direction: column; gap: 0.4rem; margin: 1rem 0; }
.btn-cor { padding: 0.5rem; border-radius: 8px; border: none; color: white; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.35rem; transition: transform 0.18s ease, filter 0.18s ease, box-shadow 0.18s ease; }
.btn-cor:hover { filter: brightness(0.9); transform: translateY(-1px); box-shadow: 0 4px 10px rgba(15, 23, 42, 0.2); }
.btn-cor.selected { box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.9), 0 4px 10px rgba(15, 23, 42, 0.25); transform: translateY(-1px); }
.btn-cor:focus-visible, .btn-cancel:focus-visible, .btn-confirm:focus-visible { outline: 2px solid #93c5fd; outline-offset: 2px; }
.btn-cor.vermelho { background: var(--vermelho); }
.btn-cor.amarelo { background: var(--amarelo); color: black; }
.btn-cor.verde { background: var(--verde); }
.btn-cor.azul { background: var(--azul); }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
.btn-cancel, .btn-confirm { padding: 0.5rem 0.85rem; border-radius: 8px; border: none; cursor: pointer; font-size: 0.8rem; transition: transform 0.18s ease, filter 0.18s ease, box-shadow 0.18s ease; }
.btn-cancel:hover, .btn-confirm:hover:not(:disabled) { filter: brightness(0.9); transform: translateY(-1px); box-shadow: 0 4px 10px rgba(15, 23, 42, 0.18); }
.btn-confirm { background: var(--accent-color, #1e40af); color: white; }
.btn-confirm:disabled { cursor: not-allowed; opacity: 0.55; }

/* Resumo organizado em blocos por seção, sem cartões para cada item. */
.prontuario-texto :deep(h3) {
  margin: 0.85rem 0 0;
  padding: 0.55rem 0.7rem 0.25rem;
  border: 1px solid #e2e8f0;
  border-bottom: 0;
  border-radius: 8px 8px 0 0;
  background: #f8fafc;
  color: #475569;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.prontuario-texto :deep(h3:first-child) { margin-top: 0; }
.prontuario-texto :deep(h3 + p),
.prontuario-texto :deep(h3 + ul),
.prontuario-texto :deep(h3 + ol) {
  margin: 0;
  padding: 0.35rem 0.7rem 0.65rem;
  border: 1px solid #e2e8f0;
  border-top: 0;
  border-radius: 0 0 8px 8px;
  background: #ffffff;
}
.prontuario-texto :deep(ul),
.prontuario-texto :deep(ol) { list-style: none; padding: 0; margin: 0; display: grid; gap: 0.55rem; }
.prontuario-texto :deep(li) { padding: 0.15rem 0; border: 0; background: transparent; }
.prontuario-texto :deep(li)::before { content: '-'; display: inline-block; margin-right: 0.4rem; color: #64748b; font-weight: 700; }
.prontuario-texto :deep(li strong) { display: inline; margin-right: 0.25rem; color: #64748b; font-size: 0.72rem; }

[data-theme="dark"] .row-ia .chat-bubble {
  background-color: #1e293b;
  color: #e2e8f0;
  border-color: #334155;
}

[data-theme="dark"] .row-profissional .chat-bubble {
  background-color: #1d4ed8;
  color: #eff6ff;
}

[data-theme="dark"] .card-classificacao.em-análise { background-color: #1e293b; border-left-color: #94a3b8; color: #cbd5e1; }
[data-theme="dark"] .card-classificacao.em-análise .card-status-title { color: #e2e8f0; }
[data-theme="dark"] .card-classificacao.vermelho { background-color: #3f1d24; border-left-color: #f87171; color: #fecaca; }
[data-theme="dark"] .card-classificacao.vermelho .card-status-title { color: #fecaca; }
[data-theme="dark"] .card-classificacao.amarelo { background-color: #3b2f0b; border-left-color: #fbbf24; color: #fef3c7; }
[data-theme="dark"] .card-classificacao.amarelo .card-status-title { color: #fef3c7; }
[data-theme="dark"] .card-classificacao.verde { background-color: #123522; border-left-color: #4ade80; color: #bbf7d0; }
[data-theme="dark"] .card-classificacao.verde .card-status-title { color: #bbf7d0; }
[data-theme="dark"] .card-classificacao.azul { background-color: #172554; border-left-color: #60a5fa; color: #bfdbfe; }
[data-theme="dark"] .card-classificacao.azul .card-status-title { color: #bfdbfe; }

[data-theme="dark"] .card-prontuario,
[data-theme="dark"] .prontuario-content { color: #e2e8f0; }
[data-theme="dark"] .prontuario-texto :deep(h3) { background: #1e293b; border-color: #334155; color: #cbd5e1; }
[data-theme="dark"] .prontuario-texto :deep(h3 + p),
[data-theme="dark"] .prontuario-texto :deep(h3 + ul),
[data-theme="dark"] .prontuario-texto :deep(h3 + ol) { background: #111827; border-color: #334155; color: #e2e8f0; }
[data-theme="dark"] .prontuario-texto :deep(li) { background: transparent; border-color: transparent; color: #e2e8f0; }
[data-theme="dark"] .prontuario-texto :deep(li)::before { color: #cbd5e1; }
[data-theme="dark"] .prontuario-texto :deep(li strong) { color: #cbd5e1; }
[data-theme="dark"] .paciente-info-strip { color: #cbd5e1; border-color: #334155; }

@media (max-width: 1100px) {
  .workspace-grid { grid-template-columns: minmax(0, 1fr) 350px; }
  .sub-title { display: none; }
}

@media (max-width: 820px) {
  .main-body { overflow: auto; }
  .sidebar-gpt { width: 210px; min-width: 210px; }
  .workspace-grid { grid-template-columns: 1fr; overflow: auto; }
  .panel-chat { min-height: 62vh; }
  .panel-summary { min-height: 520px; }
}
</style>