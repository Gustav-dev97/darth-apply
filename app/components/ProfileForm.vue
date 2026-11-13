<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  getProfile,
  saveProfile,
  enhanceSummary,
  type UserProfileInput,
} from "../services/api";

const form = ref<UserProfileInput>({
  full_name: "",
  email: "",
  phone: "",
  city: "",
  state: "",
  headline: "",
  summary: "",
});

const loading = ref(false);
const saving = ref(false);
const enhancing = ref(false);
const error = ref<string | null>(null);
const success = ref<string | null>(null);

async function load() {
  loading.value = true;
  error.value = null;
  success.value = null;
  try {
    const profile = await getProfile();
    if (profile) {
      form.value = {
        full_name: profile.full_name,
        email: profile.email,
        phone: profile.phone ?? "",
        city: profile.city ?? "",
        state: profile.state ?? "",
        headline: profile.headline ?? "",
        summary: profile.summary ?? "",
      };
    }
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    loading.value = false;
  }
}

async function saveToDb() {
  const payload: UserProfileInput = {
    full_name: form.value.full_name.trim(),
    email: form.value.email.trim(),
    phone: form.value.phone?.trim() || null,
    city: form.value.city?.trim() || null,
    state: form.value.state?.trim().toUpperCase() || null,
    headline: form.value.headline?.trim() || null,
    summary: form.value.summary?.trim() || null,
  };
  return await saveProfile(payload);
}

async function improveSummary() {
  if (!form.value.summary?.trim()) return;
  enhancing.value = true;
  error.value = null;
  try {
    // 1. Pede para a IA melhorar
    const enhanced = await enhanceSummary(form.value.summary);
    form.value.summary = enhanced;
    
    // 2. Salva automaticamente no banco
    await saveToDb();
    
    success.value = "Resumo aprimorado e salvo com sucesso!";
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    enhancing.value = false;
  }
}

async function save() {
  saving.value = true;
  error.value = null;
  success.value = null;
  try {
    const saved = await saveToDb();
    success.value = `Perfil salvo (id ${saved.id}, atualizado em ${new Date(
      saved.updated_at,
    ).toLocaleString("pt-BR")})`;
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="profile-form">
    <h2>Perfil Profissional</h2>

    <p v-if="loading">Carregando perfil…</p>

    <form v-else @submit.prevent="save">
      <div class="field">
        <label>Nome completo *</label>
        <input v-model="form.full_name" required maxlength="200" />
      </div>

      <div class="field">
        <label>Email *</label>
        <input v-model="form.email" type="email" required maxlength="200" />
      </div>

      <div class="row">
        <div class="field">
          <label>Telefone</label>
          <input v-model="form.phone" maxlength="50" />
        </div>
        <div class="field">
          <label>Cidade</label>
          <input v-model="form.city" maxlength="120" />
        </div>
        <div class="field field-narrow">
          <label>UF</label>
          <input v-model="form.state" maxlength="2" />
        </div>
      </div>

      <div class="field">
        <label>Headline</label>
        <input
          v-model="form.headline"
          maxlength="300"
          placeholder="Ex.: Desenvolvedor Back-end Python"
        />
      </div>

      <div class="field">
        <div class="label-row">
          <label>Resumo</label>
          <button type="button" class="btn-ai" @click="improveSummary" :disabled="enhancing">
            {{ enhancing ? 'Gerando...' : '✨ Melhorar com IA' }}
          </button>
        </div>
        <textarea v-model="form.summary" rows="5"></textarea>
      </div>

      <div class="actions">
        <button type="submit" :disabled="saving">
          {{ saving ? "Salvando…" : "Salvar" }}
        </button>
      </div>

      <p v-if="error" class="msg error">Erro: {{ error }}</p>
      <p v-if="success" class="msg success">{{ success }}</p>
    </form>
  </div>
</template>

<style scoped>
.profile-form {
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
.profile-form h2 { margin-top: 0; }
.field { display: flex; flex-direction: column; margin-bottom: 0.9rem; }
.label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.field label { font-size: 0.85rem; font-weight: 600; color: #333; }
.field input, .field textarea {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.95rem;
  font-family: inherit;
}
.field input:focus, .field textarea:focus { outline: 2px solid #7a1fa2; border-color: transparent; }
.row { display: grid; grid-template-columns: 2fr 2fr 1fr; gap: 0.75rem; }
.field-narrow input { text-transform: uppercase; max-width: 100px; }

/* Botão de IA */
.btn-ai {
  background: linear-gradient(135deg, #7a1fa2, #b219c9);
  color: #fff;
  border: 0;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.1s;
}
.btn-ai:hover:not(:disabled) { transform: scale(1.05); }
.btn-ai:disabled { opacity: 0.6; cursor: wait; }

.actions { margin-top: 1rem; }
.actions button {
  background: #1f1f1f;
  color: #fff;
  border: 0;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}
.actions button:hover:not(:disabled) { background: #333; }
.actions button:disabled { opacity: 0.6; cursor: wait; }
.msg { margin-top: 1rem; font-size: 0.9rem; }
.msg.error { color: #b00020; }
.msg.success { color: #1b7a2e; }
</style>