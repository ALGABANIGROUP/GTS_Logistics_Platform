import os

TARGET_KEYWORDS = ["BrowserRouter"]
FOUND = []

def search_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if any(keyword in line for keyword in TARGET_KEYWORDS):
                FOUND.append((filepath, idx + 1, line.strip()))

def scan_directory(root_dir):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".jsx") or file.endswith(".js"):
                search_file(os.path.join(root, file))

if __name__ == "__main__":
    print("🔍 Scanning for duplicate <BrowserRouter>...")
    frontend_src_path = "E:/GTS Logistics/frontend/src"
    scan_directory(frontend_src_path)

    if FOUND:
        print("\n❗ Found <BrowserRouter> usage in the following files:\n")
        for path, line_num, code in FOUND:
            print(f"{path} (Line {line_num}): {code}")
    else:
        print("\n✅ No duplicate <BrowserRouter> usage found.")
