'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'next/navigation'; // Added
import UniversalFilter from '@/components/shared/UniversalFilter'; // Added

// Add Recharts imports
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

export default function BetsPage() {
    const searchParams = useSearchParams(); // Added for filter sync
    const [formData, setFormData] = useState({
        match_id: '',
        market: '1x2',
        selection: '',
        odds: '',
        stake: '',
        is_paper_trade: true
    });
    const [status, setStatus] = useState('');
    const [bets, setBets] = useState<Bet[]>([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState<any>(null); // For charts

    // Fetch Bets List
    const fetchBets = async () => {
        try {
            // Include searchParams in request
            const queryString = searchParams.toString();
            const response = await axios.get(`http://localhost:8000/api/bets/?${queryString}`);
            setBets(response.data);
            processChartData(response.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
        }
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
        // Sort by date ascending for line chart
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

    useEffect(() => {
        fetchBets();
    }, [searchParams]); // Re-fetch on filter change

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus('Submitting...');
        try {
            await axios.post('http://localhost:8000/api/bets/', {
                ...formData,
                match_id: parseInt(formData.match_id),
                odds: parseFloat(formData.odds),
                stake: parseFloat(formData.stake)
            });
            setStatus('Bet placed successfully!');
            // Reset form
            setFormData({ ...formData, match_id: '', selection: '', odds: '', stake: '' });
            fetchBets(); // Refresh list
        } catch (err) {
            console.error(err);
            setStatus('Error placing bet. Check console.');
        }
    };

    // Dynamic Selection Input
    const renderSelectionInput = () => {
        if (formData.market === '1x2') {
            return (
                <select
                    className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white"
                    value={formData.selection}
                    onChange={e => setFormData({ ...formData, selection: e.target.value })}
                    required
                >
                    <option value="">Selecione...</option>
                    <option value="Home">Home (Casa)</option>
                    <option value="Draw">Draw (Empate)</option>
                    <option value="Away">Away (Fora)</option>
                </select>
            );
        } else if (formData.market === 'btts') {
            return (
                <select
                    className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white"
                    value={formData.selection}
                    onChange={e => setFormData({ ...formData, selection: e.target.value })}
                    required
                >
                    <option value="">Selecione...</option>
                    <option value="Yes">Sim (Ambas Marcam)</option>
                    <option value="No">Não</option>
                </select>
            );
        } else {
            return (
                <input
                    type="text"
                    placeholder="Ex: Over 2.5"
                    className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white"
                    value={formData.selection}
                    onChange={e => setFormData({ ...formData, selection: e.target.value })}
                    required
                />
            );
        }
    };

    // Only replacing the Render/Return part where we display the list
    return (
        <main className="min-h-screen bg-slate-950 text-white p-8">
            <div className="max-w-7xl mx-auto">
                <header className="mb-8 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                            Gestão de Banca
                        </h1>
                        <p className="text-slate-400">Acompanhe as suas apostas e performance</p>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                    {/* Charts Section */}
                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 shadow-lg col-span-2">
                        <h2 className="text-xl font-bold mb-4 text-slate-200">Evolução da Banca (P/L)</h2>
                        <div className="h-[250px] w-full">
                            {stats?.plData?.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={stats.plData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                        <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                                        <YAxis stroke="#94a3b8" fontSize={12} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                                        />
                                        <Line type="monotone" dataKey="pl" stroke="#10b981" strokeWidth={2} dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex items-center justify-center text-slate-500">
                                    Sem dados suficientes
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 shadow-lg">
                        <h2 className="text-xl font-bold mb-4 text-slate-200">Mercados</h2>
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
                                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex items-center justify-center text-slate-500">
                                    Sem dados
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-lg overflow-hidden">
                    <div className="p-6 border-b border-slate-800 flex justify-between items-center">
                        <h2 className="text-xl font-bold text-white">Histórico de Apostas</h2>
                        <UniversalFilter />
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-slate-950 text-slate-400 text-xs uppercase font-semibold">
                                <tr>
                                    <th className="px-6 py-4">Data</th>
                                    <th className="px-6 py-4">Jogo</th>
                                    <th className="px-6 py-4">Seleção</th>
                                    <th className="px-6 py-4">Odd</th>
                                    <th className="px-6 py-4">Stake</th>
                                    <th className="px-6 py-4">Status</th>
                                    <th className="px-6 py-4">P/L</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {bets.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                                            Nenhuma aposta encontrada.
                                        </td>
                                    </tr>
                                ) : (
                                    bets.map(bet => (
                                        <tr key={bet.id} className="hover:bg-slate-800/50 transition-colors">
                                            <td className="px-6 py-4 text-slate-300 font-mono text-sm">
                                                {new Date(bet.placed_at).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4">
                                                {bet.match ? (
                                                    <div className="flex flex-col">
                                                        <span className="text-white font-medium text-sm">
                                                            {(typeof bet.match.home_team === 'object' ? bet.match.home_team.name : bet.match.home_team)} vs {(typeof bet.match.away_team === 'object' ? bet.match.away_team.name : bet.match.away_team)}
                                                        </span>
                                                        <span className="text-slate-500 text-xs">{bet.match.round}</span>
                                                    </div>
                                                ) : (
                                                    <span className="text-slate-500 italic">Info indisponível</span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="text-slate-200 font-medium">{bet.selection}</span>
                                                <span className="text-slate-500 text-xs ml-2">({bet.market})</span>
                                            </td>
                                            <td className="px-6 py-4 text-yellow-400 font-mono">{bet.odds}</td>
                                            <td className="px-6 py-4 text-slate-300">€{bet.stake}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 py-1 rounded-full text-xs font-bold uppercase ${bet.status === 'won' ? 'bg-green-500/20 text-green-400' :
                                                    bet.status === 'lost' ? 'bg-red-500/20 text-red-400' :
                                                        'bg-yellow-500/20 text-yellow-400'
                                                    }`}>
                                                    {bet.status}
                                                </span>
                                            </td>
                                            <td className={`px-6 py-4 font-bold ${(bet.profit_loss || 0) > 0 ? 'text-green-500' :
                                                (bet.profit_loss || 0) < 0 ? 'text-red-500' : 'text-slate-500'
                                                }`}>
                                                {bet.profit_loss ? `€${bet.profit_loss}` : '-'}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    );
}
