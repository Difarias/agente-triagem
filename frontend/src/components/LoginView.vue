<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo">
        <span class="icon">🩺</span>
        <h2>Triagem SESAB</h2>
        <p>Suporte à Decisão Clínica com IA</p>
      </div>

      <div class="tabs">
        <button :class="{ active: isLogin }" @click="isLogin = true">Login</button>
        <button :class="{ active: !isLogin }" @click="isLogin = false">Cadastrar</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div v-if="!isLogin" class="form-group">
          <label>Nome Completo</label>
          <input v-model="form.enf_nome" type="text" placeholder="Enf. Silva" required />
        </div>

        <div v-if="!isLogin" class="form-group">
          <label>COREN</label>
          <input v-model="form.enf_coren" type="text" placeholder="COREN-BA 123456" required />
        </div>

        <div class="form-group">
          <label>E-mail</label>
          <input v-model="form.enf_email" type="email" placeholder="enfermeiro@hospital.ba.gov.br" required />
        </div>

        <div class="form-group">
          <label>Senha</label>
          <input v-model="form.enf_senha" type="password" placeholder="••••••••" required />
        </div>

        <button type="submit" class="btn-submit">
          {{ isLogin ? 'Entrar no Sistema' : 'Criar Conta' }}
        </button>

        <p v-if="erro" class="error-msg">{{ erro }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../services/api';

const emit = defineEmits(['login-sucesso']);

const isLogin = ref(true);
const erro = ref('');

const form = ref({
  enf_nome: '',
  enf_coren: '',
  enf_email: '',
  enf_senha: ''
});

const handleSubmit = async () => {
  erro.value = '';
  try {
    if (isLogin.value) {
      const res = await api.post('/auth/login', {
        enf_email: form.value.enf_email,
        enf_senha: form.value.enf_senha
      });
      
      // Garante a captura do objeto do enfermeiro independente do formato da API
      const enfermeiroData = res.data.enfermeiro || res.data;
      emit('login-sucesso', enfermeiroData);
    } else {
      await api.post('/auth/cadastro', form.value);
      alert('Cadastro realizado com sucesso! Faça login.');
      isLogin.value = true;
    }
  } catch (err) {
    erro.value = err.response?.data?.detail || 'Ocorreu um erro. Tente novamente.';
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: var(--bg-primary);
}

.login-card {
  background: var(--bg-secondary);
  padding: 2.5rem;
  border-radius: 12px;
  width: 100%;
  max-width: 420px;
  border: 1px solid var(--border-color);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
}

.logo {
  text-align: center;
  margin-bottom: 1.5rem;
}

.logo .icon {
  font-size: 2.5rem;
}

.logo h2 {
  color: var(--text-main);
  font-size: 1.5rem;
}

.logo p {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.tabs {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.tabs button {
  flex: 1;
  padding: 0.75rem;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-weight: 600;
}

.tabs button.active {
  color: var(--accent-color);
  border-bottom: 2px solid var(--accent-color);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 0.4rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--bg-chat);
  color: var(--text-main);
}

.btn-submit {
  width: 100%;
  padding: 0.85rem;
  border-radius: 6px;
  border: none;
  background: var(--accent-color);
  color: white;
  font-weight: bold;
  cursor: pointer;
  margin-top: 1rem;
}

.btn-submit:hover {
  opacity: 0.9;
}

.error-msg {
  color: var(--vermelho);
  font-size: 0.85rem;
  margin-top: 1rem;
  text-align: center;
}
</style>