"use client";

import { useState, useEffect } from "react";
import Link from "next/link"; // Next.js Link
import { ArrowRightIcon, ArrowPathIcon, TrashIcon } from "@heroicons/react/24/solid";
// import SystemStatusWidget from "@/components/shared/SystemStatusWidget";

export default function Home() {
    const [signals, setSignals] = useState<any[]>([]);
    const [updating, setUpdating] = useState(false);
    const [clearingSignals, setClearingSignals] = useState(false);

    const fetchSignals = () => {
        fetch("http://localhost:8000/api/signals/today")
            .then(res => res.json())
            .then(data => {
                // Filter out duplicates based on match + strategy
                const seen = new Set();
                const unique = (data.signals || []).filter((signal: any) => {
                    const key = `${signal.home_team}-${signal.away_team}-${signal.strategy_name}`;
                    if (seen.has(key)) return false;
                    seen.add(key);
                    return true;
                });
                setSignals(unique);
            })
            .catch(err => console.error("Failed to load signals", err));
    };

    useEffect(() => {
        fetchSignals();
    }, []);

    const handleUpdate = async () => {
        setUpdating(true);
        try {
            await fetch("http://localhost:8000/api/system/update", { method: "POST" });
            alert("Update started! Check back in a minute.");
        } catch (e) {
            alert("Update failed.");
        } finally {
            setTimeout(() => setUpdating(false), 2000); // Reset button state
        }
    };

    const handleClearSignals = async () => {
        if (!confirm("Limpar todas as oportunidades? Esta ação não pode ser desfeita.")) {
            return;
        }

        setClearingSignals(true);
        try {
            const res = await fetch("http://localhost:8000/api/signals/clear", { method: "POST" });
            if (res.ok) {
                setSignals([]);
                alert("Oportunidades limpas com sucesso!");
            } else {
                alert("Erro ao limpar oportunidades");
            }
        } catch (e) {
            alert("Erro ao limpar oportunidades");
        } finally {
            setClearingSignals(false);
        }
    };

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <div className="container mx-auto px-4 py-8">
                {/* Header Section */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-bold text-white">
                            Bet<span className="text-primary-500">On</span>
                        </h1>
                        <p className="text-slate-400">Sistema de Automação de Apostas</p>
                    </div>

                    {/* Update button DISABLED - use Data Quality page instead */}
                    <div className="text-right">
                        <p className="text-xs text-slate-500 mb-1">Updates via Data Quality →</p>
                        <button
                            disabled
                            className="flex items-center gap-2 px-4 py-2 rounded font-bold text-slate-500 bg-slate-700 cursor-not-allowed opacity-50"
                            title="Desativado - Use o dashboard Data Quality para updates"
                        >
                            <ArrowPathIcon className="h-5 w-5" />
                            Update Games (Disabled)
                        </button>
                    </div>
                </div>

                {/* Status Cards - MOVED TO TOP */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                        <h3 className="text-slate-400 text-sm font-medium mb-2">Status do Sistema</h3>
                        <p className="text-2xl font-bold text-green-500">✓ Online</p>
                    </div>

                    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                        <h3 className="text-slate-400 text-sm font-medium mb-2">Modo</h3>
                        <p className="text-2xl font-bold text-yellow-500">Paper Trading</p>
                    </div>

                    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                        <h3 className="text-slate-400 text-sm font-medium mb-2">Banca</h3>
                        <p className="text-2xl font-bold text-white">€1,000.00</p>
                    </div>
                </div>

                {/* Quick Links - AFTER STATUS */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
                    {/* 1. Calendário */}
                    <a
                        href="/calendar"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">📅</div>
                        <h3 className="font-semibold">Calendário</h3>
                    </a>

                    {/* 2. Jogos */}
                    <a
                        href="/matches"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">⚽</div>
                        <h3 className="font-semibold">Jogos</h3>
                    </a>

                    {/* 3. Análises de Mercados */}
                    <a
                        href="/analysis/markets"
                        className="bg-gradient-to-br from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg p-6 text-center transition-all shadow-lg hover:shadow-emerald-500/50"
                    >
                        <div className="text-3xl mb-2">📈</div>
                        <h3 className="font-semibold">Análises de Mercados</h3>
                        <p className="text-xs mt-1 opacity-90">Over/Under, BTTS, 1X2</p>
                    </a>

                    {/* 4. Análise Pareto */}
                    <a
                        href="/analysis/pareto"
                        className="bg-gradient-to-br from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-lg p-6 text-center transition-all shadow-lg hover:shadow-purple-500/50"
                    >
                        <div className="text-3xl mb-2">📊</div>
                        <h3 className="font-semibold">Análise Pareto</h3>
                        <p className="text-xs mt-1 opacity-90">Top 20% Equipas</p>
                    </a>

                    {/* 5. Mercados (duplicado? - mantido para legacy) */}
                    {/* Removido para evitar duplicação */}

                    {/* 6. Pulso */}
                    <a
                        href="/analysis/league"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">💓</div>
                        <h3 className="font-semibold">Pulso</h3>
                    </a>

                    {/* 7. Estratégias */}
                    <a
                        href="/strategies"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">🧠</div>
                        <h3 className="font-semibold">Estratégias</h3>
                    </a>

                    {/* 8. Apostas */}
                    <a
                        href="/bets"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">🎯</div>
                        <h3 className="font-semibold">Apostas</h3>
                    </a>

                    {/* 9. Banca */}
                    <a
                        href="/bankroll"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">💰</div>
                        <h3 className="font-semibold">Gestão de Banca</h3>
                    </a>

                    {/* Data Quality - Extra (mantido) */}
                    <a
                        href="/data-quality"
                        className="bg-gradient-to-br from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-lg p-6 text-center transition-all shadow-lg hover:shadow-blue-500/50"
                    >
                        <div className="text-3xl mb-2">🔍</div>
                        <h3 className="font-semibold">Data Quality</h3>
                        <p className="text-xs mt-1 opacity-90">Monitor de Dados</p>
                    </a>
                </div>

                {/* Signals Feed - MOVED TO BOTTOM */}
                {signals.length > 0 && (
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                                <h2 className="text-2xl font-bold text-white">⚡ Oportunidades do Dia</h2>
                                <span className="bg-yellow-500 text-black text-xs font-bold px-2 py-1 rounded-full animate-pulse">
                                    {signals.length}
                                </span>
                            </div>

                            <button
                                onClick={handleClearSignals}
                                disabled={clearingSignals}
                                className={`flex items-center gap-2 px-4 py-2 rounded font-bold text-white transition-all ${clearingSignals
                                    ? "bg-slate-600 cursor-not-allowed"
                                    : "bg-red-600 hover:bg-red-500"
                                    }`}
                            >
                                <TrashIcon className="h-5 w-5" />
                                {clearingSignals ? "Limpando..." : "Limpar Todas"}
                            </button>
                        </div>
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {signals.map((signal, idx) => (
                                <div key={idx} className="bg-slate-800 border-l-4 border-yellow-500 p-4 rounded shadow-lg hover:bg-slate-750 transition-colors">
                                    <div className="flex justify-between items-start mb-2">
                                        <span className="text-xs font-mono text-slate-400">{new Date(signal.match_date).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })}</span>
                                        <span className="text-xs bg-slate-900 text-yellow-500 px-2 py-1 rounded font-bold">{signal.strategy_name}</span>
                                    </div>
                                    <h3 className="font-bold text-lg mb-1">{signal.home_team} vs {signal.away_team}</h3>
                                    <div className="flex justify-between items-center mt-3">
                                        <span className="text-sm text-slate-300">Target: <strong className="text-white">{signal.target_outcome}</strong></span>
                                        <Link
                                            href={`/matches?search=${encodeURIComponent(signal.home_team)}`}
                                            className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded"
                                        >
                                            Analisar →
                                        </Link>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Footer */}
                <div className="mt-12 text-center text-slate-500 text-sm">
                    <p>BetOn v0.1.0 - Sistema em desenvolvimento</p>
                    <p className="mt-2">⚠️ Apostar responsavelmente. Nunca aposte mais do que pode perder.</p>
                </div>
            </div>
        </main >
    )
}
