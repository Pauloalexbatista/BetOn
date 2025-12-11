"""
Data Quality Analyzer
Analyzes database quality, completeness, and identifies issues across data sources.
"""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from datetime import datetime, timedelta

from database.models import Team, Match, Odds

logger = logging.getLogger(__name__)


class DataQualityAnalyzer:
    """Analyzes data quality across teams, matches, and odds"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_team_quality(self) -> Dict[str, Any]:
        """
        Analyze team data quality.
        Returns: metrics on duplicates, naming issues, missing data
        """
        try:
            teams = self.db.query(Team).all()
            total = len(teams)
            
            # Detect potential duplicates by similar names
            duplicates = []
            team_names = [t.name.lower().strip() for t in teams]
            seen = set()
            
            for i, team in enumerate(teams):
                name_lower = team.name.lower().strip()
                # Check for exact duplicates
                if team_names.count(name_lower) > 1 and name_lower not in seen:
                    similar = [t.name for t in teams if t.name.lower().strip() == name_lower]
                    duplicates.append({
                        "name": team.name,
                        "variants": similar,
                        "count": len(similar)
                    })
                    seen.add(name_lower)
                
                # Check for very similar names (e.g., "Boavista" vs "Boavista FC")
                for j, other in enumerate(teams):
                    if i >= j:
                        continue
                    if self._are_similar_teams(team.name, other.name):
                        dup_key = f"{min(team.name, other.name)}_{max(team.name, other.name)}"
                        if dup_key not in seen:
                            duplicates.append({
                                "name": f"{team.name} / {other.name}",
                                "variants": [team.name, other.name],
                                "count": 2,
                                "type": "similar"
                            })
                            seen.add(dup_key)
            
            # Teams without league
            without_league = self.db.query(Team).filter(
                or_(Team.league == None, Team.league == "")
            ).count()
            
            # Teams without country
            without_country = self.db.query(Team).filter(
                or_(Team.country == None, Team.country == "")
            ).count()
            
            return {
                "total": total,
                "duplicates_count": len(duplicates),
                "duplicates": duplicates[:10],  # Top 10
                "without_league": without_league,
                "without_country": without_country,
                "health": "good" if len(duplicates) < 5 else "warning" if len(duplicates) < 15 else "critical"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing team quality: {e}")
            return {"error": str(e)}
    
    
    def _are_similar_teams(self, name1: str, name2: str) -> bool:
        """Check if two team names are likely the same team"""
        # Blacklist: Teams that should NEVER be considered duplicates
        BLACKLIST_PAIRS = [
            ("Manchester United", "Manchester City"),
            ("Inter Milan", "AC Milan"),
            ("Real Madrid", "Atletico Madrid"),
            ("Sporting", "Sporting Gijon"),
        ]
        
        # Check blacklist first
        n1_lower = name1.lower()
        n2_lower = name2.lower()
        
        for team1, team2 in BLACKLIST_PAIRS:
            t1_lower = team1.lower()
            t2_lower = team2.lower()
            
            # Check both directions
            if (t1_lower in n1_lower and t2_lower in n2_lower) or \
               (t1_lower in n2_lower and t2_lower in n1_lower):
                return False  # Not similar - blacklisted
        
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        
        # Exact match
        if n1 == n2:
            return False  # Will be caught by exact duplicate check
        
        # One is substring of other (e.g., "Porto" vs "FC Porto")
        if n1 in n2 or n2 in n1:
            return True
        
        # Common suffixes/prefixes
        common_parts = ['fc', 'sc', 'cf', 'afc', 'united', 'city', 'athletic', 'clube']
        n1_clean = n1
        n2_clean = n2
        for part in common_parts:
            n1_clean = n1_clean.replace(part, '').strip()
            n2_clean = n2_clean.replace(part, '').strip()
        
        if n1_clean == n2_clean and len(n1_clean) > 3:
            return True
        
        return False
    
    def analyze_match_coverage(self) -> Dict[str, Any]:
        """
        Analyze match data completeness.
        Returns: metrics on matches, scores, rounds, dates
        """
        try:
            total = self.db.query(Match).count()
            
            # Status breakdown
            scheduled = self.db.query(Match).filter(Match.status == "scheduled").count()
            finished = self.db.query(Match).filter(Match.status == "finished").count()
            other_status = total - scheduled - finished
            
            # Missing data
            missing_rounds = self.db.query(Match).filter(
                or_(Match.round == None, Match.round == "")
            ).count()
            
            finished_without_scores = self.db.query(Match).filter(
                and_(
                    Match.status == "finished",
                    or_(Match.home_score == None, Match.away_score == None)
                )
            ).count()
            
            # Upcoming matches (next 7 days)
            # Use naive datetime to match database
            from datetime import datetime as dt
            today = dt.now().replace(hour=0, minute=0, second=0, microsecond=0)
            next_week = today + timedelta(days=7)
            upcoming = self.db.query(Match).filter(
                and_(
                    Match.match_date >= today,
                    Match.match_date <= next_week,
                    Match.status == "scheduled"
                )
            ).count()
            
            # Matches with odds
            matches_with_odds = self.db.query(Match.id).filter(
                Match.id.in_(
                    self.db.query(Odds.match_id).distinct()
                )
            ).count()
            
            matches_without_odds = total - matches_with_odds
            odds_coverage = (matches_with_odds / total * 100) if total > 0 else 0
            
            # League breakdown
            league_stats = self.db.query(
                Match.league,
                func.count(Match.id).label('total'),
                func.sum(case((Match.status == 'finished', 1), else_=0)).label('finished'),
                func.sum(case((Match.status == 'scheduled', 1), else_=0)).label('scheduled')
            ).group_by(Match.league).all()
            
            leagues = [
                {
                    "name": stat[0] or "Unknown",
                    "total": stat[1],
                    "finished": stat[2],
                    "scheduled": stat[3]
                }
                for stat in league_stats
            ]
            
            return {
                "total": total,
                "scheduled": scheduled,
                "finished": finished,
                "other_status": other_status,
                "upcoming_7_days": upcoming,
                "missing_rounds": missing_rounds,
                "finished_without_scores": finished_without_scores,
                "with_odds": matches_with_odds,
                "without_odds": matches_without_odds,
                "odds_coverage_percentage": round(odds_coverage, 1),
                "leagues": leagues,
                "health": self._assess_match_health(
                    missing_rounds, finished_without_scores, odds_coverage
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing match coverage: {e}")
            return {"error": str(e)}
    
    def _assess_match_health(self, missing_rounds: int, missing_scores: int, odds_coverage: float) -> str:
        """Assess overall match data health"""
        issues = 0
        if missing_rounds > 20:
            issues += 1
        if missing_scores > 10:
            issues += 1
        if odds_coverage < 60:
            issues += 1
        
        if issues == 0:
            return "good"
        elif issues == 1:
            return "warning"
        else:
            return "critical"
    
    def analyze_odds_coverage(self) -> Dict[str, Any]:
        """
        Analyze odds data coverage and sources.
        Returns: metrics on odds availability by bookmaker, market, league
        """
        try:
            total_odds = self.db.query(Odds).count()
            
            # By bookmaker
            by_bookmaker = self.db.query(
                Odds.bookmaker,
                func.count(Odds.id).label('count')
            ).group_by(Odds.bookmaker).all()
            
            bookmakers = [
                {"name": stat[0] or "Unknown", "count": stat[1]}
                for stat in by_bookmaker
            ]
            
            # By market
            by_market = self.db.query(
                Odds.market,
                func.count(Odds.id).label('count')
            ).group_by(Odds.market).all()
            
            markets = [
                {"name": stat[0] or "Unknown", "count": stat[1]}
                for stat in by_market
            ]
            
            # Unique matches with odds
            unique_matches = self.db.query(Odds.match_id).distinct().count()
            total_matches = self.db.query(Match).count()
            coverage = (unique_matches / total_matches * 100) if total_matches > 0 else 0
            
            # Recent odds (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_odds = self.db.query(Odds).filter(
                Odds.timestamp >= week_ago
            ).count()
            
            return {
                "total": total_odds,
                "unique_matches_covered": unique_matches,
                "coverage_percentage": round(coverage, 1),
                "recent_7_days": recent_odds,
                "by_bookmaker": bookmakers,
                "by_market": markets,
                "health": "good" if coverage >= 80 else "warning" if coverage >= 60 else "critical"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing odds coverage: {e}")
            return {"error": str(e)}
    
    def analyze_data_gaps(self) -> Dict[str, Any]:
        """
        Identify specific data gaps and missing records.
        Returns: actionable items to improve data quality
        """
        try:
            gaps = []
            
            # Check for matches without odds
            matches_no_odds = self.db.query(Match).filter(
                ~Match.id.in_(
                    self.db.query(Odds.match_id).distinct()
                )
            ).limit(10).all()
            
            if matches_no_odds:
                gaps.append({
                    "type": "missing_odds",
                    "severity": "high",
                    "count": self.db.query(Match).filter(
                        ~Match.id.in_(self.db.query(Odds.match_id).distinct())
                    ).count(),
                    "description": f"{len(matches_no_odds)} matches without any odds data",
                    "examples": [
                        f"{m.home_team.name if m.home_team else 'Unknown'} vs {m.away_team.name if m.away_team else 'Unknown'} ({m.match_date.strftime('%Y-%m-%d') if m.match_date else 'No date'})"
                        for m in matches_no_odds[:5]
                    ]
                })
            
            # Check for finished matches without scores
            matches_no_scores = self.db.query(Match).filter(
                and_(
                    Match.status == "finished",
                    or_(Match.home_score == None, Match.away_score == None)
                )
            ).limit(10).all()
            
            if matches_no_scores:
                gaps.append({
                    "type": "missing_scores",
                    "severity": "critical",
                    "count": len(matches_no_scores),
                    "description": f"{len(matches_no_scores)} finished matches without scores",
                    "examples": [
                        f"{m.home_team.name if m.home_team else 'Unknown'} vs {m.away_team.name if m.away_team else 'Unknown'} ({m.match_date.strftime('%Y-%m-%d') if m.match_date else 'No date'})"
                        for m in matches_no_scores[:5]
                    ]
                })
            
            # Check for missing upcoming fixtures
            today = datetime.now()
            next_month = today + timedelta(days=30)
            upcoming_count = self.db.query(Match).filter(
                and_(
                    Match.match_date >= today,
                    Match.match_date <= next_month,
                    Match.status == "scheduled"
                )
            ).count()
            
            if upcoming_count < 20:  # Arbitrary threshold
                gaps.append({
                    "type": "limited_fixtures",
                    "severity": "medium",
                    "count": upcoming_count,
                    "description": f"Only {upcoming_count} scheduled matches in next 30 days",
                    "recommendation": "Run schedule collector to fetch upcoming fixtures"
                })
            
            return {
                "total_gaps": len(gaps),
                "gaps": gaps,
                "health": "good" if len(gaps) == 0 else "warning" if len(gaps) <= 2 else "critical"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing data gaps: {e}")
            return {"error": str(e)}
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """
        Aggregate statistics by data source.
        Note: Requires tracking source in database (may not be fully implemented yet)
        """
        try:
            # For now, infer sources from available data
            # In future, add 'source' column to models
            
            stats = {
                "api_football": {
                    "description": "API-Football data (fixtures, odds, standings)",
                    "matches": self.db.query(Match).filter(Match.api_id != None).count(),
                    "teams": self.db.query(Team).filter(Team.api_id != None).count(),
                },
                "manual_collected": {
                    "description": "Manually collected or scraped data",
                    "matches": self.db.query(Match).filter(Match.api_id == None).count(),
                    "teams": self.db.query(Team).filter(Team.api_id == None).count(),
                },
                "odds_sources": {
                    "description": "Odds from various bookmakers",
                    "total_odds": self.db.query(Odds).count(),
                    "bookmakers": [
                        b[0] for b in self.db.query(Odds.bookmaker).distinct().all()
                    ]
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting source statistics: {e}")
            return {"error": str(e)}
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive quality report combining all analyses.
        This is the main entry point for the dashboard.
        """
        try:
            teams = self.analyze_team_quality()
            matches = self.analyze_match_coverage()
            odds = self.analyze_odds_coverage()
            gaps = self.analyze_data_gaps()
            sources = self.get_source_statistics()
            
            # Overall health assessment
            health_scores = []
            for analysis in [teams, matches, odds, gaps]:
                if "health" in analysis:
                    health_scores.append(analysis["health"])
            
            critical_count = health_scores.count("critical")
            warning_count = health_scores.count("warning")
            
            if critical_count > 0:
                overall_health = "critical"
            elif warning_count > 1:
                overall_health = "warning"
            else:
                overall_health = "good"
            
            # Generate recommendations
            recommendations = self._generate_recommendations(teams, matches, odds, gaps)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "overall_health": overall_health,
                    "critical_issues": critical_count,
                    "warnings": warning_count,
                    "status_message": self._get_status_message(overall_health)
                },
                "teams": teams,
                "matches": matches,
                "odds": odds,
                "gaps": gaps,
                "sources": sources,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "summary": {
                    "overall_health": "error",
                    "status_message": "Failed to generate report"
                }
            }
    
    def _generate_recommendations(
        self, 
        teams: Dict, 
        matches: Dict, 
        odds: Dict, 
        gaps: Dict
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Team issues
        if teams.get("duplicates_count", 0) > 0:
            recommendations.append({
                "priority": "high",
                "category": "teams",
                "message": f"{teams['duplicates_count']} potential duplicate teams found",
                "action": "Review and consolidate duplicate teams",
                "script": "python backend/scripts/consolidate_teams.py"
            })
        
        # Match issues
        if matches.get("finished_without_scores", 0) > 5:
            recommendations.append({
                "priority": "critical",
                "category": "matches",
                "message": f"{matches['finished_without_scores']} finished matches missing scores",
                "action": "Results will be updated when matches finish - no action needed",
                "script": None
            })
        
        # Odds coverage - use ODDS coverage, not match coverage
        odds_coverage = odds.get("coverage_percentage", 0)
        if odds_coverage < 50:
            recommendations.append({
                "priority": "high",
                "category": "odds",
                "message": f"Only {odds_coverage}% of matches have odds",
                "action": "Run odds collector via Data Quality dashboard",
                "script": "python backend/collectors/live_odds_collector.py"
            })
        
        # Upcoming fixtures - only warn if REALLY low
        upcoming = matches.get("upcoming_7_days", 0)
        if upcoming < 5:
            recommendations.append({
                "priority": "medium",
                "category": "schedule",
                "message": f"Only {upcoming} matches scheduled in next 7 days",
                "action": "Run odds collector - it auto-creates fixtures",
                "script": "Use Data Quality dashboard 'Executar Odds Collector' button"
            })
        
        
        # Data gaps
        for gap in gaps.get("gaps", []):
            if gap.get("severity") == "critical":
                recommendations.append({
                    "priority": "critical",
                    "category": "gaps",
                    "message": gap.get("description", "Critical data gap"),
                    "action": gap.get("recommendation", "Manual review required"),
                    "script": None
                })
        
        return recommendations
    
    def _get_status_message(self, health: str) -> str:
        """Get user-friendly status message"""
        messages = {
            "good": "✅ Data quality is good. Minor issues may exist.",
            "warning": "⚠️ Data quality issues detected. Review recommendations.",
            "critical": "🔴 Critical data quality issues require attention.",
            "error": "❌ Unable to assess data quality."
        }
        return messages.get(health, "Unknown status")
