import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db, SessionLocal
from database.models import Strategy

def test_get_db():
    print("Testing get_db generator...")
    gen = get_db()
    try:
        db = next(gen)
        print("Success: Session yielded.")
        strategies = db.query(Strategy).all()
        print(f"Query Success. Count: {len(strategies)}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # cleanup
        try:
            next(gen)
        except StopIteration:
            pass
        except Exception as e:
            print(f"Cleanup Error: {e}")

if __name__ == "__main__":
    test_get_db()
