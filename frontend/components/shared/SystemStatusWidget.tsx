"use client";

import { useState, useEffect } from "react";
import { ChartBarIcon, ServerIcon, DatabaseIcon } from "@heroicons/react/24/solid";

interface APIStatus {
    api_football: {
        configured: boolean;
        status: string;
        quota?: {
            limit_day: number | string;
            current: number;
            remaining: number | null;
        };
        usage?: {
            today: number;
            percentage: number;
        };
    };
    the_odds_api: {
        configured: boolean;
        status: string;
        info?: {
            note: string;
            free_tier_limit: string;
        };
    };
}

interface DatabaseStatus {
    status: string;
    counts: {
        teams: number;
        matches_total: number;
        matches_finished: number;
        matches_scheduled: number;
        odds: number;
        strategies: number;
        bets: number;
    };
    warnings: string[];
    suggestions: (string | null)[];
}

export default function SystemStatusWidget() {
    const [apiStatus, setApiStatus] = useState<APIStatus | null>(null);
    const [dbStatus, setDbStatus] = useState<DatabaseStatus | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const [apiRes, dbRes] = await Promise.all([
                    fetch("http://localhost:8000/api/system/api-status"),
                    fetch("http://localhost:8000/api/system/database-status")
                ]);

                if (apiRes.ok) {
                    const apiData = await apiRes.json();
                    setApiStatus(apiData);
                }

                if (dbRes.ok) {
                    const dbData = await dbRes.json();
                    setDbStatus(dbData);
                }
            } catch (error) {
                console.error("Error fetching system status:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStatus();
        // Refresh every 5 minutes
        const interval = setInterval(fetchStatus, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
                <div className="animate-pulse text-slate-400">A carregar status do sistema...</div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* API Status */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
                <div className="flex items-center gap-2 mb-3">
                    <ServerIcon className="h-5 w-5 text-blue-400" />
                    <h3 className="font-semibold text-white">APIs Status</h3>
                </div>

                {apiStatus && (
                    <div className="space-y-3">
                        {/* API-Football */}
                        <div className="bg-slate-900/50 rounded p-3">
                            <div className="flex justify-between items-start mb-2">
                                <span className="text-sm font-medium text-slate-300">API-Football</span>
                                <span className={`text-xs px-2 py-1 rounded ${apiStatus.api_football.status === "active"
                                        ? "bg-green-900 text-green-300"
                                        : "bg-slate-700 text-slate-400"
                                    }`}>
                                    {apiStatus.api_football.configured ? apiStatus.api_football.status : "Não configurada"}
                                </span>
                            </div>

                            {apiStatus.api_football.quota && (
                                <div className="space-y-1">
                                    <div className="flex justify-between text-xs">
                                        <span className="text-slate-400">Usado hoje</span>
                                        <span className="text-white font-mono">
                                            {apiStatus.api_football.quota.current} / {apiStatus.api_football.quota.limit_day}
                                        </span>
                                    </div>
                                    {apiStatus.api_football.usage && (
                                        <>
                                            <div className="w-full bg-slate-700 rounded-full h-2">
                                                <div
                                                    className={`h-2 rounded-full transition-all ${apiStatus.api_football.usage.percentage > 80
                                                            ? "bg-red-500"
                                                            : apiStatus.api_football.usage.percentage > 50
                                                                ? "bg-yellow-500"
                                                                : "bg-green-500"
                                                        }`}
                                                    style={{ width: `${apiStatus.api_football.usage.percentage}%` }}
                                                />
                                            </div>
                                            <div className="text-xs text-slate-400 text-right">
                                                {apiStatus.api_football.usage.percentage}% usado
                                            </div>
                                        </>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* The Odds API */}
                        <div className="bg-slate-900/50 rounded p-3">
                            <div className="flex justify-between items-start mb-2">
                                <span className="text-sm font-medium text-slate-300">The Odds API</span>
                                <span className={`text-xs px-2 py-1 rounded ${apiStatus.the_odds_api.configured
                                        ? "bg-blue-900 text-blue-300"
                                        : "bg-slate-700 text-slate-400"
                                    }`}>
                                    {apiStatus.the_odds_api.configured ? "Configurada" : "Não configurada"}
                                </span>
                            </div>
                            {apiStatus.the_odds_api.info && (
                                <div className="text-xs text-slate-400 mt-2">
                                    {apiStatus.the_odds_api.info.free_tier_limit}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Database Status */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
                <div className="flex items-center gap-2 mb-3">
                    <DatabaseIcon className="h-5 w-5 text-purple-400" />
                    <h3 className="font-semibold text-white">Base de Dados</h3>
                </div>

                {dbStatus && (
                    <div className="space-y-3">
                        <div className="grid grid-cols-2 gap-2 text-xs">
                            <div className="bg-slate-900/50 rounded p-2">
                                <div className="text-slate-400">Jogos</div>
                                <div className="text-white font-bold text-lg">{dbStatus.counts.matches_total}</div>
                            </div>
                            <div className="bg-slate-900/50 rounded p-2">
                                <div className="text-slate-400">Equipas</div>
                                <div className="text-white font-bold text-lg">{dbStatus.counts.teams}</div>
                            </div>
                            <div className="bg-slate-900/50 rounded p-2">
                                <div className="text-slate-400">Odds</div>
                                <div className="text-white font-bold text-lg">{dbStatus.counts.odds}</div>
                            </div>
                            <div className="bg-slate-900/50 rounded p-2">
                                <div className="text-slate-400">Estratégias</div>
                                <div className="text-white font-bold text-lg">{dbStatus.counts.strategies}</div>
                            </div>
                        </div>

                        {dbStatus.warnings.length > 0 && (
                            <div className="bg-yellow-900/20 border border-yellow-700/50 rounded p-2">
                                <div className="text-xs text-yellow-400 space-y-1">
                                    {dbStatus.warnings.map((warning, idx) => (
                                        <div key={idx}>⚠️ {warning}</div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
