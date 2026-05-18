import os
import sys
from datetime import datetime

# Adiciona o diretório backend ao path para importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import SessionLocal, init_db
from database.models import Match, OddsHistory

def seed_data():
    # Inicializa as tabelas se ainda não estiverem
    init_db()
    
    db = SessionLocal()
    
    # Limpa dados existentes para evitar duplicados
    db.query(OddsHistory).delete()
    db.query(Match).delete()
    db.commit()
    
    print("🌱 A semear dados do Mundial de 2026...")
    
    # 1. Criar Jogos (Matches) com ELOs e dados de FIFA
    matches_data = [
        {
            "home_team": "México",
            "away_team": "Coreia do Sul",
            "date": datetime(2026, 6, 11, 20, 0),
            "league_id": 1,
            "season": 2026,
            "home_elo": 1800,
            "away_elo": 1760,
            "home_fifa": 1650,
            "away_fifa": 1580,
            "status": "SCHEDULED",
            "result": "vs"
        },
        {
            "home_team": "Portugal",
            "away_team": "RD Congo",
            "date": datetime(2026, 6, 17, 13, 0),
            "league_id": 1,
            "season": 2026,
            "home_elo": 1980,
            "away_elo": 1710,
            "home_fifa": 1740,
            "away_fifa": 1540,
            "status": "SCHEDULED",
            "result": "vs"
        },
        {
            "home_team": "Portugal",
            "away_team": "Uzbequistão",
            "date": datetime(2026, 6, 23, 13, 0),
            "league_id": 1,
            "season": 2026,
            "home_elo": 1980,
            "away_elo": 1760,
            "home_fifa": 1740,
            "away_fifa": 1580,
            "status": "SCHEDULED",
            "result": "vs"
        },
        {
            "home_team": "Portugal",
            "away_team": "Colômbia",
            "date": datetime(2026, 6, 27, 19, 30),
            "league_id": 1,
            "season": 2026,
            "home_elo": 1980,
            "away_elo": 1940,
            "home_fifa": 1740,
            "away_fifa": 1710,
            "status": "SCHEDULED",
            "result": "vs"
        },

        {
            "home_team": "EUA",
            "away_team": "Suíça",
            "date": datetime(2026, 6, 12, 19, 0),
            "league_id": 1,
            "season": 2026,
            "home_elo": 1820,
            "away_elo": 1780,
            "home_fifa": 1660,
            "away_fifa": 1610,
            "status": "SCHEDULED",
            "result": "vs"
        },
        {
            "home_team": "Brasil",
            "away_team": "Marrocos",
            "date": datetime(2026, 6, 14, 21, 0),
            "league_id": 1,
            "season": 2026,
            "home_elo": 2010,
            "away_elo": 1880,
            "home_fifa": 1780,
            "away_fifa": 1660,
            "status": "SCHEDULED",
            "result": "vs"
        }
    ]
    
    for m_info in matches_data:
        match = Match(**m_info)
        db.add(match)
        db.commit()
        db.refresh(match)
        
        # 2. Gravar histórico de odds para simular Smart Money (Declínios de odd)
        if match.home_team == "México":
            # Caso 1: Queda acentuada na odd do México (Smart Money)
            # Abertura (12 horas atrás)
            h1 = OddsHistory(match_id=match.id, market_type="México", odd_value=2.10, recorded_at=datetime.utcnow() - timedelta(hours=12))
            # Atual (Agora)
            h2 = OddsHistory(match_id=match.id, market_type="México", odd_value=1.90, recorded_at=datetime.utcnow()) # Queda de 9.5%!
            db.add_all([h1, h2])
        elif match.home_team == "EUA":
            # Caso 2: Queda acentuada na odd dos EUA (Smart Money)
            # Abertura
            h1 = OddsHistory(match_id=match.id, market_type="EUA", odd_value=2.20, recorded_at=datetime.utcnow() - timedelta(hours=8))
            # Atual
            h2 = OddsHistory(match_id=match.id, market_type="EUA", odd_value=1.85, recorded_at=datetime.utcnow()) # Queda de 15.9%!
            db.add_all([h1, h2])
        elif match.home_team == "Portugal":
            # Caso 3: Flutuação normal (Sem Smart Money)
            h1 = OddsHistory(match_id=match.id, market_type="Portugal", odd_value=2.60, recorded_at=datetime.utcnow() - timedelta(hours=6))
            h2 = OddsHistory(match_id=match.id, market_type="Portugal", odd_value=2.55, recorded_at=datetime.utcnow())
            db.add_all([h1, h2])
        else:
            # Caso 4: Odds simples
            h1 = OddsHistory(match_id=match.id, market_type="Brasil", odd_value=1.50, recorded_at=datetime.utcnow())
            db.add(h1)
            
        db.commit()
        
    print("✅ Sementeira concluída com sucesso!")
    db.close()

if __name__ == "__main__":
    from datetime import timedelta
    seed_data()
