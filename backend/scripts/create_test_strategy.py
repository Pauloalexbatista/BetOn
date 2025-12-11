"""
Create test strategy via API
"""
import requests
import json

# Strategy data
strategy = {
    "name": "Top 4 Portugal - Vitórias",
    "description": "Estratégia focada nos 4 grandes de Portugal quando jogam para ganhar",
    "strategy_type": "single",
    "target_outcome": "win",
    "is_active": True,
    "teams": ["Benfica", "Porto", "Sporting", "Braga", "SC Braga"],
    "leagues": ["Primeira Liga"]
}

# Create strategy
response = requests.post(
    "http://localhost:8000/api/strategies/",
    json=strategy
)

if response.status_code in [200, 201]:
    result = response.json()
    print(f"✅ Estratégia criada com sucesso!")
    print(f"   ID: {result['id']}")
    print(f"   Nome: {result['name']}")
    print(f"   Tipo: {result['strategy_type']}")
    print(f"   Equipas: {len(result.get('teams', []))}")
    print(f"\n🔗 Ver estratégia:")
    print(f"   http://localhost:3000/strategies/{result['id']}")
else:
    print(f"❌ Erro ao criar estratégia: {response.status_code}")
    print(response.text)
