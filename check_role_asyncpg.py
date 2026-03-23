#!/usr/bin/env python
"""Direct check of user role without complex dependencies"""
import asyncio
import asyncpg

async def check_role():
    """Check user role directly via asyncpg"""
    try:
        # Direct connection
        conn = await asyncpg.connect(
            host="dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com",
            port=5432,
            user="gabani_transport_solutions_user",
            password="__SET_IN_SECRET_MANAGER__",
            database="gabani_transport_solutions",
            ssl="require"
        )
        
        print("\n=== Checking User: enjoy983@hotmail.com ===")
        row = await conn.fetchrow(
            "SELECT id, email, role, is_active FROM users WHERE email = $1",
            "enjoy983@hotmail.com"
        )
        
        if row:
            print(f"✅ User Found")
            print(f"   ID: {row['id']}")
            print(f"   Email: {row['email']}")
            print(f"   Role (DB): '{row['role']}'")
            print(f"   Is Active: {row['is_active']}")
        else:
            print("❌ User not found")
        
        print("\n=== All Super Admins ===")
        rows = await conn.fetch(
            "SELECT id, email, role FROM users WHERE role = 'super_admin' LIMIT 10"
        )
        if rows:
            for r in rows:
                print(f"   - {r['email']} (role='{r['role']}')")
        else:
            print("   No super_admin users found")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_role())
