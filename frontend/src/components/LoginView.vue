<template>
  <div class="auth-layout">
    <!-- PAINEL ESQUERDO: FORMULÁRIO DE AUTENTICAÇÃO -->
    <div class="auth-panel-form">
      <div class="form-wrapper">
        <!-- CABEÇALHO DO FORMULÁRIO -->
        <div class="brand-header">
          <span class="brand-icon">🩺</span>
          <h1 class="brand-title">Susane Triagem</h1>
          <p class="brand-subtitle">Suporte à Decisão Clínica com Inteligência Artificial</p>
        </div>

        <!-- TABS DE NAVEGAÇÃO (LOGIN / CADASTRO) -->
        <div class="auth-tabs">
          <button 
            :class="['tab-btn', { active: isLogin }]" 
            @click="isLogin = true; erro = ''"
          >
            Acessar
          </button>
          <button 
            :class="['tab-btn', { active: !isLogin }]" 
            @click="isLogin = false; erro = ''"
          >
            Cadastrar
          </button>
        </div>

        <!-- FORMULÁRIO -->
        <form @submit.prevent="handleSubmit" class="auth-form">
          <div v-if="!isLogin" class="form-group">
            <label for="nome">Nome Completo</label>
            <input 
              id="nome"
              v-model="form.enf_nome" 
              type="text" 
              placeholder="Enfª. Maria Silva" 
              required 
            />
          </div>

          <div v-if="!isLogin" class="form-group">
            <label for="coren">COREN</label>
            <input 
              id="coren"
              v-model="form.enf_coren" 
              type="text" 
              placeholder="COREN-BA 123456" 
              required 
            />
          </div>

          <div class="form-group">
            <label for="email">E-mail Profissional</label>
            <input 
              id="email"
              v-model="form.enf_email" 
              type="email" 
              placeholder="enfermeiro@hospital.ba.gov.br" 
              required 
            />
          </div>

          <div class="form-group">
            <label for="senha">Senha</label>
            <input 
              id="senha"
              v-model="form.enf_senha" 
              type="password" 
              placeholder="••••••••" 
              required 
            />
          </div>

          <button type="submit" class="btn-primary" :disabled="carregando">
            <span v-if="carregando">Processando...</span>
            <span v-else>{{ isLogin ? 'Entrar no Sistema' : 'Criar Conta' }}</span>
          </button>

          <p v-if="erro" class="error-alert">{{ erro }}</p>
        </form>

        <!-- RODAPÉ ACADÊMICO / CRÉDITOS -->
        <div class="academic-footer">
          <p class="project-tag">Projeto de Pesquisa & Validação Científica</p>
          <p class="project-version">Versão 1.0.0</p>
          <div class="logos-grid">
            <img src="../assets/uesc_logo.jpeg" alt="Logo UESC" class="institution-logo" title="UESC" @error="$event.target.style.display='none'" />
            <img src="../assets/ppgmc_logo.jpeg" alt="Programa de Mestrado" class="institution-logo" title="Mestrado" @error="$event.target.style.display='none'" />
            <img src="../assets/mtilab_logo.jpg" alt="Logo MTILab" class="institution-logo" title="MTILab" />
          </div>
        </div>
      </div>
    </div>

    <!-- PAINEL DIREITO: HERO / BANNER ILUSTRATIVO -->
    <div class="auth-panel-hero">
      <div class="hero-overlay">
        <div class="hero-content">
          <span class="hero-badge">PROTOCOLO DE TRIAGEM</span>
          <h2>Apoio inteligente para uma classificação de risco rápida e assertiva.</h2>
          <p>Ferramenta de copiloto para enfermagem baseada em diretrizes clínicas e inteligência artificial.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../services/api';

const emit = defineEmits(['login-sucesso']);

const isLogin = ref(true);
const erro = ref('');
const carregando = ref(false);

const form = ref({
  enf_nome: '',
  enf_coren: '',
  enf_email: '',
  enf_senha: ''
});

const handleSubmit = async () => {
  erro.value = '';
  carregando.value = true;
  try {
    if (isLogin.value) {
      const res = await api.post('/auth/login', {
        enf_email: form.value.enf_email,
        enf_senha: form.value.enf_senha
      });
      
      const enfermeiroData = res.data.enfermeiro || res.data;
      emit('login-sucesso', enfermeiroData);
    } else {
      await api.post('/auth/cadastro', form.value);
      alert('Cadastro realizado com sucesso! Faça login para prosseguir.');
      isLogin.value = true;
    }
  } catch (err) {
    erro.value = err.response?.data?.detail || 'Ocorreu um erro ao processar. Verifique seus dados.';
  } finally {
    carregando.value = false;
  }
};
</script>

