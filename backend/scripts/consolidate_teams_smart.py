"""
Smart Team Consolidation
Automatically detects and merges similar team names based on fuzzy matching.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Team, Match
import re
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """Normalize team name for comparison"""
    # Remove common prefixes/suffixes
    name = re.sub(r'^(FC|SC|CD|GD|CF|AC)\s+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(FC|SAD|AC)$', '', name, flags=re.IGNORECASE)
    
    # Remove accents and special chars
    replacements = {
        'ã': 'a', 'á': 'a', 'à': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ü': 'u',
        'ç': 'c'
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
        name = name.replace(old.upper(), new.upper())
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    return name.strip().lower()


# Blacklist: Teams that should NEVER be merged
BLACKLIST_PAIRS = [
    ("Manchester United", "Manchester City"),
    ("Inter Milan", "AC Milan"),
    ("Real Madrid", "Atletico Madrid"),
    ("Sporting", "Sporting Gijon"),
]


def is_blacklisted(name1: str, name2: str) -> bool:
    """Check if two teams are in blacklist (should not be merged)"""
    n1_lower = name1.lower()
    n2_lower = name2.lower()
    
    for team1, team2 in BLACKLIST_PAIRS:
        t1_lower = team1.lower()
        t2_lower = team2.lower()
        
        # Check both directions
        if (t1_lower in n1_lower and t2_lower in n2_lower) or \
           (t1_lower in n2_lower and t2_lower in n1_lower):
            return True
    
    return False


def similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two names"""
    # Check blacklist first
    if is_blacklisted(name1, name2):
        return 0.0  # Force no match
    
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    # Exact match after normalization
    if norm1 == norm2:
        return 1.0
    
    # Check if one contains the other
    if norm1 in norm2 or norm2 in norm1:
        return 0.9
    
    # Sequence matching
    return SequenceMatcher(None, norm1, norm2).ratio()


def find_duplicate_groups(teams):
    """Group duplicate teams together"""
    groups = []
    processed = set()
    
    for i, team1 in enumerate(teams):
        if team1.id in processed:
            continue
        
        # Start a new group
        group = [team1]
        processed.add(team1.id)
        
        # Find similar teams
        for team2 in teams[i+1:]:
            if team2.id in processed:
                continue
            
            sim = similarity(team1.name, team2.name)
            
            # High similarity threshold
            if sim >= 0.85:
                group.append(team2)
                processed.add(team2.id)
        
        # Only keep groups with duplicates
        if len(group) > 1:
            groups.append(group)
    
    return groups


def choose_primary_team(group):
    """Choose the primary team from a duplicate group"""
    # Prefer shorter names (usually cleaner)
    # Prefer names without prefixes
    
    scored = []
    for team in group:
        score = 0
        
        # Shorter is better
        score -= len(team.name)
        
        # No prefix/suffix is better
        if not re.match(r'^(FC|SC|CD|GD|CF|AC)\s+', team.name, re.IGNORECASE):
            score += 10
        if not re.search(r'\s+(FC|SAD|AC)$', team.name, re.IGNORECASE):
            score += 10
        
        # Has more data is better
        if team.league:
            score += 5
        if team.country:
            score += 5
        
        scored.append((score, team))
    
    # Return team with highest score
    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[0][1]


def consolidate_smart():
    """Smart consolidation - finds and merges all duplicates"""
    db = SessionLocal()
    
    try:
        # Get all teams
        teams = db.query(Team).all()
        logger.info(f"Found {len(teams)} teams total")
        
        # Find duplicate groups
        duplicate_groups = find_duplicate_groups(teams)
        logger.info(f"Found {len(duplicate_groups)} duplicate groups")
        
        if not duplicate_groups:
            logger.info("✅ No duplicates found!")
            return 0
        
        total_merged = 0
        total_deleted = 0
        
        for group in duplicate_groups:
            # Choose primary
            primary = choose_primary_team(group)
            duplicates = [t for t in group if t.id != primary.id]
            
            logger.info(f"\n📦 Group: {[t.name for t in group]}")
            logger.info(f"   Primary: {primary.name} (ID: {primary.id})")
            
            for dup in duplicates:
                logger.info(f"   Merging: {dup.name} (ID: {dup.id}) → {primary.name}")
                
                # Update matches (home)
                home_count = db.query(Match).filter(
                    Match.home_team_id == dup.id
                ).update({Match.home_team_id: primary.id})
                
                # Update matches (away)
                away_count = db.query(Match).filter(
                    Match.away_team_id == dup.id
                ).update({Match.away_team_id: primary.id})
                
                logger.info(f"      Moved: {home_count} home + {away_count} away matches")
                total_merged += (home_count + away_count)
                
                # Delete duplicate
                db.delete(dup)
                total_deleted += 1
        
        db.commit()
        
        logger.info(f"\n✅ Consolidation Complete!")
        logger.info(f"   Groups processed: {len(duplicate_groups)}")
        logger.info(f"   Matches moved: {total_merged}")
        logger.info(f"   Teams deleted: {total_deleted}")
        
        return total_deleted
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    consolidate_smart()
