'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, TrendingUp, BarChart3, Calendar } from 'lucide-react';

interface MarketData {
    count: number;
    percentage: number;
}

interface BettingMarkets {
    total_matches: number;
    season: string;
    markets: {
        over_under: {
            [key: string]: MarketData;
        };
        btts: {
            yes: MarketData;
            no: MarketData;
        };
        '1x2': {
            home_win: MarketData;
            draw: MarketData;
            away_win: MarketData;
        };
    };
}

interface MarketsData {
    betting_markets: {
        all_time: BettingMarkets;
        current_season: BettingMarkets | null;
    };
    summary: {
        available_seasons: string[];
        current_season: string | null;
    };
}

export default function MarketsPage() {
    const [data, setData] = useState<MarketsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedView, setSelectedView] = useState<'all' | 'current'>('all');

    useEffect(() => {
        fetchMarketsData();
    }, []);

    const fetchMarketsData = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:8000/api/analysis/pareto-analysis');

            if (!response.ok) {
                throw new Error('Failed to fetch markets data');
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

    const currentMarkets = selectedView === 'all'
        ? data.betting_markets.all_time
        : data.betting_markets.current_season || data.betting_markets.all_time;

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-4xl font-bold mb-2">📊 Análise de Mercados</h1>
                    <p className="text-muted-foreground">
                        Estatísticas completas de todos os mercados de apostas
                    </p>
                </div>

                {/* Season Filter */}
                <div className="flex gap-2">
                    <button
                        onClick={() => setSelectedView('all')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${selectedView === 'all'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                            }`}
                    >
                        📈 Histórico Completo
                    </button>
                    <button
                        onClick={() => setSelectedView('current')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${selectedView === 'current'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                            }`}
                    >
                        🔥 Época Atual ({data.summary.current_season})
                    </button>
                </div>
            </div>

            {/* Summary Card */}
            <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Calendar className="h-5 w-5" />
                        {currentMarkets.season}
                    </CardTitle>
                    <CardDescription>
                        Análise baseada em {currentMarkets.total_matches} jogos
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="text-sm text-muted-foreground">
                        {data.summary.available_seasons.length} épocas disponíveis: {data.summary.available_seasons.join(', ')}
                    </div>
                </CardContent>
            </Card>

            {/* Over/Under Markets */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-green-600" />
                        Mercado Over/Under
                    </CardTitle>
                    <CardDescription>
                        Percentagem de jogos com mais ou menos golos
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(currentMarkets.markets.over_under).map(([market, data]) => {
                            const isOver = market.startsWith('over');
                            const threshold = market.split('_')[1];

                            return (
                                <div
                                    key={market}
                                    className={`p-4 rounded-lg border-2 ${isOver
                                            ? 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800'
                                            : 'bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800'
                                        }`}
                                >
                                    <div className="text-xs font-medium text-muted-foreground uppercase mb-1">
                                        {isOver ? 'Over' : 'Under'} {threshold}
                                    </div>
                                    <div className={`text-3xl font-bold ${isOver ? 'text-green-600 dark:text-green-400' : 'text-blue-600 dark:text-blue-400'
                                        }`}>
                                        {data.percentage}%
                                    </div>
                                    <div className="text-xs text-muted-foreground mt-1">
                                        {data.count} jogos
                                    </div>

                                    {/* Progress bar */}
                                    <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full ${isOver ? 'bg-green-600' : 'bg-blue-600'}`}
                                            style={{ width: `${data.percentage}%` }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Insights */}
                    <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                        <p className="text-sm font-medium">💡 Insight:</p>
                        <p className="text-sm text-muted-foreground mt-1">
                            Over 1.5 Goals ({currentMarkets.markets.over_under['over_1.5'].percentage}%) é o mercado mais seguro com alta probabilidade.
                            Over 2.5 ({currentMarkets.markets.over_under['over_2.5'].percentage}%) está próximo de 50/50.
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* BTTS Market */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="h-5 w-5 text-purple-600" />
                        BTTS (Both Teams To Score)
                    </CardTitle>
                    <CardDescription>
                        Probabilidade de ambas as equipas marcarem
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-6 rounded-lg bg-purple-50 dark:bg-purple-950/20 border-2 border-purple-200 dark:border-purple-800">
                            <div className="text-sm font-medium text-muted-foreground uppercase mb-2">
                                BTTS Yes
                            </div>
                            <div className="text-4xl font-bold text-purple-600 dark:text-purple-400">
                                {currentMarkets.markets.btts.yes.percentage}%
                            </div>
                            <div className="text-sm text-muted-foreground mt-2">
                                {currentMarkets.markets.btts.yes.count} jogos
                            </div>
                            <div className="mt-3 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-purple-600"
                                    style={{ width: `${currentMarkets.markets.btts.yes.percentage}%` }}
                                />
                            </div>
                        </div>

                        <div className="p-6 rounded-lg bg-gray-50 dark:bg-gray-900 border-2 border-gray-200 dark:border-gray-700">
                            <div className="text-sm font-medium text-muted-foreground uppercase mb-2">
                                BTTS No
                            </div>
                            <div className="text-4xl font-bold text-gray-600 dark:text-gray-400">
                                {currentMarkets.markets.btts.no.percentage}%
                            </div>
                            <div className="text-sm text-muted-foreground mt-2">
                                {currentMarkets.markets.btts.no.count} jogos
                            </div>
                            <div className="mt-3 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gray-600"
                                    style={{ width: `${currentMarkets.markets.btts.no.percentage}%` }}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="mt-4 p-4 bg-purple-50 dark:bg-purple-950/20 rounded-lg border border-purple-200 dark:border-purple-800">
                        <p className="text-sm font-medium">💡 Insight:</p>
                        <p className="text-sm text-muted-foreground mt-1">
                            BTTS Yes tem ligeira vantagem ({currentMarkets.markets.btts.yes.percentage}% vs {currentMarkets.markets.btts.no.percentage}%).
                            Mercado equilibrado, ideal para combinar com outras apostas.
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* 1X2 Market */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        🏆 Mercado 1X2 (Resultado Final)
                    </CardTitle>
                    <CardDescription>
                        Distribuição de vitórias em casa, empates e vitórias fora
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                        <div className="p-6 rounded-lg bg-green-50 dark:bg-green-950/20 border-2 border-green-200 dark:border-green-800">
                            <div className="text-sm font-medium text-muted-foreground uppercase mb-2">
                                Casa (1)
                            </div>
                            <div className="text-4xl font-bold text-green-600 dark:text-green-400">
                                {currentMarkets.markets['1x2'].home_win.percentage}%
                            </div>
                            <div className="text-sm text-muted-foreground mt-2">
                                {currentMarkets.markets['1x2'].home_win.count} jogos
                            </div>
                            <div className="mt-3 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-green-600"
                                    style={{ width: `${currentMarkets.markets['1x2'].home_win.percentage}%` }}
                                />
                            </div>
                        </div>

                        <div className="p-6 rounded-lg bg-gray-50 dark:bg-gray-900 border-2 border-gray-200 dark:border-gray-700">
                            <div className="text-sm font-medium text-muted-foreground uppercase mb-2">
                                Empate (X)
                            </div>
                            <div className="text-4xl font-bold text-gray-600 dark:text-gray-400">
                                {currentMarkets.markets['1x2'].draw.percentage}%
                            </div>
                            <div className="text-sm text-muted-foreground mt-2">
                                {currentMarkets.markets['1x2'].draw.count} jogos
                            </div>
                            <div className="mt-3 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gray-600"
                                    style={{ width: `${currentMarkets.markets['1x2'].draw.percentage}%` }}
                                />
                            </div>
                        </div>

                        <div className="p-6 rounded-lg bg-blue-50 dark:bg-blue-950/20 border-2 border-blue-200 dark:border-blue-800">
                            <div className="text-sm font-medium text-muted-foreground uppercase mb-2">
                                Fora (2)
                            </div>
                            <div className="text-4xl font-bold text-blue-600 dark:text-blue-400">
                                {currentMarkets.markets['1x2'].away_win.percentage}%
                            </div>
                            <div className="text-sm text-muted-foreground mt-2">
                                {currentMarkets.markets['1x2'].away_win.count} jogos
                            </div>
                            <div className="mt-3 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-blue-600"
                                    style={{ width: `${currentMarkets.markets['1x2'].away_win.percentage}%` }}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="mt-4 p-4 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-200 dark:border-green-800">
                        <p className="text-sm font-medium">💡 Insight:</p>
                        <p className="text-sm text-muted-foreground mt-1">
                            Vantagem casa significativa: {currentMarkets.markets['1x2'].home_win.percentage}% vs {currentMarkets.markets['1x2'].away_win.percentage}% fora
                            (+{(currentMarkets.markets['1x2'].home_win.percentage - currentMarkets.markets['1x2'].away_win.percentage).toFixed(1)}% diferença).
                            Empates são raros ({currentMarkets.markets['1x2'].draw.percentage}%).
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* Comparison Card */}
            {data.betting_markets.current_season && (
                <Card className="bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-950/20 dark:to-red-950/20">
                    <CardHeader>
                        <CardTitle>📈 Comparação: Histórico vs Época Atual</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <p className="font-medium">Over 2.5 Goals:</p>
                                <p className="text-muted-foreground">
                                    Histórico: {data.betting_markets.all_time.markets.over_under['over_2.5'].percentage}% |
                                    Atual: {data.betting_markets.current_season.markets.over_under['over_2.5'].percentage}%
                                    <span className={`ml-2 font-bold ${data.betting_markets.current_season.markets.over_under['over_2.5'].percentage <
                                            data.betting_markets.all_time.markets.over_under['over_2.5'].percentage
                                            ? 'text-red-600' : 'text-green-600'
                                        }`}>
                                        ({data.betting_markets.current_season.markets.over_under['over_2.5'].percentage -
                                            data.betting_markets.all_time.markets.over_under['over_2.5'].percentage > 0 ? '+' : ''}
                                        {(data.betting_markets.current_season.markets.over_under['over_2.5'].percentage -
                                            data.betting_markets.all_time.markets.over_under['over_2.5'].percentage).toFixed(1)}%)
                                    </span>
                                </p>
                            </div>
                            <div>
                                <p className="font-medium">BTTS Yes:</p>
                                <p className="text-muted-foreground">
                                    Histórico: {data.betting_markets.all_time.markets.btts.yes.percentage}% |
                                    Atual: {data.betting_markets.current_season.markets.btts.yes.percentage}%
                                    <span className={`ml-2 font-bold ${data.betting_markets.current_season.markets.btts.yes.percentage <
                                            data.betting_markets.all_time.markets.btts.yes.percentage
                                            ? 'text-red-600' : 'text-green-600'
                                        }`}>
                                        ({data.betting_markets.current_season.markets.btts.yes.percentage -
                                            data.betting_markets.all_time.markets.btts.yes.percentage > 0 ? '+' : ''}
                                        {(data.betting_markets.current_season.markets.btts.yes.percentage -
                                            data.betting_markets.all_time.markets.btts.yes.percentage).toFixed(1)}%)
                                    </span>
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
