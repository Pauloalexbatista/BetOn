import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Strategy

def debug():
    db = SessionLocal()
    try:
        strategies = db.query(Strategy).all()
        print(f"Success! Found {len(strategies)} strategies.")
        for s in strategies:
            print(s.name)
    except Exception as e:
        print(f"Error querying strategies: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug()
