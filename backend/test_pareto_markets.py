"""
Test script for enhanced Pareto analysis
"""
from analysis.pareto_analyzer import ParetoAnalyzer
import json

analyzer = ParetoAnalyzer()

print("=" * 60)
print("📊 ENHANCED PARETO ANALYSIS TEST")
print("=" * 60)

# Get available seasons
seasons = analyzer.get_available_seasons()
print(f"\n📅 Épocas disponíveis: {len(seasons)}")
for season in seasons:
    print(f"   - {season}")

# Analyze all-time markets
print("\n" + "=" * 60)
print("📈 MERCADOS - HISTÓRICO COMPLETO")
print("=" * 60)

markets_all = analyzer.analyze_betting_markets()
print(f"\nTotal de jogos: {markets_all['total_matches']}")

print("\n🎯 Over/Under:")
for market, data in markets_all['markets']['over_under'].items():
    print(f"   {market}: {data['percentage']}% ({data['count']} jogos)")

print("\n⚽ BTTS (Both Teams To Score):")
for market, data in markets_all['markets']['btts'].items():
    print(f"   {market}: {data['percentage']}% ({data['count']} jogos)")

print("\n🏆 1X2:")
for market, data in markets_all['markets']['1x2'].items():
    print(f"   {market}: {data['percentage']}% ({data['count']} jogos)")

# Analyze current season if available
if seasons:
    current_season = seasons[0]
    print("\n" + "=" * 60)
    print(f"📈 MERCADOS - ÉPOCA ATUAL ({current_season})")
    print("=" * 60)
    
    markets_current = analyzer.analyze_betting_markets(season=current_season)
    print(f"\nTotal de jogos: {markets_current['total_matches']}")
    
    print("\n🎯 Over/Under:")
    for market, data in markets_current['markets']['over_under'].items():
        print(f"   {market}: {data['percentage']}% ({data['count']} jogos)")
    
    print("\n⚽ BTTS:")
    for market, data in markets_current['markets']['btts'].items():
        print(f"   {market}: {data['percentage']}% ({data['count']} jogos)")
    
    print("\n🏆 1X2:")
    for market, data in markets_current['markets']['1x2'].items():
        print(f"   {market}: {data['percentage']}% ({data['count']} jogos)")

print("\n" + "=" * 60)
print("✅ Test completed!")
print("=" * 60)
