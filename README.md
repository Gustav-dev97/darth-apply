<div align="center">
  <h1>Darth Apply</h1>
  <p><em>Junte-se ao Lado Sombrio da busca por emprego.</em></p>
  <p>Um agente de candidaturas a vagas de código aberto e com prioridade local.<br/>Porque, se o recrutamento é automatizado, o candidato também pode automatizar.</p>
</div>

<div align="center">

![Python](https://img.shields.io/badge/-Python-000?&logo=Python)
![TypeScript](https://img.shields.io/badge/-TypeScript-000?&logo=TypeScript)
![Rust](https://img.shields.io/badge/-Rust-000?&logo=Rust)
![FastAPI](https://img.shields.io/badge/-FastAPI-000?&logo=fastapi)
![Vue.js](https://img.shields.io/badge/-Vue.js-000?&logo=vuedotjs)
![Vite](https://img.shields.io/badge/-Vite-000?&logo=vite&logoColor=purple)
![Tauri](https://img.shields.io/badge/-Tauri-000?&logo=Tauri)
![SQLite](https://img.shields.io/badge/-SQLite-000?&logo=sqlite)

</div>

> [!WARNING]
> **Status: em desenvolvimento ativo.** As fases 0–3 estão concluídas. A estrutura desktop do Tauri, o frontend em Vue 3, o backend em FastAPI, o mecanismo de IA local (Gemma 2 9B via `llama-cpp-python`) e o gerador de currículos compatíveis com ATS (DOCX + PDF) estão totalmente operacionais. Os próximos marcos são o instalador personalizado e a camada de automação com Playwright.

## Índice

- [Sobre](#sobre)
- [Tecnologias](#tecnologias)
- [Desenvolvimento](#desenvolvimento)
- [Executando o aplicativo (Desenvolvimento)](#executando-o-aplicativo-desenvolvimento)
- [Modelo de IA Local](#modelo-de-ia-local)
- [Compilação da Versão de Lançamento](#compilacao-da-versao-de-lancamento)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Roteiro](#roteiro)
- [Aviso Legal](#aviso-legal)
- [Licença](#licenca)
- [Créditos](#creditos)

## Sobre

**Darth Apply** é um agente desktop com prioridade local que ajuda candidatos a automatizar as partes tediosas da busca por emprego: pesquisar vagas em várias plataformas (Gupy, Indeed, Catho, Sólides, LinkedIn), avaliar a compatibilidade com um perfil, adaptar currículos para o ATS de cada vaga e preencher previamente formulários de candidatura — tudo em um único aplicativo privado e de código aberto que é executado inteiramente na sua máquina.

O nome é uma brincadeira: se os recrutadores automatizam a seleção de candidatos, os candidatos também devem poder automatizar o próprio lado. Combater fogo com fogo.

Princípios fundamentais:

- **Prioridade local.** Seu perfil, currículos, histórico de candidaturas e sessões do navegador nunca saem da sua máquina. Nenhum servidor central.
- **Sem APIs externas de IA.** O LLM é executado inteiramente na sua máquina. Sem limites de uso, custos ou indisponibilidade de serviços.
- **Fidelidade ao candidato.** A IA reformula o conteúdo fornecido pelo usuário — nunca inventa experiências, empresas, certificações ou tecnologias.
- **Assistido, não imprudente.** O envio de candidaturas exige aprovação explícita do usuário. Sem envio indiscriminado de candidaturas.
- **A IA é uma ferramenta, não uma autoridade.** O usuário revisa tudo o que o LLM gera antes de utilizar o conteúdo.

## Tecnologias

| Camada | Tecnologia | Finalidade |
|---|---|---|
| Estrutura desktop | **Tauri 2** | Janela nativa, bandeja do sistema, inicialização automática e instalador |
| Frontend | **Vue 3 + TypeScript + Vite** | Interface do usuário |
| Backend | **Python 3.13 + FastAPI** | Lógica principal, orquestração e processamento de documentos |
| IA (local) | **llama-cpp-python + Gemma 2 9B** | Inferência de LLM 100% offline (GGUF, sem API) |
| Banco de dados | **SQLite + SQLAlchemy** | Persistência local |
| Documentos | **python-docx + LibreOffice headless** | Geração de DOCX e PDF compatíveis com ATS |
| Análise de PDF | **PyMuPDF** | Verificação ATS dos arquivos gerados |
| Automação | **Playwright** *(planejado)* | Automação do navegador e preenchimento de formulários |

## Desenvolvimento

### Pré-requisitos

- **Node.js 20+** e **pnpm**
- **Rust** (via rustup) com a toolchain MSVC no Windows
- **Python 3.13** (fixado via `.python-version`, gerenciado pelo `uv`)
- **`uv`** para gerenciamento de pacotes Python
- **LibreOffice** (opcional, mas necessário para exportação em PDF)

### Configuração inicial

Execute os seguintes comandos na raiz do projeto:

```bash
# 1. Instalar as dependências do Node e Python
pnpm install-reqs

# 2. Gerar os ícones do aplicativo (apenas uma vez)
pnpm build:icons

# 3. Criar o ambiente virtual do Python
uv venv
uv pip install .
```

## Executando o aplicativo (Desenvolvimento)

O Darth Apply utiliza um **único comando unificado** para iniciar toda a estrutura (backend + frontend + janela Tauri) com suporte completo a atualização automática durante o desenvolvimento.

```bash
pnpm dev
```

O que esse comando faz internamente:

Inicia o backend FastAPI em `http://127.0.0.1:8008` usando nodemon. Isso significa que qualquer alteração em um arquivo `.py` dentro de `src/backends` reiniciará automaticamente o backend.

Inicia o servidor de desenvolvimento Vite em `http://localhost:3000` com Hot Module Replacement (HMR). Qualquer alteração em um arquivo `.vue` ou `.ts` atualiza a interface instantaneamente, sem uma recarga completa.

Aguarda até que ambas as portas estejam disponíveis e, em seguida, abre a janela desktop do Tauri.

> [!TIP]
> Você não precisa mais abrir dois terminais. Basta executar `pnpm dev` e começar a programar. Se precisar interromper tudo, pressione Ctrl+C uma vez.

## Modelo de IA Local

O mecanismo de IA local requer um arquivo de modelo GGUF. Como o modelo possui aproximadamente 7 GB, ele não é armazenado no repositório (o GitHub limita arquivos a 100 MB).

Durante o desenvolvimento, você deve baixá-lo manualmente:

Baixe o Gemma 2 9B (Q6_K) no Hugging Face: bartowski/gemma-2-9b-it-GGUF

Coloque o arquivo `.gguf` no diretório de dados do aplicativo:

```text
%APPDATA%\DarthApply\models\gemma-2-9b-it-Q6_K.gguf
```

Na versão de lançamento, o modelo será incluído diretamente no instalador (veja abaixo), portanto os usuários finais não precisarão baixar nada.

## Compilação da Versão de Lançamento

O Darth Apply utiliza um instalador personalizado do Inno Setup 6 em vez do empacotador NSIS padrão do Tauri. O motivo é técnico: o instalador NSIS do Tauri possui um limite de 2 GB por arquivo, o que não comporta o modelo de IA local de aproximadamente 7 GB. O Inno Setup 6 oferece suporte a instaladores de tamanho arbitrário por meio de saída em múltiplos volumes.

Fluxo de lançamento:

```bash
# 1. Compilar o aplicativo Tauri sem gerar o instalador
pnpm tauri build --no-bundle

# 2. Copiar a saída da compilação + o modelo .gguf para uma pasta de build
# 3. Compilar o script do Inno Setup (.iss) para gerar o instalador final
```

O instalador final será dividido em arquivos de múltiplos volumes (DarthApply-Setup.exe + DarthApply-Setup-1.bin, etc.), distribuídos em conjunto. O instalador inclui tanto o aplicativo quanto o modelo de IA, o que significa zero downloads durante a execução e nenhuma dependência de CDN.

## Estrutura do Projeto

```text
darth-apply/
├── app/                          # Frontend Vue 3
│   ├── components/
│   │   ├── ProfileForm.vue
│   │   ├── ExperienceList.vue
│   │   ├── EducationList.vue
│   │   ├── CourseList.vue
│   │   ├── ProjectList.vue
│   │   ├── SkillList.vue
│   │   ├── LinkList.vue
│   │   ├── ResumeGenerator.vue
│   │   └── ProfileView.vue
│   └── services/api.ts
│
├── src-tauri/                    # Camada Rust / Tauri
│   ├── src/main.rs
│   └── tauri.conf.json
│
├── src/backends/                 # Backend Python
│   ├── main.py                   # FastAPI + Uvicorn
│   ├── api/
│   │   ├── profile.py            # CRUD do perfil
│   │   ├── resume.py             # IA + geração de currículos
│   │   ├── schemas.py            # Schemas Pydantic
│   │   └── llm_manager.py        # Carregador do modelo GGUF
│   ├── db/                       # Modelos e sessão SQLAlchemy
│   └── resume_engine/
│       ├── builder.py            # Gerador DOCX
│       ├── pdf_exporter.py       # DOCX → PDF via LibreOffice
│       └── ats_checker.py        # Verificação ATS
│
└── package.json
```

## Roteiro

| Fase | Escopo | Status |
|---|---|---|
| 0 | Configuração inicial (Tauri + Vue + FastAPI, Python 3.13, sidecar em modo de desenvolvimento) | ✅ Concluído |
| 1 | SQLite + CRUD do perfil + primeiras telas | ✅ Concluído |
| 2 | Importação de currículos, análise e exportação de DOCX/PDF compatíveis com ATS | ✅ Concluído |
| 3 | Mecanismo de IA local (Gemma 2) para reformulação de resumo, experiência, projetos e cursos | ✅ Concluído |
| 4 | Instalador Inno Setup com modelo de IA incluído | 🚧 Próximo |
| 5 | Título profissional gerado por IA | 🚧 Próximo |
| 6 | Descoberta de vagas + mecanismo de correspondência | ⏳ Planejado |
| 7 | Adaptador Gupy (pesquisa + fluxo de candidatura) | ⏳ Planejado |
| 8 | Adaptadores Indeed, Catho, Sólides | ⏳ Planejado |
| 9 | Adaptador LinkedIn + direcionamento para candidaturas externas | ⏳ Planejado |
| 10 | Integração Playwright + fluxo de aprovação | ⏳ Planejado |

## Aviso Legal

O Darth Apply utiliza inteligência artificial para auxiliar na elaboração e personalização de currículos. O conteúdo gerado pode conter imprecisões, omissões ou interpretações inadequadas. O usuário é o único responsável por revisar, validar e aprovar todas as informações antes de utilizá-las ou enviá-las a qualquer empregador ou plataforma. O projeto é fornecido "como está", sem qualquer tipo de garantia.

O Darth Apply não contorna CAPTCHAs, mecanismos anti-bot ou limites de requisições das plataformas. Quando uma plataforma exige interação humana (autenticação de dois fatores, desafios de segurança ou confirmação final), o agente devolve o controle ao usuário.

## Licença

O Darth Apply possui licenciamento duplo:

- Novo código desenvolvido para o Darth Apply: **MIT** — consulte [`LICENSE`](./LICENSE).
- Código herdado do template `vue-tauri-fastapi-sidecar`: **Apache 2.0** — consulte [`LICENSE-APACHE`](./LICENSE-APACHE).

Essa divisão respeita o licenciamento Apache 2.0 do template original, mantendo o código próprio do Darth Apply sob a licença MIT, mais permissiva.

## Créditos

O Darth Apply foi desenvolvido com base no vue-tauri-fastapi-sidecar de @AlanSynn (Apache 2.0), que, por sua vez, foi fortemente inspirado no dieharders/example-tauri-v2-python-server-sidecar. Agradecimentos a ambos por disponibilizarem seu trabalho.