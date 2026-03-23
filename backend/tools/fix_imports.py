# backend/tools/fix_imports.py
import os
import re
from pathlib import Path

def fix_python_files():
    """Fix Python import statements across project files"""
    backend_path = Path(__file__).parent.parent
    fixed_files = []

    # Target files that might need fixing
    target_files = [
        backend_path / "main.py",
        backend_path / "core" / "config.py",
        backend_path / "routes" / "finance_routes.py",
        backend_path / "routes" / "documents_routes.py",
        backend_path / "routes" / "finance_reports.py",
        backend_path / "routes" / "finance_ai_routes.py",
    ]

    for file_path in target_files:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Perform import corrections
                old_content = content

                # Replace backend.database → database
                content = re.sub(r'from backend\.database\.', 'from database.', content)
                content = re.sub(r'import backend\.database\.', 'import database.', content)

                # Replace backend.core → core
                content = re.sub(r'from backend\.core\.', 'from core.', content)
                content = re.sub(r'import backend\.core\.', 'import core.', content)

                # Replace backend.routes → routes
                content = re.sub(r'from backend\.routes\.', 'from routes.', content)
                content = re.sub(r'import backend\.routes\.', 'import routes.', content)

                if content != old_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_files.append(str(file_path))
                    print(f"✅ Fixed: {file_path.name}")

            except Exception as e:
                print(f"❌ Failed to fix {file_path}: {e}")

    return fixed_files


def create_init_files():
    """Create missing __init__.py files to ensure package imports"""
    backend_path = Path(__file__).parent.parent
    init_files = [
        backend_path / "__init__.py",
        backend_path / "database" / "__init__.py",
        backend_path / "core" / "__init__.py",
        backend_path / "routes" / "__init__.py",
        backend_path / "tools" / "__init__.py",
    ]

    created_files = []
    for init_file in init_files:
        if not init_file.exists():
            init_file.write_text('')
            created_files.append(str(init_file))
            print(f"✅ Created: {init_file}")

    return created_files


def main():
    print("🔧 Starting system import repair...")

    created = create_init_files()
    fixed = fix_python_files()

    print(f"\n📊 Results:")
    print(f"   📁 {len(created)} __init__.py file(s) created")
    print(f"   🔧 {len(fixed)} Python file(s) fixed")

    if created or fixed:
        print("\n🎉 Repair completed successfully! Try running the system again.")
    else:
        print("\n✅ No repairs needed — system imports are already correct.")


if __name__ == "__main__":
    main()
