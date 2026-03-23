# check_env.py

import os
from dotenv import load_dotenv

# Optional: Load from specific path
load_dotenv(dotenv_path="D:/GTS/.env")

required_keys = [
    "DATABASE_URL",
    "JWT_SECRET_KEY",
    "OPENAI_API_KEY",
    "DATABASE_NAME",
    "DATABASE_USER",
    "DATABASE_PASSWORD",
    "DATABASE_HOST",
    "DATABASE_PORT",
]


def check_env_keys():
    print("Checking environment variables...\n")
    missing_keys = []

    for key in required_keys:
        value = os.getenv(key)
        if value:
            print(f"[OK] {key}: FOUND")
        else:
            print(f"[MISSING] {key}")
            missing_keys.append(key)

    if missing_keys:
        print("\nMissing keys in .env:")
        for key in missing_keys:
            print(f" - {key}")
    else:
        print("\nAll required keys are present.")


if __name__ == "__main__":
    check_env_keys()
