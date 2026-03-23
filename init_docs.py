import os, psycopg2

url = os.environ.get("PGURL") or "postgresql://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a/gabani_transport_solutions?sslmode=require"

sql = """
CREATE TABLE IF NOT EXISTS documents (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  file_url TEXT NOT NULL,
  file_type TEXT,
  expires_at TIMESTAMP NULL,
  notify_before_days INTEGER,
  owner_id INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
"""

print("Connecting to:", url)
conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute(sql)
conn.commit()
cur.close()
conn.close()
print("OK - documents table ready")
