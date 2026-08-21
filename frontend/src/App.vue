<template>
  <div id="app">
    <!-- 1. TELA DE LOGIN -->
    <LoginView 
      v-if="telaAtual === 'login'" 
      @login-sucesso="handleLoginSucesso" 
    />

    <!-- 2. TELA DE CHAT -->
    <ChatView 
      v-else-if="telaAtual === 'chat'" 
      :enfermeiro="enfermeiroLogado" 
      @logout="handleLogout" 
      @abrir-sobre="telaAtual = 'sobre'"
    />

    <!-- 3. TELA SOBRE -->
    <SobreView 
      v-else-if="telaAtual === 'sobre'" 
      @voltar="telaAtual = 'chat'" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import LoginView from './components/LoginView.vue';
import ChatView from './components/ChatView.vue';
import SobreView from './components/SobreView.vue';

const enfermeiroLogado = ref(null);
const telaAtual = ref('login'); // Pode ser: 'login', 'chat' ou 'sobre'

const handleLoginSucesso = (enfermeiro) => {
  enfermeiroLogado.value = enfermeiro;
  localStorage.setItem('enfermeiro_sesab', JSON.stringify(enfermeiro));
  telaAtual.value = 'chat';
};

const handleLogout = () => {
  enfermeiroLogado.value = null;
  localStorage.removeItem('enfermeiro_sesab');
  telaAtual.value = 'login';
};

onMounted(() => {
  const salvo = localStorage.getItem('enfermeiro_sesab');
  if (salvo) {
    try {
      enfermeiroLogado.value = JSON.parse(salvo);
      telaAtual.value = 'chat';
    } catch (e) {
      localStorage.removeItem('enfermeiro_sesab');
      telaAtual.value = 'login';
    }
  }
});
</script>

<style>
@import './assets/main.css';
</style>