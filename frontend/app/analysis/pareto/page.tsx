'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Award, Filter, FileText } from 'lucide-react';

interface TeamData {
    team_id: number;
    name: string;
    total_matches: number;
    wins: number;
    draws: number;
    losses: number;
    win_rate: number;
    over_25_rate: number;
    btts_rate: number;
    home_win_rate: number;
    points: number;
    points_percentage: number;
}

interface ParetoResponse {
    teams: TeamData[];
    top_20_percent: TeamData[];
    top_20_count: number;
    total_teams: number;
    total_matches: number;
    season: string;
    market: string;
}

export default function ParetoReportPage() {
    const [data, setData] = useState<ParetoResponse | null>(null);
    const [seasons, setSeasons] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [selectedSeason, setSelectedSeason] = useState<string>('all');
    const [selectedMarket, setSelectedMarket] = useState<string>('win_rate');

    useEffect(() => {
        fetchSeasons();
    }, []);

    useEffect(() => {
        if (seasons.length > 0 || selectedSeason === 'all') {
            fetchData();
        }
    }, [selectedSeason, selectedMarket]);

    const fetchSeasons = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/analysis/pareto-analysis');
            const result = await response.json();
            setSeasons(result.summary.available_seasons || []);
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch seasons:', err);
            setLoading(false);
        }
    };

    const fetchData = async () => {
        try {
            setLoading(true);
            const seasonParam = selectedSeason === 'all' ? '' : `?season=${selectedSeason}`;
            const marketParam = selectedSeason === 'all' ? `?market=${selectedMarket}` : `&market=${selectedMarket}`;

            const url = `http://localhost:8000/api/analysis/pareto-teams${seasonParam}${marketParam}`;

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }

            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Loader2 className="h-8 w-8 animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mx-auto p-6">
                <Card className="border-red-500">
                    <CardHeader>
                        <CardTitle className="text-red-500">Error</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p>{error}</p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (!data) return null;

    const getMarketValue = (team: TeamData) => {
        switch (selectedMarket) {
            case 'over_2.5': return team.over_25_rate;
            case 'btts_yes': return team.btts_rate;
            case 'home_win': return team.home_win_rate;
            default: return team.win_rate;
        }
    };

    const getMarketLabel = () => {
        switch (selectedMarket) {
            case 'over_2.5': return 'Over 2.5%';
            case 'btts_yes': return 'BTTS%';
            case 'home_win': return 'Home Win%';
            default: return 'Win Rate';
        }
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            <div>
                <h1 className="text-4xl font-bold mb-2 flex items-center gap-2">
                    <FileText className="h-8 w-8" />
                    Relatório Pareto (80/20)
                </h1>
                <p className="text-muted-foreground">
                    Análise dos top 20% performers por época e mercado
                </p>
            </div>

            {/* Filters */}
            <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Filter className="h-5 w-5" />
                        Filtros
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">📅 Época</label>
                            <select
                                value={selectedSeason}
                                onChange={(e) => setSelectedSeason(e.target.value)}
                                className="w-full p-2 border rounded-lg bg-background"
                            >
                                <option value="all">Todas as Épocas</option>
                                {seasons.map((season) => (
                                    <option key={season} value={season}>{season}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">🎯 Mercado</label>
                            <select
                                value={selectedMarket}
                                onChange={(e) => setSelectedMarket(e.target.value)}
                                className="w-full p-2 border rounded-lg bg-background"
                            >
                                <option value="win_rate">Win Rate (Vitórias)</option>
                                <option value="over_2.5">Over 2.5 Goals</option>
                                <option value="btts_yes">BTTS Yes</option>
                                <option value="home_win">Vitória Casa</option>
                            </select>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Equipas</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{data.total_teams}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Top 20%</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-yellow-600">{data.top_20_count}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Jogos</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{data.total_matches}</div>
                        <p className="text-xs text-muted-foreground">{data.season}</p>
                    </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm">{getMarketLabel()}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-600">
                            {data.top_20_percent[0] ? getMarketValue(data.top_20_percent[0]).toFixed(1) : 0}%
                        </div>
                        <p className="text-xs text-muted-foreground">Top Performer</p>
                    </CardContent>
                </Card>
            </div>

            {/* Top 20% */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Award className="h-5 w-5 text-yellow-500" />
                        Top 20% - {getMarketLabel()}
                    </CardTitle>
                    <CardDescription>
                        As {data.top_20_count} equipas com melhor {getMarketLabel()} em {data.season}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {data.top_20_percent.map((team, index) => (
                            <div
                                key={team.team_id}
                                className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 text-white font-bold">
                                        {index + 1}
                                    </div>
                                    <div>
                                        <div className="font-bold text-lg">{team.name}</div>
                                        <div className="text-sm text-muted-foreground">
                                            {team.wins}V - {team.draws}E - {team.losses}D | {team.total_matches} jogos
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-6">
                                    <div className="text-right">
                                        <div className="text-3xl font-bold text-green-600">
                                            {getMarketValue(team).toFixed(1)}%
                                        </div>
                                        <div className="text-xs text-muted-foreground">{getMarketLabel()}</div>
                                    </div>

                                    <Badge variant={getMarketValue(team) >= 70 ? "default" : "secondary"}>
                                        {getMarketValue(team) >= 80 ? "🔥 Elite" : getMarketValue(team) >= 70 ? "⭐ Top" : "✓ Good"}
                                    </Badge>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Complete Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Ranking Completo - {getMarketLabel()}</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b-2">
                                    <th className="text-left p-3">#</th>
                                    <th className="text-left p-3">Equipa</th>
                                    <th className="text-center p-3">Jogos</th>
                                    <th className="text-center p-3">V</th>
                                    <th className="text-center p-3">E</th>
                                    <th className="text-center p-3">D</th>
                                    <th className="text-center p-3">{getMarketLabel()}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.teams.map((team, index) => {
                                    const isTop20 = index < data.top_20_count;
                                    const value = getMarketValue(team);

                                    return (
                                        <tr
                                            key={team.team_id}
                                            className={`border-b hover:bg-accent ${isTop20 ? 'bg-yellow-50 dark:bg-yellow-950/20' : ''}`}
                                        >
                                            <td className="p-3 font-bold">{index + 1}</td>
                                            <td className="p-3 font-semibold">{team.name}</td>
                                            <td className="p-3 text-center">{team.total_matches}</td>
                                            <td className="p-3 text-center text-green-600 font-bold">{team.wins}</td>
                                            <td className="p-3 text-center text-gray-600">{team.draws}</td>
                                            <td className="p-3 text-center text-red-600 font-bold">{team.losses}</td>
                                            <td className="p-3 text-center">
                                                <span className={`font-bold ${value >= 70 ? 'text-green-600' :
                                                        value >= 50 ? 'text-blue-600' : 'text-gray-600'
                                                    }`}>
                                                    {value.toFixed(1)}%
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>

            {/* Insights */}
            <Card className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
                <CardHeader>
                    <CardTitle>💡 Insights</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                    <div className="p-3 bg-white dark:bg-gray-900 rounded-lg">
                        <p className="font-semibold">🎯 Princípio 80/20</p>
                        <p className="text-sm text-muted-foreground mt-1">
                            Focar nos top {data.top_20_count} equipas ({data.season}) pode gerar 80% dos resultados em {getMarketLabel()}.
                        </p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
