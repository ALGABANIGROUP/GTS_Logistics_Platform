# finance_env_fix.py
import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

FIN_KEYS = [
    "FINANCE_DATABASE_URL",
    "FINANCE_DB_URL",
    "FINANCE_DB_DSN",
    "FINANCE_SYNC_DATABASE_URL",
    "FINANCE_ASYNC_DATABASE_URL",
    "SQLALCHEMY_FINANCE_DATABASE_URI",
]

def _mask(url: str) -> str:
    if not url:
        return url
    try:
        scheme, netloc, path, query, frag = urlsplit(url)
        if "@" in netloc and ":" in netloc.split("@")[0]:
            cred, host = netloc.split("@", 1)
            user = cred.split(":", 1)[0]
            netloc = f"{user}:***@{host}"
        return urlunsplit((scheme, netloc, path, query, frag))
    except Exception:
        return url

def _fix(url: str) -> str:
    if not url:
        return url
    parts = urlsplit(url)
    q = [(k, v) for (k, v) in parse_qsl(parts.query, keep_blank_values=True) if k.lower() != "ssl"]
    has_sslmode = any(k.lower() == "sslmode" for (k, _) in q)
    if not has_sslmode:
        q.append(("sslmode", "require"))
    new_query = urlencode(q)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))

def apply():
    for k, v in list(os.environ.items()):
        if ((k.startswith("FINANCE") or k == "SQLALCHEMY_FINANCE_DATABASE_URI")
            and (("URL" in k) or ("DSN" in k))):
            if v:
                fixed = _fix(v)
                if fixed != v:
                    os.environ[k] = fixed
    os.environ.setdefault("PGSSLMODE", "require")
    to_log = []
    for k in FIN_KEYS:
        v = os.environ.get(k)
        if v:
            to_log.append(f"{k}={_mask(v)}")
    if to_log:
        print("[finance_env_fix] Applied; " + " | ".join(to_log))
