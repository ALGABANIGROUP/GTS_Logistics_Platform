import os, sys, importlib
ROOT = r"D:\GTS Logistics"
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

errors = []
for dirpath, _, files in os.walk(BACKEND):
    for f in files:
        if not f.endswith(".py"): continue
        if f in ("__init__.py",): continue
        rel = os.path.relpath(os.path.join(dirpath, f), BACKEND)
        mod = rel[:-3].replace(os.sep, ".")
        try:
            importlib.import_module(mod)
        except Exception as e:
            errors.append((mod, repr(e)))

if errors:
    print("⚠️ Import errors detected:")
    for mod, err in errors:
        print(f" - {mod}: {err}")
else:
    print("✅ All modules imported without error")
