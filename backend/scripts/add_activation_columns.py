import os
from sqlalchemy import create_engine, text, inspect

def ensure_columns():
    # Read DATABASE_URL from environment (fallback for local use)
    db_url = os.getenv("DATABASE_URL", "postgresql://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions?sslmode=require")

    if not db_url:
        raise SystemExit("DATABASE_URL env var is required.")

    # Create engine and inspector
    engine = create_engine(db_url)
    insp = inspect(engine)

    # Ensure required columns exist
    with engine.begin() as conn:
        cols = {col["name"] for col in insp.get_columns("users")}

        # Add activation_token if missing
        if "activation_token" not in cols:
            conn.execute(text('ALTER TABLE users ADD COLUMN activation_token VARCHAR(255)'))
            print("[schema] added activation_token to users")
        else:
            print("[schema] activation_token already exists")

        # Add activation_expires_at if missing
        if "activation_expires_at" not in cols:
            conn.execute(text('ALTER TABLE users ADD COLUMN activation_expires_at TIMESTAMP WITH TIME ZONE'))
            print("[schema] added activation_expires_at to users")
        else:
            print("[schema] activation_expires_at already exists")

if __name__ == "__main__":
    ensure_columns()
