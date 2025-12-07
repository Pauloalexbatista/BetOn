"use client"

import { useState, useEffect } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import UniversalFilter from "@/components/shared/UniversalFilter"
import { ChartBarIcon, ChartPieIcon, ShieldCheckIcon, ArrowTrendingUpIcon } from "@heroicons/react/24/solid"

// New Interface matching backend list response
interface LeagueStat {
    league: string
    season: string
    total_matches: number
    avg_goals: number
    btts_pct: number
    over_1_5_pct: number
    over_2_5_pct: number
    home_win_pct: number
    draw_pct: number
    away_win_pct: number
    team?: string // New field for team-specific stats
}

export default function LeagueAnalysisPage() {
    const searchParams = useSearchParams()

    // Read from URL (default to empty string for "All")
    const league = searchParams.get("league") || ""
    const season = searchParams.get("season")

    // State
    const [data, setData] = useState<LeagueStat[]>([])
    const [summary, setSummary] = useState<LeagueStat | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Sorting State
    const [sortConfig, setSortConfig] = useState<{ key: keyof LeagueStat, direction: 'asc' | 'desc' } | null>(null)

    // Helper: Calculate Grand Total (Weighted Average)
    const calculateSummary = (items: LeagueStat[]) => {
        try {
            if (items.length === 0) {
                setSummary(null)
                return
            }

            const totalMatches = items.reduce((sum, item) => sum + item.total_matches, 0)

            if (totalMatches === 0) {
                setSummary(null)
                return
            }

            const weightedAvg = (key: keyof LeagueStat) => {
                const sum = items.reduce((acc, item) => {
                    const val = Number(item[key])
                    return acc + (isNaN(val) ? 0 : val) * item.total_matches
                }, 0)
                return Number((sum / totalMatches).toFixed(1))
            }

            const avgGoals = items.reduce((acc, item) => acc + (Number(item.avg_goals) * item.total_matches), 0) / totalMatches

            setSummary({
                league: items[0]?.league || "Múltiplas",
                season: "TOTAL",
                total_matches: totalMatches,
                avg_goals: Number(avgGoals.toFixed(2)),
                btts_pct: weightedAvg("btts_pct"),
                over_1_5_pct: weightedAvg("over_1_5_pct"),
                over_2_5_pct: weightedAvg("over_2_5_pct"),
                home_win_pct: weightedAvg("home_win_pct"),
                draw_pct: weightedAvg("draw_pct"),
                away_win_pct: weightedAvg("away_win_pct")
            })
        } catch (e) {
            console.error("Summary calc error", e)
            setError("Erro ao calcular sumário.")
        }
    }

    // Fetch data
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true)
            setError(null)
            try {
                const query = new URLSearchParams()
                if (league) query.set("league", league)
                if (season) query.set("season", season)

                const res = await fetch(`http://localhost:8000/api/analysis/league-pulse?${query.toString()}`)
                if (res.ok) {
                    const json: LeagueStat[] = await res.json()
                    setData(json)
                    calculateSummary(json)
                } else {
                    console.error("Failed to fetch data", res.status)
                    setError(`Erro API: ${res.status}`)
                }
            } catch (error) {
                console.error("Error fetching league pulse:", error)
                setError("Erro de conexão.")
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [league, season])


    // Sort Helper (Generic)
    const sortData = (items: LeagueStat[], config: { key: keyof LeagueStat, direction: 'asc' | 'desc' } | null) => {
        if (!config) return items
        return [...items].sort((a, b) => {
            const { key, direction } = config
            let aValue: any = a[key]
            let bValue: any = b[key]
            // Handle string
            if (typeof aValue === 'string') {
                return direction === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue)
            }
            // Handle number
            return direction === 'asc' ? aValue - bValue : bValue - aValue
        })
    }

    const handleSort = (key: keyof LeagueStat) => {
        let direction: 'asc' | 'desc' = 'desc' // Default stats to desc
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'desc') {
            direction = 'asc'
        }
        setSortConfig({ key, direction })
    }

    const sortedData = sortData(data, sortConfig)

    const SortIcon = ({ config, column }: { config: any, column: keyof LeagueStat }) => {
        if (config?.key !== column) return <span className="text-slate-600 ml-1 text-xs opacity-50">⇅</span>
        return config.direction === 'asc' ? <span className="text-blue-400 ml-1">↑</span> : <span className="text-blue-400 ml-1">↓</span>
    }

    // Determine dynamic title
    const getPageTitle = () => {
        if (league && !season) return `Histórico Completo: ${league}`
        if (!league && season) return `Comparativo Ligas: ${season}`
        if (league && season) return `Análise Detalhada: ${league} (${season})`
        return "Visão Global"
    }

    return (
        <div className="p-8 space-y-8 min-h-screen bg-background/50">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-4xl font-black bg-gradient-to-r from-pink-500 via-rose-500 to-purple-600 bg-clip-text text-transparent">
                        Pulso do Campeonato 💓
                    </h1>
                    <p className="text-muted-foreground mt-2 text-lg">
                        {getPageTitle()}
                    </p>
                </div>

                {/* Navigation Buttons */}
                <div className="flex gap-4 items-center">
                    <Link href="/analysis/teams" className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded font-bold shadow-lg hover:shadow-blue-500/20 driver-step-teams transition-all">
                        Ver Equipas 🏃‍♂️
                    </Link>
                    <Link href="/" className="text-muted-foreground hover:text-primary transition-colors flex items-center gap-2">
                        ← Voltar ao Dashboard
                    </Link>
                </div>
            </div>

            {/* Filters */}
            <UniversalFilter />

            {/* Loader */}
            {loading && <div className="text-center py-20 text-xl animate-pulse">A carregar dados... 🩺</div>}

            {/* Error */}
            {error && <div className="p-4 bg-red-900/50 text-red-200 rounded border border-red-700 text-center">{error}</div>}

            {/* Content */}
            {!loading && summary && (
                <div className="space-y-8">

                    {/* 1. Grand Summary Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {/* Avg Goals */}
                        <Card className="border-l-4 border-l-blue-500 shadow-lg bg-slate-900/50">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Média Global</CardTitle>
                                <ChartBarIcon className="h-4 w-4 text-blue-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-4xl font-bold text-blue-400">{summary.avg_goals}</div>
                                <p className="text-xs text-muted-foreground mt-1">Golos por Jogo</p>
                            </CardContent>
                        </Card>

                        {/* Over 2.5 */}
                        <Card className="border-l-4 border-l-green-500 shadow-lg bg-slate-900/50">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Global Over 2.5</CardTitle>
                                <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-4xl font-bold text-green-400">{summary.over_2_5_pct}%</div>
                                <div className="text-xs font-semibold text-green-600 mt-2">Over 1.5: {summary.over_1_5_pct}%</div>
                            </CardContent>
                        </Card>

                        {/* BTTS */}
                        <Card className="border-l-4 border-l-orange-500 shadow-lg bg-slate-900/50">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Global BTTS</CardTitle>
                                <ChartPieIcon className="h-4 w-4 text-orange-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-4xl font-bold text-orange-400">{summary.btts_pct}%</div>
                                <p className="text-xs text-muted-foreground mt-1">Ambas Marcam</p>
                            </CardContent>
                        </Card>

                        {/* Home Win */}
                        <Card className="border-l-4 border-l-purple-500 shadow-lg bg-slate-900/50">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Taxa Vitória Casa</CardTitle>
                                <ShieldCheckIcon className="h-4 w-4 text-purple-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-4xl font-bold text-purple-400">{summary.home_win_pct}%</div>
                                <div className="flex gap-2 mt-2 text-xs text-muted-foreground">
                                    <span>E: {summary.draw_pct}%</span>
                                    <span>F: {summary.away_win_pct}%</span>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* 2. Detailed Table (League Breakdown) */}
                    {sortedData.length > 0 && (
                        <div className="bg-slate-900 rounded-lg shadow border border-slate-800 overflow-hidden">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-slate-950 text-slate-400 border-b border-slate-800 select-none">
                                        <th className="p-4 font-semibold hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('league')}>
                                            Liga <SortIcon config={sortConfig} column="league" />
                                        </th>
                                        <th className="p-4 font-semibold hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('season')}>
                                            Época <SortIcon config={sortConfig} column="season" />
                                        </th>
                                        <th className="p-4 font-semibold text-center hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('total_matches')}>
                                            Jogos <SortIcon config={sortConfig} column="total_matches" />
                                        </th>
                                        <th className="p-4 font-semibold text-center text-blue-400 hover:text-blue-300 cursor-pointer transition-colors" onClick={() => handleSort('avg_goals')}>
                                            Golos/Jogo <SortIcon config={sortConfig} column="avg_goals" />
                                        </th>
                                        <th className="p-4 font-semibold text-center text-green-400 hover:text-green-300 cursor-pointer transition-colors" onClick={() => handleSort('over_2_5_pct')}>
                                            +2.5 (%) <SortIcon config={sortConfig} column="over_2_5_pct" />
                                        </th>
                                        <th className="p-4 font-semibold text-center text-orange-400 hover:text-orange-300 cursor-pointer transition-colors" onClick={() => handleSort('btts_pct')}>
                                            BTTS (%) <SortIcon config={sortConfig} column="btts_pct" />
                                        </th>
                                        <th className="p-4 font-semibold text-center text-purple-400 hover:text-purple-300 cursor-pointer transition-colors" onClick={() => handleSort('home_win_pct')}>
                                            Casa (%) <SortIcon config={sortConfig} column="home_win_pct" />
                                        </th>
                                        <th className="p-4 font-semibold text-center hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('draw_pct')}>
                                            Empate (%) <SortIcon config={sortConfig} column="draw_pct" />
                                        </th>
                                        <th className="p-4 font-semibold text-center hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('away_win_pct')}>
                                            Fora (%) <SortIcon config={sortConfig} column="away_win_pct" />
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800">
                                    {sortedData.map((row) => (
                                        <tr key={`${row.league}-${row.season}`} className="hover:bg-slate-800/50 transition-colors">
                                            <td className="p-4 font-medium text-white">{row.league}</td>
                                            <td className="p-4 text-slate-400">{row.season}</td>
                                            <td className="p-4 text-center text-slate-300">{row.total_matches}</td>
                                            <td className="p-4 text-center font-bold text-blue-400">{row.avg_goals}</td>
                                            <td className="p-4 text-center font-bold text-green-400">{row.over_2_5_pct}%</td>
                                            <td className="p-4 text-center font-bold text-orange-400">{row.btts_pct}%</td>
                                            <td className="p-4 text-center font-bold text-purple-400">{row.home_win_pct}%</td>
                                            <td className="p-4 text-center text-slate-500">{row.draw_pct}%</td>
                                            <td className="p-4 text-center text-slate-500">{row.away_win_pct}%</td>
                                        </tr>
                                    ))}
                                    {/* Footer / Total Row */}
                                    <tr className="bg-slate-950/80 font-bold border-t-2 border-slate-700">
                                        <td className="p-4 text-white" colSpan={2}>TOTAL / MÉDIA GLOBAL</td>
                                        <td className="p-4 text-center text-white">{summary.total_matches}</td>
                                        <td className="p-4 text-center text-blue-400">{summary.avg_goals}</td>
                                        <td className="p-4 text-center text-green-400">{summary.over_2_5_pct}%</td>
                                        <td className="p-4 text-center text-orange-400">{summary.btts_pct}%</td>
                                        <td className="p-4 text-center text-purple-400">{summary.home_win_pct}%</td>
                                        <td className="p-4 text-center text-slate-400">{summary.draw_pct}%</td>
                                        <td className="p-4 text-center text-slate-400">{summary.away_win_pct}%</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {!loading && data.length === 0 && !error && (
                <div className="text-center py-20 text-muted-foreground">
                    Sem dados para mostrar com estes filtros. 🧹
                </div>
            )}

        </div>
    )
}
