from datetime import datetime, timedelta
from database.database import SessionLocal
from database.models import Match, OddsHistory
from collectors.api_football_client import APIFootballClient
from collectors.the_odds_client import TheOddsClient

class SyncEngine:
    def __init__(self):
        self.db = SessionLocal()
        self.football = APIFootballClient()
        self.odds = TheOddsClient()

    async def sync_data(self, league_id: int, season: int, sport_key: str):
        # 1. Throttling: Verificar última atualização
        last_sync = self.db.query(OddsHistory).order_by(OddsHistory.recorded_at.desc()).first()
        if last_sync and (datetime.utcnow() - last_sync.recorded_at) < timedelta(minutes=15):
            return {"status": "cached", "message": "Sync recente, servindo dados da base."}

        # 2. Fetch & Persist
        # (Simplificado para o fluxo de marcha)
        odds_data = await self.odds.get_odds(sport=sport_key)
        
        for match_data in odds_data:
            # Lógica de persistência simplificada
            match = Match(home_team=match_data['home_team'], away_team=match_data['away_team'], status="SCHEDULED")
            self.db.add(match)
            self.db.commit()
            
            # Gravar histórico de odds
            for bookmaker in match_data.get('bookmakers', []):
                for outcome in bookmaker.get('markets', [{}])[0].get('outcomes', []):
                    history = OddsHistory(match_id=match.id, odd_value=outcome['price'], market_type=outcome['name'])
                    self.db.add(history)
            self.db.commit()
            
        return {"status": "success", "message": "Dados sincronizados com sucesso."}

    def get_smart_money_alerts(self):
        # Lógica de Smart Money: Comparar primeira e última odd
        alerts = []
        matches = self.db.query(Match).all()
        for match in matches:
            history = self.db.query(OddsHistory).filter(OddsHistory.match_id == match.id).order_by(OddsHistory.recorded_at).all()
            if len(history) >= 2:
                first, last = history[0].odd_value, history[-1].odd_value
                if (first - last) / first >= 0.05:
                    alerts.append({"match": f"{match.home_team} vs {match.away_team}", "drop": "5%+"})
        return alerts