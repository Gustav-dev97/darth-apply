<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
    createSkill,
    deleteSkill,
    getProfile,
    updateSkill,
    type Skill,
    type SkillInput,
} from "../services/api";

const items = ref<Skill[]>([]);
const loading = ref(false);
const saving = ref(false);
const error = ref<string | null>(null);
const editingId = ref<number | null>(null);

const blank = (): SkillInput => ({
    name: "",
    category: "",
    proficiency: 3,
});

const form = ref<SkillInput>(blank());

async function load() {
    loading.value = true;
    error.value = null;
    try {
        const profile = await getProfile();
        items.value = profile?.skills ?? [];
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

function startEdit(s: Skill) {
    editingId.value = s.id;
    form.value = {
        name: s.name,
        category: s.category ?? "",
        proficiency: s.proficiency ?? 3,
    };
}

function cancel() {
    editingId.value = null;
    error.value = null;
}

async function save() {
    saving.value = true;
    error.value = null;
    try {
        const payload: SkillInput = {
            name: form.value.name.trim(),
            category: form.value.category?.trim() || null,
            proficiency: form.value.proficiency ?? null,
        };
        if (editingId.value && editingId.value > 0) {
            await updateSkill(editingId.value, payload);
        } else {
            await createSkill(payload);
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
    if (!confirm("Remover esta habilidade?")) return;
    try {
        await deleteSkill(id);
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
            <h2>Habilidades</h2>
            <button v-if="editingId === null" class="btn-add" @click="startAdd">
                + Adicionar
            </button>
        </div>

        <p v-if="loading">Carregando…</p>
        <p v-if="error" class="msg error">Erro: {{ error }}</p>

        <ul v-if="items.length && editingId === null" class="list">
            <li v-for="s in items" :key="s.id" class="card">
                <div class="card-body">
                    <strong>{{ s.name }}</strong>
                    <span v-if="s.category" class="tag">{{ s.category }}</span>
                    <span v-if="s.proficiency" class="stars">
                        {{ "★".repeat(s.proficiency) }}{{ "☆".repeat(5 - s.proficiency) }}
                    </span>
                </div>
                <div class="card-actions">
                    <button @click="startEdit(s)">Editar</button>
                    <button class="danger" @click="remove(s.id)">Excluir</button>
                </div>
            </li>
        </ul>
        <p v-if="!loading && !items.length && editingId === null" class="empty">
            Nenhuma habilidade cadastrada.
        </p>

        <form v-if="editingId !== null" class="form" @submit.prevent="save">
            <div class="row">
                <div class="field">
                    <label>Nome *</label>
                    <input v-model="form.name" required maxlength="100" />
                </div>
                <div class="field">
                    <label>Categoria</label>
                    <input v-model="form.category" maxlength="80" placeholder="Ex.: Linguagem, Framework" />
                </div>
                <div class="field">
                    <label>Proficiência</label>
                    <select v-model.number="form.proficiency">
                        <option :value="1">1 — Básico</option>
                        <option :value="2">2 — Limitado</option>
                        <option :value="3">3 — Bom</option>
                        <option :value="4">4 — Avançado</option>
                        <option :value="5">5 — Expert</option>
                    </select>
                </div>
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
.section {
    padding: 0.5rem 0;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.section-header h2 {
    margin: 0 0 0.75rem;
}

.btn-add {
    background: #7a1fa2;
    color: #fff;
    border: 0;
    padding: 0.4rem 0.9rem;
    border-radius: 4px;
    cursor: pointer;
}

.list {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
}

.card {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}

.card-body {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.tag {
    background: #eee;
    padding: 0.1rem 0.5rem;
    border-radius: 10px;
    font-size: 0.75rem;
    color: #333;
}

.stars {
    color: #d4a900;
    font-size: 0.9rem;
}

.card-actions button {
    background: transparent;
    border: 1px solid #ccc;
    padding: 0.25rem 0.6rem;
    border-radius: 4px;
    margin-left: 0.35rem;
    cursor: pointer;
    font-size: 0.85rem;
}

.card-actions button.danger {
    color: #b00020;
    border-color: #b00020;
}

.form {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 1rem;
}

.field {
    display: flex;
    flex-direction: column;
    margin-bottom: 0.75rem;
    flex: 1;
}

.field label {
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.2rem;
}

.field input,
.field select {
    padding: 0.45rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-family: inherit;
    font-size: 0.9rem;
}

.row {
    display: flex;
    gap: 0.75rem;
}

.actions {
    display: flex;
    gap: 0.5rem;
}

.actions button {
    background: #1f1f1f;
    color: #fff;
    border: 0;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
}

.actions button.ghost {
    background: transparent;
    color: #333;
    border: 1px solid #ccc;
}

.msg.error {
    color: #b00020;
    font-size: 0.9rem;
}

.empty {
    color: #888;
    font-style: italic;
}
</style>