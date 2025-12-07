import sqlite3
import os

DB_PATH = "beton.db"

def migrate():
    print("Migrating database to V2...")
    
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(strategies)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "target_outcome" in columns:
            print("Column 'target_outcome' already exists. Skipping.")
        else:
            print("Adding 'target_outcome' column...")
            cursor.execute("ALTER TABLE strategies ADD COLUMN target_outcome TEXT DEFAULT 'home_win'")
            conn.commit()
            print("Migration successful!")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
