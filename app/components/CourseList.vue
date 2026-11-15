<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
    createCourse,
    deleteCourse,
    getProfile,
    enhanceDescription,
    type Course,
    type CourseInput,
} from "../services/api";

const items = ref<Course[]>([]);
const loading = ref(false);
const saving = ref(false);
const enhancing = ref(false);
const error = ref<string | null>(null);
const showForm = ref(false);

const blank = (): CourseInput => ({
    name: "",
    institution: "",
    completion_date: "",
    description: "",
});

const form = ref<CourseInput>(blank());

async function load() {
    loading.value = true;
    error.value = null;
    try {
        const profile = await getProfile();
        items.value = profile?.courses ?? [];
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

async function improveDescription() {
    if (!form.value.description?.trim()) return;
    enhancing.value = true;
    error.value = null;
    try {
        // Usa enhanceDescription com context_type "course"
        form.value.description = await enhanceDescription(
            form.value.description,
            "course",
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
        const payload: CourseInput = {
            name: form.value.name.trim(),
            institution: form.value.institution?.trim() || null,
            completion_date: form.value.completion_date || null,
            description: form.value.description?.trim() || null,
        };
        await createCourse(payload);
        showForm.value = false;
        await load();
    } catch (e: any) {
        error.value = e?.message ?? String(e);
    } finally {
        saving.value = false;
    }
}

async function remove(id: number) {
    if (!confirm("Remover este curso?")) return;
    try {
        await deleteCourse(id);
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
            <h2>Cursos Complementares</h2>
            <button v-if="!showForm" class="btn-add" @click="startAdd">+ Adicionar</button>
        </div>

        <p v-if="loading">Carregando…</p>
        <p v-if="error" class="msg error">Erro: {{ error }}</p>

        <ul v-if="items.length && !showForm" class="list">
            <li v-for="c in items" :key="c.id" class="card">
                <div class="card-body">
                    <strong>{{ c.name }}</strong>
                    <span v-if="c.institution"> | {{ c.institution }}</span>
                    <div class="dates" v-if="c.completion_date">Concluído em: {{ c.completion_date }}</div>
                    <p v-if="c.description" class="desc">
                        ✔ Descrição salva para filtragem de vagas (não visível no currículo).
                    </p>
                </div>
                <div class="card-actions">
                    <button class="danger" @click="remove(c.id)">Excluir</button>
                </div>
            </li>
        </ul>
        <p v-if="!loading && !items.length && !showForm" class="empty">Nenhum curso cadastrado.</p>

        <form v-if="showForm" class="form" @submit.prevent="save">
            <div class="field">
                <label>Nome do Curso *</label>
                <input v-model="form.name" required maxlength="200" placeholder="Ex: Formação em Data Science" />
            </div>

            <div class="row">
                <div class="field">
                    <label>Instituição</label>
                    <input v-model="form.institution" maxlength="200" placeholder="Ex: Alura, Coursera, UNOPAR" />
                </div>
                <div class="field">
                    <label>Data de Conclusão</label>
                    <input v-model="form.completion_date" type="date" />
                </div>
            </div>

            <div class="field">
                <div class="label-row">
                    <label>Descrição (usada pela IA, não vai pro DOCX)</label>
                    <button type="button" class="btn-ai" @click="improveDescription" :disabled="enhancing">
                        {{ enhancing ? "Gerando..." : "✨ Melhorar com IA" }}
                    </button>
                </div>
                <textarea v-model="form.description" rows="4"
                    placeholder="O que você aprendeu? A IA extrai as palavras-chave para o Job Matching."></textarea>
                <small class="hint">
                    Esta descrição é armazenada no banco para o futuro Job Matching (filtragem de
                    vagas). Ela <strong>não aparece</strong> no currículo gerado — apenas o nome do
                    curso, instituição e data.
                </small>
            </div>

            <div class="actions">
                <button type="submit" :disabled="saving">
                    {{ saving ? "Salvando…" : "Salvar" }}
                </button>
                <button type="button" class="ghost" @click="showForm = false">Cancelar</button>
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

.dates {
    font-size: 0.85rem;
    color: #555;
    margin: 0.15rem 0;
}

.desc {
    font-size: 0.85rem;
    color: #1b7a2e;
    margin: 0.4rem 0 0;
    font-style: italic;
}

.card-actions button {
    background: transparent;
    border: 1px solid #ccc;
    padding: 0.25rem 0.6rem;
    border-radius: 4px;
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
.field textarea {
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
    margin-top: 1rem;
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

.hint {
    font-size: 0.75rem;
    color: #666;
    margin-top: 0.3rem;
    line-height: 1.3;
}

/* Botão de IA */
.label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
}

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

.btn-ai:hover:not(:disabled) {
    transform: scale(1.05);
}

.btn-ai:disabled {
    opacity: 0.6;
    cursor: wait;
}
</style>