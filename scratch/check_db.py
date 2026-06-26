import sqlite3

conn = sqlite3.connect('backend/datasets.db')
c = conn.cursor()
c.execute("select name, file_path from datasets")
rows = c.fetchall()
print("ALL DATASETS:")
for r in rows:
    if "large" in r[0] or "sales" in r[0] or "customers" in r[0]:
        print(r)
conn.close()
