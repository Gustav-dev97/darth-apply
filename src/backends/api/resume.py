"""
Resume generation endpoints.
"""

import json
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, selectinload

from db import UserProfile, get_db
from resume_engine import (
    build_resume,
    convert_docx_to_pdf,
    find_libreoffice,
    get_resumes_dir,
)
from resume_engine.ats_checker import check_resume_docx, check_resume_pdf
from resume_engine.models import list_models

from .schemas import EnhanceSummaryRequest, EnhanceDescriptionRequest
from .llm_manager import get_llm

router = APIRouter(prefix="/api/resume", tags=["resume"])

DOCX_MEDIA = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _require_profile(db: Session) -> UserProfile:
    profile = (
        db.query(UserProfile)
        .options(
            selectinload(UserProfile.experiences),
            selectinload(UserProfile.educations),
            selectinload(UserProfile.skills),
            selectinload(UserProfile.links),
            selectinload(UserProfile.projects),
            selectinload(UserProfile.courses),
        )
        .first()
    )
    if not profile:
        raise HTTPException(404, "Profile not created yet")
    return profile


def _clean_output(text: str) -> str:
    """Remove vícios de terceira pessoa e limpa formatação."""
    replacements = [
        (r"(?i)\bDemonstra interesse em\b", "Interesse em"),
        (r"(?i)\bDemonstra interesse por\b", "Interesse por"),
        (r"(?i)\bDemonstra conhecimento em\b", "Conhecimento em"),
        (r"(?i)\bDemonstra habilidade em\b", "Habilidade em"),
        (r"(?i)\bDemonstra facilidade em\b", "Facilidade em"),
        (r"(?i)\bPossui interesse em\b", "Interesse em"),
        (r"(?i)\bPossui conhecimento em\b", "Conhecimento em"),
        (r"(?i)\bPossui experiência em\b", "Experiência em"),
        (r"(?i)\bPossui habilidade em\b", "Habilidade em"),
        (r"(?i)\bApresenta interesse em\b", "Interesse em"),
        (r"(?i)\bApresenta conhecimento em\b", "Conhecimento em"),
        (r"(?i)\bTem interesse em\b", "Interesse em"),
        (r"(?i)\bTem conhecimento em\b", "Conhecimento em"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)

    text = re.sub(r"(?m)^•\s*$\n?", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\n+•", "\n•", text)

    return text.strip()


@router.post("/enhance-summary")
def enhance_summary(payload: EnhanceSummaryRequest):
    llm = get_llm()
    if llm is None:
        raise HTTPException(503, "Modelo de IA local não encontrado.")

    extraction_prompt = (
        "Você é uma máquina de extração de dados. Leia o texto do candidato e extraia as informações "
        "em um objeto JSON.\n"
        "NÃO adicione saudações, NÃO adicione explicações. Retorne APENAS o JSON bruto.\n\n"
        "Use exatamente estas chaves:\n"
        "- formacao_concluida: [cursos já finalizados]\n"
        "- formacao_em_andamento: [cursos ainda em curso]\n"
        "- experiencia: [estágios, empregos, vivência profissional]\n"
        "- conhecimentos: [tecnologias, ferramentas, habilidades técnicas]\n"
        "- perfil: [características comportamentais explícitas]\n"
        "- interesses: [desejos, áreas de interesse]\n"
        "- objetivo: [o que busca no momento]\n\n"
        "Se uma categoria não for mencionada, retorne uma lista vazia [].\n"
        "ATENÇÃO: Mantenha as siglas EXATAMENTE como estão no texto original.\n\n"
        f'Texto do Candidato:\n"{payload.raw_summary}"'
    )

    try:
        extract_output = llm.create_chat_completion(
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.0,
            max_tokens=500,
        )
        raw_json_text = extract_output["choices"][0]["message"]["content"].strip()

        match = re.search(r"\{.*\}", raw_json_text, re.DOTALL)
        if match:
            facts = json.loads(match.group(0))
        else:
            raise ValueError("Nenhum JSON encontrado na resposta da IA.")

    except Exception as e:
        print(f"[AVISO] Falha na extração JSON: {e}. Usando fallback.", flush=True)
        facts = {"raw_text": payload.raw_summary}

    generation_prompt = (
        "Você é um especialista em currículos ATS e otimização para a plataforma Gupy.\n"
        "Sua tarefa é escrever EXATAMENTE 4 bullets para o 'Resumo de Qualificações' usando as informações do JSON fornecido.\n\n"
        "REGRAS INVIOLÁVEIS:\n"
        "1. NÃO INVENTE. Use apenas o que está no JSON.\n"
        "2. TAMANHO E DENSIDADE (CRÍTICO): Você é naturalmente muito curto. VOCÊ DEVE EXPANDIR O TEXTO. "
        "Cada bullet DEVE conter OBRIGATORIAMENTE de 3 a 4 frases longas e detalhadas. NÃO resuma as informações. "
        "Explique o contexto de cada habilidade e como ela é aplicada.\n"
        "3. PORTUGUÊS FLUENTE: Evite jargões corporativos vazios. Use português natural.\n"
        "4. TOM IMPESSOAL: NUNCA use pronomes e NUNCA comece um bullet com verbos na 3ª pessoa. Use APENAS frases nominais: 'Profissional com...', 'Conhecimento em...', 'Interesse em...', 'Facilidade para...'.\n"
        "5. FORMAÇÃO: Use 'formacao_concluida' para 'Profissional com formação em [Curso]'. Use 'formacao_em_andamento' para 'Profissional em formação em [Curso]'. Combine ambas.\n"
        "6. PALAVRAS-CHAVE: Identifique a área de atuação do candidato e extraia os termos técnicos exatos.\n\n"
        "ESTRUTURA OBRIGATÓRIA DOS 4 BULLETS:\n"
        "• Bullet 1 (Formação e Experiência): Combine 'formacao_concluida', 'formacao_em_andamento' e 'experiencia'. Descreva a base acadêmica e a vivência prática.\n"
        "• Bullet 2 (Conhecimentos Técnicos): Use a lista 'conhecimentos'. Detalhe as ferramentas e tecnologias, explicando o domínio técnico.\n"
        "• Bullet 3 (Perfil Comportamental): Use a lista 'perfil'. Descreva como essas características auxiliam no ambiente de trabalho. Se a lista estiver vazia, escreva: 'Perfil voltado para o aprendizado contínuo e o desenvolvimento profissional.'\n"
        "• Bullet 4 (Objetivo e Interesses): Combine 'objetivo' e 'interesses'. Descreva a expectativa de carreira e o que busca na área.\n\n"
        "EXEMPLOS DE REFERÊNCIA (Observe o tamanho longo das frases):\n"
        "Exemplo 1 (TI):\n"
        "• Profissional com formação em ADS e em formação em Ciência da Computação, com vivência acadêmica adquirida por meio do desenvolvimento de projetos web e de back-end, aplicando conceitos teóricos em soluções práticas.\n"
        "• Conhecimento em Java, Python e JavaScript, com habilidade na construção de APIs REST e integração com bancos de dados relacionais, além de experiência no desenvolvimento de interfaces e sistemas completos.\n"
        "• Facilidade para atuar tanto no back-end quanto no front-end, características mencionadas entre suas habilidades profissionais, permitindo uma visão ampla do ciclo de desenvolvimento. Interesse em aprofundar conhecimentos em engenharia de software.\n"
        "• Interesse em obter uma oportunidade na área de tecnologia para aplicar conhecimentos práticos e ampliar a experiência profissional em desenvolvimento web, contribuindo com soluções eficientes.\n\n"
        "Exemplo 2 (Direito):\n"
        "• Profissional em formação em Direito, com vivência acadêmica adquirida por meio de atividades da faculdade envolvendo análise de processos, elaboração de documentos e pesquisas de legislação, desenvolvendo um olhar crítico sobre a área jurídica.\n"
        "• Conhecimento em leitura e escrita, com capacidade de organização que auxilia na execução de tarefas acadêmicas complexas, além de habilidade para interpretar textos legais e estruturar argumentos.\n"
        "• Facilidade para estudar casos jurídicos, características mencionadas entre suas habilidades profissionais, com foco na resolução de problemas e na busca por atualização constante. Interesse por atividades relacionadas à área trabalhista e civil.\n"
        "• Interesse em obter uma oportunidade para aplicar os conhecimentos adquiridos na prática, buscando ampliar a experiência profissional no campo do Direito e contribuir para a área.\n\n"
        f"JSON do Candidato:\n{json.dumps(facts, ensure_ascii=False, indent=2)}\n\n"
        "Agora, gere os 4 bullets seguindo o padrão longo dos exemplos:"
    )

    try:
        gen_output = llm.create_chat_completion(
            messages=[{"role": "user", "content": generation_prompt}],
            temperature=0.4,
            max_tokens=1000,
            repeat_penalty=1.1,
        )

        enhanced = gen_output["choices"][0]["message"]["content"].strip()
        enhanced = (
            enhanced.replace("<end_of_turn>", "")
            .replace("<start_of_turn>", "")
            .replace("```", "")
            .strip()
        )

        enhanced = _clean_output(enhanced)

        return {"enhanced_summary": enhanced}

    except Exception as e:
        raise HTTPException(500, detail=f"Erro na geração: {str(e)}")


@router.post("/enhance-description")
def enhance_description(payload: EnhanceDescriptionRequest):
    llm = get_llm()
    if llm is None:
        raise HTTPException(503, "Modelo de IA local não encontrado.")

    if payload.context_type == "experience":
        system_instructions = (
            "Você é um especialista em currículos ATS. Sua tarefa é transformar o texto informal do candidato "
            "em uma descrição profissional de experiência utilizando o método STAR (Situação, Tarefa, Ação, Resultado).\n"
            "REGRAS:\n"
            "1. NÃO INVENTE dados, empresas ou tecnologias. Se o usuário não deu métricas numéricas (ex: 'aumentei em 20%'), NÃO invente números. Foque no impacto qualitativo.\n"
            "2. Formate a saída como uma lista de 3 a 4 bullets (usando '•').\n"
            "3. Cada bullet deve cobrir uma parte do STAR: Contexto/Cargo, Responsabilidades, Ações práticas e Resultados.\n"
            "4. Use verbos de ação fortes no início de cada bullet (ex: 'Desenvolvi', 'Implementei', 'Otimizei').\n"
            "5. NUNCA use pronomes ('eu', 'ele'). Use linguagem impessoal ('Responsável por...', 'Desenvolvimento de...').\n\n"
            "EXEMPLO DE ENTRADA:\n"
            "Trabalhei como dev junior na empresa X. Eu fazia api em python e banco de dados. Ajudei a equipe a entregar o projeto mais rapido.\n\n"
            "EXEMPLO DE SAÍDA:\n"
            "• Atuação como Desenvolvedor Júnior na empresa X, integrando a equipe de desenvolvimento de software (Situação).\n"
            "• Responsável pela criação e manutenção de APIs utilizando Python e integração com bancos de dados relacionais (Tarefa).\n"
            "• Implementação de melhorias no código e otimização de processos, colaborando ativamente com a equipe para acelerar a entrega das demandas (Ação).\n"
            "• Contribuição para a conclusão eficiente do projeto, garantindo a qualidade técnica e a agilidade nas entregas da equipe (Resultado).\n\n"
        )
    elif payload.context_type == "course":
        system_instructions = (
            "Você é um especialista em currículos ATS. Sua tarefa é transformar o texto informal do candidato "
            "em uma descrição técnica e detalhada do conteúdo do curso.\n"
            "REGRAS:\n"
            "1. NÃO INVENTE. Use apenas o que foi fornecido.\n"
            "2. Formate a saída como uma lista de 2 a 3 bullets (usando '•').\n"
            "3. Extraia as palavras-chave mais importantes (ferramentas, metodologias, conceitos).\n"
            "4. Use linguagem impessoal (ex: 'Estudo de...', 'Desenvolvimento de...').\n\n"
            "EXEMPLO DE ENTRADA:\n"
            "Fiz um curso de python focado em dados, aprendi pandas e numpy e a fazer uns graficos.\n\n"
            "EXEMPLO DE SAÍDA:\n"
            "• Estudo aprofundado de Python voltado para a análise de dados.\n"
            "• Desenvolvimento de habilidades práticas com as bibliotecas Pandas e NumPy para manipulação e tratamento de dados.\n"
            "• Criação de visualizações gráficas para interpretação de métricas e resultados.\n\n"
        )
    else:
        system_instructions = (
            "Você é um especialista em currículos ATS. Sua tarefa é transformar o texto informal do candidato "
            "em uma descrição profissional e técnica de projeto.\n"
            "REGRAS:\n"
            "1. NÃO INVENTE. Use apenas o que foi fornecido.\n"
            "2. Formate a saída como uma lista de 3 a 4 bullets (usando '•').\n"
            "3. Estruture os bullets focando em: O problema/objetivo do projeto, as tecnologias utilizadas, as ações de desenvolvimento e o resultado final.\n"
            "4. Use linguagem impessoal (ex: 'Desenvolvimento de...', 'Implementação de...').\n\n"
            "EXEMPLO DE ENTRADA:\n"
            "Fiz um site de biblioteca com react e google books api. O usuario podia favoritar livros e ler online.\n\n"
            "EXEMPLO DE SAÍDA:\n"
            "• Desenvolvimento de uma aplicação web para gerenciamento de biblioteca virtual, com o objetivo de facilitar a busca e o acesso a livros (Objetivo).\n"
            "• Utilização das tecnologias React para o front-end e integração com a Google Books API para a obtenção de dados dos livros (Tecnologias).\n"
            "• Implementação de funcionalidades como sistema de favoritos e leitura online, garantindo uma experiência de usuário fluida e intuitiva (Ações).\n"
            "• Entrega de uma plataforma funcional que permite aos usuários organizar suas leituras e acessar conteúdos de forma prática (Resultado).\n\n"
        )

    title_context = (
        f" (Cargo/Projeto/Curso: {payload.context_title})"
        if payload.context_title
        else ""
    )

    prompt = (
        f"{system_instructions}"
        f"Agora, melhore a seguinte descrição{title_context}:\n"
        f'Texto original: "{payload.raw_text}"'
    )

    try:
        gen_output = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600,
            repeat_penalty=1.1,
        )

        enhanced = gen_output["choices"][0]["message"]["content"].strip()
        enhanced = (
            enhanced.replace("<end_of_turn>", "")
            .replace("<start_of_turn>", "")
            .replace("```", "")
            .strip()
        )

        labels_pattern = r"\s*\((?:Situação|Tarefa|Ação|Ações|Resultado|Objetivo|Tecnologias|Situation|Task|Action|Result|Technologies)\)\.?"
        enhanced = re.sub(labels_pattern, ".", enhanced, flags=re.IGNORECASE)

        enhanced = re.sub(r"([^\n])\s*•\s*", r"\1\n• ", enhanced)

        enhanced = re.sub(r"[ \t]+\n", "\n", enhanced)
        enhanced = re.sub(r"\.{2,}", ".", enhanced)
        enhanced = re.sub(r"\n{3,}", "\n\n", enhanced).strip()

        return {"enhanced_text": enhanced}

    except Exception as e:
        raise HTTPException(500, detail=f"Erro na geração: {str(e)}")


@router.get("/templates")
def get_templates():
    return list_models()


@router.post("/generate")
def generate_resume(model_id: str = "classico", db: Session = Depends(get_db)):
    profile = _require_profile(db)
    resumes_dir = get_resumes_dir()

    # 1. Gera o DOCX
    docx_path = resumes_dir / f"curriculo-{model_id}.docx"
    doc = build_resume(profile, model_id=model_id)
    doc.save(str(docx_path))

    # 2. Converte o MESMO DOCX para PDF (garante visual idêntico)
    pdf_path = convert_docx_to_pdf(docx_path, resumes_dir)

    # 3. ATS checks
    docx_ats = check_resume_docx(docx_path, profile)
    pdf_ats = check_resume_pdf(pdf_path, profile) if pdf_path else None

    return {
        "model_id": model_id,
        "docx_path": str(docx_path),
        "pdf_path": str(pdf_path) if pdf_path else None,
        "libreoffice_available": find_libreoffice() is not None,
        "docx_ats": docx_ats,
        "pdf_ats": pdf_ats,
    }


@router.get("/download/{model_id}/{fmt}")
def download_resume(model_id: str, fmt: str):
    if fmt not in ("docx", "pdf"):
        raise HTTPException(400, "format must be 'docx' or 'pdf'")

    path = get_resumes_dir() / f"curriculo-{model_id}.{fmt}"
    if not path.exists():
        raise HTTPException(404, "Resume has not been generated yet")

    media = DOCX_MEDIA if fmt == "docx" else "application/pdf"
    return FileResponse(path, filename=f"curriculo-{model_id}.{fmt}", media_type=media)