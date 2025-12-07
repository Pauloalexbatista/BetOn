'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'next/navigation';
import UniversalFilter from '@/components/shared/UniversalFilter';

interface Team {
    id: number;
    name: string;
    logo_url?: string;
}

interface Match {
    id: number;
    home_team: Team;
    away_team: Team;
    league: string;
    match_date: string;
    status: string;
    home_score?: number;
    away_score?: number;
    home_odds?: number;
    draw_odds?: number;
    away_odds?: number;
    round_calculated?: number;
    home_position?: number;
    away_position?: number;
}

export default function MatchesPage() {
    const searchParams = useSearchParams();
    const [matches, setMatches] = useState<Match[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Fetch Matches with Filters (URL Params handled by UniversalFilter)
    useEffect(() => {
        const fetchMatches = async () => {
            setLoading(true);
            try {
                // searchParams contains ?league=X&season=Y etc. which backend accepts
                const queryString = searchParams.toString();
                const response = await axios.get(`http://localhost:8000/api/matches/?${queryString}`);
                setMatches(response.data);
                setLoading(false);
            } catch (err) {
                console.error("Error fetching matches:", err);
                setError('Failed to load matches. Is the backend running?');
                setLoading(false);
            }
        };

        fetchMatches();
    }, [searchParams]);

    // Sorting State
    const [sortConfig, setSortConfig] = useState<{ key: keyof Match | 'home_team' | 'away_team', direction: 'asc' | 'desc' } | null>(null);

    // Sorting Helper
    const sortedMatches = [...matches].sort((a, b) => {
        if (!sortConfig) return 0;

        let aValue: any = a[sortConfig.key as keyof Match];
        let bValue: any = b[sortConfig.key as keyof Match];

        // Access nested properties
        if (sortConfig.key === 'home_team') {
            aValue = a.home_team.name;
            bValue = b.home_team.name;
        } else if (sortConfig.key === 'away_team') {
            aValue = a.away_team.name;
            bValue = b.away_team.name;
        }

        if (aValue < bValue) {
            return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
            return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
    });

    const requestSort = (key: keyof Match | 'home_team' | 'away_team') => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    const getSortIcon = (key: string) => {
        if (!sortConfig || sortConfig.key !== key) return <span className="text-slate-600 ml-1">↕</span>;
        return <span className="text-blue-400 ml-1">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>;
    };

    if (loading && matches.length === 0) return <div className="p-8 text-white text-center">Loading matches...</div>;
    if (error) return <div className="p-8 text-red-500 text-center">{error}</div>;

    return (
        <main className="min-h-screen bg-slate-900 text-white p-8">
            <div className="container mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold">Jogos</h1>
                    <a href="/" className="text-slate-400 hover:text-white">← Voltar</a>
                </div>

                {/* Filters Row */}
                <UniversalFilter />

                <div className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700 mt-6">
                    <table className="w-full text-left">
                        <thead className="bg-slate-700">
                            <tr>
                                <th onClick={() => requestSort('match_date')} className="p-4 cursor-pointer hover:bg-slate-600 select-none">
                                    Data {getSortIcon('match_date')}
                                </th>
                                <th onClick={() => requestSort('league')} className="p-4 cursor-pointer hover:bg-slate-600 select-none">
                                    Liga {getSortIcon('league')}
                                </th>
                                <th onClick={() => requestSort('home_team')} className="p-4 text-right cursor-pointer hover:bg-slate-600 select-none">
                                    Casa {getSortIcon('home_team')}
                                </th>
                                <th className="p-4 text-center">vs</th>
                                <th onClick={() => requestSort('away_team')} className="p-4 cursor-pointer hover:bg-slate-600 select-none">
                                    Fora {getSortIcon('away_team')}
                                </th>
                                <th className="p-4 text-center text-xs text-slate-400">1</th>
                                <th className="p-4 text-center text-xs text-slate-400">X</th>
                                <th className="p-4 text-center text-xs text-slate-400">2</th>
                                <th onClick={() => requestSort('status')} className="p-4 cursor-pointer hover:bg-slate-600 select-none">
                                    Status {getSortIcon('status')}
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                            {sortedMatches.map((match) => (
                                <tr key={match.id} className="hover:bg-slate-700/50 transition-colors">
                                    <td className="p-4 text-slate-300">
                                        <div>{new Date(match.match_date).toLocaleDateString()}</div>
                                        <div className="text-xs text-slate-500">Jornada {match.round_calculated}</div>
                                    </td>
                                    <td className="p-4 text-slate-400 text-sm">{match.league}</td>
                                    <td className="p-4 text-right font-medium">
                                        {match.home_team.name}
                                        {match.home_position && <span className="ml-2 text-xs bg-slate-700 px-1 rounded text-slate-300">#{match.home_position}</span>}
                                    </td>
                                    <td className="p-4 text-center text-slate-500">
                                        {match.home_score !== null ? (
                                            <span className="bg-slate-900 px-2 py-1 rounded font-mono">
                                                {match.home_score} - {match.away_score}
                                            </span>
                                        ) : (
                                            "vs"
                                        )}
                                    </td>
                                    <td className="p-4 font-medium">
                                        {match.away_team.name}
                                        {match.away_position && <span className="ml-2 text-xs bg-slate-700 px-1 rounded text-slate-300">#{match.away_position}</span>}
                                    </td>
                                    <td className="p-4 text-center text-xs text-yellow-400 font-mono">
                                        {match.home_odds ? match.home_odds.toFixed(2) : '-'}
                                    </td>
                                    <td className="p-4 text-center text-xs text-yellow-400 font-mono">
                                        {match.draw_odds ? match.draw_odds.toFixed(2) : '-'}
                                    </td>
                                    <td className="p-4 text-center text-xs text-yellow-400 font-mono">
                                        {match.away_odds ? match.away_odds.toFixed(2) : '-'}
                                    </td>
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-xs ${match.status === 'finished' ? 'bg-green-900 text-green-300' :
                                            match.status === 'scheduled' ? 'bg-blue-900 text-blue-300' :
                                                'bg-slate-600'
                                            }`}>
                                            {match.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {matches.length === 0 && !loading && (
                        <div className="p-8 text-center text-slate-500">
                            Nenhum jogo encontrado.
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}
