"use client";

import { useState, useEffect } from "react";
import Link from "next/link"; // Next.js Link
import { ArrowRightIcon, ArrowPathIcon } from "@heroicons/react/24/solid";
// import SystemStatusWidget from "@/components/shared/SystemStatusWidget";

export default function Home() {
    const [signals, setSignals] = useState<any[]>([]);
    const [updating, setUpdating] = useState(false);

    useEffect(() => {
        // Fetch Daily Signals
        fetch("http://localhost:8000/api/signals/today")
            .then(res => res.json())
            .then(data => setSignals(data.signals || []))
            .catch(err => console.error("Failed to load signals", err));
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

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <div className="container mx-auto px-4 py-8">
                {/* Header Section */}
                <div className="flex justify-between items-center mb-12">
                    <div>
                        <h1 className="text-4xl font-bold text-white">
                            Bet<span className="text-primary-500">On</span>
                        </h1>
                        <p className="text-slate-400">Sistema de Automação de Apostas</p>
                    </div>

                    <button
                        onClick={handleUpdate}
                        disabled={updating}
                        className={`flex items-center gap-2 px-4 py-2 rounded font-bold text-white transition-all ${updating ? "bg-slate-600 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-500 shadow-lg hover:shadow-blue-500/20"
                            }`}
                    >
                        <ArrowPathIcon className={`h-5 w-5 ${updating ? "animate-spin" : ""}`} />
                        {updating ? "Updating..." : "Update Games"}
                    </button>
                </div>

                {/* Signals Feed (New!) */}
                {signals.length > 0 && (
                    <div className="mb-12">
                        <div className="flex items-center gap-2 mb-4">
                            <h2 className="text-2xl font-bold text-white">⚡ Oportunidades do Dia</h2>
                            <span className="bg-yellow-500 text-black text-xs font-bold px-2 py-1 rounded-full animate-pulse">
                                {signals.length} NOVAS
                            </span>
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
                                        <button className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded">
                                            Analisar →
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Status Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
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

                {/* System Status Widget - Temporarily disabled */}
                {/* <div className="mb-12">
                    <SystemStatusWidget />
                </div> */}

                {/* Quick Links */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <a
                        href="/matches"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">⚽</div>
                        <h3 className="font-semibold">Jogos</h3>
                    </a>

                    <a
                        href="/bets"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">🎯</div>
                        <h3 className="font-semibold">Apostas</h3>
                    </a>

                    <a
                        href="/strategies"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">🧠</div>
                        <h3 className="font-semibold">Estratégias</h3>
                    </a>

                    <a
                        href="/analysis/league"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">💓</div>
                        <h3 className="font-semibold">Pulso</h3>
                    </a>

                    <a
                        href="/calendar"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">📅</div>
                        <h3 className="font-semibold">Calendário</h3>
                    </a>

                    <a
                        href="/bankroll"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">💰</div>
                        <h3 className="font-semibold">Banca</h3>
                    </a>

                    <a
                        href="/analysis/pareto"
                        className="bg-gradient-to-br from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-lg p-6 text-center transition-all shadow-lg hover:shadow-purple-500/50"
                    >
                        <div className="text-3xl mb-2">📊</div>
                        <h3 className="font-semibold">Análise Pareto</h3>
                        <p className="text-xs mt-1 opacity-90">Top 20% Equipas</p>
                    </a>

                    <a
                        href="/analysis/markets"
                        className="bg-gradient-to-br from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg p-6 text-center transition-all shadow-lg hover:shadow-emerald-500/50"
                    >
                        <div className="text-3xl mb-2">📈</div>
                        <h3 className="font-semibold">Mercados</h3>
                        <p className="text-xs mt-1 opacity-90">Over/Under, BTTS, 1X2</p>
                    </a>
                </div>

                {/* Setup Instructions */}
                {/* Initial Setup Complete */}

                {/* Footer */}
                <div className="mt-12 text-center text-slate-500 text-sm">
                    <p>BetOn v0.1.0 - Sistema em desenvolvimento</p>
                    <p className="mt-2">⚠️ Apostar responsavelmente. Nunca aposte mais do que pode perder.</p>
                </div>
            </div>
        </main >
    )
}
