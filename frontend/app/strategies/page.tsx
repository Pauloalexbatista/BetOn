"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import axios from "axios";

interface Strategy {
    id: number;
    name: string;
    description: string;
    is_active: boolean;
    strategy_type: string;
    conditions: any[];
}

export default function StrategiesPage() {
    const [strategies, setStrategies] = useState<Strategy[]>([]);
    const [loading, setLoading] = useState(true);
    const [showBuilderModal, setShowBuilderModal] = useState(false);

    useEffect(() => {
        fetchStrategies();
    }, []);

    const fetchStrategies = async () => {
        try {
            const res = await axios.get("http://localhost:8000/api/strategies/");
            setStrategies(res.data);
        } catch (err) {
            console.error("Failed to load strategies", err);
        } finally {
            setLoading(false);
        }
    };

    const toggleStrategy = async (id: number) => {
        try {
            await axios.put(`http://localhost:8000/api/strategies/${id}/toggle`);
            fetchStrategies(); // Refresh
        } catch (err) {
            console.error("Failed to toggle strategy", err);
        }
    };

    const deleteStrategy = async (id: number) => {
        if (!confirm("Are you sure?")) return;
        try {
            await axios.delete(`http://localhost:8000/api/strategies/${id}`);
            fetchStrategies();
        } catch (err) {
            console.error("Failed to delete strategy", err);
        }
    };

    return (
        <main className="min-h-screen bg-slate-900 text-white p-8">
            <div className="container mx-auto max-w-5xl">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold">Minhas Estratégias</h1>
                        <p className="text-slate-400">Automatiza as tuas ideias e recebe sinais.</p>
                    </div>
                    <button
                        onClick={() => setShowBuilderModal(true)}
                        className="bg-green-600 hover:bg-green-500 text-white px-6 py-3 rounded-lg font-bold transition-colors flex items-center gap-2"
                    >
                        + Nova Estratégia
                    </button>
                </div>

                <div className="mb-6">
                    <Link href="/" className="text-slate-400 hover:text-white text-sm">
                        ← Voltar ao Dashboard
                    </Link>
                </div>

                {loading ? (
                    <div className="text-center py-20 text-slate-500">A carregar o cérebro...</div>
                ) : strategies.length === 0 ? (
                    <div className="bg-slate-800 rounded-lg p-12 text-center border border-slate-700">
                        <h3 className="text-xl font-bold mb-2">Sem Estratégias Ativas</h3>
                        <p className="text-slate-400 mb-6">Ainda não definiste nenhuma regra. Começa agora!</p>
                        <Link
                            href="/strategies/builder"
                            className="text-blue-400 hover:text-blue-300 underline"
                        >
                            Criar a primeira estratégia
                        </Link>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {strategies.map(strategy => (
                            <div key={strategy.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700 flex justify-between items-center group hover:border-blue-500/50 transition-all">
                                <div>
                                    <div className="flex items-center gap-3 mb-1">
                                        <h3 className="text-xl font-bold">{strategy.name}</h3>
                                        <span className={`text-xs px-2 py-1 rounded ${strategy.is_active ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
                                            {strategy.is_active ? 'ATIVO' : 'PAUSA'}
                                        </span>
                                        <span className={`text-xs px-2 py-1 rounded ${strategy.strategy_type === 'single'
                                            ? 'bg-blue-900 text-blue-200'
                                            : 'bg-purple-900 text-purple-200'
                                            }`}>
                                            {strategy.strategy_type === 'single' ? 'SIMPLES' : 'ACUMULADOR'}
                                        </span>
                                    </div>
                                    <p className="text-slate-400 text-sm mb-2">{strategy.description}</p>
                                    <div className="flex gap-2 text-xs text-slate-500">
                                        <span className="bg-slate-900 px-2 py-1 rounded">{strategy.conditions.length} Condições</span>
                                    </div>
                                </div>

                                <div className="flex gap-3 opacity-50 group-hover:opacity-100 transition-opacity">
                                    <Link
                                        href={`/strategies/${strategy.id}`}
                                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-medium"
                                    >
                                        Ver Jogos
                                    </Link>
                                    <button
                                        onClick={() => toggleStrategy(strategy.id)}
                                        className="p-2 hover:bg-slate-700 rounded"
                                        title={strategy.is_active ? "Pausar" : "Ativar"}
                                    >
                                        {strategy.is_active ? '⏸️' : '▶️'}
                                    </button>
                                    <Link
                                        href={`/strategies/backtest?id=${strategy.id}`}
                                        className="p-2 hover:bg-blue-900/30 text-blue-400 rounded"
                                        title="Backtest (Testar no passado)"
                                    >
                                        📉
                                    </Link>
                                    <button
                                        onClick={() => deleteStrategy(strategy.id)}
                                        className="p-2 hover:bg-red-900/30 text-red-400 rounded"
                                        title="Apagar"
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Builder Selection Modal */}
            {showBuilderModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={() => setShowBuilderModal(false)}>
                    <div className="bg-slate-800 rounded-lg p-8 max-w-2xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
                        <h2 className="text-2xl font-bold text-white mb-6">Escolhe o Tipo de Estratégia</h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Single */}
                            <Link
                                href="/strategies/single/new"
                                className="bg-blue-900/30 border-2 border-blue-500 hover:bg-blue-900/50 p-6 rounded-lg transition-all group"
                            >
                                <div className="text-4xl mb-4">🎯</div>
                                <h3 className="text-xl font-bold text-white mb-2">Apostas Simples</h3>
                                <p className="text-gray-400 text-sm mb-4">
                                    Apostas individuais. Cada jogo é independente.
                                </p>
                                <div className="text-blue-400 group-hover:text-blue-300">
                                    Criar →
                                </div>
                            </Link>

                            {/* Accumulator */}
                            <Link
                                href="/strategies/accumulator/new"
                                className="bg-purple-900/30 border-2 border-purple-500 hover:bg-purple-900/50 p-6 rounded-lg transition-all group"
                            >
                                <div className="text-4xl mb-4">🚀</div>
                                <h3 className="text-xl font-bold text-white mb-2">Acumuladores</h3>
                                <p className="text-gray-400 text-sm mb-4">
                                    Apostas múltiplas agrupadas por jornada. Odds combinadas.
                                </p>
                                <div className="text-purple-400 group-hover:text-purple-300">
                                    Criar →
                                </div>
                            </Link>
                        </div>

                        <div className="mt-6 text-center">
                            <button
                                onClick={() => setShowBuilderModal(false)}
                                className="text-gray-400 hover:text-white"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
}
