<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  createProject,
  deleteProject,
  getProfile,
  enhanceDescription, // NOVO IMPORT
  type Project,
  type ProjectInput,
} from "../services/api";

const items = ref<Project[]>([]);
const loading = ref(false);
const saving = ref(false);
const enhancing = ref(false); // NOVO ESTADO
const error = ref<string | null>(null);
const showForm = ref(false);

const blank = (): ProjectInput => ({
  name: "",
  link: "",
  description: "",
  start_date: "",
  end_date: "",
});

const form = ref<ProjectInput>(blank());

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const profile = await getProfile();
    items.value = profile?.projects ?? [];
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    loading.value = false;
  }
}

function startAdd() {
  form.value = blank();
  showForm.value = true;
}

// NOVA FUNÇÃO DE IA
async function improveDescription() {
  if (!form.value.description?.trim()) return;
  enhancing.value = true;
  error.value = null;
  try {
    form.value.description = await enhanceDescription(
      form.value.description,
      "project",
      form.value.name
    );
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    enhancing.value = false;
  }
}

async function save() {
  saving.value = true;
  error.value = null;
  try {
    const payload: ProjectInput = {
      name: form.value.name.trim(),
      link: form.value.link?.trim() || null,
      description: form.value.description?.trim() || null,
      start_date: form.value.start_date || null,
      end_date: form.value.end_date || null,
    };
    await createProject(payload);
    showForm.value = false;
    await load();
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    saving.value = false;
  }
}

async function remove(id: number) {
  if (!confirm("Remover este projeto?")) return;
  try {
    await deleteProject(id);
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
      <h2>Projetos Pessoais e Acadêmicos</h2>
      <button v-if="!showForm" class="btn-add" @click="startAdd">+ Adicionar</button>
    </div>

    <p v-if="loading">Carregando…</p>
    <p v-if="error" class="msg error">Erro: {{ error }}</p>

    <ul v-if="items.length && !showForm" class="list">
      <li v-for="proj in items" :key="proj.id" class="card">
        <div class="card-body">
          <strong>{{ proj.name }}</strong>
          <span v-if="proj.link"> | <a :href="proj.link" target="_blank" style="color:#7a1fa2">Link</a></span>
          <div class="dates" v-if="proj.start_date || proj.end_date">
            {{ proj.start_date || '?' }} → {{ proj.end_date || '?' }}
          </div>
          <p v-if="proj.description" class="desc">{{ proj.description }}</p>
        </div>
        <div class="card-actions">
          <button class="danger" @click="remove(proj.id)">Excluir</button>
        </div>
      </li>
    </ul>
    <p v-if="!loading && !items.length && !showForm" class="empty">Nenhum projeto cadastrado.</p>

    <form v-if="showForm" class="form" @submit.prevent="save">
      <div class="field">
        <label>Nome do Projeto *</label>
        <input v-model="form.name" required maxlength="200" placeholder="Ex: Portfólio Interativo 3D" />
      </div>
      
      <div class="field">
        <label>Link (Opcional)</label>
        <input v-model="form.link" type="url" maxlength="500" placeholder="https://github.com/..." />
      </div>

      <div class="row">
        <div class="field">
          <label>Data de Início</label>
          <input v-model="form.start_date" type="date" />
        </div>
        <div class="field">
          <label>Data de Fim</label>
          <input v-model="form.end_date" type="date" />
        </div>
      </div>

      <!-- BOTÃO DE IA ADICIONADO AQUI -->
      <div class="field">
        <div class="label-row">
          <label>Descrição (bullets)</label>
          <button type="button" class="btn-ai" @click="improveDescription" :disabled="enhancing">
            {{ enhancing ? 'Gerando...' : '✨ Melhorar com IA' }}
          </button>
        </div>
        <textarea v-model="form.description" rows="5" placeholder="Uma linha por bullet. Ou escreva livremente e a IA organiza."></textarea>
      </div>

      <div class="actions">
        <button type="submit" :disabled="saving">{{ saving ? "Salvando…" : "Salvar" }}</button>
        <button type="button" class="ghost" @click="showForm = false">Cancelar</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.section { padding: 0.5rem 0; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.section-header h2 { margin: 0 0 0.75rem; }
.btn-add { background: #7a1fa2; color: #fff; border: 0; padding: 0.4rem 0.9rem; border-radius: 4px; cursor: pointer; }
.list { list-style: none; padding: 0; margin: 0 0 1rem; }
.card { background: #fff; border: 1px solid #e0e0e0; border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; gap: 1rem; }
.card-body { flex: 1; }
.dates { font-size: 0.85rem; color: #555; margin: 0.15rem 0; }
.desc { font-size: 0.9rem; margin: 0.4rem 0 0; white-space: pre-wrap; }
.card-actions button { background: transparent; border: 1px solid #ccc; padding: 0.25rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
.card-actions button.danger { color: #b00020; border-color: #b00020; }
.form { background: #fff; border: 1px solid #e0e0e0; border-radius: 6px; padding: 1rem; }
.field { display: flex; flex-direction: column; margin-bottom: 0.75rem; flex: 1; }
.field label { font-size: 0.8rem; font-weight: 600; margin-bottom: 0.2rem; }
.field input, .field textarea { padding: 0.45rem; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; font-size: 0.9rem; }
.row { display: flex; gap: 0.75rem; }
.actions { display: flex; gap: 0.5rem; margin-top: 1rem; }
.actions button { background: #1f1f1f; color: #fff; border: 0; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
.actions button.ghost { background: transparent; color: #333; border: 1px solid #ccc; }
.msg.error { color: #b00020; font-size: 0.9rem; }
.empty { color: #888; font-style: italic; }

/* ESTILOS DO BOTÃO DE IA */
.label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.btn-ai {
  background: linear-gradient(135deg, #7a1fa2, #b219c9);
  color: #fff;
  border: 0;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.1s;
}
.btn-ai:hover:not(:disabled) { transform: scale(1.05); }
.btn-ai:disabled { opacity: 0.6; cursor: wait; }
</style>