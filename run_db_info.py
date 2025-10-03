import sqlite3, json
conn = sqlite3.connect('travel_app.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info('trip')")
rows = cur.fetchall()
print('PRAGMA table_info for trip:')
for r in rows:
    print(r)
print('\nAll tables:')
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(row)
conn.close()