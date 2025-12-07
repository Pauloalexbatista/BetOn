"use client";

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import axios from 'axios';

// Interfaces for API response
interface BacktestResult {
    match_id: number;
    date: string;
    home: string;
    away: string;
    target?: string;
    odds?: number;
    result: boolean; // true/false
    profit: number;
    bankroll: number;
}

export default function BacktestPage() {
    const searchParams = useSearchParams();
    const strategyId = searchParams.get('id');

    const [results, setResults] = useState<BacktestResult[]>([]);
    const [stats, setStats] = useState({
        total_profit: 0,
        roi: 0,
        win_rate: 0,
        final_balance: 0,
        total_bets: 0
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!strategyId) {
            setError("Estratégia não especificada.");
            setLoading(false);
            return;
        }
        runBacktest();
    }, [strategyId]);

    const runBacktest = async () => {
        try {
            const res = await axios.post(`http://localhost:8000/api/strategies/${strategyId}/backtest`);
            const data: BacktestResult[] = res.data;
            setResults(data);
            calculateStats(data);
        } catch (err) {
            console.error(err);
            setError("Erro ao executar backtest.");
        } finally {
            setLoading(false);
        }
    };

    const calculateStats = (data: BacktestResult[]) => {
        if (data.length === 0) return;

        const initialBankroll = 1000;
        const totalBets = data.length;
        const wins = data.filter(r => r.result).length;
        const winRate = (wins / totalBets) * 100;
        const finalBalance = data[data.length - 1].bankroll;
        const totalProfit = finalBalance - initialBankroll;
        const roi = (totalProfit / initialBankroll) * 100; // Simple ROI on starting bankroll

        setStats({
            total_profit: totalProfit,
            roi: parseFloat(roi.toFixed(2)),
            win_rate: parseFloat(winRate.toFixed(2)),
            final_balance: finalBalance,
            total_bets: totalBets
        });
    };

    if (loading) return <div className="p-10 text-white text-center">A simular passados 3 anos de jogos... ⏳</div>;
    if (error) return <div className="p-10 text-red-500 text-center">{error}</div>;

    return (
        <div className="min-h-screen bg-slate-900 text-white p-8 font-sans">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-emerald-400">📊 Resultado do Backtest</h1>
                        <p className="text-slate-400 text-sm">Estratégia ID: #{strategyId} | {stats.total_bets} Apostas analisadas</p>
                    </div>
                    <a href="/strategies" className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded text-sm transition">
                        ← Voltar
                    </a>
                </div>

                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
                    <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-lg">
                        <p className="text-slate-400 text-sm mb-1">Lucro Total</p>
                        <p className={`text-3xl font-bold ${stats.total_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            €{stats.total_profit.toFixed(2)}
                        </p>
                    </div>
                    <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-lg">
                        <p className="text-slate-400 text-sm mb-1">ROI (Banca)</p>
                        <p className={`text-3xl font-bold ${stats.roi >= 0 ? 'text-blue-400' : 'text-red-400'}`}>
                            {stats.roi}%
                        </p>
                    </div>
                    <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-lg">
                        <p className="text-slate-400 text-sm mb-1">Win Rate</p>
                        <p className="text-3xl font-bold text-yellow-400">
                            {stats.win_rate}%
                        </p>
                    </div>
                    <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-lg">
                        <p className="text-slate-400 text-sm mb-1">Banca Final</p>
                        <p className="text-3xl font-bold text-white">
                            €{stats.final_balance.toFixed(2)}
                        </p>
                    </div>
                </div>

                {/* Detailed Table */}
                <div className="bg-slate-800 rounded-lg shadow-xl overflow-hidden border border-slate-700">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-slate-900 text-slate-400 uppercase text-xs font-semibold">
                                <tr>
                                    <th className="p-4">Data</th>
                                    <th className="p-4">Jogo</th>
                                    <th className="p-4 text-center">Aposta</th>
                                    <th className="p-4 text-center">Odd</th>
                                    <th className="p-4 text-center">Resultado</th>
                                    <th className="p-4 text-right">Lucro</th>
                                    <th className="p-4 text-right">Banca</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-700">
                                {results.map((row, idx) => (
                                    <tr key={idx} className="hover:bg-slate-750 transition duration-150">
                                        <td className="p-4 text-sm text-slate-300 whitespace-nowrap">
                                            {new Date(row.date).toLocaleDateString('pt-PT')}
                                        </td>
                                        <td className="p-4 text-sm text-slate-300">
                                            {row.home} vs {row.away}
                                        </td>
                                        <td className="p-4 text-sm text-center font-mono text-yellow-500">
                                            {row.target || "Win"}
                                        </td>
                                        <td className="p-4 text-center text-sm font-mono text-yellow-400">
                                            {row.odds ? row.odds.toFixed(2) : '-'}
                                        </td>
                                        <td className="p-4 text-center">
                                            <span className={`px-2 py-1 rounded text-xs font-bold ${row.result
                                                ? 'bg-green-900 text-green-300'
                                                : 'bg-red-900 text-red-300'
                                                }`}>
                                                {row.result ? 'WON' : 'LOST'}
                                            </span>
                                        </td>
                                        <td className={`p-4 text-right font-bold text-sm ${row.profit > 0 ? 'text-green-400' : 'text-red-400'
                                            }`}>
                                            {row.profit > 0 ? '+' : ''}€{row.profit.toFixed(2)}
                                        </td>
                                        <td className="p-4 text-right text-sm text-slate-300 font-mono">
                                            €{row.bankroll.toFixed(2)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
