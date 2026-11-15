<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  createExperience,
  deleteExperience,
  getProfile,
  updateExperience,
  enhanceDescription, // NOVO IMPORT
  type Experience,
  type ExperienceInput,
} from "../services/api";

const items = ref<Experience[]>([]);
const loading = ref(false);
const saving = ref(false);
const enhancing = ref(false); // NOVO ESTADO
const error = ref<string | null>(null);
const editingId = ref<number | null>(null);

const blank = (): ExperienceInput => ({
  company: "",
  role: "",
  location: "",
  start_date: "",
  end_date: "",
  is_current: false,
  description: "",
});

const form = ref<ExperienceInput>(blank());

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const profile = await getProfile();
    items.value = profile?.experiences ?? [];
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    loading.value = false;
  }
}

function startAdd() {
  editingId.value = -1;
  form.value = blank();
}

function startEdit(exp: Experience) {
  editingId.value = exp.id;
  form.value = {
    company: exp.company,
    role: exp.role,
    location: exp.location ?? "",
    start_date: exp.start_date,
    end_date: exp.end_date ?? "",
    is_current: exp.is_current,
    description: exp.description ?? "",
  };
}

function cancel() {
  editingId.value = null;
  error.value = null;
}

// NOVA FUNÇÃO DE IA
async function improveDescription() {
  if (!form.value.description?.trim()) return;
  enhancing.value = true;
  error.value = null;
  try {
    form.value.description = await enhanceDescription(
      form.value.description,
      "experience",
      form.value.role
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
    const payload: ExperienceInput = {
      company: form.value.company.trim(),
      role: form.value.role.trim(),
      location: form.value.location?.trim() || null,
      start_date: form.value.start_date,
      end_date: form.value.is_current ? null : form.value.end_date || null,
      is_current: form.value.is_current,
      description: form.value.description?.trim() || null,
    };
    if (editingId.value && editingId.value > 0) {
      await updateExperience(editingId.value, payload);
    } else {
      await createExperience(payload);
    }
    editingId.value = null;
    await load();
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  } finally {
    saving.value = false;
  }
}

async function remove(id: number) {
  if (!confirm("Remover esta experiência?")) return;
  try {
    await deleteExperience(id);
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
      <h2>Experiências</h2>
      <button v-if="editingId === null" class="btn-add" @click="startAdd">
        + Adicionar
      </button>
    </div>

    <p v-if="loading">Carregando…</p>
    <p v-if="error" class="msg error">Erro: {{ error }}</p>

    <ul v-if="items.length && editingId === null" class="list">
      <li v-for="exp in items" :key="exp.id" class="card">
        <div class="card-body">
          <strong>{{ exp.role }} · {{ exp.company }}</strong>
          <div class="dates">
            {{ exp.start_date }} →
            {{ exp.is_current ? "Atual" : exp.end_date || "?" }}
            <span v-if="exp.location"> · {{ exp.location }}</span>
          </div>
          <p v-if="exp.description" class="desc">{{ exp.description }}</p>
        </div>
        <div class="card-actions">
          <button @click="startEdit(exp)">Editar</button>
          <button class="danger" @click="remove(exp.id)">Excluir</button>
        </div>
      </li>
    </ul>
    <p v-if="!loading && !items.length && editingId === null" class="empty">
      Nenhuma experiência cadastrada.
    </p>

    <form v-if="editingId !== null" class="form" @submit.prevent="save">
      <div class="row">
        <div class="field">
          <label>Cargo *</label>
          <input v-model="form.role" required maxlength="200" />
        </div>
        <div class="field">
          <label>Empresa *</label>
          <input v-model="form.company" required maxlength="200" />
        </div>
      </div>

      <div class="row">
        <div class="field">
          <label>Local</label>
          <input v-model="form.location" maxlength="200" />
        </div>
        <div class="field">
          <label>Início *</label>
          <input v-model="form.start_date" type="date" required />
        </div>
        <div class="field">
          <label>Fim</label>
          <input v-model="form.end_date" type="date" :disabled="form.is_current" />
        </div>
      </div>

      <label class="check">
        <input v-model="form.is_current" type="checkbox" />
        Trabalho atual
      </label>

      <!-- BOTÃO DE IA ADICIONADO AQUI -->
      <div class="field">
        <div class="label-row">
          <label>Descrição</label>
          <button type="button" class="btn-ai" @click="improveDescription" :disabled="enhancing">
            {{ enhancing ? 'Gerando...' : '✨ Melhorar com IA (STAR)' }}
          </button>
        </div>
        <textarea v-model="form.description" rows="5" placeholder="Descreva o que você fez. A IA vai aplicar o método STAR."></textarea>
      </div>

      <div class="actions">
        <button type="submit" :disabled="saving">
          {{ saving ? "Salvando…" : "Salvar" }}
        </button>
        <button type="button" class="ghost" @click="cancel">Cancelar</button>
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
.card-actions button { background: transparent; border: 1px solid #ccc; padding: 0.25rem 0.6rem; border-radius: 4px; margin-left: 0.35rem; cursor: pointer; font-size: 0.85rem; }
.card-actions button.danger { color: #b00020; border-color: #b00020; }
.form { background: #fff; border: 1px solid #e0e0e0; border-radius: 6px; padding: 1rem; }
.field { display: flex; flex-direction: column; margin-bottom: 0.75rem; flex: 1; }
.field label { font-size: 0.8rem; font-weight: 600; margin-bottom: 0.2rem; }
.field input, .field textarea { padding: 0.45rem; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; font-size: 0.9rem; }
.field input:disabled { background: #f0f0f0; color: #888; }
.row { display: flex; gap: 0.75rem; }
.check { display: block; margin: 0.25rem 0 0.75rem; font-size: 0.9rem; }
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