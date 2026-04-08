#!/usr/bin/env python
"""Create test users in the database (synchronous version)"""
import sys
import os

# Add workspace root to path
workspace_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, workspace_root)

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
import os as os_module

# Load environment
try:
    from dotenv import load_dotenv
    env_file = os.path.join(workspace_root, ".env")
    if os.path.exists(env_file):
        load_dotenv(env_file)
except:
    pass

# Get database URL and convert to sync if needed
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./gts.db"
)

# Convert async URLs to sync
if "+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg://", "+psycopg2://")
elif "+aiosqlite://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+aiosqlite://", "sqlite://")

# Import security
from backend.security.passwords import hash_password

# Import models
from backend.models.user import User


def create_test_users():
    # Create sync engine
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    
    users_to_create = [
        {
            "email": "enjoy983@hotmail.com",
            "password": "Gabani@2026",
            "full_name": "Admin User",
            "role": "admin",
        },
        {
            "email": "admin@gts.com",
            "password": "admin123",
            "full_name": "System Administrator",
            "role": "admin",
        },
        {
            "email": "manager@gts.com",
            "password": "manager123",
            "full_name": "Operations Manager",
            "role": "manager",
        },
        {
            "email": "admin@gts.local",
            "password": "admin123",
            "full_name": "System Administrator",
            "role": "admin",
        },
        {
            "email": "manager@gts.local",
            "password": "manager123",
            "full_name": "Account Manager",
            "role": "manager",
        },
        {
            "email": "user@gts.local",
            "password": "user123",
            "full_name": "Regular User",
            "role": "user",
        },
    ]
    
    session = Session()
    try:
        for user_data in users_to_create:
            # Check if user exists
            existing = session.query(User).filter(
                User.email == user_data["email"]
            ).first()
            
            if existing:
                print(f"✅ User already exists: {user_data['email']}")
                continue
            
            # Create new user
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                hashed_password=hash_password(user_data["password"]),
                is_active=True,
            )
            
            session.add(user)
            print(f"📝 Created user: {user_data['email']} (role: {user_data['role']})")
        
        session.commit()
        print("\n✅ All test users created successfully!")
        print("\nTest Credentials:")
        print("-" * 50)
        for user_data in users_to_create:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Role: {user_data['role']}")
            print()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
    engine.dispose()


if __name__ == "__main__":
    try:
        create_test_users()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
