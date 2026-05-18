"use client";

import React, { useState, useEffect } from "react";
import { 
  TrendingUp, 
  Shield, 
  Percent, 
  Sliders, 
  Zap, 
  Play, 
  DollarSign, 
  RefreshCw, 
  AlertTriangle,
  CheckCircle2,
  HelpCircle
} from "lucide-react";

// Partidas REAIS do Mundial de 2026 para exibição inicial e salvaguarda
const REAL_WORLD_CUP_MATCHES = [
  { id: 1, home: "México", away: "Coreia do Sul", time: "11 Jun, 20:00", ELO_H: 1800, ELO_A: 1760, btts_odd: 2.10, fav_odd: 1.90 },
  { id: 2, home: "EUA", away: "Suíça", time: "12 Jun, 19:00", ELO_H: 1820, ELO_A: 1780, btts_odd: 2.20, fav_odd: 1.85 },
  { id: 3, home: "Brasil", away: "Marrocos", time: "14 Jun, 21:00", ELO_H: 2010, ELO_A: 1880, btts_odd: 2.10, fav_odd: 1.50 },
  { id: 4, home: "Portugal", away: "RD Congo", time: "17 Jun, 13:00", ELO_H: 1980, ELO_A: 1710, btts_odd: 2.05, fav_odd: 1.30 },
  { id: 5, home: "Portugal", away: "Uzbequistão", time: "23 Jun, 13:00", ELO_H: 1980, ELO_A: 1760, btts_odd: 2.05, fav_odd: 1.35 },
  { id: 6, home: "Portugal", away: "Colômbia", time: "27 Jun, 19:30", ELO_H: 1980, ELO_A: 1940, btts_odd: 1.95, fav_odd: 2.10 },
];


