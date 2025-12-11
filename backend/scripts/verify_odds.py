import sqlite3

def check_odds():
    try:
        conn = sqlite3.connect('backend/beton.db')
        cursor = conn.cursor()
        
        # Check overall odds availability
        print("Checking odds availability...")
        cursor.execute("""
            SELECT 
                league, 
                COUNT(*) as total_matches,
                COUNT(home_odds) as has_home_odds,
                COUNT(draw_odds) as has_draw_odds,
                COUNT(away_odds) as has_away_odds
            FROM matches
            GROUP BY league
        """)
        
        results = cursor.fetchall()
        print(f"{'League':<20} | {'Total':<8} | {'Odds %':<8}")
        print("-" * 45)
        
        for row in results:
            league, total, h_odds, d_odds, a_odds = row
            # Calculate average availability
            odds_count = (h_odds + d_odds + a_odds) / 3
            coverage = (odds_count / total * 100) if total > 0 else 0
            
            print(f"{league:<20} | {total:<8} | {coverage:.1f}%")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_odds()
