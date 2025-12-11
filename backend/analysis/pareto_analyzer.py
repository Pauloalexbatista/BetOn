"""
Pareto Analysis Module (80/20 Rule)
Identifies the top 20% of factors that generate 80% of results
"""
import sqlite3
from typing import Dict, List, Tuple
from datetime import datetime
import json

class ParetoAnalyzer:
    """
    Analyzes betting data using the Pareto Principle (80/20 rule)
    to identify the most profitable teams, strategies, and bet types.
    """
    
    def __init__(self, db_path: str = 'beton.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def analyze_teams_roi(self, min_matches: int = 10) -> List[Dict]:
        """
        Analyze ROI by team
        
        Args:
            min_matches: Minimum number of matches to consider
            
        Returns:
            List of teams with their ROI metrics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all teams with their match statistics
        query = """
        SELECT 
            t.id,
            t.name,
            COUNT(DISTINCT m.id) as total_matches,
            SUM(CASE 
                WHEN m.home_team_id = t.id AND m.home_score > m.away_score THEN 1
                WHEN m.away_team_id = t.id AND m.away_score > m.home_score THEN 1
                ELSE 0
            END) as wins,
            SUM(CASE 
                WHEN m.home_score = m.away_score THEN 1
                ELSE 0
            END) as draws,
            SUM(CASE 
                WHEN m.home_team_id = t.id AND m.home_score < m.away_score THEN 1
                WHEN m.away_team_id = t.id AND m.away_score < m.home_score THEN 1
                ELSE 0
            END) as losses
        FROM teams t
        LEFT JOIN matches m ON (m.home_team_id = t.id OR m.away_team_id = t.id)
        WHERE m.status = 'finished'
        GROUP BY t.id, t.name
        HAVING total_matches >= ?
        ORDER BY wins DESC
        """
        
        cursor.execute(query, (min_matches,))
        results = cursor.fetchall()
        
        teams_analysis = []
        for row in results:
            team_id, name, total_matches, wins, draws, losses = row
            
            if total_matches > 0:
                win_rate = (wins / total_matches) * 100
                
                # Calculate points (3 for win, 1 for draw)
                points = (wins * 3) + draws
                max_points = total_matches * 3
                points_percentage = (points / max_points) * 100 if max_points > 0 else 0
                
                teams_analysis.append({
                    'team_id': team_id,
                    'name': name,
                    'total_matches': total_matches,
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'win_rate': round(win_rate, 2),
                    'points': points,
                    'points_percentage': round(points_percentage, 2)
                })
        
        # Sort by win rate
        teams_analysis.sort(key=lambda x: x['win_rate'], reverse=True)
        
        conn.close()
        return teams_analysis
    
    def get_top_20_percent_teams(self, min_matches: int = 10) -> List[Dict]:
        """
        Get the top 20% of teams by win rate
        
        Args:
            min_matches: Minimum number of matches to consider
            
        Returns:
            Top 20% of teams
        """
        all_teams = self.analyze_teams_roi(min_matches)
        
        # Calculate 20% threshold
        top_20_count = max(1, int(len(all_teams) * 0.2))
        
        return all_teams[:top_20_count]
    
    def analyze_home_vs_away(self) -> Dict:
        """
        Analyze home vs away performance
        
        Returns:
            Dictionary with home/away statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Home team statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_matches,
                SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) as home_wins,
                SUM(CASE WHEN home_score = away_score THEN 1 ELSE 0 END) as draws,
                SUM(CASE WHEN home_score < away_score THEN 1 ELSE 0 END) as away_wins
            FROM matches
            WHERE status = 'finished'
        """)
        
        result = cursor.fetchone()
        total, home_wins, draws, away_wins = result
        
        analysis = {
            'total_matches': total,
            'home_wins': home_wins,
            'home_win_rate': round((home_wins / total * 100), 2) if total > 0 else 0,
            'draws': draws,
            'draw_rate': round((draws / total * 100), 2) if total > 0 else 0,
            'away_wins': away_wins,
            'away_win_rate': round((away_wins / total * 100), 2) if total > 0 else 0
        }
        
        conn.close()
        return analysis
    
    def analyze_betting_markets(self, season: str = None) -> Dict:
        """
        Analyze all betting markets (Over/Under, BTTS, 1X2)
        
        Args:
            season: Optional season filter (e.g., '2024-25')
            
        Returns:
            Dictionary with market statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build query with optional season filter
        where_clause = "WHERE status = 'finished'"
        params = []
        
        if season:
            where_clause += " AND season = ?"
            params.append(season)
        
        # Get all finished matches
        query = f"""
            SELECT 
                home_score,
                away_score,
                season
            FROM matches
            {where_clause}
        """
        
        cursor.execute(query, params)
        matches = cursor.fetchall()
        
        if not matches:
            conn.close()
            return {
                'total_matches': 0,
                'season': season or 'All',
                'markets': {}
            }
        
        # Initialize counters
        total = len(matches)
        over_05 = over_15 = over_25 = over_35 = 0
        under_05 = under_15 = under_25 = under_35 = 0
        btts_yes = btts_no = 0
        home_win = draw = away_win = 0
        
        for home_score, away_score, _ in matches:
            total_goals = home_score + away_score
            
            # Over/Under markets
            if total_goals > 0.5: over_05 += 1
            else: under_05 += 1
            
            if total_goals > 1.5: over_15 += 1
            else: under_15 += 1
            
            if total_goals > 2.5: over_25 += 1
            else: under_25 += 1
            
            if total_goals > 3.5: over_35 += 1
            else: under_35 += 1
            
            # BTTS (Both Teams To Score)
            if home_score > 0 and away_score > 0:
                btts_yes += 1
            else:
                btts_no += 1
            
            # 1X2 Market
            if home_score > away_score:
                home_win += 1
            elif home_score == away_score:
                draw += 1
            else:
                away_win += 1
        
        analysis = {
            'total_matches': total,
            'season': season or 'All Seasons',
            'markets': {
                'over_under': {
                    'over_0.5': {'count': over_05, 'percentage': round((over_05/total)*100, 2)},
                    'under_0.5': {'count': under_05, 'percentage': round((under_05/total)*100, 2)},
                    'over_1.5': {'count': over_15, 'percentage': round((over_15/total)*100, 2)},
                    'under_1.5': {'count': under_15, 'percentage': round((under_15/total)*100, 2)},
                    'over_2.5': {'count': over_25, 'percentage': round((over_25/total)*100, 2)},
                    'under_2.5': {'count': under_25, 'percentage': round((under_25/total)*100, 2)},
                    'over_3.5': {'count': over_35, 'percentage': round((over_35/total)*100, 2)},
                    'under_3.5': {'count': under_35, 'percentage': round((under_35/total)*100, 2)}
                },
                'btts': {
                    'yes': {'count': btts_yes, 'percentage': round((btts_yes/total)*100, 2)},
                    'no': {'count': btts_no, 'percentage': round((btts_no/total)*100, 2)}
                },
                '1x2': {
                    'home_win': {'count': home_win, 'percentage': round((home_win/total)*100, 2)},
                    'draw': {'count': draw, 'percentage': round((draw/total)*100, 2)},
                    'away_win': {'count': away_win, 'percentage': round((away_win/total)*100, 2)}
                }
            }
        }
        
        conn.close()
        return analysis
    
    def get_available_seasons(self) -> List[str]:
        """
        Get list of available seasons in the database
        
        Returns:
            List of season strings
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT season 
            FROM matches 
            WHERE season IS NOT NULL 
            ORDER BY season DESC
        """)
        
        seasons = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return seasons
    
    def analyze_bet_types_roi(self) -> List[Dict]:
        """
        Analyze ROI by bet type (if bets data exists)
        
        Returns:
            List of bet types with their ROI
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if bets table has data
        cursor.execute("SELECT COUNT(*) FROM bets")
        bet_count = cursor.fetchone()[0]
        
        if bet_count == 0:
            conn.close()
            return []
        
        # Analyze by bet type
        query = """
        SELECT 
            bet_type,
            COUNT(*) as total_bets,
            SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as losses,
            SUM(stake) as total_staked,
            SUM(CASE WHEN status = 'won' THEN payout ELSE 0 END) as total_payout
        FROM bets
        GROUP BY bet_type
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        bet_analysis = []
        for row in results:
            bet_type, total_bets, wins, losses, total_staked, total_payout = row
            
            win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
            roi = ((total_payout - total_staked) / total_staked * 100) if total_staked > 0 else 0
            
            bet_analysis.append({
                'bet_type': bet_type,
                'total_bets': total_bets,
                'wins': wins,
                'losses': losses,
                'win_rate': round(win_rate, 2),
                'total_staked': round(total_staked, 2),
                'total_payout': round(total_payout, 2),
                'roi': round(roi, 2)
            })
        
        # Sort by ROI
        bet_analysis.sort(key=lambda x: x['roi'], reverse=True)
        
        conn.close()
        return bet_analysis
    
    def generate_report(self, output_file: str = None) -> Dict:
        """
        Generate comprehensive Pareto analysis report
        
        Args:
            output_file: Optional file path to save JSON report
            
        Returns:
            Complete analysis report
        """
        print("🔍 Generating Pareto Analysis Report...")
        print("=" * 60)
        
        # Analyze teams
        print("\n📊 Analyzing teams...")
        all_teams = self.analyze_teams_roi(min_matches=5)
        top_20_teams = self.get_top_20_percent_teams(min_matches=5)
        
        print(f"   Total teams analyzed: {len(all_teams)}")
        print(f"   Top 20% teams: {len(top_20_teams)}")
        
        # Analyze home vs away
        print("\n🏠 Analyzing home vs away performance...")
        home_away = self.analyze_home_vs_away()
        
        # Analyze bet types
        print("\n🎯 Analyzing bet types...")
        bet_types = self.analyze_bet_types_roi()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_teams': len(all_teams),
                'top_20_percent_count': len(top_20_teams),
                'total_matches_analyzed': home_away['total_matches']
            },
            'top_20_percent_teams': top_20_teams,
            'all_teams': all_teams,
            'home_vs_away': home_away,
            'bet_types': bet_types
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📈 PARETO ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"\n🏆 Top 20% Teams ({len(top_20_teams)} teams):")
        for i, team in enumerate(top_20_teams[:5], 1):
            print(f"   {i}. {team['name']}: {team['win_rate']}% win rate ({team['wins']}/{team['total_matches']})")
        
        print(f"\n🏠 Home Advantage:")
        print(f"   Home wins: {home_away['home_win_rate']}%")
        print(f"   Away wins: {home_away['away_win_rate']}%")
        print(f"   Draws: {home_away['draw_rate']}%")
        
        if bet_types:
            print(f"\n🎯 Best Bet Types:")
            for i, bet in enumerate(bet_types[:3], 1):
                print(f"   {i}. {bet['bet_type']}: {bet['roi']}% ROI ({bet['win_rate']}% win rate)")
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Report saved to: {output_file}")
        
        return report
    
    def get_top_20_percent_team_ids(self, season: str = None, market: str = 'win_rate', min_matches: int = 5) -> List[int]:
        """
        Get list of team IDs in top 20% for filtering
        
        Args:
            season: Optional season filter
            market: Market type ('win_rate', 'over_2.5', 'btts_yes', 'home_win')
            min_matches: Minimum matches to consider
            
        Returns:
            List of team IDs in top 20%
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build query with optional season filter
        where_clause = "WHERE m.status = 'finished'"
        params = [min_matches]
        
        if season:
            where_clause += " AND m.season = ?"
            params.append(season)
        
        query = f"""
        SELECT 
            t.id,
            COUNT(DISTINCT m.id) as total_matches,
            SUM(CASE 
                WHEN m.home_team_id = t.id AND m.home_score > m.away_score THEN 1
                WHEN m.away_team_id = t.id AND m.away_score > m.home_score THEN 1
                ELSE 0
            END) as wins,
            SUM(CASE 
                WHEN m.home_score + m.away_score > 2.5 THEN 1
                ELSE 0
            END) as over_25,
            SUM(CASE 
                WHEN m.home_score > 0 AND m.away_score > 0 THEN 1
                ELSE 0
            END) as btts,
            SUM(CASE 
                WHEN m.home_team_id = t.id AND m.home_score > m.away_score THEN 1
                ELSE 0
            END) as home_wins,
            SUM(CASE 
                WHEN m.home_team_id = t.id THEN 1
                ELSE 0
            END) as home_matches
        FROM teams t
        LEFT JOIN matches m ON (m.home_team_id = t.id OR m.away_team_id = t.id)
        {where_clause}
        GROUP BY t.id
        HAVING total_matches >= ?
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Calculate metric based on market
        teams_with_metric = []
        for row in results:
            team_id, total, wins, over_25, btts, home_wins, home_matches = row
            
            if market == 'over_2.5':
                metric = (over_25 / total) * 100 if total > 0 else 0
            elif market == 'btts_yes':
                metric = (btts / total) * 100 if total > 0 else 0
            elif market == 'home_win':
                metric = (home_wins / home_matches) * 100 if home_matches > 0 else 0
            else:  # win_rate
                metric = (wins / total) * 100 if total > 0 else 0
            
            teams_with_metric.append((team_id, metric))
        
        # Sort by metric
        teams_with_metric.sort(key=lambda x: x[1], reverse=True)
        
        # Get top 20%
        top_20_count = max(1, int(len(teams_with_metric) * 0.2))
        top_20_ids = [team_id for team_id, _ in teams_with_metric[:top_20_count]]
        
        conn.close()
        return top_20_ids
    
    def calculate_confidence_score(self, team_id: int, market: str = 'win_rate', last_n: int = 5) -> Dict:
        """
        Calculate confidence score for a team based on multiple factors
        
        Args:
            team_id: Team ID
            market: Target market type
            last_n: Number of recent games to consider for form
            
        Returns:
            Dictionary with confidence score and breakdown
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get overall team stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_matches,
                SUM(CASE 
                    WHEN (m.home_team_id = ? AND m.home_score > m.away_score) OR
                         (m.away_team_id = ? AND m.away_score > m.home_score)
                    THEN 1 ELSE 0
                END) as wins,
                SUM(CASE WHEN m.home_score + m.away_score > 2.5 THEN 1 ELSE 0 END) as over_25,
                SUM(CASE WHEN m.home_score > 0 AND m.away_score > 0 THEN 1 ELSE 0 END) as btts
            FROM matches m
            WHERE (m.home_team_id = ? OR m.away_team_id = ?)
            AND m.status = 'finished'
        """, (team_id, team_id, team_id, team_id))
        
        result = cursor.fetchone()
        if not result or result[0] == 0:
            conn.close()
            return {'confidence': 0, 'breakdown': {}}
        
        total, wins, over_25, btts = result
        
        # Calculate base metrics
        win_rate = (wins / total) * 100 if total > 0 else 0
        over_25_rate = (over_25 / total) * 100 if total > 0 else 0
        btts_rate = (btts / total) * 100 if total > 0 else 0
        
        # Get recent form (last N games)
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN (m.home_team_id = ? AND m.home_score > m.away_score) OR
                         (m.away_team_id = ? AND m.away_score > m.home_score)
                    THEN 1 ELSE 0
                END as won
            FROM matches m
            WHERE (m.home_team_id = ? OR m.away_team_id = ?)
            AND m.status = 'finished'
            ORDER BY m.match_date DESC
            LIMIT ?
        """, (team_id, team_id, team_id, team_id, last_n))
        
        recent_results = cursor.fetchall()
        recent_wins = sum(row[0] for row in recent_results)
        recent_form = (recent_wins / len(recent_results)) * 100 if recent_results else 0
        
        # Get home/away advantage
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN m.home_team_id = ? THEN 1 ELSE 0 END) as home_matches,
                SUM(CASE WHEN m.home_team_id = ? AND m.home_score > m.away_score THEN 1 ELSE 0 END) as home_wins
            FROM matches m
            WHERE (m.home_team_id = ? OR m.away_team_id = ?)
            AND m.status = 'finished'
        """, (team_id, team_id, team_id, team_id))
        
        home_result = cursor.fetchone()
        home_matches, home_wins = home_result if home_result else (0, 0)
        home_advantage = (home_wins / home_matches) * 100 if home_matches > 0 else 0
        
        # Calculate market-specific performance
        if market == 'over_2.5':
            market_performance = over_25_rate
        elif market == 'btts_yes':
            market_performance = btts_rate
        else:  # win_rate or home_win
            market_performance = win_rate
        
        # Calculate weighted confidence score
        confidence = (
            (win_rate * 0.40) +           # 40% weight on overall win rate
            (market_performance * 0.30) +  # 30% weight on market performance
            (recent_form * 0.20) +         # 20% weight on recent form
            (home_advantage * 0.10)        # 10% weight on home advantage
        )
        
        breakdown = {
            'win_rate': round(win_rate, 2),
            'market_performance': round(market_performance, 2),
            'recent_form': round(recent_form, 2),
            'home_advantage': round(home_advantage, 2),
            'total_matches': total,
            'recent_matches': len(recent_results)
        }
        
        conn.close()
        
        return {
            'confidence': round(confidence, 2),
            'breakdown': breakdown
        }

def main():
    """Main function to run Pareto analysis"""
    analyzer = ParetoAnalyzer()
    report = analyzer.generate_report(output_file='pareto_analysis.json')
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
