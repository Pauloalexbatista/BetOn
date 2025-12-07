"use client";

import { useEffect, useState } from 'react';

export default function BankrollPage() {
    // State
    const [summary, setSummary] = useState({ current_balance: 1000, active_exposure: 0 });
    const [bets, setBets] = useState([]);
    const [alerts, setAlerts] = useState<string[]>([]);
    const [refresh, setRefresh] = useState(0);

    // Kelly Calc State
    const [kellyOdds, setKellyOdds] = useState(2.00);
    const [kellyProb, setKellyProb] = useState(55);
    const [kellyResult, setKellyResult] = useState({ recommended_stake: 0, percent: 0 });

    // Modal State
    const [showModal, setShowModal] = useState(false);
    const [newBet, setNewBet] = useState({
        match_id: 0,
        match_name: "",
        selection: "",
        market: "Match Odds",
        odds: "2.00",
        stake: "10.00"
    });

    // Fetch Data
    useEffect(() => {
        fetchData();
    }, [refresh]);

    const fetchData = () => {
        // Summary
        fetch('http://localhost:8000/api/bankroll/summary')
            .then(res => res.json())
            .then(data => setSummary(data));

        // Alerts
        fetch('http://localhost:8000/api/bankroll/alerts')
            .then(res => res.json())
            .then(data => setAlerts(data.alerts || []));

        // Bets
        fetch('http://localhost:8000/api/bankroll/all-bets?limit=20')
            .then(res => res.json())
            .then(data => setBets(data));
    };

    const calculateKelly = () => {
        const probDecimal = kellyProb / 100;
        fetch('http://localhost:8000/api/bankroll/kelly', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ odds: kellyOdds, probability: probDecimal })
        })
            .then(res => res.json())
            .then(data => setKellyResult(data));
    };

    const handlePlaceBet = () => {
        const payload = {
            match_id: 1, // Default dummy ID
            selection: `${newBet.match_name} - ${newBet.selection}`,
            market: newBet.market,
            odds: parseFloat(newBet.odds.toString()),
            stake: parseFloat(newBet.stake.toString()),
            strategy: "Manual"
        };

        fetch('http://localhost:8000/api/bankroll/bets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(res => {
                if (res.ok) {
                    setShowModal(false);
                    setRefresh(prev => prev + 1);
                } else {
                    alert("Erro ao criar aposta!");
                }
            });
    };

    const handleDelete = (id: number) => {
        if (!confirm("Tem a certeza que quer cancelar esta aposta?")) return;
        fetch(`http://localhost:8000/api/bankroll/bets/${id}`, { method: 'DELETE' })
            .then(() => setRefresh(prev => prev + 1));
    };

    const handleSettle = (id: number, won: boolean) => {
        if (!confirm(won ? "Marcar como GANHO?" : "Marcar como PERDIDO?")) return;
        fetch(`http://localhost:8000/api/bankroll/bets/${id}/settle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ won: won })
        })
            .then(() => setRefresh(prev => prev + 1));
    };

    return (
        <div className="min-h-screen bg-gray-900 text-gray-100 p-8 font-sans">
            <div className="max-w-7xl mx-auto">

                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-emerald-400">🏦 Gestão de Banca</h1>
                    <div className="space-x-4">
                        <button
                            onClick={() => setShowModal(true)}
                            className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded shadow transition font-bold"
                        >
                            + Nova Aposta
                        </button>
                        <a href="http://localhost:3000" className="bg-gray-700 px-4 py-2 rounded hover:bg-gray-600 transition">
                            ← Voltar
                        </a>
                    </div>
                </div>

                {/* Risk Alerts Banner */}
                {alerts.length > 0 && (
                    <div className="bg-red-900/50 border border-red-500 text-red-100 p-4 rounded-xl mb-8 shadow-lg animate-pulse">
                        <h3 className="font-bold text-lg mb-2 flex items-center">
                            ⚠️ Alertas de Risco
                        </h3>
                        <ul className="list-disc list-inside space-y-1">
                            {alerts.map((alert, idx) => (
                                <li key={idx} className="font-medium">{alert}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Top Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {/* Balance */}
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl relative overflow-hidden">
                        <p className="text-gray-400 text-sm font-medium uppercase tracking-wider">Saldo Disponível</p>
                        <p className="text-4xl font-bold text-white mt-1">€{summary.current_balance.toFixed(2)}</p>
                    </div>

                    {/* Exposure */}
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
                        <p className="text-gray-400 text-sm font-medium uppercase tracking-wider">Capital em Jogo</p>
                        <p className="text-4xl font-bold text-yellow-500 mt-1">€{summary.active_exposure.toFixed(2)}</p>
                        <p className="text-xs text-gray-500 mt-2">
                            {(summary.active_exposure / (summary.current_balance + summary.active_exposure || 1) * 100).toFixed(1)}% da banca
                        </p>
                    </div>

                    {/* Kelly Quick Calc */}
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl bg-gradient-to-br from-gray-800 to-gray-900">
                        <p className="text-emerald-400 text-sm font-bold uppercase tracking-wider mb-2">🧠 Calculadora Kelly</p>
                        <div className="flex space-x-2 mb-3">
                            <input type="number" placeholder="Odd" value={kellyOdds} onChange={e => setKellyOdds(parseFloat(e.target.value))} className="w-1/3 bg-gray-700 rounded p-1 text-sm border border-gray-600" />
                            <input type="number" placeholder="Prob %" value={kellyProb} onChange={e => setKellyProb(parseFloat(e.target.value))} className="w-1/3 bg-gray-700 rounded p-1 text-sm border border-gray-600" />
                            <button onClick={calculateKelly} className="bg-emerald-600 text-white rounded px-3 text-xs font-bold w-1/3">CALC</button>
                        </div>
                        {kellyResult.recommended_stake > 0 && (
                            <div className="text-sm bg-gray-700/50 p-2 rounded text-center">
                                Sugestão: <span className="text-emerald-400 font-bold">€{kellyResult.recommended_stake}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Modal */}
                {showModal && (
                    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
                        <div className="bg-gray-800 p-8 rounded-xl shadow-2xl border border-gray-600 w-full max-w-md">
                            <h2 className="text-xl font-bold mb-4 text-white">📝 Registar Aposta</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-gray-400 text-sm mb-1">Jogo / Descrição</label>
                                    <input type="text" className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                        placeholder="Ex: Benfica vs Porto"
                                        value={newBet.match_name} onChange={e => setNewBet({ ...newBet, match_name: e.target.value })} />
                                </div>
                                <div className="flex space-x-4">
                                    <div className="w-1/2">
                                        <label className="block text-gray-400 text-sm mb-1">Seleção</label>
                                        <input type="text" className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                            placeholder="Ex: Home Win"
                                            value={newBet.selection} onChange={e => setNewBet({ ...newBet, selection: e.target.value })} />
                                    </div>
                                    <div className="w-1/2">
                                        <label className="block text-gray-400 text-sm mb-1">Mercado</label>
                                        <select className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                            value={newBet.market} onChange={e => setNewBet({ ...newBet, market: e.target.value })}>
                                            <option>Match Odds</option>
                                            <option>Over/Under 2.5</option>
                                            <option>BTTS</option>
                                            <option>Accumulator</option>
                                        </select>
                                    </div>
                                </div>
                                <div className="flex space-x-4">
                                    <div className="w-1/2">
                                        <label className="block text-gray-400 text-sm mb-1">Odd</label>
                                        <input type="text" className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                            value={newBet.odds} onChange={e => setNewBet({ ...newBet, odds: e.target.value })} />
                                    </div>
                                    <div className="w-1/2">
                                        <label className="block text-gray-400 text-sm mb-1">Stake (€)</label>
                                        <input type="text" className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                            value={newBet.stake} onChange={e => setNewBet({ ...newBet, stake: e.target.value })} />
                                    </div>
                                </div>
                            </div>

                            <div className="flex space-x-3 mt-8">
                                <button onClick={() => setShowModal(false)} className="flex-1 bg-gray-700 text-white py-2 rounded hover:bg-gray-600">Cancelar</button>
                                <button onClick={handlePlaceBet} className="flex-1 bg-emerald-600 text-white py-2 rounded hover:bg-emerald-500 font-bold">Confirmar</button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Bets History Table */}
                <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden border border-gray-700">
                    <div className="px-6 py-4 border-b border-gray-700">
                        <h2 className="text-lg font-bold text-white">📜 Histórico de Apostas</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left bg-gray-800">
                            <thead className="bg-gray-900 text-gray-400 uppercase text-xs font-semibold">
                                <tr>
                                    <th className="p-4">Data</th>
                                    <th className="p-4">Seleção</th>
                                    <th className="p-4 text-center">Odd</th>
                                    <th className="p-4 text-right">Stake</th>
                                    <th className="p-4 text-center">Status</th>
                                    <th className="p-4 text-right">P/L</th>
                                    <th className="p-4 text-center">Ações</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {bets.map((bet: any) => (
                                    <tr key={bet.id} className="hover:bg-gray-750 transition">
                                        <td className="p-4 text-sm text-gray-400">{new Date(bet.placed_at).toLocaleDateString()}</td>
                                        <td className="p-4 text-sm font-medium text-white">
                                            {bet.selection} <span className="text-gray-500 text-xs">({bet.market})</span>
                                        </td>
                                        <td className="p-4 text-center text-yellow-500 font-mono">{bet.odds.toFixed(2)}</td>
                                        <td className="p-4 text-right text-gray-300 font-mono">€{bet.stake.toFixed(2)}</td>
                                        <td className="p-4 text-center">
                                            <span className={`px-2 py-1 rounded text-xs font-bold uppercase
                                                ${bet.status === 'won' ? 'bg-green-900 text-green-300' :
                                                    bet.status === 'lost' ? 'bg-red-900 text-red-300' :
                                                        'bg-yellow-900 text-yellow-300'}`}>
                                                {bet.status}
                                            </span>
                                        </td>
                                        <td className={`p-4 text-right font-bold ${bet.profit_loss > 0 ? 'text-green-400' : bet.profit_loss < 0 ? 'text-red-400' : 'text-gray-500'}`}>
                                            {bet.profit_loss ? `€${bet.profit_loss.toFixed(2)}` : '-'}
                                        </td>
                                        <td className="p-4 text-center space-x-2">
                                            {bet.status === 'pending' && (
                                                <>
                                                    <button onClick={() => handleSettle(bet.id, true)} className="text-xs bg-green-700 hover:bg-green-600 text-white px-2 py-1 rounded">✔</button>
                                                    <button onClick={() => handleSettle(bet.id, false)} className="text-xs bg-red-700 hover:bg-red-600 text-white px-2 py-1 rounded">✖</button>
                                                    <button onClick={() => handleDelete(bet.id)} className="text-xs bg-gray-600 hover:bg-gray-500 text-white px-2 py-1 rounded">🗑</button>
                                                </>
                                            )}
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
