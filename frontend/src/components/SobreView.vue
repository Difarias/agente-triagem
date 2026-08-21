<template>
  <div class="sobre-layout">
    <!-- 1. HEADER TOPO-A-TOPO (IDENTICO AO DASHBOARD) -->
    <header class="top-header-full">
      <div class="header-left">
        <span class="brand-logo-fallback">🩺</span>
        <div class="header-brand-title">
          <h1>Susane Triagem</h1>
          <span class="badge-prototipo">PROTÓTIPO DE VALIDAÇÃO CIENTÍFICA</span>
        </div>
      </div>

      <div class="header-right">
        <button class="btn-voltar" @click="voltar">
          ← Voltar ao Atendimento
        </button>
      </div>
    </header>

    <!-- 2. CONTEÚDO PRINCIPAL (MINI LANDING PAGE) -->
    <main class="sobre-content">
      <div class="hero-section">
        <span class="section-badge">SOBRE O PROJETO</span>
        <h2 class="main-title">Inovação em Saúde Pública & Inteligência Artificial</h2>
        <p class="description">
          O <strong>Susane Triagem</strong> é um sistema de suporte à decisão clínica projetado para otimizar o fluxo de triagem em unidades de saúde. Fundamentado nas diretrizes e diretivas do protocolo oficial de triagem e classificação de risco da <strong>Secretaria de Saúde do Estado da Bahia (SESAB)</strong>, o copiloto atua de forma interativa junto à equipe de enfermagem, proporcionando agilidade, padronização e maior precisão diagnóstica.
        </p>
      </div>

      <!-- SEÇÃO EQUIPE -->
      <section class="team-section">
        <h3 class="section-title">Equipe de Desenvolvimento e Pesquisa</h3>
        
        <div class="team-grid">
          <div class="team-card" v-for="membro in equipe" :key="membro.nome">
            <div class="avatar-wrapper">
              <img 
                v-if="membro.foto" 
                :src="membro.foto" 
                :alt="membro.nome" 
                class="avatar-img"
                @error="membro.foto = null"
              />
              <div v-else class="avatar-placeholder">
                {{ obterIniciais(membro.nome) }}
              </div>
            </div>
            <h4 class="member-name">{{ membro.nome }}</h4>
            <span class="member-role">{{ membro.funcao }}</span>
          </div>
        </div>
      </section>

      <!-- SEÇÃO INSTITUCIONAL & CRÉDITOS -->
      <section class="institutional-section">
        <div class="institutional-card">
          <h3>Origem e Apoio Acadêmico</h3>
          <p>
            Esta plataforma é fruto de pesquisas científicas desenvolvidas no âmbito do 
            <strong>Programa de Pós-Graduação em Modelagem Computacional em Ciência e Tecnologia (PPGMC)</strong> 
            da <strong>Universidade Estadual de Santa Cruz (UESC)</strong>, representando um avanço tecnológico diretamente concebido e mantido pelo <strong>MTILAB</strong> (Laboratório de Modelação e Tecnologia da Informação).
          </p>

          <div class="logos-row">
            <img src="../assets/uesc_logo.jpeg" alt="UESC" class="inst-logo" @error="$event.target.style.display='none'" />
            <img src="../assets/ppgmc_logo.jpeg" alt="PPGMC" class="inst-logo" @error="$event.target.style.display='none'" />
            <img src="../assets/mtilab_logo.jpg" alt="MTILab" class="inst-logo" />
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const emit = defineEmits(['voltar']);

// Função auxiliar para carregar imagens estáticas dinamicamente no Vite
const getImageUrl = (name) => {
  if (!name) return null;
  return new URL(`../assets/${name}`, import.meta.url).href;
};

const equipe = ref([
  { 
    nome: 'Amanda Morais Almeida', 
    funcao: 'Engenheira de Produção', 
    foto: getImageUrl('amanda_image.jpg') 
  },
  { 
    nome: 'Diêgo Farias de Freitas', 
    funcao: 'Cientista da Computação / Desenvolvedor', 
    foto: getImageUrl('diego.png') 
  },
  { 
    nome: 'Emanuella Gomes Maia', 
    funcao: 'Pesquisadora / Especialista', 
    foto: getImageUrl('emanuella.jpg') 
  },
  { 
    nome: 'Paulo Eduardo Ambrosio', 
    funcao: 'Orientador / Coordenador MTILab', 
    foto: getImageUrl('paulo.jpg') 
  }
]);

const voltar = () => {
  emit('voltar');
};

const obterIniciais = (nome) => {
  if (!nome) return '';
  const partes = nome.trim().split(' ');
  if (partes.length === 1) return partes[0].substring(0, 2).toUpperCase();
  return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
};
</script>

<style scoped>
/* LAYOUT GLOBAL */
.sobre-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100vw;
  background-color: var(--bg-primary, #f8fafc);
  color: var(--text-main, #0f172a);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow-x: hidden;
}

/* HEADER IDENTICO AO DASHBOARD */
.top-header-full {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1.2rem;
  background-color: #1e40af;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
  height: 58px;
  flex-shrink: 0;
}

.header-left { display: flex; align-items: center; gap: 0.8rem; }
.brand-logo-fallback { font-size: 1.4rem; }
.header-brand-title { display: flex; align-items: center; gap: 0.6rem; }
.header-brand-title h1 { font-size: 1.1rem; font-weight: 700; margin: 0; color: #ffffff; }

.badge-prototipo {
  font-size: 0.6rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.2);
  color: #e0f2fe;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-voltar {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-voltar:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
}

/* CONTAINER PRINCIPAL DA LANDING PAGE */
.sobre-content {
  flex: 1;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

/* HERO SECTION */
.hero-section {
  text-align: center;
}

.section-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #1e40af;
  background-color: #dbeafe;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  margin-bottom: 0.8rem;
  letter-spacing: 0.5px;
}

.main-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.description {
  font-size: 1rem;
  color: #475569;
  line-height: 1.6;
  max-width: 780px;
  margin: 0 auto;
}

/* SEÇÃO EQUIPE */
.team-section {
  text-align: center;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 2rem;
  position: relative;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
}

.team-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.team-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.avatar-wrapper {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  margin-bottom: 1rem;
  overflow: hidden;
  border: 3px solid #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f1f5f9;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top; 
}

.avatar-placeholder {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1e40af;
}

.member-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.3rem 0;
}

.member-role {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.2;
}

/* INSTITUCIONAL */
.institutional-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.institutional-card h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #0f172a;
  margin-top: 0;
  margin-bottom: 0.8rem;
}

.institutional-card p {
  font-size: 0.92rem;
  color: #475569;
  line-height: 1.6;
  max-width: 700px;
  margin: 0 auto 1.5rem auto;
}

.logos-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
}

.inst-logo {
  height: 38px;
  width: auto;
  object-fit: contain;
  opacity: 0.85;
  transition: opacity 0.2s;
}

.inst-logo:hover {
  opacity: 1;
}

@media (max-width: 640px) {
  .team-grid { grid-template-columns: repeat(2, 1fr); }
  .main-title { font-size: 1.4rem; }
}
</style>