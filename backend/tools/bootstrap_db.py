import os, re, asyncio
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from sqlalchemy.ext.asyncio import create_async_engine

def _mask(dsn: str) -> str:
    return re.sub('//([^:/@]+):([^@]+)@', lambda m: f'//{m.group(1)}:***@', dsn)

def _clean_asyncpg(dsn: str) -> str:
    if dsn.startswith('postgresql://'):
        dsn = 'postgresql+asyncpg://' + dsn[len('postgresql://'):]
    parts = urlsplit(dsn)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))
    q.pop('sslmode', None)
    if parts.scheme.startswith('postgresql+asyncpg'):
        if 'ssl' not in q:
            q['ssl'] = 'true'
    new_query = urlencode(q)
    cleaned = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    cleaned = re.sub('([?&])sslmode=[^&]*(&|$)', lambda m: '&' if m.group(2) else '', cleaned)
    cleaned = cleaned.replace('?&', '?').rstrip('&?')
    return cleaned

async def main():
    raw = os.getenv('ASYNC_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not raw:
        raise SystemExit('Set ASYNC_DATABASE_URL')
    dsn = _clean_asyncpg(raw)
    print('bootstrap raw =', _mask(raw))
    print('bootstrap dsn =', _mask(dsn))
    engine = create_async_engine(dsn, future=True)
    async with engine.begin() as conn:
        try:
            from models.document import Base
        except Exception:
            from models.document import Base
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(bind=sync_conn))
    print('bootstrap: OK')
if __name__ == '__main__':
    asyncio.run(main())
