"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'next/navigation';
import UniversalFilter from '@/components/shared/UniversalFilter';

interface Match {
    id: number;
    home_team: { name: string };
    away_team: { name: string };
    league: string;
    match_date: string;
    status: string;
    home_score?: number;
    away_score?: number;
    round_calculated: number;
    home_position?: number;
    away_position?: number;
}

export default function CalendarPage() {
    const searchParams = useSearchParams();
    const [matches, setMatches] = useState<Match[]>([]);
    const [groupedMatches, setGroupedMatches] = useState<Record<number, Match[]>>({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const league = searchParams.get("league");
    const season = searchParams.get("season");

    useEffect(() => {
        if (!league || !season) return;

        const fetchMatches = async () => {
            setLoading(true);
            try {
                // Fetch ALL matches for the season (high limit)
                const params = new URLSearchParams(searchParams.toString());
                params.set("limit", "1000"); // Ensure we get the whole season

                const res = await axios.get(`http://localhost:8000/api/matches/?${params.toString()}`);
                const data: Match[] = res.data;

                setMatches(data);
                groupMatchesByRound(data);
                setError('');
            } catch (err) {
                console.error(err);
                setError("Failed to load season calendar.");
            } finally {
                setLoading(false);
            }
        };

        fetchMatches();
    }, [searchParams]);

    const groupMatchesByRound = (data: Match[]) => {
        const groups: Record<number, Match[]> = {};
        data.forEach(m => {
            // Use round_calculated if available, or fallback to 0 (Unknown)
            const r = m.round_calculated || 0;
            if (!groups[r]) groups[r] = [];
            groups[r].push(m);
        });
        setGroupedMatches(groups);
    };

    // Sort rounds
    const rounds = Object.keys(groupedMatches).map(Number).sort((a, b) => a - b);

    return (
        <main className="min-h-screen bg-slate-900 text-white p-8">
            <div className="container mx-auto max-w-6xl">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-orange-400">📅 Calendário do Campeonato</h1>
                        <p className="text-slate-400">Estrutura completa por Jornada.</p>
                    </div>
                    <a href="/" className="text-slate-400 hover:text-white">← Voltar</a>
                </div>

                <UniversalFilter />

                {!league || !season ? (
                    <div className="bg-slate-800 p-12 rounded-lg border border-slate-700 text-center border-dashed">
                        <span className="text-4xl block mb-4">👆</span>
                        <h3 className="text-xl font-bold text-slate-300 mb-2">Selecione uma Liga e Época</h3>
                        <p className="text-slate-500">Para ver o calendário completo, precisamos saber qual o campeonato.</p>
                    </div>
                ) : loading ? (
                    <div className="text-center py-20 text-slate-500">A carregar todas as jornadas... ⚽</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {rounds.map(r => (
                            <div key={r} className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700 shadow-lg flex flex-col">
                                <div className="bg-slate-700/50 p-3 border-b border-slate-700 flex justify-between items-center">
                                    <h3 className="font-bold text-orange-300">Jornada {r > 0 ? r : 'Extra/Desconhecida'}</h3>
                                    <span className="text-xs text-slate-400">{groupedMatches[r].length} Jogos</span>
                                </div>
                                <div className="divide-y divide-slate-700/50">
                                    {groupedMatches[r].map(m => (
                                        <div key={m.id} className="p-3 hover:bg-slate-700/30 transition-colors text-sm">
                                            <div className="flex justify-between text-xs text-slate-500 mb-1">
                                                <span>{new Date(m.match_date).toLocaleDateString()}</span>
                                                <span>{m.status}</span>
                                            </div>
                                            <div className="flex justify-between items-center">
                                                <div className="flex-1 text-right pr-2 font-medium truncate" title={m.home_team.name}>
                                                    {m.home_team.name}
                                                </div>
                                                <div className="bg-slate-900 px-2 py-1 rounded text-xs font-mono whitespace-nowrap">
                                                    {m.home_score !== null ? `${m.home_score} - ${m.away_score}` : 'vs'}
                                                </div>
                                                <div className="flex-1 text-left pl-2 font-medium truncate" title={m.away_team.name}>
                                                    {m.away_team.name}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </main>
    );
}
