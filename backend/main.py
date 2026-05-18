from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
from typing import List, Dict, Optional
from collectors.api_football_client import APIFootballClient
from collectors.the_odds_client import TheOddsClient
from collectors.sync_engine import SyncEngine
from database.database import init_db

# Inicializa a base de dados ao arrancar
init_db()

app = FastAPI(
    title="🏛️ BetOn Backend API",
    description="Motor quantitativo de análise e simulação de apostas para o Campeonato do Mundo",
    version="1.0.0"
)

# Configuração de CORS para permitir comunicação do Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DADOS ---

class MartingaleInput(BaseModel):
    banca_total: float
    odd_media: float
    lucro_alvo: float

class InPlayInput(BaseModel):
    odd_pre_jogo: float
    minuto: int
    resultado_atual: str  # ex: "0-0", "1-1"
    odd_live: float

# --- TABELA DE ELO MOCK (MUNDIAL) ---
# Ratings ELO atualizados das seleções para o Campeonato do Mundo
WORLD_CUP_ELO: Dict[str, int] = {
    "Argentina": 2130,
    "França": 2110,
    "Espanha": 2040,
    "Inglaterra": 2020,
    "Brasil": 2010,
    "Portugal": 2000,
    "Países Baixos": 1960,
    "Bélgica": 1940,
    "Itália": 1920,
    "Alemanha": 1910,
    "Uruguai": 1900,
    "Croácia": 1880,
    "Marrocos": 1850,
    "Colômbia": 1840,
    "Japão": 1820,
    "EUA": 1790,
    "Suíça": 1780,
    "Dinamarca": 1770,
    "Coreia do Sul": 1760,
    "África do Sul": 1650,
}

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Fundações do Império BetOn ativas na VPS!",
        "version": "1.0.0"
    }

@app.get("/api/test/football")
async def test_football():
    client = APIFootballClient()
    data = await client.get_standings(league_id=94, season=2025)
    return {"source": "API-Football", "data": data}

@app.get("/api/test/odds")
async def test_odds():
    client = TheOddsClient()
    data = await client.get_odds(sport="soccer_portugal_primeira_liga")
    return {"source": "The Odds API", "data": data}

@app.post("/api/sync/data")
async def sync_data(league_id: int = 94, season: int = 2025, sport_key: str = "soccer_portugal_primeira_liga"):
    engine = SyncEngine()
    return await engine.sync_data(league_id, season, sport_key)

@app.get("/api/analysis/smart-money")
async def get_smart_money():
    engine = SyncEngine()
    return {"alerts": engine.get_smart_money_alerts()}

from database.models import SimulatedBet
from database.database import SessionLocal

@app.post("/api/bets")
def create_bet(bet_data: dict):
    db = SessionLocal()
    new_bet = SimulatedBet(**bet_data, status="Pendente")
    db.add(new_bet)
    db.commit()
    db.refresh(new_bet)
    return new_bet

@app.get("/api/bets")
def get_bets():
    db = SessionLocal()
    return db.query(SimulatedBet).all()

@app.get("/api/matches")
def get_matches():
    from database.models import Match
    db = SessionLocal()
    return db.query(Match).all()

@app.put("/api/bets/{bet_id}")
def update_bet(bet_id: int, status: str):
    db = SessionLocal()
    bet = db.query(SimulatedBet).filter(SimulatedBet.id == bet_id).first()
    if bet:
        bet.status = status
        db.commit()
    return bet



@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "sqlite_connected"}

@app.post("/api/calculators/martingale")
def calculate_martingale(data: MartingaleInput):
    """
    Calcula dinamicamente a sequência de stakes e o índice de sobrevivência
    para a estratégia Martingale Modificado com base em qualquer odd média.
    """
    banca = data.banca_total
    odd = data.odd_media
    lucro = data.lucro_alvo
    
    if odd <= 1.0:
        raise HTTPException(status_code=400, detail="A odd média deve ser superior a 1.0")
        
    stakes = []
    acumulado = 0.0
    passo = 1
    
    while True:
        # Fórmula exata para recuperar perdas acumuladas (L) + obter lucro alvo (P)
        # Stake_N = (L + P) / (Odd - 1)
        proxima_stake = (acumulado + lucro) / (odd - 1.0)
        proxima_stake = round(proxima_stake, 2)
        
        if acumulado + proxima_stake > banca:
            break
            
        stakes.append({
            "passo": passo,
            "stake": proxima_stake,
            "custo_total": round(acumulado + proxima_stake, 2)
        })
        
        acumulado += proxima_stake
        passo += 1
        
    # Probabilidade teórica de falência baseada na taxa média de acerto do mercado 50/50 (BTTS SIM ~ 50%)
    probabilidade_falencia = round((0.5 ** len(stakes)) * 100, 2) if stakes else 100.0
        
    return {
        "banca_total": banca,
        "odd_media": odd,
        "lucro_alvo": lucro,
        "passos_sobrevivencia": len(stakes),
        "sequencia_stakes": stakes,
        "banca_utilizada": round(acumulado, 2),
        "banca_restante": round(banca - acumulado, 2),
        "probabilidade_falencia_percent": probabilidade_falencia
    }

