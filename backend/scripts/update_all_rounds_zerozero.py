"""
Update ALL rounds for Primeira Liga using ZeroZero data
This script will:
1. Fetch all rounds (1-34) from ZeroZero
2. Update existing matches with correct round numbers and dates
3. Optionally create new matches if they don't exist
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
from database.database import SessionLocal
from database.models import Match, Team

TIMEOUT = 10
DELAY_BETWEEN_ROUNDS = 2  # seconds


def fetch_round_matches(round_num: int):
    """Fetch matches for a specific round from ZeroZero"""
    url = f"https://www.zerozero.pt/competicao/liga-portuguesa?jornada_in={round_num}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        
        if response.status_code != 200:
            print(f"  ❌ Error: Status code {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        matches = []
        
        # Find all links
        all_links = soup.find_all('a')
        
        # Look for score patterns
        for i, link in enumerate(all_links):
            link_text = link.get_text(strip=True)
            
            # Check if this looks like a score (e.g., "1-1", "2-0")
            if re.match(r'^\d+\s*-\s*\d+$', link_text):
                match_data = parse_score_context(all_links, i, round_num)
                if match_data:
                    matches.append(match_data)
        
        return matches
        
    except requests.Timeout:
        print(f"  ⏱️ TIMEOUT after {TIMEOUT}s")
        return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []


def parse_score_context(all_links, score_idx, round_num):
    """Parse match from score link and surrounding context"""
    try:
        score_text = all_links[score_idx].get_text(strip=True)
        
        # Parse score
        score_match = re.match(r'^(\d+)\s*-\s*(\d+)$', score_text)
        if not score_match:
            return None
        
        home_score = int(score_match.group(1))
        away_score = int(score_match.group(2))
        
        # Look for team names before and after the score
        home_team = None
        away_team = None
        match_date = None
        
        # Search backwards for home team
        for i in range(score_idx - 1, max(0, score_idx - 5), -1):
            text = all_links[i].get_text(strip=True)
            href = all_links[i].get('href', '')
            
            if text and len(text) > 2 and '/equipa/' in href:
                home_team = text
                break
        
        # Search forwards for away team
        for i in range(score_idx + 1, min(len(all_links), score_idx + 5)):
            text = all_links[i].get_text(strip=True)
            href = all_links[i].get('href', '')
            
            if text and len(text) > 2 and '/equipa/' in href:
                away_team = text
                break
        
        if home_team and away_team:
            return {
                'round': round_num,
                'date': match_date,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'status': 'finished'
            }
        
        return None
        
    except Exception as e:
        return None


def normalize_team_name(name: str) -> str:
    """Normalize team names for matching"""
    # Common variations
    mappings = {
        'Sporting': 'Sporting CP',
        'Sp Lisbon': 'Sporting CP',
        'Porto': 'FC Porto',
        'Braga': 'SC Braga',
        'Famalicão': 'FC Famalicão',
        'Arouca': 'FC Arouca',
        'Alverca': 'FC Alverca',
        'Tondela': 'CD Tondela',
        'Amadora': 'Est. Amadora',
    }
    
    # Check if name matches any mapping
    for key, value in mappings.items():
        if key in name:
            return value
    
    return name


def find_or_create_team(db, team_name: str) -> Team:
    """Find team by name or create if doesn't exist"""
    # Normalize name
    normalized = normalize_team_name(team_name)
    
    # Try exact match first
    team = db.query(Team).filter(Team.name == normalized).first()
    if team:
        return team
    
    # Try partial match
    team = db.query(Team).filter(Team.name.contains(team_name)).first()
    if team:
        return team
    
    # Try reverse partial match
    team = db.query(Team).filter(Team.name.like(f'%{team_name}%')).first()
    if team:
        return team
    
    # Create new team
    print(f"    ℹ️  Creating new team: {normalized}")
    new_team = Team(name=normalized, league="Primeira Liga")
    db.add(new_team)
    db.flush()
    return new_team


def update_database(db, all_rounds_data, season="2024/2025"):
    """Update database with all rounds data"""
    
    updated_count = 0
    created_count = 0
    skipped_count = 0
    
    for round_data in all_rounds_data:
        round_num = round_data['round']
        matches = round_data['matches']
        
        print(f"\n  Processing Jornada {round_num}: {len(matches)} matches")
        
        for match_data in matches:
            try:
                # Get or create teams
                home_team = find_or_create_team(db, match_data['home_team'])
                away_team = find_or_create_team(db, match_data['away_team'])
                
                # Find existing match
                existing = db.query(Match).filter(
                    Match.home_team_id == home_team.id,
                    Match.away_team_id == away_team.id,
                    Match.league == "Primeira Liga",
                    Match.season == season
                ).first()
                
                if existing:
                    # Update existing match
                    existing.round = str(round_num)
                    if match_data['home_score'] is not None:
                        existing.home_score = match_data['home_score']
                        existing.away_score = match_data['away_score']
                        existing.status = 'finished'
                    updated_count += 1
                    print(f"    ✅ Updated: {home_team.name} vs {away_team.name}")
                else:
                    # Create new match (if it doesn't exist)
                    # We'll skip creation for now and just report
                    skipped_count += 1
                    print(f"    ⚠️  Not in DB: {home_team.name} vs {away_team.name}")
                    
            except Exception as e:
                print(f"    ❌ Error processing match: {e}")
                continue
    
    db.commit()
    
    return {
        'updated': updated_count,
        'created': created_count,
        'skipped': skipped_count
    }


def main():
    print("="*70)
    print("🔄 ZeroZero Round Update Script")
    print("="*70)
    print("\nThis script will:")
    print("  1. Fetch all rounds (1-34) from ZeroZero.pt")
    print("  2. Update existing matches with correct round numbers")
    print("  3. Update scores for finished matches")
    print("\n" + "="*70)
    
    # Ask for confirmation
    response = input("\n⚠️  Continue? This will update the database. (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled by user")
        return
    
    db = SessionLocal()
    all_rounds_data = []
    
    try:
        # Fetch all rounds
        print("\n📥 Fetching data from ZeroZero...")
        print("-"*70)
        
        for round_num in range(1, 35):  # Jornadas 1-34
            print(f"\n🔍 Fetching Jornada {round_num}...")
            matches = fetch_round_matches(round_num)
            
            if matches:
                all_rounds_data.append({
                    'round': round_num,
                    'matches': matches
                })
                print(f"  ✅ Found {len(matches)} matches")
            else:
                print(f"  ⚠️  No matches found (may not be played yet)")
            
            # Be polite to the server
            if round_num < 34:
                time.sleep(DELAY_BETWEEN_ROUNDS)
        
        # Summary of fetched data
        total_matches = sum(len(r['matches']) for r in all_rounds_data)
        print(f"\n{'='*70}")
        print(f"📊 Fetched {len(all_rounds_data)} rounds with {total_matches} total matches")
        print("="*70)
        
        # Update database
        print("\n💾 Updating database...")
        print("-"*70)
        
        stats = update_database(db, all_rounds_data)
        
        # Final summary
        print(f"\n{'='*70}")
        print("✅ UPDATE COMPLETE!")
        print("="*70)
        print(f"  Updated: {stats['updated']} matches")
        print(f"  Created: {stats['created']} matches")
        print(f"  Skipped: {stats['skipped']} matches (not in DB)")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        db.rollback()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
