import sqlite3

print("=" * 60)
print("ROOT DATABASE (beton.db)")
print("=" * 60)

conn = sqlite3.connect('beton.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM teams")
print(f"\nTotal teams: {cursor.fetchone()[0]}")

cursor.execute("SELECT name FROM teams WHERE name LIKE '%Lisbon%' OR name LIKE '%Portugal%' OR name LIKE '%Lisboa%' OR name LIKE '%Braga%'")
duplicates = cursor.fetchall()

if duplicates:
    print(f"\nDuplicates found: {len(duplicates)}")
    for (name,) in duplicates:
        print(f"  - {name}")
else:
    print("\n✅ No duplicates!")

conn.close()

print("\n" + "=" * 60)
print("BACKEND DATABASE (backend/beton.db)")
print("=" * 60)

conn = sqlite3.connect('backend/beton.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM teams")
print(f"\nTotal teams: {cursor.fetchone()[0]}")

cursor.execute("SELECT name FROM teams WHERE name LIKE '%Lisbon%' OR name LIKE '%Portugal%' OR name LIKE '%Lisboa%' OR name LIKE '%Braga%'")
duplicates = cursor.fetchall()

if duplicates:
    print(f"\nDuplicates found: {len(duplicates)}")
    for (name,) in duplicates:
        print(f"  - {name}")
else:
    print("\n✅ No duplicates!")

conn.close()
