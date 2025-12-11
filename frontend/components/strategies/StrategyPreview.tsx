/**
 * Strategy Preview Component - Enhanced
 * Shows quick preview with auto-refresh and history
 */

"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';

interface PreviewResult {
    matches_found: number;
    win_rate: number;
    roi_estimate: number;
    total_profit: number;
    sample_matches: Array<{
        id: number;
        date: string;
        home: string;
        away: string;
        result: boolean;
        odds: number;
        ev?: number;
    }>;
    accumulators?: Array<{
        date: string;
        legs: number;
        combined_odds: number;
        is_win: boolean;
        profit: number;
        matches: Array<{
            id: number;
            date: string;
            home: string;
            away: string;
            result: boolean;
            odds: number;
            ev?: number;
        }>;
    }>;
    upcoming_matches?: {
        matches: Array<any>;
        accumulators: Array<{
            date: string;
            legs: number;
            combined_odds: number;
            matches: Array<{
                id: number;
                date: string;
                home: string;
                away: string;
            }>;
        }>;
    };
    target_outcome?: string; // Add this
    execution_time_ms: number;
}

interface StrategyPreviewProps {
    conditions: any[];
    targetOutcome: string;
    leagues: string[];
    teams: string[];
}

export default function StrategyPreview({
    conditions,
    targetOutcome,
    leagues,
    teams
}: StrategyPreviewProps) {
    const [preview, setPreview] = useState<PreviewResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [previewHistory, setPreviewHistory] = useState<PreviewResult[]>([]);
    const [mode, setMode] = useState<'single' | 'acca' | 'upcoming'>('single'); // Unified types

    // Auto-refresh with debounce
    useEffect(() => {
        if (!autoRefresh || conditions.length === 0) return;

        const timer = setTimeout(() => {
            fetchPreview();
        }, 1500); // 1.5s debounce

        return () => clearTimeout(timer);
    }, [conditions, targetOutcome, leagues, teams, autoRefresh]);

    const fetchPreview = async () => {
        if (conditions.length === 0) {
            setError('Adicione pelo menos uma condição para ver preview');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const res = await axios.post('http://127.0.0.1:8000/api/strategies/preview', {
                conditions,
                target_outcome: targetOutcome,
                leagues: leagues.length > 0 ? leagues : null,
                teams: teams.length > 0 ? teams : null,
                limit: 100
            });
            setPreview(res.data);

            // Save to history (keep last 3)
            if (res.data) {
                setPreviewHistory(prev => [res.data, ...prev].slice(0, 3));
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Erro ao gerar preview');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (conditions.length === 0) {
        return (
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 text-center">
                <p className="text-slate-400">💡 Adicione condições para ver preview da estratégia</p>
            </div>
        );
    }

    return (
        <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-lg p-6">
            {/* Header with Mode Toggle & Stats */}
            <div className="flex flex-col gap-4 mb-4">
                <div className="flex justify-between items-center">
                    <div>
                        <h3 className="text-lg font-bold text-blue-400">🔍 Preview Rápido</h3>
                        <div className="flex items-center gap-3 mt-1">
                            {autoRefresh && (
                                <span className="text-xs text-green-400 flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                                    Ativo
                                </span>
                            )}
                        </div>
                    </div>

                    <button
                        onClick={fetchPreview}
                        disabled={loading}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded text-sm transition-colors font-medium"
                    >
                        {loading ? '⏳' : '🔄'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="bg-red-900/20 border border-red-500 rounded p-3 text-red-300 text-sm mb-4">
                    ❌ {error}
                </div>
            )}

            {/* Loading Skeleton */}
            {loading && !preview && (
                <div className="space-y-4 animate-pulse">
                    <div className="h-32 bg-slate-800/50 rounded-lg"></div>
                </div>
            )}

            {preview && (
                <div className="space-y-4">
                    {/* Metrics Grid */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
                            <p className="text-xs text-slate-400 mb-1">Jogos Encontrados</p>
                            <div className="flex items-baseline gap-2">
                                <p className="text-3xl font-bold text-white">{preview.matches_found}</p>
                                {preview.upcoming_matches && preview.upcoming_matches.matches.length > 0 && (
                                    <span className="text-sm font-bold text-emerald-400 animate-pulse">
                                        + {preview.upcoming_matches.matches.length} Futuros
                                    </span>
                                )}
                            </div>
                            <p className="text-xs text-slate-500 mt-1">de 100 analisados</p>
                        </div>

                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
                            <p className="text-xs text-slate-400 mb-1">Win Rate</p>
                            <p className={`text-3xl font-bold ${preview.win_rate >= 55 ? 'text-green-400' :
                                preview.win_rate >= 45 ? 'text-yellow-400' :
                                    'text-red-400'
                                }`}>
                                {preview.win_rate}%
                            </p>
                            <p className="text-xs text-slate-500 mt-1">
                                {preview.win_rate >= 55 ? '✅ Excelente' : '⚠️ Normal'}
                            </p>
                        </div>

                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
                            <p className="text-xs text-slate-400 mb-1">ROI Estimado</p>
                            <p className={`text-3xl font-bold ${preview.roi_estimate >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {preview.roi_estimate > 0 ? '+' : ''}{preview.roi_estimate}%
                            </p>
                            <p className="text-xs text-slate-500 mt-1">
                                €{preview.total_profit > 0 ? '+' : ''}{preview.total_profit.toFixed(2)}
                            </p>
                        </div>
                    </div>

                    {/* History Comparison */}
                    {previewHistory.length > 1 && (
                        <div className="p-3 bg-slate-800/30 rounded border border-slate-700">
                            <p className="text-xs text-slate-400 mb-2 font-medium">📊 Comparação com Anterior:</p>
                            <div className="flex gap-6 text-xs">
                                <div className="flex items-center gap-2">
                                    <span className="text-slate-500">Win Rate:</span>
                                    <span className="text-slate-400">{previewHistory[1].win_rate}%</span>
                                    <span className="text-slate-600">→</span>
                                    <span className={`font-bold ${previewHistory[0].win_rate > previewHistory[1].win_rate
                                        ? 'text-green-400'
                                        : previewHistory[0].win_rate < previewHistory[1].win_rate
                                            ? 'text-red-400'
                                            : 'text-slate-400'
                                        }`}>
                                        {previewHistory[0].win_rate}%
                                        {previewHistory[0].win_rate > previewHistory[1].win_rate ? ' ↑' :
                                            previewHistory[0].win_rate < previewHistory[1].win_rate ? ' ↓' : ' →'}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="text-slate-500">ROI:</span>
                                    <span className="text-slate-400">{previewHistory[1].roi_estimate}%</span>
                                    <span className="text-slate-600">→</span>
                                    <span className={`font-bold ${previewHistory[0].roi_estimate > previewHistory[1].roi_estimate
                                        ? 'text-green-400'
                                        : previewHistory[0].roi_estimate < previewHistory[1].roi_estimate
                                            ? 'text-red-400'
                                            : 'text-slate-400'
                                        }`}>
                                        {previewHistory[0].roi_estimate > 0 ? '+' : ''}{previewHistory[0].roi_estimate}%
                                        {previewHistory[0].roi_estimate > previewHistory[1].roi_estimate ? ' ↑' :
                                            previewHistory[0].roi_estimate < previewHistory[1].roi_estimate ? ' ↓' : ' →'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Content Area - Switch based on Mode */}
                    <div className="flex gap-2 mb-4">
                        <button
                            onClick={() => setMode('single')}
                            className={`flex-1 py-1.5 px-3 rounded text-xs font-bold transition-all ${mode === 'single'
                                ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                }`}
                        >
                            Simples (Histórico)
                        </button>
                        <button
                            onClick={() => setMode('acca')}
                            className={`flex-1 py-1.5 px-3 rounded text-xs font-bold transition-all ${mode === 'acca'
                                ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50'
                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                }`}
                        >
                            Múltiplas (Accas)
                        </button>
                        <button
                            onClick={() => setMode('upcoming')}
                            className={`flex-1 py-1.5 px-3 rounded text-xs font-bold transition-all ${mode === 'upcoming'
                                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/50'
                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                }`}
                        >
                            Próximos Jogos 🚀
                        </button>
                    </div>

                    {mode === 'single' && (
                        <>
                            {/* Sample Matches (Single) */}
                            {preview.sample_matches.length > 0 && (
                                <div>
                                    <p className="text-sm text-slate-400 mb-2 font-medium">📋 Exemplos de Jogos (Passado):</p>
                                    <div className="space-y-1.5 h-64 overflow-y-auto pr-1">
                                        {preview.sample_matches.map((match: any, idx: number) => (
                                            <div
                                                key={idx}
                                                className={`p-2 rounded border flex flex-col gap-1 ${match.result
                                                    ? 'bg-green-900/10 border-green-900/30'
                                                    : 'bg-red-900/10 border-red-900/30'
                                                    }`}
                                            >
                                                <div className="flex justify-between items-center text-xs">
                                                    <span className="font-medium text-slate-200">
                                                        {match.home} <span className="text-slate-500">vs</span> {match.away}
                                                    </span>
                                                    <span className="text-slate-500">
                                                        {new Date(match.date).toLocaleDateString('pt-PT')}
                                                    </span>
                                                </div>
                                                <div className="flex justify-between items-center text-xs">
                                                    <span className={`px-1.5 rounded bg-slate-800 text-slate-400`}>
                                                        {preview.target_outcome || 'Match Winner'}
                                                    </span>
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-slate-400">@{match.odds.toFixed(2)}</span>
                                                        <span className={`font-bold ${match.result ? 'text-green-500' : 'text-red-500'}`}>
                                                            {match.result ? 'WON' : 'LOST'}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    )}

                    {mode === 'acca' && (
                        <>
                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <p className="text-sm text-slate-400 font-medium">🚀 Múltiplas Diárias (Simulação Histórica)</p>
                                    <span className="text-xs px-2 py-0.5 rounded bg-purple-900/30 text-purple-300 border border-purple-800">
                                        Top picks agrupadas por dia
                                    </span>
                                </div>
                                <div className="space-y-3 h-64 overflow-y-auto pr-1">
                                    {(preview.accumulators && preview.accumulators.length > 0) ? (
                                        <div className="space-y-3">
                                            {preview.accumulators.map((acca: any, idx: number) => (
                                                <div key={idx} className="bg-slate-800/50 rounded border border-slate-700 p-3">
                                                    <div className="flex justify-between items-start mb-2">
                                                        <div>
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-sm font-bold text-white text-purple-200">
                                                                    {acca.date}
                                                                </span>
                                                                <span className="text-[10px] bg-slate-700 text-slate-300 px-1 rounded">
                                                                    {acca.legs} Jogos
                                                                </span>
                                                            </div>
                                                        </div>
                                                        <div className="text-right">
                                                            <span className="block text-xs text-slate-400">Odd Combinada</span>
                                                            <span className="font-mono text-purple-300 font-bold">{acca.combined_odds.toFixed(2)}</span>
                                                        </div>
                                                    </div>

                                                    {/* Mini list of legs */}
                                                    <div className="space-y-1 mb-2">
                                                        {acca.matches.map((m: any, mi: number) => (
                                                            <div key={mi} className="flex justify-between text-xs text-slate-500">
                                                                <span>{m.home} vs {m.away}</span>
                                                                <span className={m.result ? 'text-green-500' : 'text-red-500'}>
                                                                    @{m.odds.toFixed(2)} {m.result ? '✓' : '✗'}
                                                                </span>
                                                            </div>
                                                        ))}
                                                    </div>

                                                    <div className={`mt-2 py-1 px-2 rounded text-center text-xs font-bold ${acca.is_win
                                                        ? 'bg-green-900/50 text-green-300 border border-green-700'
                                                        : 'bg-red-900/50 text-red-300 border border-red-700'}`}>
                                                        {acca.is_win ? `✅ GANHO (+€${acca.profit.toFixed(2)})` : `❌ PERDIDO (-€10.00)`}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-center py-8 text-slate-500 text-sm">
                                            Não existem jogos suficientes no mesmo dia para criar múltiplas.
                                        </div>
                                    )}
                                </div>
                            </div>
                        </>
                    )}

                    {mode === 'upcoming' && (
                        <>
                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <p className="text-sm text-emerald-400 font-medium">📅 Próximos Jogos & Múltiplas</p>
                                    <span className="text-xs px-2 py-0.5 rounded bg-emerald-900/30 text-emerald-300 border border-emerald-800">
                                        Oportunidades Futuras
                                    </span>
                                </div>

                                {preview.upcoming_matches && preview.upcoming_matches.accumulators && preview.upcoming_matches.accumulators.length > 0 ? (
                                    <div className="space-y-3 h-64 overflow-y-auto pr-1">
                                        {preview.upcoming_matches.accumulators.map((acca: any, idx: number) => (
                                            <div key={idx} className="bg-slate-800/80 rounded border border-emerald-700/50 p-3 shadow-lg shadow-emerald-900/10">
                                                <div className="flex justify-between items-start mb-2">
                                                    <div>
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-sm font-bold text-emerald-200">
                                                                {acca.date}
                                                            </span>
                                                            <span className="text-[10px] bg-slate-700 text-slate-300 px-1 rounded">
                                                                {acca.legs} Jogos
                                                            </span>
                                                        </div>
                                                        <span className="text-[10px] text-slate-400">Agendado</span>
                                                    </div>
                                                    <div className="text-right">
                                                        <span className="block text-xs text-slate-400">Odd Estimada</span>
                                                        {/* Odds are 1.0 for future typically, or real if we have them. Assuming 1.0 for unknown */}
                                                        <span className="font-mono text-emerald-300 font-bold">
                                                            {acca.combined_odds > 1 ? acca.combined_odds.toFixed(2) : '--'}
                                                        </span>
                                                    </div>
                                                </div>

                                                <div className="space-y-1 mb-2">
                                                    {acca.matches.map((m: any, mi: number) => (
                                                        <div key={mi} className="flex justify-between text-xs text-slate-400">
                                                            <span className="text-slate-200">{m.home} vs {m.away}</span>
                                                            <span className="text-slate-500">
                                                                {new Date(m.date).toLocaleDateString('pt-PT')}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>

                                                <button className="w-full mt-2 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-bold transition-colors">
                                                    Criar Aposta Agora
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-12 bg-slate-800/30 rounded border border-dashed border-slate-700">
                                        <p className="text-slate-400 mb-1">Nenhum jogo futuro encontrado.</p>
                                        <p className="text-xs text-slate-500">Verifique se as equipas têm jogos agendados.</p>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                    {/* Interpretation */}
                    {preview.matches_found > 0 && (
                        <div className={`p-4 rounded-lg border ${preview.roi_estimate >= 5
                            ? 'bg-green-900/20 border-green-700 text-green-300'
                            : preview.roi_estimate >= 0
                                ? 'bg-yellow-900/20 border-yellow-700 text-yellow-300'
                                : 'bg-red-900/20 border-red-700 text-red-300'
                            }`}>
                            <p className="text-sm font-medium">
                                {preview.roi_estimate >= 5
                                    ? '✅ Estratégia promissora! ROI positivo e win rate sólido.'
                                    : preview.roi_estimate >= 0
                                        ? '⚠️ Estratégia marginal. Considere ajustar condições.'
                                        : '❌ Estratégia não lucrativa. Recomenda-se modificar.'}
                            </p>
                        </div>
                    )}

                    {preview.matches_found === 0 && (
                        <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4 text-yellow-300">
                            <p className="text-sm font-medium">
                                ⚠️ Nenhum jogo encontrado! Condições muito restritivas.
                            </p>
                            <p className="text-xs mt-1 text-yellow-400">
                                Sugestão: Relaxe alguns valores ou remova condições.
                            </p>
                        </div>
                    )}

                    {/* Footer */}
                    <p className="text-xs text-slate-500 text-center pt-2 border-t border-slate-700">
                        Baseado em {preview.matches_found} jogos • Calculado em {preview.execution_time_ms}ms
                    </p>
                </div>
            )}
            {!preview && !loading && (
                <div className="text-center py-12 text-slate-400">
                    <div className="text-4xl mb-3">📊</div>
                    <p className="font-medium">Clique em "Atualizar" ou ative auto-atualização</p>
                    <p className="text-xs text-slate-500 mt-1">
                        Análise rápida baseada nos últimos 100 jogos
                    </p>
                </div>
            )}
        </div>
    );
}
