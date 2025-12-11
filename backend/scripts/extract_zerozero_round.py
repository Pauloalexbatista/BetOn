"""
Extract real match data from ZeroZero - UPDATED VERSION
Based on actual HTML structure discovered via browser inspection
"""

import requests
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
import re

TIMEOUT = 10

def extract_round_data(round_num: int = 13):
    """Extract match data from a specific round"""
    
    url = f"https://www.zerozero.pt/competicao/liga-portuguesa?jornada_in={round_num}"
    
    print(f"🔍 Fetching Jornada {round_num} from ZeroZero...")
    print(f"URL: {url}\n")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        
        if response.status_code != 200:
            print(f"❌ Error: Status code {response.status_code}")
            return []
        
        print(f"✅ Page loaded successfully ({len(response.content)} bytes)\n")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        matches = []
        
        # ZeroZero structure: date text nodes followed by <a> tags for teams/scores
        # Look for the main content div that contains matches
        # Usually in a div with id or class related to 'jogos' or 'resultados'
        
        # Find all text nodes that look like dates (DD/MM format)
        content = soup.find('body')
        if not content:
            print("❌ Could not find body element")
            return []
        
        # Strategy: Find all <a> tags that contain team names and scores
        # Team links usually go to /equipa/... or /jogo/...
        # Score links go to /jogo/...
        
        # Look for divs or sections that contain match info
        # Common pattern: div with class containing 'jogo', 'match', 'resultado'
        
        # Try to find match containers
        match_containers = soup.find_all('div', class_=lambda x: x and ('jogo' in x.lower() or 'match' in x.lower() or 'game' in x.lower()))
        
        if match_containers:
            print(f"Found {len(match_containers)} match containers with class filter")
            for container in match_containers:
                match_data = parse_match_container(container, round_num)
                if match_data:
                    matches.append(match_data)
        
        # If no matches found, try alternative: look for score links
        if not matches:
            print("Trying alternative parsing: looking for score patterns...")
            
            # Find all links that might be scores (contain digits and dash)
            all_links = soup.find_all('a')
            
            for i, link in enumerate(all_links):
                link_text = link.get_text(strip=True)
                
                # Check if this looks like a score (e.g., "1-1", "2-0")
                if re.match(r'^\d+\s*-\s*\d+$', link_text):
                    # Found a score! Look for team names around it
                    match_data = parse_score_context(all_links, i, round_num)
                    if match_data:
                        matches.append(match_data)
        
        return matches
        
    except requests.Timeout:
        print(f"⏱️ TIMEOUT after {TIMEOUT}s")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def parse_match_container(container, round_num):
    """Parse a match container div"""
    try:
        # Extract all text and links
        links = container.find_all('a')
        
        if len(links) < 3:
            return None
        
        # Typical structure: [home_team_link, score_link, away_team_link]
        # Or: [home_team_link, home_img, score, away_img, away_team_link]
        
        texts = [link.get_text(strip=True) for link in links]
        
        # Find score
        score_idx = None
        for i, text in enumerate(texts):
            if re.match(r'^\d+\s*-\s*\d+$', text):
                score_idx = i
                break
        
        if score_idx and score_idx > 0 and score_idx < len(texts) - 1:
            home_team = texts[score_idx - 1]
            away_team = texts[score_idx + 1]
            score_text = texts[score_idx]
            
            # Parse score
            home_score, away_score = map(int, score_text.split('-'))
            
            return {
                'round': round_num,
                'date': None,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'status': 'finished'
            }
        
        return None
        
    except Exception as e:
        return None


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
        # Usually: [..., home_team, home_img?, SCORE, away_img?, away_team, ...]
        
        home_team = None
        away_team = None
        
        # Search backwards for home team (skip image links)
        for i in range(score_idx - 1, max(0, score_idx - 5), -1):
            text = all_links[i].get_text(strip=True)
            href = all_links[i].get('href', '')
            
            # Skip image links and empty text
            if text and len(text) > 2 and '/equipa/' in href:
                home_team = text
                break
        
        # Search forwards for away team
        for i in range(score_idx + 1, min(len(all_links), score_idx + 5)):
            text = all_links[i].get_text(strip=True)
            href = all_links[i].get('href', '')
            
            # Skip image links and empty text
            if text and len(text) > 2 and '/equipa/' in href:
                away_team = text
                break
        
        if home_team and away_team:
            return {
                'round': round_num,
                'date': None,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'status': 'finished'
            }
        
        return None
        
    except Exception as e:
        return None


def main():
    print("="*60)
    print("🧪 ZeroZero Round Data Extraction Test (v2)")
    print("="*60 + "\n")
    
    # Test with Jornada 13
    matches = extract_round_data(13)
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTS: Found {len(matches)} matches")
    print("="*60 + "\n")
    
    if matches:
        for i, match in enumerate(matches, 1):
            date_str = match['date'].strftime('%d/%m/%Y') if match['date'] else 'TBD'
            score = f"{match['home_score']}-{match['away_score']}" if match['home_score'] is not None else "vs"
            
            print(f"{i:2}. {date_str:12} | {match['home_team']:20} {score:5} {match['away_team']:20} [{match['status']}]")
    else:
        print("❌ No matches found - parsing may need adjustment")
        print("\nℹ️  The HTML structure might be different than expected.")
        print("   Consider using browser automation for more reliable scraping.")
    
    print(f"\n{'='*60}")
    print("✅ Test Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
