"""
Database Migration: Add strategy_type column to strategies table
"""
import sqlite3
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'beton.db')
    
    print(f"🔧 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(strategies)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'strategy_type' in columns:
            print("✅ Column 'strategy_type' already exists. Skipping migration.")
            return
        
        # Add strategy_type column
        print("📝 Adding 'strategy_type' column...")
        cursor.execute("""
            ALTER TABLE strategies 
            ADD COLUMN strategy_type TEXT DEFAULT 'single'
        """)
        
        # Update existing records to have strategy_type = 'single'
        cursor.execute("""
            UPDATE strategies 
            SET strategy_type = 'single' 
            WHERE strategy_type IS NULL
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   - Added column: strategy_type (default: 'single')")
        print(f"   - Updated {cursor.rowcount} existing strategies")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
