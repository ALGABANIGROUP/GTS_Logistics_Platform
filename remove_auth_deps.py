#!/usr/bin/env python3
"""Remove authentication dependencies from MapleLoad Canada routes"""
import re

file_path = "backend/routes/mapleload_canada_routes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove ",\n    current_user: dict = Depends(get_current_user)" pattern
pattern = r',\s*current_user:\s*dict\s*=\s*Depends\(get_current_user\)'
original_count = len(re.findall(pattern, content))
content = re.sub(pattern, '', content)
new_count = len(re.findall(pattern, content))

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

removed = original_count - new_count
print(f"✅ Removed {removed} authentication dependencies from MapleLoad Canada routes")
print(f"📄 File: {file_path}")
