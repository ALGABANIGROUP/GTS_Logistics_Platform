import os
import ast
from collections import defaultdict

 # Project root path
BASE_DIR = "E:/GTS Logistics"

 # To collect class names and their locations
class_locations = defaultdict(list)

 # Function to find classes in a file
def find_classes_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            node = ast.parse(f.read(), filename=file_path)
        except SyntaxError:
            return

        for obj in node.body:
            if isinstance(obj, ast.ClassDef):
                class_locations[obj.name].append(file_path)

# EN .py
 # Search for all .py files in the project
for root, dirs, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            find_classes_in_file(file_path)

# EN
 # Print only duplicate class names
print("🔎 Duplicate class names across the project:\n")
for class_name, paths in class_locations.items():
    if len(paths) > 1:
        print(f"🚨 Class '{class_name}' is defined in {len(paths)} places:")
        for path in paths:
            print(f"   └─ {path}")
        print()
