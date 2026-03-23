import os

# EN
PROJECT_DIR = "E:/GTS Logistics/backend"

# EN
old_import = "from backend.database.session import get_async_db"
new_import = "from backend.database.session import get_async_session"

# EN
for root, dirs, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if old_import in content:
                print(f"🛠️ Updating import in: {file_path}")
                updated_content = content.replace(old_import, new_import)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)

print("✅ All matching imports updated.")
