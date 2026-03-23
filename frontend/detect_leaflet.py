import os

leaflet_keywords = [
    "leaflet",
    "react-leaflet",
    "MapContainer",
    "TileLayer",
    "Marker",
    "Popup"
]

project_dir = "."  # 🔁 EN frontend

def search_leaflet_usage():
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith((".js", ".jsx", ".ts", ".tsx")):
                filepath = os.path.join(root, file)
                with open(filepath, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for keyword in leaflet_keywords:
                        if keyword in content:
                            print(f"🔍 Found '{keyword}' in: {filepath}")
                            break

if __name__ == "__main__":
    search_leaflet_usage()
