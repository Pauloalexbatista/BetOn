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
    }>;
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
            const res = await axios.post('http://localhost:8000/api/strategies/preview', {
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
            {/* Header with Auto-refresh Toggle */}
            <div className="flex justify-between items-center mb-4">
                <div>
                    <h3 className="text-lg font-bold text-blue-400">🔍 Preview Rápido</h3>
                    <div className="flex items-center gap-3 mt-1">
                        <label className="text-xs text-slate-400 flex items-center gap-1.5 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={autoRefresh}
                                onChange={(e) => setAutoRefresh(e.target.checked)}
                                className="rounded w-3.5 h-3.5"
                            />
                            Auto-atualizar
                        </label>
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
                    {loading ? '⏳ A calcular...' : '🔄 Atualizar'}
                </button>
            </div>

            {error && (
                <div className="bg-red-900/20 border border-red-500 rounded p-3 text-red-300 text-sm mb-4">
                    ❌ {error}
                </div>
            )}

            {/* Loading Skeleton */}
            {loading && !preview && (
                <div className="space-y-4 animate-pulse">
                    <div className="grid grid-cols-3 gap-4">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="bg-slate-800/50 rounded-lg h-24"></div>
                        ))}
                    </div>
                    <div className="h-32 bg-slate-800/50 rounded-lg"></div>
                </div>
            )}

            {preview && (
                <div className="space-y-4">
                    {/* Metrics Grid */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
                            <p className="text-xs text-slate-400 mb-1">Jogos Encontrados</p>
                            <p className="text-3xl font-bold text-white">{preview.matches_found}</p>
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
                                {preview.win_rate >= 55 ? '✅ Excelente' :
                                    preview.win_rate >= 45 ? '⚠️ Razoável' :
                                        '❌ Fraco'}
                            </p>
                        </div>

                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
                            <p className="text-xs text-slate-400 mb-1">ROI Estimado</p>
                            <p className={`text-3xl font-bold ${preview.roi_estimate >= 5 ? 'text-green-400' :
                                    preview.roi_estimate >= 0 ? 'text-yellow-400' :
                                        'text-red-400'
                                }`}>
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

                    {/* Sample Matches */}
                    {preview.sample_matches.length > 0 && (
                        <div>
                            <p className="text-sm text-slate-400 mb-2 font-medium">📋 Exemplos de Jogos Matched:</p>
                            <div className="space-y-1.5">
                                {preview.sample_matches.map((match, idx) => (
                                    <div
                                        key={idx}
                                        className="flex items-center justify-between bg-slate-800/30 rounded-lg p-3 text-sm hover:bg-slate-800/50 transition-colors"
                                    >
                                        <div className="flex-1">
                                            <span className="text-slate-300 font-medium">
                                                {match.home} <span className="text-slate-500">vs</span> {match.away}
                                            </span>
                                            <span className="text-xs text-slate-500 ml-2">
                                                {new Date(match.date).toLocaleDateString('pt-PT')}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs text-slate-400 font-mono">
                                                @{match.odds.toFixed(2)}
                                            </span>
                                            <span className={`px-2.5 py-1 rounded text-xs font-bold ${match.result
                                                    ? 'bg-green-900/50 text-green-300 border border-green-700'
                                                    : 'bg-red-900/50 text-red-300 border border-red-700'
                                                }`}>
                                                {match.result ? '✅ WON' : '❌ LOST'}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
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