@app.get("/api/elo/teams")
def get_elo_ratings():
    """Retorna os ratings ELO de todas as seleções do Mundial"""
    return WORLD_CUP_ELO

@app.get("/api/elo/probability")
def get_match_probability(home: str, away: str):
    """
    Calcula a probabilidade matemática exata de um jogo com base no rating ELO.
    Utiliza a curva logística de ELO de futebol com ajuste neutro para o Mundial.
    """
    if home not in WORLD_CUP_ELO or away not in WORLD_CUP_ELO:
        raise HTTPException(
            status_code=404, 
            detail=f"Uma ou ambas as equipas não foram encontradas. Equipas válidas: {list(WORLD_CUP_ELO.keys())}"
        )
        
    elo_home = WORLD_CUP_ELO[home]
    elo_away = WORLD_CUP_ELO[away]
    
    # Fator Atmosfera (Crowd Boost)
    crowd_boost = 0
    hosts = ["EUA", "Canadá", "México"]
    crowd_favorites = ["México", "Argentina", "Brasil"]
    
    if home in hosts: crowd_boost += 150
    if away in hosts: crowd_boost -= 150
    if home in crowd_favorites: crowd_boost += 80
    if away in crowd_favorites: crowd_boost -= 80
    
    # Diferença de ELO ajustada pelo Fator Atmosfera
    diff = (elo_home - elo_away) + crowd_boost
    
    # Função logística padrão do ELO
    prob_home = 1.0 / (1.0 + math.pow(10.0, -diff / 400.0))
    prob_away = 1.0 - prob_home
    
    # O empate no futebol em ELO reduz a probabilidade de vitória de ambos
    draw_prob = 0.26 * (1.0 - abs(prob_home - prob_away))
    
    home_adj = prob_home * (1.0 - draw_prob)
    away_adj = prob_away * (1.0 - draw_prob)
    
    return {
        "match": f"{home} vs {away}",
        "home_team": home,
        "away_team": away,
        "home_elo": elo_home,
        "away_elo": elo_away,
        "crowd_boost_applied": crowd_boost,
        "probabilities": {
            "home_win": round(home_adj * 100, 2),
            "draw": round(draw_prob * 100, 2),
            "away_win": round(away_adj * 100, 2)
        }
    }

@app.post("/api/signals/inplay")
def check_inplay_signal(data: InPlayInput):
    """
    Analisa se um jogo ao vivo (In-Play) ativou a nossa estratégia premium de
    'Favoritos ao Intervalo' proposta pelo Rei Paulo.
    """
    # Critério: Super favorito pré-jogo (odd < 1.30)
    e_super_favorito = data.odd_pre_jogo < 1.30
    
    # Critério: Jogo empatado
    placar = data.resultado_atual.split("-")
    e_empate = len(placar) == 2 and placar[0].strip() == placar[1].strip()
    
    # Critério: Minuto de jogo avançado (30+ minutos ou intervalo)
    tempo_adequado = data.minuto >= 30 and data.minuto <= 60
    
    # Critério: Odd live disparou para o limiar lucrativo (>= 1.50)
    odd_lucrativa = data.odd_live >= 1.50
    
    alertar = e_super_favorito and e_empate and tempo_adequado and odd_lucrativa
    
    return {
        "dados_inseridos": data,
        "verificacoes": {
            "e_super_favorito_pre_jogo": e_super_favorito,
            "e_empate_atualmente": e_empate,
            "minuto_adequado": tempo_adequado,
            "odd_live_lucrativa": odd_lucrativa
        },
        "sinal_compra": alertar,
        "mensagem": "🚨 ALERTA LIVE: Oportunidade de Ouro detetada! Odd subiu de valor!" if alertar else "⚖️ Sem sinal. Condições não preenchidas."
    }
