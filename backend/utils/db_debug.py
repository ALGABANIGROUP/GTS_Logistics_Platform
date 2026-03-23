import asyncpg

async def fetch_data():
    results = {}

    try:
        conn = await asyncpg.connect(
            user="gabani_transport_solutions_user",
            password="__SET_IN_SECRET_MANAGER__",
            database="gabani_transport_solutions",
            host="dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com",
            port="5432"
        )

        tables = [
            "users",
            "documents",
            "news",
            "finance",
            "transactions",
            "invoices",
            "shipments",
            "alembic_version"
        ]

        for table in tables:
            try:
                query = f"SELECT * FROM {table} LIMIT 5"
                rows = await conn.fetch(query)
                results[table] = [dict(row) for row in rows]
            except Exception as table_error:
                results[table] = f"❌ Error reading {table}: {table_error}"

        await conn.close()

    except Exception as e:
        results["error"] = str(e)

    return results
