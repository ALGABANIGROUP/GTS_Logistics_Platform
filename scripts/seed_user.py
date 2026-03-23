import sys, asyncio
from sqlalchemy import select

from backend.security.auth import get_db_async, get_password_hash

# Try to import User model from most likely locations in the project
User = None
candidates = [
    ("backend.models.user", "User"),
    ("backend.models.models", "User"),
    ("backend.models.subscription", "User"),
]

for mod_name, cls_name in candidates:
    try:
        mod = __import__(mod_name, fromlist=[cls_name])
        User = getattr(mod, cls_name)
        break
    except Exception:
        pass

if User is None:
    raise RuntimeError("Could not import User model. Check backend/models/*.py")

def pick_attr(obj, names):
    for n in names:
        if hasattr(obj, n):
            return n
    return None

async def main():
    if len(sys.argv) < 4:
        print("Usage: python scripts/seed_user.py <email> <password> <full_name> [role]")
        sys.exit(1)

    email = sys.argv[1].strip()
    password = sys.argv[2]
    full_name = sys.argv[3]
    role = sys.argv[4] if len(sys.argv) >= 5 else "admin"

    # Get Session from dependency async generator
    session = None
    async for s in get_db_async():
        session = s
        break
    if session is None:
        raise RuntimeError("Could not obtain DB session from get_db_async()")

    # Check if user exists
    q = await session.execute(select(User).where(User.email == email))
    existing = q.scalar_one_or_none()
    if existing:
        print(f"User already exists: {email} (id={getattr(existing,'id',None)})")
        return

    hashed = get_password_hash(password)

    # EN
    pwd_field = pick_attr(User, ["hashed_password", "password_hash", "hash_password"])
    if pwd_field is None:
        raise RuntimeError("Could not find password hash field on User model (expected hashed_password/password_hash)")

    user = User()
    user.email = email
    setattr(user, pwd_field, hashed)

    # EN
    if hasattr(user, "full_name"):
        user.full_name = full_name
    elif hasattr(user, "name"):
        user.name = full_name

    if hasattr(user, "role"):
        user.role = role

    if hasattr(user, "is_active") and getattr(user, "is_active") is None:
        user.is_active = True

    if hasattr(user, "is_deleted") and getattr(user, "is_deleted") is None:
        user.is_deleted = False

    session.add(user)
    await session.commit()
    await session.refresh(user)

    print("Created user ✅")
    print("  email:", email)
    print("  id:", getattr(user, "id", None))
    print("  role:", getattr(user, "role", None))
    print("  pwd_field:", pwd_field)

asyncio.run(main())
