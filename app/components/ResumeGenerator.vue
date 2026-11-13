<script setup lang="ts">
import { ref } from "vue";
import {
    generateResume,
    resumeDownloadUrl,
    type ResumeGenerateResult,
} from "../services/api";

const generating = ref(false);
const error = ref<string | null>(null);
const result = ref<ResumeGenerateResult | null>(null);

async function generate() {
    generating.value = true;
    error.value = null;
    try {
        result.value = await generateResume();
    } catch (e: any) {
        error.value = e?.message ?? String(e);
    } finally {
        generating.value = false;
    }
}

function download(fmt: "docx" | "pdf") {
    window.open(resumeDownloadUrl(fmt), "_blank");
}
</script>

<template>
    <div class="resume-gen">
        <h2>Gerar Currículo</h2>
        <p class="hint">
            O currículo é montado a partir dos dados do perfil. Ele é gerado em uma
            coluna, sem imagens, sem tabelas e com bullets em texto puro — formato
            compatível com a maioria dos parsers ATS.
        </p>

        <button class="btn-generate" :disabled="generating" @click="generate">
            {{ generating ? "Gerando…" : "Gerar Currículo" }}
        </button>

        <p v-if="error" class="msg error">Erro: {{ error }}</p>

        <div v-if="result" class="result">
            <h3>Arquivos gerados</h3>

            <div class="file-card">
                <div>
                    <strong>DOCX</strong>
                    <div class="path">{{ result.docx_path }}</div>
                </div>
                <button @click="download('docx')">Baixar</button>
            </div>

            <div v-if="result.pdf_path" class="file-card">
                <div>
                    <strong>PDF</strong>
                    <div class="path">{{ result.pdf_path }}</div>
                </div>
                <button @click="download('pdf')">Baixar</button>
            </div>

            <div v-else class="warn">
                PDF não gerado. Instale o LibreOffice para habilitar a conversão:
                <code>winget install --id TheDocumentFoundation.LibreOffice</code>
            </div>

            <h3>Verificação ATS</h3>

            <div class="ats-block">
                <h4>
                    DOCX
                    <span :class="['badge', result.docx_ats.passed ? 'ok' : 'fail']">
                        {{ result.docx_ats.passed ? "Aprovado" : "Reprovado" }}
                    </span>
                </h4>
                <ul>
                    <li v-for="c in result.docx_ats.checks" :key="c.name" :class="c.passed ? 'ok' : 'fail'">
                        {{ c.passed ? "✓" : "✗" }} {{ c.name }}
                        <span v-if="c.detail" class="detail">({{ c.detail }})</span>
                    </li>
                </ul>
            </div>

            <div v-if="result.pdf_ats" class="ats-block">
                <h4>
                    PDF
                    <span :class="['badge', result.pdf_ats.passed ? 'ok' : 'fail']">
                        {{ result.pdf_ats.passed ? "Aprovado" : "Reprovado" }}
                    </span>
                </h4>
                <ul>
                    <li v-for="c in result.pdf_ats.checks" :key="c.name" :class="c.passed ? 'ok' : 'fail'">
                        {{ c.passed ? "✓" : "✗" }} {{ c.name }}
                        <span v-if="c.detail" class="detail">({{ c.detail }})</span>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>

<style scoped>
.resume-gen {
    max-width: 720px;
}

.hint {
    color: #555;
    font-size: 0.9rem;
}

.btn-generate {
    background: #7a1fa2;
    color: #fff;
    border: 0;
    padding: 0.6rem 1.2rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    margin: 0.5rem 0 1rem;
}

.btn-generate:hover:not(:disabled) {
    background: #5f1780;
}

.btn-generate:disabled {
    opacity: 0.6;
    cursor: wait;
}

.result h3 {
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    font-size: 1rem;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 0.25rem;
}

.file-card {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}

.file-card button {
    background: #1f1f1f;
    color: #fff;
    border: 0;
    padding: 0.4rem 0.9rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    white-space: nowrap;
}

.path {
    font-family: ui-monospace, Consolas, monospace;
    font-size: 0.8rem;
    color: #555;
    word-break: break-all;
    margin-top: 0.15rem;
}

.warn {
    background: #fff7e6;
    border: 1px solid #f0c674;
    border-radius: 6px;
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.warn code {
    background: #f3f3f3;
    padding: 0.1rem 0.3rem;
    border-radius: 3px;
    font-size: 0.85em;
}

.ats-block {
    margin-bottom: 1rem;
}

.ats-block h4 {
    margin: 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.badge {
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    border-radius: 10px;
    font-weight: 600;
}

.badge.ok {
    background: #e0f5e5;
    color: #1b7a2e;
}

.badge.fail {
    background: #fde2e2;
    color: #b00020;
}

.ats-block ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.ats-block li {
    font-size: 0.9rem;
    padding: 0.15rem 0;
}

.ats-block li.ok {
    color: #1b7a2e;
}

.ats-block li.fail {
    color: #b00020;
}

.detail {
    color: #666;
    font-size: 0.85em;
}

.msg.error {
    color: #b00020;
    font-size: 0.9rem;
}
</style>