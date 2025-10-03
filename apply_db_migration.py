import sqlite3

conn = sqlite3.connect('travel_app.db')
cur = conn.cursor()
cols = [r[1] for r in cur.execute("PRAGMA table_info('trip')").fetchall()]
print('Existing columns:', cols)
if 'image_url' not in cols:
    try:
        cur.execute("ALTER TABLE trip ADD COLUMN image_url TEXT")
        print('Added image_url')
    except Exception as e:
        print('Failed to add image_url:', e)
if 'thumbnail' not in cols:
    try:
        cur.execute("ALTER TABLE trip ADD COLUMN thumbnail TEXT")
        print('Added thumbnail')
    except Exception as e:
        print('Failed to add thumbnail:', e)
conn.commit()
cols2 = [r[1] for r in cur.execute("PRAGMA table_info('trip')").fetchall()]
print('After:', cols2)
conn.close()