<style scoped>
/* ESTRUTURA PRINCIPAL (SPLIT SCREEN 60/40) */
.auth-layout {
  display: flex;
  min-height: 100vh;
  width: 100vw;
  background-color: #ffffff;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden;
}

/* 1. PAINEL ESQUERDO: FORMULÁRIO (40% DA LARGURA - FUNDO BRANCO FIXO) */
.auth-panel-form {
  flex: 0 0 40%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem 2rem;
  background-color: #ffffff !important; /* Fundo branco fixo */
  color: #0f172a;
  z-index: 2;
  overflow-y: auto;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.05);
}

.form-wrapper {
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
}

.brand-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.3rem; /* Espaçamento controlado entre o ícone e o texto */
  text-align: center;
  margin-bottom: 2rem;
}

.brand-icon {
  font-size: 2rem; /* Tamanho reduzido para não poluir */
  line-height: 1; /* Elimina a folga vertical padrão de linha de texto */
  display: inline-block;
  margin: 0;
}

.brand-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.brand-subtitle {
  font-size: 0.9rem;
  color: #64748b;
  margin-top: 0.38rem;
  line-height: 1.35;
}

/* TABS (LOGIN / CADASTRO) */
.auth-tabs {
  display: flex;
  background-color: #f1f5f9;
  padding: 0.25rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.tab-btn {
  flex: 1;
  padding: 0.65rem;
  border: none;
  background: transparent;
  color: #64748b;
  font-weight: 600;
  font-size: 0.88rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background-color: #ffffff;
  color: #1e40af;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* FORMULÁRIO E INPUTS */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 0.9rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background-color: #ffffff;
  color: #0f172a;
  font-size: 0.92rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #1e40af;
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.15);
}

.btn-primary {
  margin-top: 0.5rem;
  padding: 0.85rem;
  border-radius: 8px;
  border: none;
  background-color: #1e40af;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.92rem;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-primary:active {
  transform: scale(0.99);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-alert {
  background-color: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 0.65rem;
  border-radius: 6px;
  font-size: 0.82rem;
  text-align: center;
  margin-top: 0.5rem;
}

/* RODAPÉ DAS LOGOS ACADÊMICAS */
.academic-footer {
  margin-top: 2.5rem;
  padding-top: 1.4rem;
  border-top: 1px solid #e2e8f0;
  text-align: center;
}

.project-tag {
  font-size: 0.7rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem; /* Ajustado para aproximar da versão */
}

.project-version {
  font-size: 0.62rem;
  font-weight: 600;
  color: #a1a1aa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 0;
  margin-bottom: 0.9rem; /* Margem para separar dos logos abaixo */
}

.logos-grid {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.2rem;
}

.institution-logo {
  height: 40px;
  width: auto;
  opacity: 0.8;
  filter: grayscale(20%);
  transition: opacity 0.2s ease, filter 0.2s ease;
  object-fit: contain;
}

.institution-logo:hover {
  opacity: 1;
  filter: grayscale(0%);
}

/* 2. PAINEL DIREITO: HERO BANNER (60% DA LARGURA) */
.auth-panel-hero {
  flex: 0 0 60%;
  background-image: url('../assets/banner_login.jpg');
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
}

.hero-overlay {
  flex: 1;
  background: linear-gradient(135deg, rgba(30, 64, 175, 0.88) 0%, rgba(15, 23, 42, 0.94) 100%);
  display: flex;
  align-items: flex-end;
  padding: 3.5rem 2.5rem;
  color: #ffffff;
}

.hero-content {
  max-width: 440px;
}

.hero-badge {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 1px;
  background: rgba(255, 255, 255, 0.15);
  padding: 0.3rem 0.75rem;
  border-radius: 20px;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.25);
}

.hero-content h2 {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.3;
  margin: 0 0 0.8rem 0;
  color: #ffffff;
}

.hero-content p {
  font-size: 0.92rem;
  color: #cbd5e1;
  line-height: 1.5;
  margin: 0;
}

/* ADAPTAÇÃO RESPONSIVA */
@media (max-width: 900px) {
  .auth-panel-hero {
    display: none;
  }
  .auth-panel-form {
    flex: 0 0 100%;
    width: 100%;
  }
}
</style>