# ✅ fix_imports.py – Fix incorrect import paths and skip itself
import os

# Base directory
base_dir = "E:/GTS Logistics"
this_file = os.path.abspath(__file__)

# Old → New import fixes
fixes = {
    "from backend.database.connection import get_db_connection":
        "from backend.database.connection import get_db_connection",
    "from backend.database.connection import get_db":
        "from backend.database.connection import get_db",
    "from backend.database.connection import SessionLocal":
        "from backend.database.connection import SessionLocal",
}

# Traverse all .py files and apply fixes
for root, _, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            if os.path.abspath(file_path) == this_file:
                continue  # 🚫 Skip this script itself

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            updated = False
            for old, new in fixes.items():
                if old in content:
                    content = content.replace(old, new)
                    updated = True

            if updated:
                print(f"✅ Fixing: {file_path}")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

print("🎉 All import paths have been updated successfully.")
