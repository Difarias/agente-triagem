<template>
  <div id="app">
    <LoginView v-if="!enfermeiroLogado" @login-sucesso="handleLoginSucesso" />
    <ChatView v-else :enfermeiro="enfermeiroLogado" @logout="handleLogout" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import LoginView from './components/LoginView.vue';
import ChatView from './components/ChatView.vue';

const enfermeiroLogado = ref(null);

const handleLoginSucesso = (enfermeiro) => {
  enfermeiroLogado.value = enfermeiro;
  localStorage.setItem('enfermeiro_sesab', JSON.stringify(enfermeiro));
};

const handleLogout = () => {
  enfermeiroLogado.value = null;
  localStorage.removeItem('enfermeiro_sesab');
};

onMounted(() => {
  const salvo = localStorage.getItem('enfermeiro_sesab');
  if (salvo) {
    try {
      enfermeiroLogado.value = JSON.parse(salvo);
    } catch (e) {
      localStorage.removeItem('enfermeiro_sesab');
    }
  }
});
</script>

<style>
@import './assets/main.css';
</style>