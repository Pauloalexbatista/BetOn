"""
Betfair API Client using betfairlightweight

This module provides a wrapper around the Betfair API for:
- Authentication
- Market data retrieval
- Bet placement
- Account management
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

try:
    import betfairlightweight
    from betfairlightweight import APIClient
    from betfairlightweight.filters import (
        market_filter,
        streaming_market_filter,
        streaming_market_data_filter
    )
except ImportError:
    # Graceful fallback if betfairlightweight not installed yet
    betfairlightweight = None
    APIClient = None

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BetfairClient:
    """Betfair API client wrapper"""
    
    def __init__(self):
        if not betfairlightweight:
            logger.warning("betfairlightweight not installed. Install with: pip install betfairlightweight")
            self.client = None
            return
        
        self.client: Optional[APIClient] = None
        self.is_authenticated = False
    
    def login(self) -> bool:
        """
        Authenticate with Betfair API
        
        Returns:
            bool: True if authentication successful
        """
        if not betfairlightweight:
            logger.error("betfairlightweight not available")
            return False
        
        try:
            self.client = APIClient(
                username=settings.betfair_username,
                password=settings.betfair_password,
                app_key=settings.betfair_app_key,
                certs=settings.betfair_cert_path if settings.betfair_cert_path else None
            )
            
            self.client.login()
            self.is_authenticated = True
            logger.info("Successfully authenticated with Betfair API")
            return True
            
        except Exception as e:
            logger.error(f"Betfair authentication failed: {e}")
            self.is_authenticated = False
            return False
    
    def logout(self):
        """Logout from Betfair API"""
        if self.client:
            try:
                self.client.logout()
                self.is_authenticated = False
                logger.info("Logged out from Betfair API")
            except Exception as e:
                logger.error(f"Logout failed: {e}")
    
    def get_football_events(self, country: str = "Portugal") -> List[Dict]:
        """
        Get football events for a specific country
        
        Args:
            country: Country name (default: Portugal)
            
        Returns:
            List of events
        """
        if not self.is_authenticated:
            logger.warning("Not authenticated. Call login() first")
            return []
        
        try:
            # Create market filter for football in Portugal
            market_filter_obj = market_filter(
                event_type_ids=['1'],  # 1 = Football
                market_countries=[country]
            )
            
            # Get events
            events = self.client.betting.list_events(
                filter=market_filter_obj
            )
            
            logger.info(f"Found {len(events)} football events in {country}")
            return [
                {
                    "id": event.event.id,
                    "name": event.event.name,
                    "country": event.event.country_code,
                    "timezone": event.event.timezone,
                    "open_date": event.event.open_date,
                    "market_count": event.market_count
                }
                for event in events
            ]
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []
    
    def get_market_odds(self, market_id: str) -> Optional[Dict]:
        """
        Get odds for a specific market
        
        Args:
            market_id: Betfair market ID
            
        Returns:
            Market odds data
        """
        if not self.is_authenticated:
            logger.warning("Not authenticated. Call login() first")
            return None
        
        try:
            market_book = self.client.betting.list_market_book(
                market_ids=[market_id],
                price_projection={
                    'priceData': ['EX_BEST_OFFERS']
                }
            )
            
            if market_book:
                return {
                    "market_id": market_book[0].market_id,
                    "status": market_book[0].status,
                    "runners": [
                        {
                            "selection_id": runner.selection_id,
                            "status": runner.status,
                            "back_prices": runner.ex.available_to_back if runner.ex else [],
                            "lay_prices": runner.ex.available_to_lay if runner.ex else []
                        }
                        for runner in market_book[0].runners
                    ]
                }
            
        except Exception as e:
            logger.error(f"Failed to get market odds: {e}")
            return None
    
    def place_bet(
        self,
        market_id: str,
        selection_id: int,
        stake: float,
        price: float,
        side: str = "BACK"
    ) -> Optional[Dict]:
        """
        Place a bet on Betfair
        
        Args:
            market_id: Market ID
            selection_id: Selection ID
            stake: Stake amount
            price: Odds
            side: BACK or LAY
            
        Returns:
            Bet placement result
        """
        if not self.is_authenticated:
            logger.warning("Not authenticated. Call login() first")
            return None
        
        # Safety check for paper trading mode
        if settings.paper_trading_mode:
            logger.info(f"PAPER TRADE: Would place {side} bet on {selection_id} at {price} for £{stake}")
            return {
                "status": "PAPER_TRADE",
                "message": "Paper trading mode - bet not actually placed"
            }
        
        try:
            instruction = {
                "selectionId": selection_id,
                "handicap": "0",
                "side": side,
                "orderType": "LIMIT",
                "limitOrder": {
                    "size": stake,
                    "price": price,
                    "persistenceType": "LAPSE"
                }
            }
            
            result = self.client.betting.place_orders(
                market_id=market_id,
                instructions=[instruction]
            )
            
            logger.info(f"Bet placed: {result}")
            return {
                "status": result.status,
                "market_id": market_id,
                "bet_id": result.instruction_reports[0].bet_id if result.instruction_reports else None
            }
            
        except Exception as e:
            logger.error(f"Failed to place bet: {e}")
            return None


# Singleton instance
_betfair_client: Optional[BetfairClient] = None


def get_betfair_client() -> BetfairClient:
    """Get or create Betfair client singleton"""
    global _betfair_client
    if _betfair_client is None:
        _betfair_client = BetfairClient()
    return _betfair_client
