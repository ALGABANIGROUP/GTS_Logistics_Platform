import os

def generate_structure(root_path, output_file="structure.txt"):
    with open(output_file, 'w', encoding='utf-8') as f:
        for dirpath, dirnames, filenames in os.walk(root_path):
            level = dirpath.replace(root_path, '').count(os.sep)
            indent = '│   ' * level
            f.write(f"{indent}├── {os.path.basename(dirpath)}/\n")
            sub_indent = '│   ' * (level + 1)
            for filename in filenames:
                f.write(f"{sub_indent}├── {filename}\n")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))  # auto-detect current dir
    generate_structure(project_root)
    print("✅ structure.txt has been created successfully.")
