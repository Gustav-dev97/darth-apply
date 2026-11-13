<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
    createEducation,
    deleteEducation,
    getProfile,
    updateEducation,
    type Education,
    type EducationInput,
} from "../services/api";

const items = ref<Education[]>([]);
const loading = ref(false);
const saving = ref(false);
const error = ref<string | null>(null);
const editingId = ref<number | null>(null);

const blank = (): EducationInput => ({
    institution: "",
    degree: "",
    field_of_study: "",
    start_date: "",
    end_date: "",
    is_current: false,
});

const form = ref<EducationInput>(blank());

async function load() {
    loading.value = true;
    error.value = null;
    try {
        const profile = await getProfile();
        items.value = profile?.educations ?? [];
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

function startEdit(edu: Education) {
    editingId.value = edu.id;
    form.value = {
        institution: edu.institution,
        degree: edu.degree,
        field_of_study: edu.field_of_study ?? "",
        start_date: edu.start_date,
        end_date: edu.end_date ?? "",
        is_current: edu.is_current,
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
        const payload: EducationInput = {
            institution: form.value.institution.trim(),
            degree: form.value.degree.trim(),
            field_of_study: form.value.field_of_study?.trim() || null,
            start_date: form.value.start_date,
            end_date: form.value.is_current ? null : form.value.end_date || null,
            is_current: form.value.is_current,
        };
        if (editingId.value && editingId.value > 0) {
            await updateEducation(editingId.value, payload);
        } else {
            await createEducation(payload);
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
    if (!confirm("Remover esta formação?")) return;
    try {
        await deleteEducation(id);
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
            <h2>Formação</h2>
            <button v-if="editingId === null" class="btn-add" @click="startAdd">
                + Adicionar
            </button>
        </div>

        <p v-if="loading">Carregando…</p>
        <p v-if="error" class="msg error">Erro: {{ error }}</p>

        <ul v-if="items.length && editingId === null" class="list">
            <li v-for="edu in items" :key="edu.id" class="card">
                <div class="card-body">
                    <strong>{{ edu.degree }} em {{ edu.field_of_study || "—" }}</strong>
                    <div class="sub">{{ edu.institution }}</div>
                    <div class="dates">
                        {{ edu.start_date }} →
                        {{ edu.is_current ? "Cursando" : edu.end_date || "?" }}
                    </div>
                </div>
                <div class="card-actions">
                    <button @click="startEdit(edu)">Editar</button>
                    <button class="danger" @click="remove(edu.id)">Excluir</button>
                </div>
            </li>
        </ul>
        <p v-if="!loading && !items.length && editingId === null" class="empty">
            Nenhuma formação cadastrada.
        </p>

        <form v-if="editingId !== null" class="form" @submit.prevent="save">
            <div class="row">
                <div class="field">
                    <label>Instituição *</label>
                    <input v-model="form.institution" required maxlength="200" />
                </div>
                <div class="field">
                    <label>Grau *</label>
                    <input v-model="form.degree" required maxlength="200" placeholder="Ex.: Bacharelado" />
                </div>
            </div>

            <div class="field">
                <label>Curso / Área</label>
                <input v-model="form.field_of_study" maxlength="200" />
            </div>

            <div class="row">
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
                Cursando atualmente
            </label>

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
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    gap: 1rem;
}

.card-body {
    flex: 1;
}

.sub {
    font-size: 0.9rem;
    color: #333;
    margin-top: 0.15rem;
}

.dates {
    font-size: 0.85rem;
    color: #555;
    margin-top: 0.15rem;
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

.field input {
    padding: 0.45rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-family: inherit;
    font-size: 0.9rem;
}

.field input:disabled {
    background: #f0f0f0;
    color: #888;
}

.row {
    display: flex;
    gap: 0.75rem;
}

.check {
    display: block;
    margin: 0.25rem 0 0.75rem;
    font-size: 0.9rem;
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