import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/telegram/health') as response:
        data = json.loads(response.read().decode())
        print("Success:", data)
except Exception as e:
    print("Error:", e)