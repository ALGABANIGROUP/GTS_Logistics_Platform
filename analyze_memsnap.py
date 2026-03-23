import tracemalloc
from pathlib import Path

p = Path("mem_snapshot_1770968169.txt")
text = p.read_text(encoding="utf-8")
print("=== File head preview ===")
print("\n".join(text.splitlines()[:200]))
