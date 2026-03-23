import os

def get_structure(root_dir, indent=""):
    lines = []
    for item in sorted(os.listdir(root_dir)):
        path = os.path.join(root_dir, item)
        if os.path.isdir(path):
            lines.append(f"{indent}📁 {item}/")
            lines.extend(get_structure(path, indent + "    "))
        else:
            lines.append(f"{indent}📄 {item}")
    return lines

# 🗂️ Target project root
root_project_path = r"E:\GTS Logistics"

# 🔍 Build directory tree
structure_lines = [f"📦 Project Structure for: {root_project_path}\n"]
structure_lines += get_structure(root_project_path)

# 📤 Print structure
for line in structure_lines:
    print(line)

# 💾 Save structure to file
output_path = os.path.join(root_project_path, "project_structure.txt")
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(structure_lines))

print(f"\n✅ Saved structure to: {output_path}")
