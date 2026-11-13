<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  createLink,
  deleteLink,
  getProfile,
  type Link,
  type LinkInput,
} from "../services/api";

const items = ref<Link[]>([]);
const loading = ref(false);
const saving = ref(false);
const error = ref<string | null>(null);

const form = ref<LinkInput>({ name: "", url: "" });

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const profile = await getProfile();
    items.value = profile?.links ?? [];
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    loading.value = false;
  }
}

async function save() {
  saving.value = true;
  error.value = null;
  try {
    await createLink({ name: form.value.name.trim(), url: form.value.url.trim() });
    form.value = { name: "", url: "" };
    await load();
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    saving.value = false;
  }
}

async function remove(id: number) {
  if (!confirm("Remover este link?")) return;
  try {
    await deleteLink(id);
    await load();
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  }
}

onMounted(load);
</script>

<template>
  <div class="section">
    <div class="section-header">
      <h2>Links (GitHub, LinkedIn, Portfólio)</h2>
    </div>

    <p v-if="loading">Carregando…</p>
    <p v-if="error" class="msg error">Erro: {{ error }}</p>

    <ul v-if="items.length" class="list">
      <li v-for="l in items" :key="l.id" class="card">
        <div class="card-body">
          <strong>{{ l.name }}:</strong> 
          <a :href="l.url" target="_blank" class="url">{{ l.url }}</a>
        </div>
        <div class="card-actions">
          <button class="danger" @click="remove(l.id)">Excluir</button>
        </div>
      </li>
    </ul>
    <p v-if="!loading && !items.length" class="empty">Nenhum link cadastrado.</p>

    <form class="form" @submit.prevent="save">
      <div class="row">
        <div class="field" style="flex: 1">
          <label>Nome (ex: GitHub)</label>
          <input v-model="form.name" required maxlength="100" />
        </div>
        <div class="field" style="flex: 3">
          <label>URL (ex: https://github.com/seu-user)</label>
          <input v-model="form.url" type="url" required maxlength="500" />
        </div>
      </div>
      <div class="actions">
        <button type="submit" :disabled="saving">
          {{ saving ? "Adicionando…" : "Adicionar Link" }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.section { padding: 0.5rem 0; }
.section-header h2 { margin: 0 0 0.75rem; }
.list { list-style: none; padding: 0; margin: 0 0 1rem; }
.card { background: #fff; border: 1px solid #e0e0e0; border-radius: 6px; padding: 0.6rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }
.url { color: #7a1fa2; text-decoration: none; }
.url:hover { text-decoration: underline; }
.card-actions button { background: transparent; border: 1px solid #ccc; padding: 0.25rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
.card-actions button.danger { color: #b00020; border-color: #b00020; }
.form { background: #fff; border: 1px solid #e0e0e0; border-radius: 6px; padding: 1rem; margin-top: 1rem; }
.field { display: flex; flex-direction: column; margin-bottom: 0.75rem; }
.field label { font-size: 0.8rem; font-weight: 600; margin-bottom: 0.2rem; }
.field input { padding: 0.45rem; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; }
.row { display: flex; gap: 0.75rem; }
.actions button { background: #1f1f1f; color: #fff; border: 0; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
.msg.error { color: #b00020; font-size: 0.9rem; }
.empty { color: #888; font-style: italic; }
</style>