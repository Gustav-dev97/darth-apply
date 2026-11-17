<div align="center">
  <h1>Darth Apply</h1>
  <p><em>Join the Dark Side of job hunting.</em></p>
  <p>An open-source, local-first job application agent.<br/>Because if recruitment is automated, so is the applicant.</p>
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
> **Status: active development.** Phases 0–2 are complete: the Tauri desktop shell, the Vue 3 frontend, the FastAPI sidecar, the local AI engine (Gemma 2 9B via `llama-cpp-python`), and the ATS-friendly resume generator (DOCX + PDF) are all operational. The Playwright automation layer will be added incrementally.

## Table of Contents

- [About](#about)
- [Stack](#stack)
- [Development](#development)
- [Release build](#release-build)
- [Project structure](#project-structure)
- [Roadmap](#roadmap)
- [Disclaimer](#disclaimer)
- [License](#license)
- [Credits](#credits)

## About

**Darth Apply** is a local-first desktop agent that helps candidates automate the tedious parts of job hunting: searching listings across multiple platforms (Gupy, Indeed, Catho, Sólides, LinkedIn), scoring compatibility with a profile, adapting resumes for each job's ATS, and pre-filling application forms — all from a single, private, open-source app that runs entirely on your machine.

The name is a joke: if recruiters automate candidate selection, candidates should be able to automate their side too. Fire with fire.

Core principles:

- **Local-first.** Your profile, resumes, application history and browser sessions never leave your machine. No central server.
- **No external AI APIs.** The LLM runs entirely on your machine. No quotas, no costs, no outages.
- **Fidelity to the candidate.** The AI reformulates what the user provided — it never invents experiences, companies, certifications or technologies.
- **Assisted, not reckless.** Submitting applications requires explicit user approval. No spamming.
- **AI is a tool, not an authority.** The user reviews everything the LLM generates before it is used.

## Stack

| Layer | Technology | Purpose |
|---|---|---|
| Desktop shell | **Tauri 2** | Native window, tray, autostart, installer |
| Frontend | **Vue 3 + TypeScript + Vite** | UI |
| Backend | **Python 3.13 + FastAPI** | Core logic, orchestration, document processing |
| AI (local) | **llama-cpp-python + Gemma 2 9B** | 100% offline LLM inference (GGUF, no API) |
| Database | **SQLite + SQLAlchemy** | Local persistence |
| Documents | **python-docx + LibreOffice headless** | ATS-friendly DOCX and PDF generation |
| PDF parsing | **PyMuPDF** | ATS verification of generated files |
| Automation | **Playwright** *(planned)* | Browser automation and form filling |

## Development

### Prerequisites

- Node.js 20+ and pnpm
- Rust (via rustup) with MSVC toolchain on Windows
- Python 3.13 (pinned via `.python-version`, handled by `uv`)
- `uv` for Python package management
- LibreOffice (optional, required only for PDF export)

### First-time setup

```bash
pnpm install-reqs
pnpm build:icons
uv venv
uv pip install .