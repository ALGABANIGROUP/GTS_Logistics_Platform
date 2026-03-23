## Removed all DB credential references and logic for frontend security compliance
        async with engine.connect() as conn:
            result = await conn.execute("SELECT datname, datcollate, encoding FROM pg_database;")
            databases = result.fetchall()
            print("\n✅ Connection successful! Databases available:")
            for db in databases:
                print(f"🔹 Name: {db[0]}, Collation: {db[1]}, Encoding: {db[2]}")
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
    finally:
        await engine.dispose()

# Run the test
asyncio.run(test_db_connection())
