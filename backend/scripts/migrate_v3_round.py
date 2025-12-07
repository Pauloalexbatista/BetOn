import sqlite3
import os

DB_PATH = "beton.db"

def migrate():
    print("Migrating database to V3 (Adding Round column)...")
    
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(matches)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "round" in columns:
            print("Column 'round' already exists. Skipping.")
        else:
            print("Adding 'round' column...")
            cursor.execute("ALTER TABLE matches ADD COLUMN round TEXT")
            conn.commit()
            print("Migration successful!")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
