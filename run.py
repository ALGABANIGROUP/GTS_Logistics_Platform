#!/usr/bin/env python
"""
Run script for local development
This script adds the current directory to path and runs uvicorn
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8002,
        reload=True,
        reload_dirs=["backend"]
    )