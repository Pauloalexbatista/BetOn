import os
import sys
from datetime import datetime

# Adiciona o diretório backend ao path para importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import SessionLocal
from database.models import Match, SimulatedBet

def run_test():
    print("🧪 A iniciar teste de simulação de apostas no SQLite...")
    
    db = SessionLocal()
    
    # 1. Obter a primeira partida
    match = db.query(Match).first()
    if not match:
        print("❌ Nenhuma partida encontrada na base de dados! Executa o seed script primeiro.")
        return
        
    print(f"🔹 Jogo selecionado para teste: {match.home_team} vs {match.away_team} (ID: {match.id})")
    
    # 2. Criar uma Aposta Simulada (SimulatedBet)
    bet = SimulatedBet(
        match_id=match.id,
        strategy_name="Ambas Marcam SIM",
        stake=10.0,
        odd_taken=2.10,
        status="Pendente"
    )
    db.add(bet)
    db.commit()
    db.refresh(bet)
    
    print(f"✅ Aposta colocada no SQLite com Sucesso!")
    print(f"   👉 Aposta ID: {bet.id} | Jogo ID: {bet.match_id} | Stake: €{bet.stake} | Odd: {bet.odd_taken} | Estado: {bet.status}")
    
    # 3. Listar todas as apostas ativas para mostrar que está guardada
    bets = db.query(SimulatedBet).all()
    print(f"\n📋 Lista atual de apostas no SQLite (Total: {len(bets)}):")
    for b in bets:
        print(f"   • ID: {b.id} | Jogo ID: {b.match_id} | Stake: €{b.stake} | Estado: {b.status}")
        
    # 4. Simular a resolução da aposta como GANHA (Won)
    print("\n⚡ A simular a resolução da aposta (Resultado: Ganha)...")
    bet.status = "Ganha"
    db.commit()
    
    # 5. Ler de volta do banco para confirmar a persistência definitiva
    db.refresh(bet)
    print(f"🎉 Aposta atualizada no SQLite com Sucesso!")
    print(f"   👉 Aposta ID: {bet.id} | Novo Estado: {bet.status} | Retorno Estimado: €{round(bet.stake * bet.odd_taken, 2)}")
    
    db.close()
    print("\n🏁 Fim do teste de persistência SQLite! Tudo 100% calibrado.")

if __name__ == "__main__":
    run_test()
