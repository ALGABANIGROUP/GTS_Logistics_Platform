# check_frontend_health.py

import os
import subprocess
import webbrowser
import time

print("🚀 GTS Frontend Health Checker\n============================")

# 1. Check if you're in a Vite project
if not os.path.exists("vite.config.js"):
    print("❌ Missing vite.config.js — are you in the frontend folder?")
else:
    print("✅ vite.config.js found")

# 2. Check package.json
if not os.path.exists("package.json"):
    print("❌ Missing package.json")
else:
    print("✅ package.json found")

# 3. Check node_modules
if not os.path.exists("node_modules"):
    print("⚠️ node_modules missing, trying to install...")
    try:
        subprocess.run("npm install", shell=True, check=True)
        print("✅ node_modules installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to run npm install")

# 4. Check for main.jsx
if not os.path.exists("src/main.jsx"):
    print("❌ Missing src/main.jsx (entry point)")
else:
    print("✅ src/main.jsx found")

# 5. Check port availability (5173)
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 5173))
if result == 0:
    print("✅ Port 5173 is already in use (Vite might be running)")
else:
    print("🔄 Port 5173 is free, trying to run Vite...")
    try:
        subprocess.Popen("npm run dev", shell=True)
        time.sleep(5)
        print("✅ Vite dev server started. Opening browser...")
        webbrowser.open("http://localhost:5173")
    except Exception as e:
        print("❌ Failed to start Vite server:", str(e))
sock.close()

# 6. Check BASE_URL logic
try:
    with open("src/api.js", "r") as f:
        content = f.read()
        if "localhost:8000" in content:
            print("✅ BASE_URL points to localhost:8000")
        else:
            print("⚠️ BASE_URL is not pointing to local backend")
except FileNotFoundError:
    print("❌ src/api.js not found (used to configure API calls)")

print("\n✅ Check complete.")
