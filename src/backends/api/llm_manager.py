from pathlib import Path
from llama_cpp import Llama

_llm = None

def get_model_path() -> Path:
    base_dir = Path.home() / "AppData" / "Roaming" / "DarthApply" / "models"
    return base_dir / "gemma-2-9b-it-Q6_K.gguf"

def get_llm() -> Llama | None:
    global _llm
    if _llm is not None:
        return _llm

    model_path = get_model_path()
    if not model_path.exists():
        print(f"[LLM] Modelo não encontrado em: {model_path}")
        return None

    print(f"[LLM] Carregando modelo de: {model_path}")
    # AQUI está a correção: chat_format é definido na criação do modelo
    _llm = Llama(
        model_path=str(model_path), 
        n_ctx=4096, 
        n_gpu_layers=-1, 
        chat_format="gemma", 
        verbose=False
    )
    return _llm