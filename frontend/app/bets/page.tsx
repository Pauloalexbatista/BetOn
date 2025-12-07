'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'next/navigation'; // Added
import UniversalFilter from '@/components/shared/UniversalFilter'; // Added

interface Bet {
    id: number;
    match_id: number;
    market: string;
    selection: string;
    odds: number;
    stake: number;
    status: string;
    profit_loss?: number;
    placed_at: string;
}

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

    // Fetch Bets List
    const fetchBets = async () => {
        try {
            // Include searchParams in request
            const queryString = searchParams.toString();
            const response = await axios.get(`http://localhost:8000/api/bets/?${queryString}`);
            setBets(response.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
        }
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

    return (
        <main className="min-h-screen bg-slate-900 text-white p-8">
            <div className="container mx-auto max-w-4xl">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold">Apostas</h1>
                    <a href="/" className="text-slate-400 hover:text-white">← Voltar</a>
                </div>

                <div className="mb-8">
                    <UniversalFilter />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Form */}
                    <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 h-fit">
                        <h2 className="text-xl font-bold mb-6">Registar Nova Aposta</h2>
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-slate-400 mb-2">ID do Jogo</label>
                                <input
                                    type="number"
                                    className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white"
                                    value={formData.match_id}
                                    onChange={e => setFormData({ ...formData, match_id: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-slate-400 mb-2">Mercado</label>
                                    <select
                                        className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white"
                                        value={formData.market}
                                        onChange={e => setFormData({ ...formData, market: e.target.value })}
                                    >
                                        <option value="1x2">1x2</option>
                                        <option value="over_under">Over/Under</option>
                                        <option value="btts">Ambas Marcam</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-slate-400 mb-2">Seleção</label>
                                    {renderSelectionInput()}
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-slate-400 mb-2">Odd</label>
                                    <input
                                        type="number" step="0.01"
                                        className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white"
                                        value={formData.odds}
                                        onChange={e => setFormData({ ...formData, odds: e.target.value })}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-slate-400 mb-2">Stake (€)</label>
                                    <input
                                        type="number" step="0.01"
                                        className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white"
                                        value={formData.stake}
                                        onChange={e => setFormData({ ...formData, stake: e.target.value })}
                                        required
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-bold py-3 rounded-lg transition-colors"
                            >
                                Registar Aposta
                            </button>

                            {status && (
                                <div className={`text-center p-3 rounded ${status.includes('Error') ? 'bg-red-900/50 text-red-200' : 'bg-green-900/50 text-green-200'}`}>
                                    {status}
                                </div>
                            )}
                        </form>
                    </div>

                    {/* Recent Bets List */}
                    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                        <h2 className="text-xl font-bold mb-6">Últimas Apostas</h2>
                        <div className="overflow-y-auto max-h-[600px]">
                            {bets.length === 0 ? (
                                <p className="text-slate-500">Nenhuma aposta registada.</p>
                            ) : (
                                <div className="space-y-4">
                                    {bets.map(bet => (
                                        <div key={bet.id} className="bg-slate-900 p-4 rounded border border-slate-700">
                                            <div className="flex justify-between items-start mb-2">
                                                <span className="text-sm text-slate-400">{new Date(bet.placed_at).toLocaleDateString()}</span>
                                                <span className={`px-2 py-0.5 rounded text-xs uppercase ${bet.status === 'won' ? 'bg-green-900 text-green-300' :
                                                    bet.status === 'lost' ? 'bg-red-900 text-red-300' :
                                                        'bg-yellow-900 text-yellow-300'
                                                    }`}>{bet.status}</span>
                                            </div>
                                            <div className="font-bold mb-1">{bet.selection} <span className="font-normal text-slate-500">({bet.market})</span></div>
                                            <div className="flex justify-between text-sm">
                                                <span>Odd: <span className="text-yellow-500">{bet.odds}</span></span>
                                                <span>Stake: €{bet.stake}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
