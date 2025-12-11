"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
    ArrowPathIcon,
    CheckCircleIcon,
    ExclamationTriangleIcon,
    XCircleIcon
} from "@heroicons/react/24/solid";

interface QualityReport {
    timestamp: string;
    summary: {
        overall_health: string;
        critical_issues: number;
        warnings: number;
        status_message: string;
    };
    teams: any;
    matches: any;
    odds: any;
    gaps: any;
    sources: any;
    recommendations: Recommendation[];
    odds_collector?: {
        last_run: string | null;
        days_ago: number | null;
        hours_ago: number;
        status: string;
        message: string;
    };
}

interface Recommendation {
    priority: string;
    category: string;
    message: string;
    action: string;
    script?: string;
}

export default function DataQualityPage() {
    const [report, setReport] = useState<QualityReport | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
    const [collecting, setCollecting] = useState(false);
    const [consolidating, setConsolidating] = useState(false);

    const fetchReport = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch("http://localhost:8000/api/system/data-quality");
            if (!res.ok) throw new Error("Failed to fetch quality report");
            const data = await res.json();
            setReport(data);
            setLastUpdate(new Date());
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const triggerOddsCollection = async () => {
        setCollecting(true);
        try {
            const res = await fetch("http://localhost:8000/api/system/collect-odds", {
                method: "POST"
            });
            if (!res.ok) throw new Error("Failed to start collection");

            // Wait a bit then refresh
            setTimeout(() => {
                fetchReport();
                setCollecting(false);
            }, 3000);
        } catch (err: any) {
            alert(`Error: ${err.message}`);
            setCollecting(false);
        }
    };

    const triggerTeamConsolidation = async () => {
        if (!confirm("Consolidar equipas duplicadas? Esta ação irá unificar equipas com nomes similares.")) {
            return;
        }

        setConsolidating(true);
        try {
            const res = await fetch("http://localhost:8000/api/system/consolidate-teams", {
                method: "POST"
            });
            if (!res.ok) throw new Error("Failed to start consolidation");

            // Wait a bit then refresh
            setTimeout(() => {
                fetchReport();
                setConsolidating(false);
            }, 2000);
        } catch (err: any) {
            alert(`Error: ${err.message}`);
            setConsolidating(false);
        }
    };

    useEffect(() => {
        fetchReport();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchReport, 30000);
        return () => clearInterval(interval);
    }, []);

    const getHealthIcon = (health: string) => {
        switch (health) {
            case "good":
                return <CheckCircleIcon className="h-8 w-8 text-green-500" />;
            case "warning":
                return <ExclamationTriangleIcon className="h-8 w-8 text-yellow-500" />;
            case "critical":
            case "error":
                return <XCircleIcon className="h-8 w-8 text-red-500" />;
            default:
                return null;
        }
    };

    const getHealthColor = (health: string) => {
        switch (health) {
            case "good":
                return "border-green-500 bg-green-500/10";
            case "warning":
                return "border-yellow-500 bg-yellow-500/10";
            case "critical":
            case "error":
                return "border-red-500 bg-red-500/10";
            default:
                return "border-slate-600";
        }
    };

    const getPriorityBadge = (priority: string) => {
        const classes = {
            critical: "bg-red-600 text-white",
            high: "bg-orange-600 text-white",
            medium: "bg-yellow-600 text-black",
            low: "bg-blue-600 text-white",
        };
        return classes[priority as keyof typeof classes] || "bg-slate-600 text-white";
    };

    if (loading && !report) {
        return (
            <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                <div className="container mx-auto px-4 py-8">
                    <div className="flex items-center justify-center h-96">
                        <ArrowPathIcon className="h-12 w-12 text-blue-500 animate-spin" />
                    </div>
                </div>
            </main>
        );
    }

    if (error || !report) {
        return (
            <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                <div className="container mx-auto px-4 py-8">
                    <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 text-center">
                        <XCircleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
                        <h2 className="text-xl font-bold text-white mb-2">Erro ao carregar dados</h2>
                        <p className="text-slate-300">{error || "Server not responding"}</p>
                        <button
                            onClick={fetchReport}
                            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded"
                        >
                            Tentar novamente
                        </button>
                    </div>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <Link href="/" className="text-blue-400 hover:text-blue-300 text-sm mb-2 block">
                            ← Voltar
                        </Link>
                        <h1 className="text-4xl font-bold text-white">
                            📊 Data Quality Dashboard
                        </h1>
                        <p className="text-slate-400 mt-2">
                            Monitor de qualidade de dados e fontes
                        </p>
                    </div>
                    <button
                        onClick={fetchReport}
                        disabled={loading}
                        className={`flex items-center gap-2 px-4 py-2 rounded font-bold text-white transition-all ${loading
                            ? "bg-slate-600 cursor-not-allowed"
                            : "bg-blue-600 hover:bg-blue-500"
                            }`}
                    >
                        <ArrowPathIcon className={`h-5 w-5 ${loading ? "animate-spin" : ""}`} />
                        Atualizar
                    </button>
                </div>

                {lastUpdate && (
                    <p className="text-slate-500 text-sm mb-6">
                        Última atualização: {lastUpdate.toLocaleTimeString("pt-PT")}
                    </p>
                )}

                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className={`rounded-lg p-6 border-2 ${getHealthColor(report.summary.overall_health)}`}>
                        <div className="flex items-center gap-3 mb-3">
                            {getHealthIcon(report.summary.overall_health)}
                            <h3 className="text-lg font-semibold text-white">Status Geral</h3>
                        </div>
                        <p className="text-slate-300 text-sm">{report.summary.status_message}</p>
                    </div>

                    <div className="bg-red-500/10 border-2 border-red-500 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-white mb-2">Issues Críticos</h3>
                        <p className="text-4xl font-bold text-red-500">{report.summary.critical_issues}</p>
                    </div>

                    <div className="bg-yellow-500/10 border-2 border-yellow-500 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-white mb-2">Avisos</h3>
                        <p className="text-4xl font-bold text-yellow-500">{report.summary.warnings}</p>
                    </div>
                </div>

                {/* Teams Analysis */}
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700 mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <h2 className="text-2xl font-bold text-white">🏆 Equipas</h2>
                            {getHealthIcon(report.teams.health)}
                        </div>

                        {report.teams.duplicates_count > 0 && (
                            <button
                                onClick={triggerTeamConsolidation}
                                disabled={consolidating}
                                className={`flex items-center gap-2 px-4 py-2 rounded font-bold text-white transition-all ${consolidating
                                        ? "bg-slate-600 cursor-not-allowed"
                                        : "bg-orange-600 hover:bg-orange-500"
                                    }`}
                            >
                                <ArrowPathIcon className={`h-5 w-5 ${consolidating ? "animate-spin" : ""}`} />
                                {consolidating ? "Consolidando..." : `Consolidar ${report.teams.duplicates_count} Duplicados`}
                            </button>
                        )}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                            <p className="text-slate-400 text-sm">Total</p>
                            <p className="text-2xl font-bold text-white">{report.teams.total}</p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Duplicados</p>
                            <p className={`text-2xl font-bold ${report.teams.duplicates_count > 0 ? "text-red-500" : "text-green-500"}`}>
                                {report.teams.duplicates_count}
                            </p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Sem Liga</p>
                            <p className="text-2xl font-bold text-slate-300">{report.teams.without_league}</p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Sem País</p>
                            <p className="text-2xl font-bold text-slate-300">{report.teams.without_country}</p>
                        </div>
                    </div>

                    {report.teams.duplicates && report.teams.duplicates.length > 0 && (
                        <div className="mt-4">
                            <h3 className="text-sm font-semibold text-slate-300 mb-2">Duplicados Detectados:</h3>
                            <div className="space-y-1">
                                {report.teams.duplicates.slice(0, 5).map((dup: any, idx: number) => (
                                    <div key={idx} className="text-sm text-slate-400 bg-slate-900/50 p-2 rounded">
                                        {dup.name} ({dup.count}x)
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Matches Coverage */}
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700 mb-6">
                    <div className="flex items-center gap-3 mb-4">
                        <h2 className="text-2xl font-bold text-white">⚽ Jogos</h2>
                        {getHealthIcon(report.matches.health)}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                        <div>
                            <p className="text-slate-400 text-sm">Total</p>
                            <p className="text-2xl font-bold text-white">{report.matches.total}</p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Finalizados</p>
                            <p className="text-2xl font-bold text-green-500">{report.matches.finished}</p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Agendados</p>
                            <p className="text-2xl font-bold text-blue-500">{report.matches.scheduled}</p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Com Odds</p>
                            <p className="text-2xl font-bold text-purple-500">{report.matches.with_odds}</p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Cobertura Odds</p>
                            <p className={`text-2xl font-bold ${report.matches.odds_coverage_percentage >= 80 ? "text-green-500" :
                                report.matches.odds_coverage_percentage >= 60 ? "text-yellow-500" : "text-red-500"
                                }`}>
                                {report.matches.odds_coverage_percentage}%
                            </p>
                        </div>
                    </div>

                    {report.matches.leagues && report.matches.leagues.length > 0 && (
                        <div className="mt-4">
                            <h3 className="text-sm font-semibold text-slate-300 mb-2">Por Liga:</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                {report.matches.leagues.map((league: any, idx: number) => (
                                    <div key={idx} className="bg-slate-900/50 p-3 rounded flex justify-between items-center">
                                        <span className="text-white font-medium">{league.name}</span>
                                        <span className="text-slate-400 text-sm">
                                            {league.total} jogos ({league.finished} fin., {league.scheduled} agend.)
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Odds Coverage */}
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700 mb-6">
                    <div className="flex items-center gap-3 mb-4">
                        <h2 className="text-2xl font-bold text-white">💰 Odds</h2>
                        {getHealthIcon(report.odds.health)}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                            <p className="text-slate-400 text-sm">Total Registos</p>
                            <p className="text-2xl font-bold text-white">{report.odds.total}</p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Jogos Cobertos</p>
                            <p className="text-2xl font-bold text-purple-500">{report.odds.unique_matches_covered}</p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Cobertura</p>
                            <p className={`text-2xl font-bold ${report.odds.coverage_percentage >= 80 ? "text-green-500" :
                                report.odds.coverage_percentage >= 60 ? "text-yellow-500" : "text-red-500"
                                }`}>
                                {report.odds.coverage_percentage}%
                            </p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Últimos 7 dias</p>
                            <p className="text-2xl font-bold text-blue-500">{report.odds.recent_7_days}</p>
                        </div>
                    </div>

                    {report.odds.by_bookmaker && report.odds.by_bookmaker.length > 0 && (
                        <div className="mt-4">
                            <h3 className="text-sm font-semibold text-slate-300 mb-2">Por Bookmaker:</h3>
                            <div className="flex flex-wrap gap-2">
                                {report.odds.by_bookmaker.map((bm: any, idx: number) => (
                                    <div key={idx} className="bg-slate-900/50 px-3 py-2 rounded">
                                        <span className="text-white font-medium">{bm.name}</span>
                                        <span className="text-slate-400 text-sm ml-2">({bm.count})</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Odds Collector Status */}
                {report.odds_collector && (
                    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700 mb-6">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <h2 className="text-2xl font-bold text-white">🔄 Odds Collector</h2>
                                {report.odds_collector.status === "good" && (
                                    <CheckCircleIcon className="h-6 w-6 text-green-500" />
                                )}
                                {report.odds_collector.status === "warning" && (
                                    <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500" />
                                )}
                                {report.odds_collector.status === "critical" && (
                                    <XCircleIcon className="h-6 w-6 text-red-500" />
                                )}
                            </div>

                            <button
                                onClick={triggerOddsCollection}
                                disabled={collecting}
                                className={`flex items-center gap-2 px-4 py-2 rounded font-bold text-white transition-all ${collecting
                                    ? "bg-slate-600 cursor-not-allowed"
                                    : "bg-blue-600 hover:bg-blue-500"
                                    }`}
                            >
                                <ArrowPathIcon className={`h-5 w-5 ${collecting ? "animate-spin" : ""}`} />
                                {collecting ? "Executando..." : "Executar Agora"}
                            </button>
                        </div>

                        <div className={`p-4 rounded-lg border-l-4 ${report.odds_collector.status === "good"
                            ? "border-green-500 bg-green-500/10"
                            : report.odds_collector.status === "warning"
                                ? "border-yellow-500 bg-yellow-500/10"
                                : "border-red-500 bg-red-500/10"
                            }`}>
                            <p className="text-white font-medium mb-2">{report.odds_collector.message}</p>
                            {report.odds_collector.last_run && (
                                <div className="text-sm text-slate-300">
                                    <p>Última execução: {new Date(report.odds_collector.last_run).toLocaleString("pt-PT")}</p>
                                    <p className="mt-1">
                                        Há {report.odds_collector.days_ago} dias
                                        {report.odds_collector.hours_ago < 24 && ` (${report.odds_collector.hours_ago}h)`}
                                    </p>
                                </div>
                            )}
                            {report.odds_collector.status === "critical" && (
                                <div className="mt-3 text-xs bg-red-900/30 p-2 rounded">
                                    ⚠️ <strong>Atenção:</strong> Execute o collector diariamente para construir histórico de odds!
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Recommendations */}
                {report.recommendations && report.recommendations.length > 0 && (
                    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                        <h2 className="text-2xl font-bold text-white mb-4">💡 Recomendações</h2>
                        <div className="space-y-3">
                            {report.recommendations.map((rec, idx) => (
                                <div
                                    key={idx}
                                    className={`p-4 rounded-lg border-l-4 ${rec.priority === "critical" ? "border-red-500 bg-red-500/10" :
                                        rec.priority === "high" ? "border-orange-500 bg-orange-500/10" :
                                            rec.priority === "medium" ? "border-yellow-500 bg-yellow-500/10" :
                                                "border-blue-500 bg-blue-500/10"
                                        }`}
                                >
                                    <div className="flex items-start justify-between mb-2">
                                        <span className={`text-xs font-bold px-2 py-1 rounded ${getPriorityBadge(rec.priority)}`}>
                                            {rec.priority.toUpperCase()}
                                        </span>
                                        <span className="text-xs text-slate-400 uppercase">{rec.category}</span>
                                    </div>
                                    <p className="text-white font-medium mb-1">{rec.message}</p>
                                    <p className="text-slate-300 text-sm mb-2">→ {rec.action}</p>
                                    {rec.script && (
                                        <code className="text-xs bg-slate-900 text-green-400 px-2 py-1 rounded block">
                                            {rec.script}
                                        </code>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
