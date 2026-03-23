# backend/auth/roles.py

ROLES = {
    "admin": ["admin", "manager", "finance", "ai", "driver", "user"],
    "manager": ["manager", "finance", "ai", "driver", "user"],
    "finance": ["finance"],
    "ai": ["ai"],
    "driver": ["driver"],
    "user": ["user"],
}
