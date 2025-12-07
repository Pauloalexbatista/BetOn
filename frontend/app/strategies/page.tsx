"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import axios from "axios";

interface Strategy {
    id: number;
    name: string;
    description: string;
    is_active: boolean;
    conditions: any[];
}

export default function StrategiesPage() {
    const [strategies, setStrategies] = useState<Strategy[]>([]);
    const [loading, setLoading] = useState(true);

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
                    <Link
                        href="/strategies/builder"
                        className="bg-green-600 hover:bg-green-500 text-white px-6 py-3 rounded-lg font-bold transition-colors flex items-center gap-2"
                    >
                        + Nova Estratégia
                    </Link>
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
                                    </div>
                                    <p className="text-slate-400 text-sm mb-2">{strategy.description}</p>
                                    <div className="flex gap-2 text-xs text-slate-500">
                                        <span className="bg-slate-900 px-2 py-1 rounded">{strategy.conditions.length} Condições</span>
                                    </div>
                                </div>

                                <div className="flex gap-3 opacity-50 group-hover:opacity-100 transition-opacity">
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
        </main>
    );
}
