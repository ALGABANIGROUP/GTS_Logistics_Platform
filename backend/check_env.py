import os
from pathlib import Path

def load_env():
    try:
        from dotenv import load_dotenv, find_dotenv
    except Exception:
        return

    project_root = Path(__file__).resolve().parents[1]
    root_env = project_root / ".env"
    backend_env = Path(__file__).resolve().parent / ".env"

    # 1) load project .env if exists
    if root_env.exists():
        load_dotenv(dotenv_path=root_env, override=False)

    # 2) then override with backend/.env if exists
    if backend_env.exists():
        load_dotenv(dotenv_path=backend_env, override=True)

if __name__ == "__main__":
    load_env()
    print("DATABASE_URL =", os.getenv("DATABASE_URL"))
    print("ASYNC_DATABASE_URL =", os.getenv("ASYNC_DATABASE_URL"))
# ensure .env is loaded whenever backend is imported
load_env()