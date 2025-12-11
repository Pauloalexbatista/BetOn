"""
Tests for Data Quality Analyzer
"""
import pytest
from analysis.data_quality_analyzer import DataQualityAnalyzer
from database.models import Team, Match, Odds
from datetime import datetime, timedelta


@pytest.mark.unit
@pytest.mark.analysis
class TestDataQualityAnalyzer:
    """Test suite for Data Quality Analyzer"""
    
    def test_analyzer_initialization(self, test_db):
        """Test that analyzer initializes correctly"""
        analyzer = DataQualityAnalyzer(test_db)
        assert analyzer is not None
        assert analyzer.db == test_db
    
    def test_team_similarity_detection(self, test_db):
        """Test that similar team names are detected"""
        analyzer = DataQualityAnalyzer(test_db)
        
        # Should detect as similar
        assert analyzer._are_similar_teams("FC Porto", "Porto") == True
        assert analyzer._are_similar_teams("Boavista", "Boavista FC") == True
        
        # Should NOT detect as similar (different teams)
        assert analyzer._are_similar_teams("Porto", "Sporting") == False
    
    def test_blacklist_protection(self, test_db):
        """Test that blacklisted teams are not marked as duplicates"""
        analyzer = DataQualityAnalyzer(test_db)
        
        # These should NOT be similar (blacklisted)
        assert analyzer._are_similar_teams("Manchester United", "Manchester City") == False
        assert analyzer._are_similar_teams("Inter Milan", "AC Milan") == False
        assert analyzer._are_similar_teams("Real Madrid", "Atletico Madrid") == False
    
    def test_analyze_team_quality_empty_db(self, test_db):
        """Test team quality analysis with empty database"""
        analyzer = DataQualityAnalyzer(test_db)
        result = analyzer.analyze_team_quality()
        
        assert 'total' in result
        assert result['total'] == 0
        assert result['duplicates_count'] == 0
    
    def test_analyze_team_quality_with_duplicates(self, test_db):
        """Test that duplicates are detected"""
        # Add test teams
        team1 = Team(name="Porto", league="Primeira Liga")
        team2 = Team(name="FC Porto", league="Primeira Liga")  # Duplicate
        test_db.add(team1)
        test_db.add(team2)
        test_db.commit()
        
        analyzer = DataQualityAnalyzer(test_db)
        result = analyzer.analyze_team_quality()
        
        assert result['total'] == 2
        assert result['duplicates_count'] > 0
    
    def test_match_coverage_analysis(self, test_db):
        """Test match coverage analysis"""
        # Add test match
        team1 = Team(name="Benfica", league="Primeira Liga")
        team2 = Team(name="Sporting", league="Primeira Liga")
        test_db.add_all([team1, team2])
        test_db.commit()
        
        match = Match(
            home_team_id=team1.id,
            away_team_id=team2.id,
            match_date=datetime.now(),
            league="Primeira Liga",
            season="2024/2025",
            status="finished",
            home_score=2,
            away_score=1
        )
        test_db.add(match)
        test_db.commit()
        
        analyzer = DataQualityAnalyzer(test_db)
        result = analyzer.analyze_match_coverage()
        
        assert 'total' in result
        assert result['total'] == 1
        assert result['finished'] == 1
    
    def test_generate_quality_report(self, test_db):
        """Test comprehensive quality report generation"""
        analyzer = DataQualityAnalyzer(test_db)
        report = analyzer.generate_quality_report()
        
        assert 'timestamp' in report
        assert 'summary' in report
        assert 'teams' in report
        assert 'matches' in report
        assert 'odds' in report
        assert 'recommendations'in report
