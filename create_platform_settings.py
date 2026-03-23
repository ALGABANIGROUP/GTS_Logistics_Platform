import os
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv('DATABASE_URL')
if db_url:
    import psycopg2
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS platform_settings (
          key TEXT PRIMARY KEY,
          value JSONB NOT NULL DEFAULT '{}',
          updated_at TIMESTAMP DEFAULT now()
        );
        INSERT INTO platform_settings(key,value)
        VALUES ('social_links', '{"linkedin":"","x":"","facebook":"","youtube":"","instagram":""}')
        ON CONFLICT (key) DO NOTHING;
        """
        cur.execute(sql)
        conn.commit()
        print('platform_settings table created and seeded')
        cur.close()
        conn.close()
    except Exception as e:
        print('DB error:', e)