import os
import signal
import sys
import asyncio
import threading
from contextlib import asynccontextmanager
from typing import TypedDict
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from inference import infer_text_api

# Database layer
from db.paths import get_db_path
from db.session import Base, engine
from db import models  # noqa: F401 — registers UserProfile on Base.metadata

# API routers
from api import profile_router, resume_router

PORT_API = 8008

server_instance = None  # Global reference to the Uvicorn server instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[sidecar] Database: {get_db_path()}", flush=True)
    Base.metadata.create_all(bind=engine)
    print("[sidecar] Database ready.", flush=True)
    try:
        yield
    except (KeyboardInterrupt, asyncio.CancelledError):
        # Ocorre quando o Uvicorn --reload detecta uma alteração e reinicia
        # o processo, ou quando o usuário envia Ctrl+C. Não é um erro.
        print("[sidecar] Shutting down gracefully...", flush=True)


app = FastAPI(
    title="API server",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS settings
origins = [
    "*",  # to whitelist any url, REMOVE THIS FOR PRODUCTION!!!
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(profile_router)
app.include_router(resume_router)


@app.get("/v1/connect")
def connect_to_api_server():
    print("[server] Connecting to server...", flush=True)
    host = f"http://localhost:{PORT_API}"
    return {
        "message": f"Connected to api server on port {PORT_API}. Refer to '{host}/docs' for api docs.",
        "data": {
            "port": PORT_API,
            "pid": os.getpid(),
            "host": host,
        },
    }


@app.get("/v1/db-status")
def db_status():
    from sqlalchemy import inspect

    inspector = inspect(engine)
    return {
        "db_path": str(get_db_path()),
        "tables": inspector.get_table_names(),
    }


class T_Query(TypedDict):
    prompt: str


@app.post("/v1/completions")
def llm_completion(payload: T_Query = Body(...)):
    return infer_text_api.completions(payload)


def kill_process():
    os.kill(os.getpid(), signal.SIGINT)


def start_api_server(**kwargs):
    global server_instance
    port = kwargs.get("port", PORT_API)
    try:
        if server_instance is None:
            print("[sidecar] Starting API server...", flush=True)
            config = Config(app, host="127.0.0.1", port=port, log_level="info")
            server_instance = Server(config)
            asyncio.run(server_instance.serve())
        else:
            print(
                "[sidecar] Failed to start new server. Server instance already running.",
                flush=True,
            )
    except Exception as e:
        print(f"[sidecar] Error, failed to start API server {e}", flush=True)


def stdin_loop():
    print("[sidecar] Waiting for commands...", flush=True)
    while True:
        user_input = sys.stdin.readline().strip()
        match user_input:
            case "sidecar shutdown":
                print("[sidecar] Received 'sidecar shutdown' command.", flush=True)
                kill_process()
            case _:
                print(
                    f"[sidecar] Invalid command [{user_input}]. Try again.", flush=True
                )


def start_input_thread():
    try:
        input_thread = threading.Thread(target=stdin_loop)
        input_thread.daemon = True
        input_thread.start()
    except:
        print("[sidecar] Failed to start input handler.", flush=True)


if __name__ == "__main__":
    start_input_thread()
    start_api_server()