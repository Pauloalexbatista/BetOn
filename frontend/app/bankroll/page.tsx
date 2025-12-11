"use client";

import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

interface Match {
    id: number;
    home_team: { name: string } | string;
    away_team: { name: string } | string;
    date: string;
    round: string;
}

interface Bet {
    id: number;
    match_id: number;
    match?: Match; // Optional match details
    market: string;
    selection: string;
    odds: number;
    stake: number;
    status: string;
    profit_loss?: number;
    placed_at: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export default function BankrollPage() {
    // State
    const [summary, setSummary] = useState({ current_balance: 1000, active_exposure: 0 });
    const [bets, setBets] = useState<Bet[]>([]);
    const [alerts, setAlerts] = useState<string[]>([]);
    const [refresh, setRefresh] = useState(0);
    const [stats, setStats] = useState<any>(null); // For charts

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
        market: "1x2",
        odds: "2.00",
        stake: "10.00"
    });

    // Fetch Data
    useEffect(() => {
        fetchData();
    }, [refresh]);

    const fetchData = () => {
        // Summary
        fetch('http://localhost:8000/api/bets/stats/summary') // Updated to use the new robust endpoint
            .then(res => res.json())
            .then(data => {
                if (data.bankroll) {
                    setSummary({
                        current_balance: data.bankroll.current,
                        active_exposure: data.bankroll.exposure
                    });
                }
            });

        // Alerts (keep original endpoint or migrate later)
        fetch('http://localhost:8000/api/bankroll/alerts')
            .then(res => res.json())
            .then(data => setAlerts(data.alerts || []))
            .catch(() => setAlerts([])); // Fail silently if endpoint not ready

        // Bets
        fetch('http://localhost:8000/api/bets/?limit=50') // Use the standard bets endpoint
            .then(res => res.json())
            .then(data => {
                setBets(data);
                processChartData(data);
            });
    };

    const processChartData = (betsData: Bet[]) => {
        // Market Distribution
        const marketCounts: Record<string, number> = {};
        betsData.forEach(bet => {
            marketCounts[bet.market] = (marketCounts[bet.market] || 0) + 1;
        });
        const marketData = Object.keys(marketCounts).map(market => ({
            name: market,
            value: marketCounts[market]
        }));

        // P/L History (Accumulated)
        const sortedBets = [...betsData].sort((a, b) => new Date(a.placed_at).getTime() - new Date(b.placed_at).getTime());
        let accumulatedPL = 0;
        const plData = sortedBets.map(bet => {
            if (bet.status === 'won' || bet.status === 'lost') {
                accumulatedPL += (bet.profit_loss || 0);
            }
            return {
                date: new Date(bet.placed_at).toLocaleDateString(),
                pl: accumulatedPL,
                bet_pl: bet.profit_loss || 0
            };
        });

        setStats({ marketData, plData });
    };

    const calculateKelly = () => {
        const probDecimal = kellyProb / 100;
        fetch('http://localhost:8000/api/bankroll/kelly', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ odds: kellyOdds, probability: probDecimal })
        })
            .then(res => res.json())
            .then(data => setKellyResult(data))
            .catch(err => console.error("Kelly calc error", err));
    };

    const handlePlaceBet = () => {
        // Use the standard API endpoint
        const payload = {
            match_id: 4872, // Default dummy ID for manual entry if not specified
            strategy_id: null,
            market: newBet.market,
            selection: newBet.selection, // This needs to match backend expectations
            odds: parseFloat(newBet.odds.toString()),
            stake: parseFloat(newBet.stake.toString()),
            is_paper_trade: true
        };

        fetch('http://localhost:8000/api/bets/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(res => {
                if (res.ok) {
                    setShowModal(false);
                    setRefresh(prev => prev + 1);
                    alert("Aposta criada com sucesso! (ID Provisório de Jogo usado)");
                } else {
                    res.json().then(err => alert(`Erro: ${err.detail || 'Erro ao criar aposta'}`));
                }
            })
            .catch(err => alert("Erro de conexão"));
    };

    const handleDelete = (id: number) => {
        if (!confirm("Tem a certeza que quer cancelar esta aposta?")) return;
        // Verify endpoint existence or use a standard one
        fetch(`http://localhost:8000/api/bankroll/bets/${id}`, { method: 'DELETE' })
            .then(() => setRefresh(prev => prev + 1))
            .catch(err => alert("Funcionalidade de delete ainda não migrada totalmente."));
    };

    const handleSettle = (id: number, won: boolean) => {
        // This is tricky without the dedicated endpoint, let's assume it exists or mock it for now
        if (!confirm(won ? "Marcar como GANHO?" : "Marcar como PERDIDO?")) return;
        fetch(`http://localhost:8000/api/bankroll/bets/${id}/settle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ won: won })
        })
            .then(() => setRefresh(prev => prev + 1))
            .catch(err => alert("Funcionalidade de settle ainda não migrada totalmente."));
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
                        <a href="/" className="bg-gray-700 px-4 py-2 rounded hover:bg-gray-600 transition">
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
                            {(summary.active_exposure / ((summary.current_balance + summary.active_exposure) || 1) * 100).toFixed(1)}% da banca
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

                {/* Bankroll Management Controls - NEW SECTION */}
                <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-xl mb-8">
                    <h2 className="text-xl font-bold mb-4 text-emerald-400">⚙️ Configurações de Banca</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Edit Balance */}
                        <div className="bg-gray-900/50 p-4 rounded-lg">
                            <label className="block text-gray-400 text-sm font-medium mb-2">
                                💰 Saldo da Banca
                            </label>
                            <div className="flex gap-2 mb-2">
                                <input
                                    type="number"
                                    step="0.01"
                                    placeholder="Novo saldo"
                                    className="flex-1 bg-gray-700 border border-gray-600 rounded p-2 text-white text-sm"
                                    id="newBalance"
                                />
                                <button
                                    onClick={async () => {
                                        const input = document.getElementById('newBalance') as HTMLInputElement;
                                        const newValue = parseFloat(input.value);
                                        if (newValue && newValue > 0) {
                                            try {
                                                const res = await fetch('http://localhost:8000/api/bankroll/set-balance', {
                                                    method: 'POST',
                                                    headers: { 'Content-Type': 'application/json' },
                                                    body: JSON.stringify({ new_balance: newValue })
                                                });
                                                const data = await res.json();
                                                if (res.ok) {
                                                    alert(data.message);
                                                    input.value = '';  // Clear input
                                                    fetchData();  // Immediately refresh data
                                                } else {
                                                    alert(`Erro: ${data.detail}`);
                                                }
                                            } catch (err) {
                                                alert('Erro ao conectar ao servidor');
                                            }
                                        }
                                    }}
                                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 rounded text-sm font-bold"
                                >
                                    Set
                                </button>
                            </div>
                            <div className="text-xs text-gray-500 mb-2">ou ajustar:</div>
                            <div className="flex gap-2">
                                <input
                                    type="number"
                                    step="0.01"
                                    placeholder="+/- valor"
                                    className="flex-1 bg-gray-700 border border-gray-600 rounded p-2 text-white text-sm"
                                    id="adjustBalance"
                                />
                                <button
                                    onClick={async () => {
                                        const input = document.getElementById('adjustBalance') as HTMLInputElement;
                                        const adjustment = parseFloat(input.value);
                                        if (adjustment) {
                                            try {
                                                const res = await fetch('http://localhost:8000/api/bankroll/adjust-balance', {
                                                    method: 'POST',
                                                    headers: { 'Content-Type': 'application/json' },
                                                    body: JSON.stringify({ adjustment: adjustment })
                                                });
                                                const data = await res.json();
                                                if (res.ok) {
                                                    alert(data.message);
                                                    input.value = '';  // Clear input
                                                    fetchData();  // Immediately refresh data
                                                } else {
                                                    alert(`Erro: ${data.detail}`);
                                                }
                                            } catch (err) {
                                                alert('Erro ao conectar ao servidor');
                                            }
                                        }
                                    }}
                                    className="bg-blue-600 hover:bg-blue-500 text-white px-4 rounded text-sm font-bold"
                                >
                                    +/-
                                </button>
                            </div>
                        </div>

                        {/* Edit Default Stake % */}
                        <div className="bg-gray-900/50 p-4 rounded-lg">
                            <label className="block text-gray-400 text-sm font-medium mb-2">
                                📊 % Stake Padrão
                            </label>
                            <div className="flex gap-2 items-center">
                                <input
                                    type="number"
                                    step="0.1"
                                    min="0"
                                    max="100"
                                    placeholder="% da banca"
                                    defaultValue="2.0"
                                    className="flex-1 bg-gray-700 border border-gray-600 rounded p-2 text-white text-sm"
                                    id="stakePercent"
                                />
                                <span className="text-white text-sm">%</span>
                                <button
                                    onClick={async () => {
                                        const input = document.getElementById('stakePercent') as HTMLInputElement;
                                        const percentage = parseFloat(input.value);
                                        if (percentage && percentage > 0 && percentage <= 100) {
                                            try {
                                                const res = await fetch('http://localhost:8000/api/bankroll/set-stake-percentage', {
                                                    method: 'POST',
                                                    headers: { 'Content-Type': 'application/json' },
                                                    body: JSON.stringify({ stake_percentage: percentage })
                                                });
                                                const data = await res.json();
                                                if (res.ok) {
                                                    alert(data.message);
                                                } else {
                                                    alert(`Erro: ${data.detail}`);
                                                }
                                            } catch (err) {
                                                alert('Erro ao conectar ao servidor');
                                            }
                                        }
                                    }}
                                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 rounded text-sm font-bold"
                                >
                                    Save
                                </button>
                            </div>
                            <div className="text-xs text-gray-500 mt-2">
                                Valor sugerido: 1-5% da banca
                            </div>
                        </div>

                        {/* Edit Max Exposure */}
                        <div className="bg-gray-900/50 p-4 rounded-lg">
                            <label className="block text-gray-400 text-sm font-medium mb-2">
                                ⚠️ Exposição Máxima (€)
                            </label>
                            <div className="flex gap-2">
                                <input
                                    type="number"
                                    step="0.01"
                                    placeholder="Máximo em jogo"
                                    className="flex-1 bg-gray-700 border border-gray-600 rounded p-2 text-white text-sm"
                                    id="maxExposure"
                                />
                                <button
                                    onClick={async () => {
                                        const input = document.getElementById('maxExposure') as HTMLInputElement;
                                        const maxValue = parseFloat(input.value);
                                        if (maxValue && maxValue > 0) {
                                            try {
                                                const res = await fetch('http://localhost:8000/api/bankroll/set-max-exposure', {
                                                    method: 'POST',
                                                    headers: { 'Content-Type': 'application/json' },
                                                    body: JSON.stringify({ max_exposure: maxValue })
                                                });
                                                const data = await res.json();
                                                if (res.ok) {
                                                    alert(data.message);
                                                    input.value = '';  // Clear input
                                                } else {
                                                    alert(`Erro: ${data.detail}`);
                                                }
                                            } catch (err) {
                                                alert('Erro ao conectar ao servidor');
                                            }
                                        }
                                    }}
                                    className="bg-red-600 hover:bg-red-500 text-white px-4 rounded text-sm font-bold"
                                >
                                    Set
                                </button>
                            </div>
                            <div className="text-xs text-gray-500 mt-2">
                                Atual: €{summary.active_exposure.toFixed(2)} ({((summary.active_exposure / ((summary.current_balance + summary.active_exposure) || 1)) * 100).toFixed(1)}%)
                            </div>
                        </div>
                    </div>
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg col-span-2">
                        <h2 className="text-xl font-bold mb-4 text-gray-200">Evolução da Banca (P/L)</h2>
                        <div className="h-[250px] w-full">
                            {stats?.plData?.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={stats.plData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                        <XAxis dataKey="date" stroke="#9CA3AF" fontSize={12} />
                                        <YAxis stroke="#9CA3AF" fontSize={12} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                                        />
                                        <Line type="monotone" dataKey="pl" stroke="#10B981" strokeWidth={2} dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex items-center justify-center text-gray-500">
                                    Sem dados suficientes
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                        <h2 className="text-xl font-bold mb-4 text-gray-200">Mercados</h2>
                        <div className="h-[250px] w-full">
                            {stats?.marketData?.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={stats.marketData}
                                            innerRadius={60}
                                            outerRadius={80}
                                            paddingAngle={5}
                                            dataKey="value"
                                        >
                                            {stats.marketData.map((entry: any, index: number) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', color: '#fff' }} />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex items-center justify-center text-gray-500">
                                    Sem dados
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Modal */}
                {showModal && (
                    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
                        <div className="bg-gray-800 p-8 rounded-xl shadow-2xl border border-gray-600 w-full max-w-md">
                            <h2 className="text-xl font-bold mb-4 text-white">📝 Registar Aposta Manual</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-gray-400 text-sm mb-1">Jogo / Descrição</label>
                                    <input type="text" className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                        placeholder="Ex: Benfica vs Porto (Info)"
                                        value={newBet.match_name} onChange={e => setNewBet({ ...newBet, match_name: e.target.value })} />
                                </div>
                                <div className="flex space-x-4">
                                    <div className="w-1/2">
                                        <label className="block text-gray-400 text-sm mb-1">Seleção</label>
                                        <input type="text" className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                            placeholder="Ex: Home"
                                            value={newBet.selection} onChange={e => setNewBet({ ...newBet, selection: e.target.value })} />
                                    </div>
                                    <div className="w-1/2">
                                        <label className="block text-gray-400 text-sm mb-1">Mercado</label>
                                        <select className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                            value={newBet.market} onChange={e => setNewBet({ ...newBet, market: e.target.value })}>
                                            <option value="1x2">1x2</option>
                                            <option value="over_under">Over/Under</option>
                                            <option value="btts">BTTS</option>
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
                    <div className="px-6 py-4 border-b border-gray-700 flex justify-between items-center">
                        <h2 className="text-lg font-bold text-white">📜 Histórico de Apostas</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left bg-gray-800">
                            <thead className="bg-gray-900 text-gray-400 uppercase text-xs font-semibold">
                                <tr>
                                    <th className="p-4">Data</th>
                                    <th className="p-4">Jogo</th>
                                    <th className="p-4">Seleção</th>
                                    <th className="p-4 text-center">Odd</th>
                                    <th className="p-4 text-right">Stake</th>
                                    <th className="p-4 text-center">Status</th>
                                    <th className="p-4 text-right">P/L</th>
                                    <th className="p-4 text-center">Ações</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {bets.length > 0 ? bets.map((bet: Bet) => (
                                    <tr key={bet.id} className="hover:bg-gray-750 transition">
                                        <td className="p-4 text-sm text-gray-400">
                                            {new Date(bet.placed_at).toLocaleDateString()}
                                        </td>
                                        <td className="p-4 text-sm font-medium text-white">
                                            {bet.match ? (
                                                <div className="flex flex-col">
                                                    <span>
                                                        {(typeof bet.match.home_team === 'object' ? bet.match.home_team.name : bet.match.home_team)} vs {(typeof bet.match.away_team === 'object' ? bet.match.away_team.name : bet.match.away_team)}
                                                    </span>
                                                    <span className="text-xs text-gray-500">{bet.match.round}</span>
                                                </div>
                                            ) : (
                                                <span className="italic text-gray-500">Manual / Info Indisp.</span>
                                            )}
                                        </td>
                                        <td className="p-4 text-sm font-medium text-gray-300">
                                            {bet.selection} <span className="text-gray-500 text-xs text-nowrap">({bet.market})</span>
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
                                        <td className={`p-4 text-right font-bold ${(bet.profit_loss || 0) > 0 ? 'text-green-400' : (bet.profit_loss || 0) < 0 ? 'text-red-400' : 'text-gray-500'}`}>
                                            {bet.profit_loss ? `€${bet.profit_loss.toFixed(2)}` : '-'}
                                        </td>
                                        <td className="p-4 text-center space-x-2">
                                            {bet.status === 'pending' && (
                                                <>
                                                    <button onClick={() => handleSettle(bet.id, true)} className="text-xs bg-green-700 hover:bg-green-600 text-white px-2 py-1 rounded" title="Ganho">✔</button>
                                                    <button onClick={() => handleSettle(bet.id, false)} className="text-xs bg-red-700 hover:bg-red-600 text-white px-2 py-1 rounded" title="Perdido">✖</button>
                                                    <button onClick={() => handleDelete(bet.id)} className="text-xs bg-gray-600 hover:bg-gray-500 text-white px-2 py-1 rounded" title="Cancelar">🗑</button>
                                                </>
                                            )}
                                        </td>
                                    </tr>
                                )) : (
                                    <tr>
                                        <td colSpan={8} className="p-8 text-center text-gray-500">Sem apostas registadas.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