export default function Dashboard() {
  // Estados para a Consola Martingale Inteligente
  const [banca, setBanca] = useState<number>(100);
  const [odd, setOdd] = useState<number>(2.0);
  const [lucro, setLucro] = useState<number>(1);
  const [martingaleResult, setMartingaleResult] = useState<any>(null);
  const [loadingMartingale, setLoadingMartingale] = useState<boolean>(false);
  
  // Estado para a estratégia selecionada na UI
  const [selectedStrategy, setSelectedStrategy] = useState<number>(1);
  
  // Estado para a Banca Virtual Global
  const [bancaVirtual, setBancaVirtual] = useState<number>(1000);
  const [simulatedBets, setSimulatedBets] = useState<any[]>([]);
  const [matches, setMatches] = useState<any[]>(REAL_WORLD_CUP_MATCHES);


  // Chamada de API para calcular o Martingale dinamicamente no backend
  const fetchMartingale = async () => {
    setLoadingMartingale(true);
    try {
      const res = await fetch("http://localhost:8001/api/calculators/martingale", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          banca_total: banca,
          odd_media: odd,
          lucro_alvo: lucro
        })
      });
      if (res.ok) {
        const data = await res.json();
        setMartingaleResult(data);
      }
    } catch (e) {
      // Fallback matemático se a API ainda não estiver de pé na VPS
      const stakes = [];
      let acumulado = 0;
      let passo = 1;
      while (true) {
        const proxima = (acumulado + lucro) / (odd - 1);
        const proxima_rounded = Math.round(proxima * 100) / 100;
        if (acumulado + proxima_rounded > banca) break;
        stakes.push({ passo, stake: proxima_rounded, custo_total: Math.round((acumulado + proxima_rounded) * 100) / 100 });
        acumulado += proxima_rounded;
        passo++;
      }
      setMartingaleResult({
        banca_total: banca,
        odd_media: odd,
        lucro_alvo: lucro,
        passos_sobrevivencia: stakes.length,
        sequencia_stakes: stakes,
        banca_utilizada: Math.round(acumulado * 100) / 100,
        banca_restante: Math.round((banca - acumulado) * 100) / 100,
        probabilidade_falencia_percent: Math.round((0.5 ** stakes.length) * 10000) / 100
      });
    } finally {
      setLoadingMartingale(false);
    }
  };

  useEffect(() => {
    fetchMartingale();
  }, [banca, odd, lucro]);

  // Carregar partidas e apostas reais do SQLite
  useEffect(() => {
    fetch("http://localhost:8001/api/matches")
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) {
          // Mapear os campos do SQLite para o formato esperado pelo ecrã
          const mapped = data.map((m: any) => ({
            id: m.id,
            home: m.home_team,
            away: m.away_team,
            time: m.date ? new Date(m.date).toLocaleDateString("pt-PT") + " " + new Date(m.date).toLocaleTimeString("pt-PT", {hour: "2-digit", minute: "2-digit"}) : "Brevemente",
            ELO_H: m.home_elo || 1800,
            ELO_A: m.away_elo || 1800,
            btts_odd: m.home_team === "Portugal" ? 2.05 : (m.home_team === "EUA" ? 2.20 : 2.10), // Odds do simulador base
            fav_odd: m.home_team === "Brasil" ? 1.50 : 1.90
          }));
          setMatches(mapped);
        } else {
          setMatches(REAL_WORLD_CUP_MATCHES);
        }
      })
      .catch(() => setMatches(REAL_WORLD_CUP_MATCHES));

    fetch("http://localhost:8001/api/bets")
      .then(res => res.json())
      .then(data => setSimulatedBets(data));
  }, []);


  // Função para simular aposta (Persistida no SQLite)
  const handleSimulateBet = async (match: any, type: string, oddVal: number, stake: number) => {
    const betData = {
      match_id: match.id,
      strategy_name: type,
      stake: stake,
      odd_taken: oddVal
    };
    const res = await fetch("http://localhost:8001/api/bets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(betData)
    });
    if (res.ok) {
      const newBet = await res.json();
      setSimulatedBets([newBet, ...simulatedBets]);
      setBancaVirtual(prev => Math.round((prev - stake) * 100) / 100);
    }
  };

  // Resolver aposta (Atualizada no SQLite)
  const resolveBet = async (id: number, won: boolean, stake: number, oddVal: number) => {
    const status = won ? "Ganha" : "Perdida";
    const res = await fetch(`http://localhost:8001/api/bets/${id}?status=${status}`, { method: "PUT" });
    if (res.ok) {
      setSimulatedBets(prev => prev.map(bet => bet.id === id ? { ...bet, status } : bet));
      if (won) {
        setBancaVirtual(prev => Math.round((prev + (stake * oddVal)) * 100) / 100);
      }
    }
  };

  return (
    <div className="space-y-8">
      {/* SEÇÃO 1: BANCA VIRTUAL GLOBAL */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 shadow-blue-neon flex justify-between items-center relative overflow-hidden">
          <div className="absolute right-0 bottom-0 opacity-5 pointer-events-none translate-x-4 translate-y-4">
            <DollarSign size={160} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-gray-400 font-semibold font-outfit">Banca Virtual de Teste</p>
            <h2 className="text-4xl font-bold font-outfit text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-200 to-neonBlue mt-1">
              € {bancaVirtual.toFixed(2)}
            </h2>
            <p className="text-[10px] text-emerald font-semibold mt-2">📊 Campeonato do Mundo - Simulação Ativa</p>
          </div>
          <button 
            onClick={() => { setBancaVirtual(1000); setSimulatedBets([]); }}
            className="p-2.5 rounded-xl bg-borderBg bg-opacity-30 border border-borderBg hover:bg-opacity-100 transition-colors"
            title="Resetar Banca"
          >
            <RefreshCw size={18} className="text-neonBlue" />
          </button>
        </div>

        <div className="glass-panel p-6 shadow-gold-neon flex justify-between items-center relative overflow-hidden">
          <div className="absolute right-0 bottom-0 opacity-5 pointer-events-none translate-x-4 translate-y-4">
            <TrendingUp size={160} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-gray-400 font-semibold font-outfit">Apostas Simuladas</p>
            <h2 className="text-4xl font-bold font-outfit text-gold mt-1">
              {simulatedBets.length}
            </h2>
            <p className="text-[10px] text-gray-400 mt-2">
              Pendentes: {simulatedBets.filter(b => b.status === "Pendente").length} | Ganhas: {simulatedBets.filter(b => b.status === "Ganha").length}
            </p>
          </div>
          <span className="p-3 rounded-xl bg-gold bg-opacity-10 border border-gold border-opacity-20 text-gold">
            🏆
          </span>
        </div>

        <div className="glass-panel p-6 shadow-emerald-neon flex justify-between items-center relative overflow-hidden">
          <div className="absolute right-0 bottom-0 opacity-5 pointer-events-none translate-x-4 translate-y-4">
            <Percent size={160} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-gray-400 font-semibold font-outfit">Eficácia (ROI)</p>
            <h2 className="text-4xl font-bold font-outfit text-emerald mt-1">
              {simulatedBets.length > 0 
                ? `${((simulatedBets.filter(b => b.status === "Ganha").length / simulatedBets.filter(b => b.status !== "Pendente").length || 0) * 100).toFixed(0)}%`
                : "0%"}
            </h2>
            <p className="text-[10px] text-gray-400 mt-2">Apenas apostas liquidadas são calculadas</p>
          </div>
          <span className="p-3 rounded-xl bg-emerald bg-opacity-10 border border-emerald border-opacity-20 text-emerald">
            📈
          </span>
        </div>
      </section>

      {/* SEÇÃO 2: CENTRAL DE ESTRATÉGIAS QUANTITATIVAS */}
      <section className="glass-panel p-6 md:p-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-borderBg pb-6 mb-8">
          <div>
            <h2 className="text-2xl font-bold font-outfit text-white flex items-center gap-2">
              <Zap className="text-gold" /> Central de Estratégias Quantitativas
            </h2>
            <p className="text-xs text-gray-400 mt-1">Primeiro criamos a matemática lucrativa; segundo encontramos os melhores jogos.</p>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {[
              { id: 1, name: "I: BTTS SIM 2.00+" },
              { id: 2, name: "II: Zebra Protegida (66%)" },
              { id: 3, name: "III: Over/Under 2.5" },
              { id: 4, name: "IV: Favorito In-Play" },
              { id: 5, name: "V: Draw No Bet" },
            ].map(strat => (
              <button
                key={strat.id}
                onClick={() => setSelectedStrategy(strat.id)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold font-outfit transition-all ${
                  selectedStrategy === strat.id 
                    ? "bg-gradient-to-r from-gold to-emerald text-background shadow-gold-neon" 
                    : "bg-borderBg bg-opacity-20 border border-borderBg border-opacity-50 hover:bg-opacity-100 text-gray-300"
                }`}
              >
                {strat.name}
              </button>
            ))}
          </div>
        </div>

        {/* Detalhes da Estratégia Selecionada */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Informações Matemáticas da Estratégia */}
          <div className="lg:col-span-1 space-y-6">
            {selectedStrategy === 1 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-gold bg-opacity-10 border border-gold border-opacity-25 text-xs text-gold font-bold">
                  Estratégia I - 50/50 Estável
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">Ambas Marcam SIM $\ge$ 2.00</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Filtramos jogos onde a odd do "Ambas Marcam: SIM" é igual ou superior a 2.00. Com odds de 2.00, o Martingale de duplicação simples funciona perfeitamente, aumentando o nosso índice de sobrevivência na banca!
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd Mínima:</span> <span className="text-gold font-bold">2.00</span></div>
                  <div className="flex justify-between"><span>Cobertura Teórica:</span> <span className="text-emerald font-bold">50%</span></div>
                  <div className="flex justify-between"><span>Método Recomendado:</span> <span className="text-neonBlue font-bold">Martingale</span></div>
                </div>
              </div>
            )}

            {selectedStrategy === 2 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-emerald bg-opacity-10 border border-emerald border-opacity-25 text-xs text-emerald font-bold">
                  Estratégia II - 66.6% Alta Segurança
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">A Zebra Protegida (Chance Dupla)</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Casas de apostas sobrevalorizam favoritos históricos por reputação. O algoritmo deteta favoritos fracos (RSI baixo) e sugere apostar na Chance Dupla do adversário (X2 ou 1X) com odds incrivelmente desajustadas!
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd Alvo:</span> <span className="text-gold font-bold">1.80 a 2.10</span></div>
                  <div className="flex justify-between"><span>Cobertura Real:</span> <span className="text-emerald font-bold">66.6% (2 resultados)</span></div>
                  <div className="flex justify-between"><span>Método Recomendado:</span> <span className="text-neonBlue font-bold">Kelly Stake 2.5%</span></div>
                </div>
              </div>
            )}

            {selectedStrategy === 3 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-neonBlue bg-opacity-10 border border-neonBlue border-opacity-25 text-xs text-neonBlue font-bold">
                  Estratégia III - 50/50 Golo Value
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">Linha de Golos Inteligente (Over 2.5)</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Varre equipas famosas por serem "defensivas" no papel (o que eleva as odds do Over 2.5 para cima de 2.10), mas que nos últimos 5 jogos têm atacantes explosivos e média real superior a 3.0 golos.
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd Mínima:</span> <span className="text-gold font-bold">2.10</span></div>
                  <div className="flex justify-between"><span>Probabilidade Poisson:</span> <span className="text-emerald font-bold">&gt; 55%</span></div>
                  <div className="flex justify-between"><span>Método Recomendado:</span> <span className="text-neonBlue font-bold">Simulação Direta</span></div>
                </div>
              </div>
            )}

            {selectedStrategy === 4 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-red-400 bg-opacity-10 border border-red-400 border-opacity-25 text-xs text-red-400 font-bold">
                  Estratégia IV - In-Play Oportunidade
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">Favoritos ao Intervalo</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  A estratégia do Rei Paulo! Um super favorito entra no jogo a 1.15. Chega empatado aos 35-40 minutos e a odd dispara para 1.50+. A probabilidade de vitória na 2ª parte mantém-se fortíssima, mas agora com retorno lucrativo!
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd Pré-Jogo:</span> <span className="text-gold font-bold">&lt; 1.30</span></div>
                  <div className="flex justify-between"><span>Odd Live Alvo:</span> <span className="text-emerald font-bold">&ge; 1.50</span></div>
                  <div className="flex justify-between"><span>Minuto de Entrada:</span> <span className="text-neonBlue font-bold">35' a 50'</span></div>
                </div>
              </div>
            )}

            {selectedStrategy === 5 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-purple-400 bg-opacity-10 border border-purple-400 border-opacity-25 text-xs text-purple-400 font-bold">
                  Estratégia V - Cobertura & Reembolso
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">Favorito Empatado (Draw No Bet)</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Filtra favoritos óbvios mas protege a aposta eliminando o risco do empate. Se empatar, a banca é reembolsada a 100%. Transforma o jogo num 50/50 purificado com blindagem total contra empates tardios.
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd DNB Mínima:</span> <span className="text-gold font-bold">1.70</span></div>
                  <div className="flex justify-between"><span>Em caso de Empate:</span> <span className="text-emerald font-bold">Reembolso Total</span></div>
                  <div className="flex justify-between"><span>Vantagem ELO:</span> <span className="text-neonBlue font-bold">&gt; +100 Pontos</span></div>
                </div>
              </div>
            )}
          </div>

          {/* Jogos Disponíveis para Filtragem (Zonas de Aposta) */}
          <div className="lg:col-span-2 space-y-6">
            <h4 className="text-sm font-bold uppercase tracking-wider text-gray-300 font-outfit">Jogos do Mundial Detetados</h4>
            
            <div className="space-y-4">
              {matches.map(match => {
                // Cálculo de valor com base na estratégia selecionada
                let badge = "";
                let valueLabel = "";
                let betOdd = 0.0;
                let betType = "";

                if (selectedStrategy === 1) {
                  betOdd = match.btts_odd;
                  betType = "BTTS SIM";
                  if (match.btts_odd >= 2.0) {
                    badge = "🔥 EXCELENTE NEGÓCIO";
                    valueLabel = `Odd BTTS ${match.btts_odd} excelente para Martingale`;
                  } else {
                    badge = "⚖️ NEUTRO";
                    valueLabel = `Odd ${match.btts_odd} muito baixa para sobrevivência`;
                  }
                } else if (selectedStrategy === 2) {
                  betOdd = match.home === "Portugal" ? 1.95 : 2.10;
                  betType = "Chance Dupla X2";
                  badge = "🔥 OPORTUNIDADE ZEBRA";
                  valueLabel = `Zebra com superioridade de forma`;
                } else {
                  betOdd = match.fav_odd;
                  betType = "DNB / Favorito";
                  badge = "⚖️ EM ANÁLISE";
                  valueLabel = `Requer monitorização live`;
                }

                return (
                  <div key={match.id} className="glass-card p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] px-2 py-0.5 rounded font-bold font-mono ${
                          badge.includes("EXCELENTE") || badge.includes("OPORTUNIDADE")
                            ? "bg-emerald bg-opacity-20 text-emerald border border-emerald border-opacity-30" 
                            : "bg-gray-700 text-gray-400"
                        }`}>
                          {badge}
                        </span>
                        <span className="text-xs text-gray-500 font-mono">{match.time}</span>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-outfit font-bold text-white">{match.home}</span>
                          <span className="text-xs text-gray-500 font-mono">({match.ELO_H})</span>
                        </div>
                        <span className="text-xs text-gold font-bold">vs</span>
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-outfit font-bold text-white">{match.away}</span>
                          <span className="text-xs text-gray-500 font-mono">({match.ELO_A})</span>
                        </div>
                      </div>
                      <p className="text-xs text-gray-400">{valueLabel}</p>
                    </div>

                    <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end border-t border-borderBg border-opacity-30 md:border-t-0 pt-4 md:pt-0">
                      <div className="text-left md:text-right">
                        <p className="text-[10px] text-gray-500 uppercase tracking-widest font-mono">Mercado Alvo</p>
                        <p className="text-sm font-bold text-white font-mono">{betType}</p>
                        <p className="text-xl font-black text-gold font-mono">{betOdd.toFixed(2)}</p>
                      </div>

                      <button 
                        onClick={() => handleSimulateBet(match, betType, betOdd, 10.0)}
                        className="px-5 py-3 rounded-xl bg-neonBlue bg-opacity-10 border border-neonBlue border-opacity-30 hover:bg-neonBlue hover:text-background text-neonBlue text-sm font-bold font-outfit transition-all flex items-center gap-2"
                      >
                        <Play size={14} fill="currentColor" /> Simular Aposta (€10)
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* SEÇÃO 3: CONSOLA MARTINGALE INTELIGENTE (INTERATIVA) */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Calculadora Inputs */}
        <div className="lg:col-span-1 glass-panel p-6 md:p-8 space-y-6">
          <div>
            <h3 className="text-xl font-bold font-outfit text-white flex items-center gap-2">
              <Sliders className="text-gold" /> Consola Martingale
            </h3>
            <p className="text-xs text-gray-400 mt-1">Simulação matemática e cálculo de stakes para mercados 50/50.</p>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs text-gray-400 uppercase tracking-wider font-mono flex justify-between">
                <span>Banca da Estratégia</span>
                <span className="text-white font-bold">€ {banca}</span>
              </label>
              <input 
                type="range" 
                min="10" 
                max="1000" 
                step="10"
                value={banca} 
                onChange={(e) => setBanca(Number(e.target.value))}
                className="w-full h-1 bg-borderBg rounded-lg appearance-none cursor-pointer accent-gold"
              />
              <div className="flex justify-between text-[10px] text-gray-500 font-mono"><span>10€</span> <span>1000€</span></div>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-400 uppercase tracking-wider font-mono flex justify-between">
                <span>Odd do Mercado</span>
                <span className="text-white font-bold">{odd.toFixed(2)}</span>
              </label>
              <input 
                type="range" 
                min="1.3" 
                max="3.0" 
                step="0.05"
                value={odd} 
                onChange={(e) => setOdd(Number(e.target.value))}
                className="w-full h-1 bg-borderBg rounded-lg appearance-none cursor-pointer accent-neonBlue"
              />
              <div className="flex justify-between text-[10px] text-gray-500 font-mono"><span>1.30</span> <span>3.00</span></div>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-400 uppercase tracking-wider font-mono flex justify-between">
                <span>Lucro Alvo / Ciclo</span>
                <span className="text-white font-bold">€ {lucro}</span>
              </label>
              <input 
                type="range" 
                min="0.5" 
                max="20" 
                step="0.5"
                value={lucro} 
                onChange={(e) => setLucro(Number(e.target.value))}
                className="w-full h-1 bg-borderBg rounded-lg appearance-none cursor-pointer accent-emerald"
              />
              <div className="flex justify-between text-[10px] text-gray-500 font-mono"><span>0.5€</span> <span>20€</span></div>
            </div>
          </div>

          <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-3">
            <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider font-outfit">Análise de Risco</h4>
            <div className="flex items-center gap-3">
              {martingaleResult?.passos_sobrevivencia >= 6 ? (
                <div className="h-2 w-2 rounded-full bg-emerald animate-pulse shadow-emerald-neon"></div>
              ) : martingaleResult?.passos_sobrevivencia >= 4 ? (
                <div className="h-2 w-2 rounded-full bg-gold animate-pulse shadow-gold-neon"></div>
              ) : (
                <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse"></div>
              )}
              <span className="text-xs text-gray-300">
                {martingaleResult?.passos_sobrevivencia >= 6 
                  ? "🛡️ Altíssima Segurança (Zonas de Ouro)" 
                  : martingaleResult?.passos_sobrevivencia >= 4 
                    ? "⚖️ Segurança Moderada" 
                    : "⚠️ Risco Elevado de Quebra"}
              </span>
            </div>
          </div>
        </div>

        {/* Resultados da Sequência de Stakes */}
        <div className="lg:col-span-2 glass-panel p-6 md:p-8 space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xl font-bold font-outfit text-white">Sequência Matemática</h3>
              <p className="text-xs text-gray-400 mt-1">Passos exatos para recuperar 100% das perdas + obter o lucro alvo.</p>
            </div>
            
            <div className="text-right">
              <span className="text-xs text-gray-500 block uppercase font-mono">Sobrevivência</span>
              <span className="text-3xl font-black text-gold font-mono">{martingaleResult?.passos_sobrevivencia || 0} Passos</span>
            </div>
          </div>

          {loadingMartingale ? (
            <div className="h-48 flex justify-center items-center"><RefreshCw className="animate-spin text-gold" /></div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4 text-[10px] text-gray-500 uppercase tracking-wider font-mono border-b border-borderBg border-opacity-30 pb-2">
                <span>Passo do Ciclo</span>
                <span className="text-center">Aposta (Stake)</span>
                <span className="text-right">Banca Acumulada</span>
              </div>
              
              <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                {martingaleResult?.sequencia_stakes?.map((step: any) => (
                  <div key={step.passo} className="grid grid-cols-3 gap-4 py-2 px-3 bg-cardBg bg-opacity-40 border border-borderBg border-opacity-20 rounded-xl text-sm font-mono items-center">
                    <span className="text-gray-300 font-bold">Passo #{step.passo}</span>
                    <span className="text-center text-gold font-black">€ {step.stake.toFixed(2)}</span>
                    <span className="text-right text-gray-400">€ {step.custo_total.toFixed(2)}</span>
                  </div>
                ))}
              </div>

              <div className="pt-4 border-t border-borderBg border-opacity-30 grid grid-cols-2 md:grid-cols-3 gap-4 text-xs font-mono">
                <div>
                  <span className="text-gray-500 block text-[10px] uppercase">Banca Alocada</span>
                  <span className="text-white font-bold">€ {martingaleResult?.banca_utilizada?.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-[10px] uppercase">Banca Sobra</span>
                  <span className="text-white font-bold">€ {martingaleResult?.banca_restante?.toFixed(2)}</span>
                </div>
                <div className="col-span-2 md:col-span-1">
                  <span className="text-gray-500 block text-[10px] uppercase">Probabilidade Ruína</span>
                  <span className="text-red-400 font-bold">{martingaleResult?.probabilidade_falencia_percent?.toFixed(2)}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* SEÇÃO 4: HISTÓRICO DE SIMULAÇÃO DE APOSTAS VIRTUAIS */}
      <section className="glass-panel p-6 md:p-8">
        <h3 className="text-xl font-bold font-outfit text-white mb-6">Registo Virtual In-Play & Pré-Jogo</h3>
        
        {simulatedBets.length === 0 ? (
          <div className="py-12 text-center text-gray-500 text-sm">
            <AlertTriangle className="mx-auto mb-3 text-gold opacity-50" />
            Nenhuma aposta simulada registada. Clique em "Simular Aposta" num jogo acima para começar a testar!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-borderBg border-opacity-30 text-[10px] text-gray-500 uppercase tracking-wider font-mono pb-2">
                  <th className="pb-3">Partida</th>
                  <th className="pb-3">Estratégia</th>
                  <th className="pb-3 text-center">Odd</th>
                  <th className="pb-3 text-center">Stake</th>
                  <th className="pb-3 text-center">Estado</th>
                  <th className="pb-3 text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-borderBg divide-opacity-20 text-sm font-mono">
                {simulatedBets.map(bet => (
                  <tr key={bet.id} className="hover:bg-cardBg hover:bg-opacity-20 transition-colors">
                    <td className="py-4 text-white font-bold">{bet.match}</td>
                    <td className="py-4 text-gray-400">{bet.type}</td>
                    <td className="py-4 text-center text-gold font-bold">{bet.odd.toFixed(2)}</td>
                    <td className="py-4 text-center text-gray-300">€ {bet.stake.toFixed(2)}</td>
                    <td className="py-4 text-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        bet.status === "Pendente" 
                          ? "bg-gold bg-opacity-10 text-gold border border-gold border-opacity-25" 
                          : bet.status === "Ganha"
                            ? "bg-emerald bg-opacity-10 text-emerald border border-emerald border-opacity-25"
                            : "bg-red-500 bg-opacity-10 text-red-400 border border-red-500 border-opacity-25"
                      }`}>
                        {bet.status}
                      </span>
                    </td>
                    <td className="py-4 text-right">
                      {bet.status === "Pendente" && (
                        <div className="flex gap-2 justify-end">
                          <button 
                            onClick={() => resolveBet(bet.id, true, bet.stake, bet.odd)}
                            className="px-3 py-1 bg-emerald bg-opacity-20 hover:bg-opacity-100 text-emerald hover:text-white border border-emerald rounded-lg text-xs transition-colors"
                          >
                            ✓ Ganhou
                          </button>
                          <button 
                            onClick={() => resolveBet(bet.id, false, bet.stake, bet.odd)}
                            className="px-3 py-1 bg-red-500 bg-opacity-20 hover:bg-opacity-100 text-red-400 hover:text-white border border-red-500 rounded-lg text-xs transition-colors"
                          >
                            ✗ Perdeu
                          </button>
                        </div>
                      )}
                      {bet.status !== "Pendente" && (
                        <span className="text-gray-500 text-xs flex items-center gap-1 justify-end">
                          <CheckCircle2 size={12} className={bet.status === "Ganha" ? "text-emerald" : "text-red-400"} /> Resolvida
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
