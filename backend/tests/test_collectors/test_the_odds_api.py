"""
Tests for The Odds API client
"""
import pytest
from unittest.mock import Mock, patch
from collectors.the_odds_api import TheOddsAPIClient


@pytest.mark.unit
@pytest.mark.collectors
class TestTheOddsAPIClient:
    """Test suite for The Odds API client"""
    
    def test_client_initialization(self):
        """Test that client initializes correctly"""
        client = TheOddsAPIClient()
        assert client is not None
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'base_url')
    
    @patch('collectors.the_odds_api.requests.get')
    def test_get_sports_success(self, mock_get):
        """Test successful sports retrieval"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"key": "soccer_portugal_primeira_liga", "title": "Primeira Liga"}
        ]
        mock_get.return_value = mock_response
        
        client = TheOddsAPIClient()
        sports = client.get_sports()
        
        assert len(sports) == 1
        assert sports[0]['key'] == 'soccer_portugal_primeira_liga'
    
    @patch('collectors.the_odds_api.requests.get')
    def test_get_odds_with_valid_sport(self, mock_get, mock_odds_api_response):
        """Test getting odds for a valid sport"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_odds_api_response
        mock_get.return_value = mock_response
        
        client = TheOddsAPIClient()
        odds = client.get_odds("soccer_portugal_primeira_liga")
        
        assert len(odds) > 0
        assert 'home_team' in odds[0]
        assert 'away_team' in odds[0]
    
    @patch('collectors.the_odds_api.requests.get')
    def test_api_error_handling(self, mock_get):
        """Test that API errors are handled gracefully"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        client = TheOddsAPIClient()
        
        with pytest.raises(Exception):
            client.get_sports()
    
    def test_market_parameter(self):
        """Test that market parameter is handled correctly"""
        client = TheOddsAPIClient()
        
        # Default should be h2h
        assert 'h2h' in client.get_supported_markets()
