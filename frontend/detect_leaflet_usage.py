import os

leaflet_keywords = ["leaflet", "react-leaflet", "L.map", "MapContainer"]
found_files = []

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".js") or file.endswith(".jsx") or file.endswith(".ts") or file.endswith(".tsx"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if any(keyword in content for keyword in leaflet_keywords):
                    print(f"🔍 Found Leaflet usage in: {path}")
                    found_files.append(path)

if not found_files:
    print("✅ No Leaflet usage found in project.")
