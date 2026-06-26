import sys
import sqlite3
import os
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend import config

print("DB Path:", config.DB_PATH)
conn = sqlite3.connect(config.DB_PATH)
c = conn.cursor()
c.execute("select name, file_path from datasets")
rows = c.fetchall()
print("SEEDED FILES IN DB:")
for r in rows:
    if "large" in r[0] or "forecast_enterprise" in r[0]:
        print(r)
conn.close()
