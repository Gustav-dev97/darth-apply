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
> **Status: early development.** Phase 0 (bootstrap) is complete: the Tauri desktop shell, the Vue 3 frontend and the FastAPI sidecar are operational in development mode. Features will be added incrementally.

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
- **Open source.** Code is auditable. You can see exactly what the app does.
- **Assisted, not reckless.** Submitting applications requires explicit user approval. No spamming.
- **AI is a tool, not an authority.** The user reviews everything the LLM generates before it is used.

## Stack

| Layer | Technology | Purpose |
|---|---|---|
| Desktop shell | **Tauri 2** | Native window, tray, autostart, installer |
| Frontend | **Vue 3 + TypeScript + Vite** | UI |
| Backend | **Python 3.13 + FastAPI** | Core logic, orchestration, document processing |
| Automation | **Playwright** *(planned)* | Browser automation and form filling |
| Database | **SQLite + SQLAlchemy** *(planned)* | Local persistence |
| AI | **Ollama** *(planned, optional)* | Local LLM inference |

## Development

### Prerequisites

- Node.js 20+ and pnpm
- Rust (via rustup) with MSVC toolchain on Windows
- Python 3.13 (pinned via `.python-version`, handled by `uv`)
- `uv` for Python package management

### First-time setup

```bash
pnpm install-reqs
pnpm build:icons