from pathlib import Path
import re

root = Path(r"c:\Users\enjoy\dev\GTS")
files = [
    "simple_db_fix.sql",
    "GTS_SAAS_READINESS_AUDIT_REPORT.md",
    "MAPLELOAD_LOAD_SOURCES_INTEGRATION.md",
    "MAPLELOAD_V4_COMPLETION_SUMMARY.md",
    "PRIORITY_1_IMPLEMENTATION_SUMMARY.md",
    "README_MAPLELOAD_V4_INDEX.md",
    "RENDER_DATABASE_REMOVAL_GUIDE.md",
    "ROAD_ALERTS_SYSTEM_GUIDE.md",
    "SAAS_READINESS_REPORT.md",
    "SAFETY_MANAGER_UPDATE_SUMMARY.md",
    "SUPPORT_EMAIL_UPDATE.md",
    "WEATHER_ALERT_SYSTEM_README.md",
    "WEBSOCKET_CALLS_COMPARISON_AR.md",
]

# Context-friendly replacements for markdown/sql text
patterns = [
    (re.compile(r'(?m)^\s*EN\s*$'), 'English content section'),
    (re.compile(r'(?m)^\s*[-*]\s+EN\s*$'), '- English item'),
    (re.compile(r'(?<![A-Za-z0-9_])EN API(?![A-Za-z0-9_])'), 'API documentation'),
    (re.compile(r'(?<![A-Za-z0-9_])EN TMS(?![A-Za-z0-9_])'), 'TMS workflow'),
    (re.compile(r'(?<![A-Za-z0-9_])EN Shipments(?![A-Za-z0-9_])'), 'shipment operations'),
    (re.compile(r'(?<![A-Za-z0-9_])EN GTS EN(?![A-Za-z0-9_])'), 'Gabani Transport Solutions (GTS)'),
    (re.compile(r'(?<![A-Za-z0-9_])EN TMS EN(?![A-Za-z0-9_])'), 'Transport Management System (TMS)'),
    (re.compile(r'(?<![A-Za-z0-9_])EN(?![A-Za-z0-9_])'), 'English'),
]

changed = []
for rel in files:
    p = root / rel
    if not p.exists():
        continue
    txt = p.read_text(encoding='utf-8')
    new = txt
    for rgx, rep in patterns:
        new = rgx.sub(rep, new)
    if new != txt:
        p.write_text(new, encoding='utf-8')
        changed.append(rel)

print('UPDATED', len(changed))
for f in changed:
    print(f)
