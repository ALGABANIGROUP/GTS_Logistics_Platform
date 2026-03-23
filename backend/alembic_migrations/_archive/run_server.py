import os
import sys
from pathlib import Path

# ✅ Add this to include the root directory in sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

print("🚀 Starting GTS Logistics Backend Server...")

os.system("uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
