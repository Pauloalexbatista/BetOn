"use client"

import { useState, useEffect } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import Link from "next/link"
import UniversalFilter from "@/components/shared/UniversalFilter"

interface TeamStat {
    team: string
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
}

export default function TeamAnalysisPage() {
    const searchParams = useSearchParams()

    // Read from URL
    const league = searchParams.get("league") || ""
    const season = searchParams.get("season")

    const [data, setData] = useState<TeamStat[]>([])
    const [loading, setLoading] = useState(false)

    // Default sorting: Weakest Home Team (as requested by user previously) or Alphabetical
    const [sortConfig, setSortConfig] = useState<{ key: keyof TeamStat, direction: 'asc' | 'desc' } | null>({ key: "home_win_pct", direction: "asc" })

    // Fetch data
    useEffect(() => {
        const fetchData = async () => {
            // Only fetch if we have some filter? Or allow global?
            // Global fetch of ALL teams might be heavy but manageable (<500 rows).
            // Let's allow it.
            setLoading(true)
            try {
                const query = new URLSearchParams()
                if (league) query.set("league", league)
                if (season) query.set("season", season)

                // Use the Team Pulse endpoint
                const res = await fetch(`http://localhost:8000/api/analysis/team-pulse?${query.toString()}`)
                if (res.ok) {
                    const json: TeamStat[] = await res.json()
                    setData(json)
                } else {
                    console.error("Failed to fetch team data", res.status)
                    setData([])
                }
            } catch (error) {
                console.error("Error fetching team pulse:", error)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [league, season])

    // Sort Helper
    const handleSort = (key: keyof TeamStat) => {
        let direction: 'asc' | 'desc' = 'desc' // Default stats to desc (highest first)
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'desc') {
            direction = 'asc'
        }
        setSortConfig({ key, direction })
    }

    const sortedData = [...data].sort((a, b) => {
        if (!sortConfig) return 0
        const { key, direction } = sortConfig

        let aValue: any = a[key]
        let bValue: any = b[key]

        // Handle string comparison for league/season/team
        if (typeof aValue === 'string') {
            return direction === 'asc'
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue)
        }

        // Handle numeric comparison
        return direction === 'asc' ? aValue - bValue : bValue - aValue
    })

    const SortIcon = ({ column }: { column: keyof TeamStat }) => {
        if (sortConfig?.key !== column) return <span className="text-slate-600 ml-1 text-xs opacity-50">⇅</span>
        return sortConfig.direction === 'asc' ? <span className="text-blue-400 ml-1">↑</span> : <span className="text-blue-400 ml-1">↓</span>
    }

    // Determine dynamic title
    const getPageTitle = () => {
        if (league && !season) return `Análise de Equipas: ${league}`
        if (!league && season) return `Comparativo de Equipas: ${season}`
        if (league && season) return `Detalhe: ${league} (${season})`
        return "Visão Global de Equipas"
    }

    return (
        <div className="p-8 space-y-8 min-h-screen bg-background/50">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-4xl font-black bg-gradient-to-r from-teal-500 via-emerald-500 to-green-600 bg-clip-text text-transparent">
                        Pulso das Equipas 🏃
                    </h1>
                    <p className="text-muted-foreground mt-2 text-lg">
                        {getPageTitle()}
                    </p>
                </div>

                {/* Navigation Buttons */}
                <div className="flex gap-4 items-center">
                    <Link href="/analysis/league" className="bg-pink-600 hover:bg-pink-500 text-white px-4 py-2 rounded font-bold shadow-lg hover:shadow-pink-500/20 transition-all">
                        Ver Campeonatos 💓
                    </Link>
                    <Link href="/" className="text-muted-foreground hover:text-primary transition-colors flex items-center gap-2">
                        ← Voltar ao Dashboard
                    </Link>
                </div>
            </div>

            {/* Filters */}
            <UniversalFilter />

            {/* Loader */}
            {loading && <div className="text-center py-20 text-xl animate-pulse">A carregar estatísticas das equipas... 🩺</div>}

            {/* Content */}
            {!loading && (
                <div className="space-y-8">
                    <div className="bg-slate-900 rounded-lg shadow border border-slate-800 overflow-hidden">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-950 text-slate-400 border-b border-slate-800 select-none">
                                    <th className="p-4 font-semibold hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('team')}>
                                        Equipa <SortIcon column="team" />
                                    </th>
                                    {/* Optional: Show League if mixed view */}
                                    {!league && (
                                        <th className="p-4 font-semibold hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('league')}>
                                            Liga <SortIcon column="league" />
                                        </th>
                                    )}
                                    <th className="p-4 font-semibold text-center hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('total_matches')}>
                                        Jogos <SortIcon column="total_matches" />
                                    </th>
                                    <th className="p-4 font-semibold text-center text-blue-400 hover:text-blue-300 cursor-pointer transition-colors" onClick={() => handleSort('avg_goals')}>
                                        Golos (Média) <SortIcon column="avg_goals" />
                                    </th>
                                    <th className="p-4 font-semibold text-center text-green-400 hover:text-green-300 cursor-pointer transition-colors" onClick={() => handleSort('over_2_5_pct')}>
                                        +2.5 (%) <SortIcon column="over_2_5_pct" />
                                    </th>
                                    <th className="p-4 font-semibold text-center text-orange-400 hover:text-orange-300 cursor-pointer transition-colors" onClick={() => handleSort('btts_pct')}>
                                        BTTS (%) <SortIcon column="btts_pct" />
                                    </th>
                                    <th className="p-4 font-semibold text-center text-purple-400 hover:text-purple-300 cursor-pointer transition-colors" onClick={() => handleSort('home_win_pct')}>
                                        Vitória Casa (%) <SortIcon column="home_win_pct" />
                                    </th>
                                    <th className="p-4 font-semibold text-center hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('draw_pct')}>
                                        Empate (Global) <SortIcon column="draw_pct" />
                                    </th>
                                    <th className="p-4 font-semibold text-center hover:text-white cursor-pointer transition-colors" onClick={() => handleSort('away_win_pct')}>
                                        Vitória Fora (%) <SortIcon column="away_win_pct" />
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {sortedData.length > 0 ? sortedData.map((row) => (
                                    <tr key={`${row.team}-${row.season}`} className="hover:bg-slate-800/50 transition-colors">
                                        <td className="p-4 font-medium text-white">{row.team}</td>
                                        {!league && <td className="p-4 text-slate-400 text-sm">{row.league}</td>}
                                        <td className="p-4 text-center text-slate-300">{row.total_matches}</td>
                                        <td className="p-4 text-center font-bold text-blue-400">{row.avg_goals}</td>
                                        <td className="p-4 text-center font-bold text-green-400">{row.over_2_5_pct}%</td>
                                        <td className="p-4 text-center font-bold text-orange-400">{row.btts_pct}%</td>
                                        <td className="p-4 text-center font-bold text-purple-400">{row.home_win_pct}%</td>
                                        <td className="p-4 text-center text-slate-500">{row.draw_pct}%</td>
                                        <td className="p-4 text-center text-slate-500">{row.away_win_pct}%</td>
                                    </tr>
                                )) : (
                                    <tr>
                                        <td colSpan={9} className="p-8 text-center text-slate-500">
                                            Sem dados para mostrar. Tente ajustar os filtros.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}
