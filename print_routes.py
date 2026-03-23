from backend.main import app

for route in app.router.routes:
    path = getattr(route, "path", "")
    methods = ",".join(sorted(getattr(route, "methods", []) or []))
    name = getattr(route, "name", "")
    print(f"{methods:15} {path:45} {name}")
