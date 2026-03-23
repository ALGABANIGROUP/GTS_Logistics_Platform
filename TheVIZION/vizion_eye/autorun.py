# autorun.py
# Importing this module logs "open" and registers atexit "close".
# Optional auto-dashboard window if VIZION_EYE_AUTODASH=1
import atexit, os, subprocess, sys
from . import db

# log program open
db.ensure_db()
db.log_event("open", None, {"proc": os.path.basename(sys.argv[0])})

def _close():
    db.log_event("close", None, {"proc": os.path.basename(sys.argv[0])})
atexit.register(_close)

# optional auto dashboard in a new console (Windows)
if os.environ.get("VIZION_EYE_AUTODASH") == "1":
    try:
        if os.name == "nt":
            # new window
            subprocess.Popen([sys.executable, "-m", "vizion_eye.cli", "dashboard"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen([sys.executable, "-m", "vizion_eye.cli", "dashboard"])
    except Exception as e:
        db.log_event("autodash_error", None, {"error": str(e)})
